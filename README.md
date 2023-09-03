# 실시간 음성 비속어 필터링 프로젝트
### 공개SW 개발자 대회에서 진행된 프로젝트입니다.


# 0. 환경세팅

1. 파이썬 버전 3.7.x 준비.(Conda 사용 추천)
2. 자기 크롬에 맞는 크롬드라이버 준비. (크롬 업데이트하면 116.0.xxxx.xxx니까 레파지토리에 있는거 그대로 사용해도 됨)
3. 크롬드라이버는 get_data와 동일한 경로에 위치

# 1. 실행

0. 터미널에 `pip install --upgrade pip` 실행 -> pip 최신버전으로 업그레이드
1. 터미널에 `pip install -r requirements.txt` 명령어 실행
2. 터미널에 `mkdir data` 명령어 실행
3. data 폴더에 각자 전달받은 csv파일 넣기
4. 터미널에 `python get_data.py --get_videos` 실행 -> video가 제대로 다운되는지 확인
5. 터미널에 `python get_data.py --get_texts` 실행 -> **크롤링이 제대로 확인되고 있는지 확인**, text폴더 확인
6. 터미널에 `python get_data.py --get_audios` 실행 -> 오디오가 클립대로 잘 분리되고 있는지 확인
7. 터미널에 `python get_data.py --labeling` 실행
8. 터미널에 `python get_data.py --save_label`
9. 터미널에서 자막 라벨링
10. 터미널에 `python get_data.py --get_images` 실행 -> mel spectrom이 잘 다운됐는지 확인

# 3. 주의사항
* 만약 라이브러리 설치 중 라이브러리 업데이트 해라는 문구가 뜨면 그냥 업데이트하면됨.


# 라벨링 입력 방법
라벨링은 int형 데이터 타입으로 기입한다. 아래는 라벨링에 대한 기준을 설명함.
- negative (욕설이 아닌 경우) : 0
- activate (욕설인 경우)
- activate (욕인데 라벨에 포함되지 않는 경우) : 8

10 : 시    ex) 시발, 씨발, 시발놈, 씨발새끼, 시발놈아 ... <br>

11 : 존    ex) 존나, 존나게 ... <br>

12 : 새    ex) 새끼, 새끼야 ... <br>

13 : 병    ex) 병신, 병신년아 ... <br>

14 : 도    ex) 또라이, 도라이년아 ... <br>

15 : 샹    ex) 썅, 썅년아 ... <br>

16 : 미    ex) 미친, 미친새끼 ... <br>

17 : 개    ex) 개새끼, 개병신년아 ... <br>

18 : 좆    ex) 좆같다, 좆병신년아 ... <br>

**만약 합성어인 경우 앞의 단어를 기준으로 라벨링**
ex. 시발새끼야 -> 10

## 중요! background(9) 라벨링 기입 x. 배경음은 특정 영상에서 추출 예정

# 최종
data 폴더 전체를 압축해서 드라이브 공유 Plz~  

---
### Beep-- ref
[발표자료](http://www.datamarket.kr/xe/board_pdzw77/63632)  
  
[발표동영상](https://www.youtube.com/watch?v=n1BqCii2yVU)

### 폴더 경로

`./data`  

`./data/video`  
- blahblah.mp4  
  
`./data/audio`  
- blahblah.wav  
- blahblah_0.wav  

`./data/text`  
- blahblah.txt  

`./data/label`  
- blahblah_0.txt  
- blahblah_0.wav  

`./data/audio_label_clip`  
- background_0.wav  
- negative_0.wav  
- positive_0.wav  

`./data/train_audios`  
- mix_0.wav  

`./data/XY_train`  
- x_0.npy
- y_0.npy



### ref
https://github.com/Tony607/Keras-Trigger-Word
