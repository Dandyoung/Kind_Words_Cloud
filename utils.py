import os
import pandas as pd
import numpy as np
from pytube import YouTube, Playlist
from moviepy.editor import *
import librosa
import librosa.display
import matplotlib.pyplot as plt
from tqdm import tqdm_notebook
import pysrt
#라벨링때매 import 한거
from pydub import AudioSegment


def make_dir(dir_):
    if not os.path.isdir(dir_):
        os.mkdir(dir_)

def save_playlist_links(playlist_urls, links_dir):
    links = []
    count = 0
    main_link = "https://www.youtube.com/watch?v="
    for playlist_url in playlist_urls:
        pl = Playlist(playlist_url)
        for tmp_link in pl.video_urls:
            try: # 비공개영상 접근 불가, key error
                yt = YouTube(tmp_link)
                link = main_link + str(yt.video_id)
                links.append(link)
                count += 1
                print('Link read', count)
            except:
                print('Except')

    df = pd.DataFrame({'links': links})
    df.to_csv(links_dir, index=False)
    print('Links saved !')

def link_to_video(link, video_dir):
    try:
        yt = YouTube(link)
        video_name = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').first().download()
        video_id = yt.video_id  # 비디오의 유효한 ID 추출
        re_name = os.path.join(video_dir, f'{video_id}.mp4')
        os.rename(video_name, re_name)
        return re_name
    except Exception as e:
        print(e)

def save_videos(df, links_videos_dir,video_dir):
    with open(links_videos_dir, 'a') as f:
        f.write('links,videos\n')
    count = 0
    for link in set(df.links):
        try: # 접근불가 영상
            name = link_to_video(link, video_dir)
            with open(links_videos_dir, 'a') as f:
                f.write('{},{}\n'.format(link, name))
            count += 1
            print('Video read', count)
        except Exception as ex:
            print(ex)

def save_text(download_path, video): #다운로드에 있는 파일을 경로변경 및 해당 파일의 경로 return
    video = video.split(os.sep)[-1].split(".")[0]
    source = os.path.join(download_path, video+".srt")
    target =  os.path.join(".", "data", "text", video+".srt")
    os.rename(source, target)
    return target

def change_dir(from_dir, before='video', after='text'):
    if after == 'audio':
        type_ = '.wav'
    elif after == 'text':
        type_ = '.srt'
    
    to_dir = from_dir.split('\\')
    to_dir[-2] = after
    to_dir[-1] = to_dir[-1].split('.')[0] + type_   
    return os.path.join(*to_dir)

def video_to_audio(video_dir):
    audio_dir = change_dir(video_dir, before='video', after='audio')
    audioclip = VideoFileClip(video_dir).audio
    audioclip.write_audiofile(audio_dir)
    return audio_dir

def srt_to_df(path):
    subs = pysrt.open(path)
    data = []

    for sub in subs:
        print(sub.start.to_time())
        time = str(sub.start.to_time())
        data.append({
            'time' : time,
            'text': sub.text
        })
    df = pd.DataFrame(data)
    return df

def clip_audio(audio_dir):
    total = pd.DataFrame(columns=['audio','text', 'length'])
    print(audio_dir)
    text_dir = change_dir(audio_dir, before='audio_dir', after='text')    
    df = srt_to_df(text_dir)

    for i in range(len(df)):
        full_audio = AudioFileClip(audio_dir)
        full_time = int(full_audio.end)
        
        tmp_dir = audio_dir[:-4] + '_{}.wav'.format(i)
        start_time = pd.Timedelta(df['time'][i]).total_seconds()
        if i != (len(df)-1):
            end_time = pd.Timedelta(df['time'][i+1]).total_seconds()
        else:
            end_time = full_time

        tmp_audio = full_audio.subclip(start_time, end_time)
        tmp_audio.write_audiofile(tmp_dir)
        
        total = total.append({'audio':tmp_dir, 
                              'text':df['text'][i], 
                              'length':(end_time-start_time) , 'start': (start_time), 'end':(end_time)}, ignore_index=True)
    return total

def save_audios(df, audios_texts_length_dir):
    result = pd.DataFrame(columns=['audio', 'text', 'length','start','end'])
    for video in df.videos:
        video_dir = video
        audio_dir = video_to_audio(video_dir)
        try:
            clip_df = clip_audio(audio_dir)
        except IndexError:
            continue
        result = result.append(clip_df, ignore_index=True) 
    result['label'] = ""
    result.to_csv(audios_texts_length_dir, index=False, encoding='utf-8')

def labeling(df, audios_texts_length_dir):
    for i, row in df.iterrows():
        if np.isnan(row['label']):
            print('Text:', row['text'])
            while True:
                try:
                    l = int(input('Label: '))
                    if l == 99:
                        df.to_csv(audios_texts_length_dir, index=False, encoding='utf-8')
                        l = int(input('Label: '))
                    df['label'][i] = l
                    break
                except ValueError:
                    print("정수를 입력해주세요 ")
    df.to_csv(audios_texts_length_dir, index=False, encoding='utf-8')
    
def save_label(audios_texts_length_dir):
    data = pd.read_csv(audios_texts_length_dir, encoding='utf-8')  # 인자로 받은 파일 경로 사용
    audio_folder = "data/label/"
    text_folder = "data/label/"
    
    os.makedirs(audio_folder, exist_ok=True)
    os.makedirs(text_folder, exist_ok=True)

    # print(data)
    for index, row in data.iterrows():
        audio_path = row['audio']
        text = row['text']
        label = int(row['label'])
        start = row['start']
        end = row['end']

        start_end_label = str(start) + '\t' + str(end) + '\t' +str(label)
        audio = AudioSegment.from_wav(audio_path)
        audio_filename = os.path.basename(audio_path)
        new_audio_path = os.path.join(audio_folder, audio_filename)
        audio.export(new_audio_path, format="wav")

        text_filename = f"{os.path.splitext(audio_filename)[0]}.txt"
        text_path = os.path.join(text_folder, text_filename)
        print(text_filename)
        
        with open(text_path, "w", encoding='utf-8') as f:
            f.write(start_end_label)
        print(f"Processed: {audio_filename}")
    
def wave_to_image(audios_texts_length_dir):
    img_dir = os.path.join('.', 'data', 'image')
    make_dir(img_dir)
    df = pd.read_csv(audios_texts_length_dir, encoding='utf-8')
    crit_y = 926100
    frame_length = 0.025
    frame_stride = 0.010

    for audio in tqdm_notebook(df.audio):
        wav = audio
        file_dir, file_id = os.path.split(wav)
        name = file_id.split(".")[0]
        save_path = os.path.join(img_dir, name+'.png')
        print(name)

        y, sr = librosa.load(wav, sr=16000)
        input_nfft = int(round(sr*frame_length))
        input_stride = int(round(sr*frame_stride))

        # y = librosa.util.fix_length(y, crit_y)
        y = librosa.util.fix_length(y, size = crit_y)

        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128) 
        log_S = librosa.power_to_db(S, ref=np.max)

        plt.imsave(save_path, log_S, cmap='gray')

