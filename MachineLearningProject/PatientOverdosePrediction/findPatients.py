from math import floor
import pandas as pd
import datetime as dt
import numpy as np

def main():
    #read in patients.csv
    patients = pd.read_csv('./datasets/patients.csv')
    #read in encounters.csv
    encounters = pd.read_csv('./datasets/encounters.csv')
    #see what the data looks like
    # print(encounters.head(10))
    #change date to datetime
    encounters['START'] = pd.to_datetime(encounters['START'])
    encounters['STOP'] = pd.to_datetime(encounters['STOP'])
    #check the info
    # print(encounters.info())
    ## Part 1
    #filter for drug overdose that happened after July 15, 1999
    drug_overdose = encounters[(encounters['REASONDESCRIPTION'] == 
    'Drug overdose') & (encounters['START'] > '1999-07-15')]
    #get patients age befor July 15, 1999
    patients['DOB'] = pd.to_datetime(patients['BIRTHDATE'])
    patients['Age'] = patients['DOB'].apply(lambda x: floor((dt.datetime(1999, 7, 15) - x).days/365)).astype(int)
    #get patients whose Age are 18 to 35 years old and save to a new dataframe
    patients_18_35 = patients[(patients['Age'] >= 18) & (patients['Age'] <= 35)]
    drug_overdose_encounters = drug_overdose[drug_overdose['PATIENT'].isin(patients_18_35['Id'])]

    ## Part 2
    #change deathdate to datetime
    drug_overdose_encounters = pd.merge(drug_overdose_encounters,
     patients_18_35,
     left_on='PATIENT', right_on='Id')
    print(drug_overdose_encounters.info())
    # change Id x to ENCOUNTER
    drug_overdose_encounters = \
        drug_overdose_encounters.rename(\
            columns={'Id_x': 'ENCOUNTER'})
    drug_overdose_encounters['DEATH_AT_VISIT_IND'] = np.zeros(len(drug_overdose_encounters))
    checkIfDeadInVisit(drug_overdose_encounters)
    print(drug_overdose_encounters.head(10))
    #extract the data we need
    od_encounter = drug_overdose_encounters[\
        ['PATIENT','ENCOUNTER','START','STOP',
        'Age','DEATH_AT_VISIT_IND']]
    od_encounter['COUNT_CURRENT_MEDS'] = np.zeros(len(od_encounter))
    #read in medications.csv
    medications = pd.read_csv('./datasets/medications.csv')
    #change date to datetime
    medications['START'] = pd.to_datetime(medications['START'])
    medications['STOP'] = pd.to_datetime(medications['STOP'])
    #find medications that started before July 15, 1999
    part_med = medications[medications['PATIENT'].isin(patients_18_35['Id'])][['START','STOP',
    'PATIENT','ENCOUNTER','DESCRIPTION']]
    print(part_med.info())
    print(od_encounter.info())
    # processPartialData(10,od_encounter, medications)
    # print(x)
    getCurrentMedsCount(od_encounter, part_med)
    print(od_encounter.head(10))
    #save current meds count
    od_encounter.to_csv('./datasets/od_encounter_med_count.csv')

    ##find current opioid use
    #read in the od encounter med count 
    # od_encounter = pd.read_csv('./datasets/od_encounter_med_count.csv')
    od_encounter['CURRENT_OPIOID_IND'] = np.zeros(len(od_encounter))
    
    opiod_list = ['Hydromorphone','Fentanyl',
    'Oxycodone-acetaminophen']
    #filter medications that contain opiod
    part_med['CONTAIN_OPIOD'] = \
        part_med.apply(lambda x: containsAny(x['DESCRIPTION'], opiod_list), axis=1)
    opiod_med = part_med[part_med['CONTAIN_OPIOD'] == True]
    print(opiod_med.info())
    checkActiveOpiod(od_encounter, opiod_med)
    
    # find readmission indicators and first readmission date
    # sort od encounter by patient and start date
    od_encounter = od_encounter.sort_values(by=['PATIENT','START'])
    # calculate the difference in days by patients
    od_encounter['START_DATE_DIFF'] = od_encounter.groupby('PATIENT')['START'].diff().dt.days
    od_encounter['START_DATE_DIFF'].fillna(-1)
    # filter out readmission dates
    od_readmit_encounter = od_encounter[od_encounter['START_DATE_DIFF'] > 0]
    findFirstReadmissionDate(od_readmit_encounter)
    find30Readmission(od_readmit_encounter)
    find90Readmission(od_readmit_encounter)
    print(od_readmit_encounter.info())
    #rename columns
    od_readmit_encounter = \
    od_readmit_encounter.rename(columns={'PATIENT': 'PATIENT_ID',
    "ENCOUNTER": "ENCOUNTER_ID",
    "START": "HOSPITAL_ENCOUNTER_DATE",
    "Age":"AGE_AT_VISIT"})
    result = od_readmit_encounter[['PATIENT_ID','ENCOUNTER_ID',
    'AGE_AT_VISIT','HOSPITAL_ENCOUNTER_DATE',
    'DEATH_AT_VISIT_IND','COUNT_CURRENT_MEDS','CURRENT_OPIOID_IND','FIRST_READMISSION_DATE',
    'READMISSION_30_DAY_IND',
    'READMISSION_90_DAY_IND']]
    ## Part 3
    # save to csv
    result.to_csv('./datasets/od_encounter_data.csv', index=False)
    print("saved to csv, finishing data processing.")
    

def containsAny(str, li):
    #check if the string contains any of the items in the list
    for item in li:
        if item in str:
            return True
    return False

def checkIfDeadInVisit(data):
    data['DEATHDATE'] = pd.to_datetime(data['DEATHDATE'])
    for index, row in data.iterrows():
        if row['DEATHDATE'] == 'NA':
            data.loc[index, 'DEATH_AT_VISIT_IND'] = 0
        else:
            if row['DEATHDATE'] >= row['START'] and row['DEATHDATE'] <= row['STOP']:
                data.loc[index, 'DEATH_AT_VISIT_IND'] = 1
   
def getCurrentMedsCount(encounters, medications):
    for index, row in encounters.iterrows():
        patient_id = row['PATIENT']
        startdate = row['START']
        encounters.loc[index, 'COUNT_CURRENT_MEDS'] =\
             countPatientMedication(patient_id,
             startdate, medications)
    print("finish counting current medications")

def processPartialData(number, encounters,medications):
    #process the first n number of encounters
    i = 0
    for index, row in encounters.iterrows():
        if i < number:
            encounters.loc[index, 'COUNT_CURRENT_MEDS'] = countPatientMedication(row['PATIENT'], row['START'], medications)
            i += 1
        else:
            break
     
def countPatientMedication(patient_id, startdate, medications):
    #count the number of medications the patient took before the encounter
    #check if the stop time is NA
    count = 0
    for index, row in medications.iterrows():    
        if row['PATIENT'] == patient_id:
            if (row['STOP'] == 'NA' or row['STOP'] > startdate):
                count += 1
                print("gain more count")
            else:
                print("no count")
    return count

def checkActiveOpiod(drug_overdose, opiod_med):
    #check if the patient is using opiod at the time of drug overdose encounter
    drug_overdose['CURRENT_OPIOD_IND'] =\
                     drug_overdose.apply(lambda x: \
                        getOpiodUseStatus(x['PATIENT'],x['START'],opiod_med), axis=1)
    print("finish checking opiod use before overdose")

def getOpiodUseStatus(patient,startdate,opiod_med):
    #check if the patient is using opiod at the time of drug overdose encounter
    for index2, row2 in opiod_med.iterrows():
        if row2['PATIENT'] == patient:
            if (row2['STOP'] == 'NA' or row2['STOP'] > startdate):
                print('find an opiod use')
                return 1
    return 0

def find90Readmission(readmissions):
    readmissions['READMISSION_90_DAY_IND'] = readmissions.apply(lambda x: \
         1 if x['START_DATE_DIFF'] <= 90 else 0, axis=1)
    print("finish finding 90 day readmission")

def find30Readmission(readmissions):
    readmissions['READMISSION_30_DAY_IND'] = readmissions.apply(lambda x: \
            1 if x['START_DATE_DIFF'] <= 30 else 0, axis=1)
    print("finish finding 30 day readmission")

def findFirstReadmissionDate(admissions):
    admissions['FIRST_READMISSION_DATE'] = admissions.groupby('PATIENT')['START'].transform('min')
    print("finish finding first readmission date")

 
if __name__ == '__main__':
    main()