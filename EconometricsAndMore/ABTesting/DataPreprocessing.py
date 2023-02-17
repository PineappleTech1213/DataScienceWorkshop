Skip to content
Search or jump to…
Pull requests
Issues
Codespaces
Marketplace
Explore
 
@DummyPuppy 
DummyPuppy
/
AB-Testing-Project
Private
Cannot fork because you own this repository and are not a member of any organizations.
Code
Issues
Pull requests
Actions
Projects
Wiki
Security
Insights
Settings
AB-Testing-Project/dataPreprocessing.py /
@DummyPuppy
DummyPuppy added python file for data preprocessing
Latest commit 320dae2 on Dec 13, 2022
 History
 1 contributor
107 lines (99 sloc)  4.13 KB

import pandas as pd
import numpy as mp
import matplotlib.pyplot as plt
# import seaborn as sns

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
def compressData(dataset, compress_by,emotion_list):
    result = dataset.groupby(compress_by)[emotion_list].mean().reset_index()
    print(result.info())
    return result
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
    

def drawDescriptiveData(dataset):
    #draw the distribution of the pre and post quiz
    plt.plot(dataset['correct_pre_percent'],dataset['correct_post_percent'],'o')
if __name__ == '__main__':
    main()
Footer
© 2023 GitHub, Inc.
Footer navigation
Terms
Privacy
Security
Status
Docs
Contact GitHub
Pricing
API
Training
Blog
About
AB-Testing-Project/dataPreprocessing.py at main · DummyPuppy/AB-Testing-Project 
