import os
from pathlib import Path

import pandas as pd
import yfinance as yf

PROJECT_DIR = Path(__file__).resolve().parent
os.chdir(PROJECT_DIR)
DATA_DIR = PROJECT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# 1. 'data' 폴더가 없으면 자동으로 생성
print(f"📁 데이터 저장 폴더: {DATA_DIR}")

# 2. 수집 조건 설정 (테슬라, 2년치 데이터 -> 약 500개 이상 데이터 포인트 확보)
ticker = "TSLA"
start_date = "2024-01-01"
end_date = "2026-01-01"

print(f"⏳ [{ticker}] 데이터를 수집 중입니다... ({start_date} ~ {end_date})")

# 3. 야후 파이낸스에서 데이터 다운로드
df = yf.download(ticker, start=start_date, end=end_date)

# 4. yfinance 최신 버전에서 발생할 수 있는 멀티인덱스 컬럼 정리 (단일화)
if isinstance(df.columns, pd.MultiIndex):
  df.columns = df.columns.get_level_values(0)

# 5. 데이터 기본 검증 (상위 5개 행 및 정보 출력)
print("\n--- [확인] 수집된 데이터 상위 5개 행 ---")
print(df.head())

print("\n--- [확인] 데이터 구조 및 결측치 여부 ---")
print(df.info())

# 6. CSV 파일로 저장 (과제 필수 요구사항 반영)
file_path = DATA_DIR / "tesla_stock_data.csv"
df.to_csv(file_path)
print(f"\n✅ 데이터 수집 완료! 저장된 파일: {file_path}")
