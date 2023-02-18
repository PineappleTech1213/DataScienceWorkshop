# AB Testing - Data Cleaning and Feature Engineering

## Project Goal: To test if students' emotion sync with the speaker has impact on their educational outcome.

Here is a simple data preprocessing and feature engineering example before AB testing or any other econometrics analysis.

First we imported needed packages, and then we define functions to read in certain datasets.



```{python}
import pandas as pd
import numpy as mp
import matplotlib.pyplot as plt
# import seaborn as sns

#read in participant video data
#path can be changed or left as default
def readInParticipantsVideo(path = 'src/datasets/ParticipantVideoData27Nov2022.csv'):
    par_video = pd.read_csv(path)
    print(par_video.info())
    emotions = []
    for x in par_video.columns:
        if 'emot' in x:
            emotions.append(x)
    print(emotions)
    part_video_data = par_video[['participant_id','video_id','frame_id','second',
    'smile'] + emotions]
    print(part_video_data.info())
    return part_video_data

#read in participant answers data
#path can be changed or left as default
def readInParticipantAnswers(path = 'src/datasets/ParticipantData27Nov2022.csv'):
    par_answers = pd.read_csv(path)
    print(par_answers.info())
    demographics = []
    self_raw_emotions = []
    for x in par_answers.columns:
        if 'dem' in x:
            demographics.append(x)
        if 'self_raw_' in x:
            self_raw_emotions.append(x)
    cols = ['participant_id','video_id','recording_elegible',
    'cam_allowed','azure_features','video_error',
     'correct_pre_quiz','correct_post_quiz'] + demographics + self_raw_emotions
    par_ans_data = par_answers[cols]
    par_ans_data['correct_pre_percent'] = par_ans_data['correct_pre_quiz']/2
    par_ans_data['correct_post_percent'] = par_ans_data['correct_post_quiz']/8
    print(par_ans_data.info())
    return par_ans_data

#read in video data
#path can be changed or left as default
def readInVideoData(path = 'src/datasets/VideosData_ABTestingProject.csv'):
    video_data = pd.read_csv(path)
    print(video_data.info())
    emotions = []
    for x in video_data.columns:
        if 'emot' in x:
            emotions.append(x)
    
    cols = ['video_id', 'frame_id','smile','gender'] + emotions
    part_video_data = video_data[cols]
    print(part_video_data.info())
    return part_video_data
 ```
 As usual, the data reading and processing part are in a main() function for easier manipulation and organization.
 
 First we need to perform aggregation on those datasets to acquired an aggregation result. The entries are recorded every 2 second, and thus fo each individual sample, we need to compute an aggregated result. Since we have defined what columns we need, it is easier to aggregate columns of values at once.
 ```{python}
#acquire aggregated results.
def compressData(dataset, compress_by,emotion_list):
    result = dataset.groupby(compress_by)[emotion_list].mean().reset_index()
    print(result.info())
    return result

#match speaker's emotional data to that of the students
def matchEmotion(participant, videos, emotion_list):
    # merge part and video by participant id , video id, frame id and second
    merged  = pd.merge(participant, videos, 
    on=['video_id'], how='left',
    suffixes=('_par','_vid'))
    print(merged.info())
    print(merged.head(10))
    emotion_diff = []
    for emotion in emotion_list:
        emo_diff = emotion+'_diff'
        emotion_diff.append(emo_diff)
        # create a new column for each emotion
        merged[emo_diff] = merged[emotion + '_par'] - merged[emotion + '_vid']
    result = merged[['participant_id','video_id'] + emotion_diff]
    print(result.info())
    print(result.head(10))
    return result
    
#as titled
def drawDescriptiveData(dataset):
    #draw the distribution of the pre and post quiz
    plt.plot(dataset['correct_pre_percent'],dataset['correct_post_percent'],'o')

```
Lastly we used those functions in the main() function in the ETL pipeline.

```{python}
def main():
    #read in data
    par_ans_data = readInParticipantAnswers("src/datasets/ParticipantData12Dec2022.csv")
    par_video_data = readInParticipantsVideo("src/datasets/ParticipantVideoData12Dec2022.csv")
    video_data = readInVideoData()
    emotion_list = ['emot_happiness','emot_neutral','emot_sadness','emot_surprise']
    compressedParticipantVideo = compressData(par_video_data, ['participant_id','video_id'],emotion_list)
    print(compressedParticipantVideo.head(10))
    compressedVideoData = compressData(video_data, ['video_id'],emotion_list)
    print(compressedVideoData.head(10))
    merged_emotion_data = matchEmotion(compressedParticipantVideo,
    compressedVideoData,emotion_list)
    merged_all_data = pd.merge(par_ans_data, merged_emotion_data,on=['participant_id','video_id'],how='left')
    print(merged_all_data.info())
    print(merged_all_data.head(10))
    merged_all_data.fillna(method='bfill',inplace=True)
    print(merged_all_data.info())
    #print all the columns and their data distribution
    print(merged_all_data.head(10))
    merged_all_data.to_csv('src/datasets/merged_data.csv')
    # matchEmotion(par_video_data,video_data,emotion_list)
    print('finishing')



if __name__ == '__main__':
    main()
 ```

## END
