import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 한글 폰트 및 스타일 설정 (그래프가 깨지지 않도록 설정)
sns.set_theme(style='whitegrid')
plt.rcParams['font.family'] = 'Malgun Gothic'  # Windows 기준 맑은 고딕
plt.rcParams['axes.unicode_minus'] = False

# 1. 시각화 결과물을 저장할 'images' 폴더 생성
images_dir = os.path.join(os.path.dirname(__file__), 'images')
if not os.path.exists(images_dir):
  os.makedirs(images_dir)
  print("📁 'images' 폴더를 생성했습니다.")

# 2. 수집된 CSV 데이터 불러오기
file_path = os.path.join(os.path.dirname(__file__), 'data', 'tesla_stock_data.csv')
print(f"⏳ 데이터 파일을 불러오는 중입니다: {file_path}")
df = pd.read_csv(file_path, index_col='Date', parse_dates=True)

# 3. 데이터 기본 정보 확인
print('\n--- [분석] 데이터 상위 5개 행 ---')
print(df.head())

print('\n--- [분석] 데이터 기본 정보 ---')
print(f'데이터 포인트 수: {len(df)}')
print(f'분석 기간: {df.index.min().date()} ~ {df.index.max().date()}')
df.info()

print('\n--- [분석] 컬럼별 결측치 수 ---')
print(df.isna().sum())
print(f'중복 날짜 수: {df.index.duplicated().sum()}')

# 4. 이동평균선(Moving Average) 계산 (과제 필수 요구사항)
# 20일 이동평균선 (단기 추세)
df['MA20'] = df['Close'].rolling(window=20).mean()
# 60일 이동평균선 (중기 추세)
df['MA60'] = df['Close'].rolling(window=60).mean()

print('\n--- [분석] MA20·MA60이 모두 계산된 첫 5개 행 ---')
print(df[['Close', 'MA20', 'MA60']].dropna(subset=['MA20', 'MA60']).head(5))

# 5. 필수 시각화 1: 테슬라 종가 및 이동평균선 트렌드 그래프 생성
plt.figure(figsize=(12, 6))
plt.plot(
    df.index, df['Close'], label='TSLA 종가 (Close)', color='black', alpha=0.6
)
plt.plot(
    df.index,
    df['MA20'],
    label='20일 이동평균선 (MA20)',
    color='blue',
    linestyle='--',
)
plt.plot(
    df.index,
    df['MA60'],
    label='60일 이동평균선 (MA60)',
    color='red',
    linestyle='-',
)

plt.title(
    '테슬라 종가와 이동평균선\n(Tesla Closing Price and Moving Averages)',
    fontsize=14,
    fontweight='bold',
    linespacing=0.9,
    pad=8,
)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Price (USD)', fontsize=12)
plt.legend(loc='upper left', fontsize=10)
plt.tight_layout()

# 그래프 저장
chart_path_1 = os.path.join(images_dir, '01_moving_average_trend.png')
plt.savefig(chart_path_1, dpi=300)
plt.close()
print(f'\n✅ 첫 번째 시각화 그래프 저장 완료: {chart_path_1}')

# 6. 필수 시각화 2: 거래량(Volume) 분포 분석 그래프 생성
plt.figure(figsize=(12, 4))
sns.histplot(
    df['Volume'], kde=True, color='purple', bins=50
)  # seaborn을 활용한 거래량 분포 시각화
plt.title(
    '테슬라 거래량 분포\n(Tesla Trading Volume Distribution)',
    fontsize=14,
    fontweight='bold',
    linespacing=0.9,
    pad=8,
)
plt.xlabel('Volume', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.tight_layout()

# 그래프 저장
chart_path_2 = os.path.join(images_dir, '02_volume_distribution.png')
plt.savefig(chart_path_2, dpi=300)
plt.close()
print(f'✅ 두 번째 시각화 그래프 저장 완료: {chart_path_2}')

# 7. 월말 종가 기준 월별 수익률 계산
monthly_close = df['Close'].resample('ME').last()
monthly_returns = monthly_close.pct_change().mul(100).dropna()

print('\n--- [분석] 월말 종가 기준 월별 수익률(%) ---')
print(monthly_returns.to_string())

# 8. 권장 시각화 3: 월별 수익률 그래프
bar_colors = [
    'seagreen' if monthly_return >= 0 else 'firebrick'
    for monthly_return in monthly_returns
]
plt.figure(figsize=(14, 5))
plt.bar(
    monthly_returns.index.strftime('%Y-%m'),
    monthly_returns.values,
    color=bar_colors,
)
plt.axhline(0, color='black', linewidth=0.8)
plt.title(
    '테슬라 월별 수익률 (월말 종가 기준)\n'
    '(Tesla Monthly Returns, Month-end Closing Price)',
    fontsize=14,
    fontweight='bold',
    linespacing=0.9,
    pad=8,
)
plt.xlabel('Month', fontsize=12)
plt.ylabel('Monthly Return (%)', fontsize=12)
plt.xticks(rotation=45, fontsize=9)
plt.tight_layout()

chart_path_3 = os.path.join(images_dir, '03_monthly_returns.png')
plt.savefig(chart_path_3, dpi=300)
plt.close()
print(f'✅ 세 번째 시각화 그래프 저장 완료: {chart_path_3}')

print('\n🎉 데이터 분석 및 시각화 코드가 성공적으로 실행되었습니다!')