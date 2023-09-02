import pandas as pd

# 원본 엑셀 파일 읽기
excel_file = './data/links.csv'
df = pd.read_csv(excel_file)

# 60개씩 나누어서 저장할 폴더 경로
output_folder = './data/'

# 데이터를 60개씩 나누어 처리
chunk_size = 60
num_chunks = len(df) // chunk_size + 1

for i in range(num_chunks):
    start_idx = i * chunk_size
    end_idx = start_idx + chunk_size
    chunk = df[start_idx:end_idx]

    # CSV 파일로 저장
    output_file = f'{output_folder}chunk_{i + 1}.csv'
    chunk.to_csv(output_file, index=False)
