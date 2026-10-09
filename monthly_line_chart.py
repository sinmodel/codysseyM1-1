import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PROJECT_DIR = Path(__file__).resolve().parent
os.chdir(PROJECT_DIR)

# 한글 폰트 및 스타일 설정
sns.set_theme(style='whitegrid')
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 1. 데이터 불러오기
file_path = PROJECT_DIR / 'data' / 'tesla_stock_data.csv'
print(f'⏳ 데이터 파일을 불러오는 중입니다: {file_path}')
df = pd.read_csv(file_path, index_col='Date', parse_dates=True)

# 2. 월별 평균 종가 계산
monthly_df = df['Close'].resample('ME').mean()

# 3. 월별 평균 주가 꺾은선 그래프(Line Chart) 시각화
plt.figure(figsize=(14, 6))
plt.plot(
    monthly_df.index.strftime('%Y-%m'),
    monthly_df.values,
    marker='o',
    color='royalblue',
    linewidth=2.5,
    markersize=6,
    label='월별 평균 종가',
)

plt.title(
    '테슬라 월별 평균 종가 추이\n'
    '(Tesla Monthly Average Closing Price Trend, 2024-2025)',
    fontsize=14,
    fontweight='bold',
    linespacing=0.9,
    pad=8,
)
plt.xlabel('Month (Year-Month)', fontsize=12)
plt.ylabel('Average Close Price (USD)', fontsize=12)

# X축 레이블 45도 회전 및 그리드 추가
plt.xticks(rotation=45, fontsize=10)
plt.legend(loc='upper left', fontsize=10)
plt.tight_layout()

# 4. 이미지 저장
images_dir = PROJECT_DIR / 'images'
images_dir.mkdir(exist_ok=True)

chart_path = images_dir / '04_monthly_price_line_chart.png'
plt.savefig(chart_path, dpi=300)
plt.close()
print(f'\n✅ 월별 꺾은선 그래프 저장 완료: {chart_path}')
