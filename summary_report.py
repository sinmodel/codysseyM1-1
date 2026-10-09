import os
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent
os.chdir(PROJECT_DIR)

# 1. 데이터 불러오기
file_path = PROJECT_DIR / "data" / "tesla_stock_data.csv"
print(f"⏳ 데이터 파일을 불러오는 중입니다: {file_path}")
df = pd.read_csv(file_path, index_col="Date", parse_dates=True)

# 2. 주요 통계 지표 계산
# 종가(Close) 기준 통계
mean_price = df["Close"].mean()
max_price = df["Close"].max()
min_price = df["Close"].min()
std_price = df["Close"].std()

# 일일 수익률 및 변동성 계산
df["Daily_Return"] = df["Close"].pct_change()
volatility = df["Daily_Return"].std() * (252**0.5)  # 연환산 변동성

# 거래량 평균
mean_volume = df["Volume"].mean()

# 3. 리포트 내용 작성
report_content = f"""
==================================================
        TESLA (TSLA) 주가 분석 최종 리포트
==================================================
1. 분석 기간: {df.index.min().strftime('%Y-%m-%d')} ~ {df.index.max().strftime('%Y-%m-%d')}
2. 데이터 총 행 수: {len(df)} 거래일

[주가(Close) 통계 요약]
- 평균 종가: ${mean_price:.2f}
- 최고 종가: ${max_price:.2f} (날짜: {df['Close'].idxmax().strftime('%Y-%m-%d')})
- 최저 종가: ${min_price:.2f} (날짜: {df['Close'].idxmin().strftime('%Y-%m-%d')})
- 종가 표준편차: ${std_price:.2f}

[리스크 및 거래량 요약]
- 연환산 변동성 (Volatility): {volatility*100:.2f}%
- 평균 일일 거래량: {mean_volume:,.0f} 주
==================================================
"""

print(report_content)

# 4. 리포트를 텍스트 파일로 저장
images_dir = PROJECT_DIR / "images"
images_dir.mkdir(exist_ok=True)

report_path = images_dir / "summary_report.txt"
with open(report_path, "w", encoding="utf-8") as f:
  f.write(report_content)

print(f"✅ 최종 통계 리포트 파일 저장 완료: {report_path}")
