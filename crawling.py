# # Voyagerx 를 통한 자막 추출  
# 
# ###   환경 :
#     1) 윈도우  + python 3.7.x  
#     2) 현재 디렉토리에 Chrome_webdriver 존재
#     3) 현재 디렉토리 중 하위 폴더 (movie)에 동영상 파일만 존재  
#     4) 다운로드는 디폴트로 설정된 곳으로 바로 다운로드 됨  

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm_notebook
import time
import pywinauto
import os
import shutil

# 크롬 드라이버 옵션
options = webdriver.ChromeOptions()
# options.add_argument('headless')

def crawling(df, chrome_dir, links_videos_texts_dir):
    save_file = links_videos_texts_dir
    with open(save_file, 'a') as f:
        f.write('links,videos,texts\n')

    browser = webdriver.Chrome(chrome_dir, options=options)
    ## 자막 추출사이트 변경
    browser.get('https://downsub.com/') 
    wait = WebDriverWait(browser, 5)

    print('-'*50)

    # 크롤링 루프
    print(df)
    for idx, row in df.iterrows():
        print(idx)
        video = row['videos'][13:]
        print(video,'추출')
        video = video.split(os.sep)[-1].split(".")[0]
  
        link = row['links']

        result =f'https://downsub.com/?url={link}'
        print(result)
        browser.get(f'https://downsub.com/?url={link}')
        browser.implicitly_wait(15)
        time.sleep(7)
        # 자막 다운로드

        try:
            wait = WebDriverWait(browser, 10)
        # element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/main/div/div[2]/div/div[1]/div[1]/div[2]/div[1]/button[1]')))
            element = wait.until(EC.presence_of_element_located(
                (By.XPATH, '/html/body/div/div/main/div/div[2]/div/div[1]/div[1]/div[2]/div[1]/button[1]/span/button')))

            print("다운로드 시작")
            element.click()
            time.sleep(15) # 자막 다운로드 대기
            print("다운로드 완료")
        except:
            print("다운로드 실패")
            pass
        
        # 자막 파일 이름 변경
        download_path = "c:/Users/{}/Downloads".format(os.getlogin())
        new_filename = os.path.join(".", "data", "text", video + ".srt")
        filename = max([download_path + "/" + f for f in os.listdir(download_path)], key=os.path.getctime)
        shutil.move(os.path.join(download_path, filename), new_filename)
        print("폴더 변경 완료")
        
        # 자막 링크 파일 쓰기
        with open(save_file, 'a') as f:
            f.write('{},{},{}\n'.format(row['links'], row['videos'], new_filename))
        print("자막 링크 파일 쓰기 완료")
        print('-'*50) 
