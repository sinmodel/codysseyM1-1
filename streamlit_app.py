from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


PROJECT_DIR = Path(__file__).resolve().parent
DATA_PATH = PROJECT_DIR / "data" / "tesla_stock_data.csv"
REQUIRED_COLUMNS = {"Close", "Volume"}

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

st.set_page_config(page_title="테슬라 주가 탐색 대시보드", layout="wide")
st.title("테슬라 주가 탐색 대시보드")
st.caption("Tesla Stock Explorer")

if not DATA_PATH.is_file():
    st.error(f"데이터 파일을 찾을 수 없습니다: {DATA_PATH}")
    st.info("먼저 프로젝트 폴더에서 `python collect_data.py`를 실행해 주세요.")
    st.stop()

df = pd.read_csv(DATA_PATH, index_col="Date", parse_dates=True).sort_index()
missing_columns = REQUIRED_COLUMNS.difference(df.columns)
if missing_columns:
    raise ValueError(f"CSV에 필요한 컬럼이 없습니다: {', '.join(sorted(missing_columns))}")
if df.empty:
    raise ValueError("주가 데이터가 비어 있습니다.")

minimum_date = df.index.min().date()
maximum_date = df.index.max().date()

st.sidebar.header("탐색 조건")
start_date = st.sidebar.date_input(
    "시작 날짜",
    value=minimum_date,
    min_value=minimum_date,
    max_value=maximum_date,
)
end_date = st.sidebar.date_input(
    "종료 날짜",
    value=maximum_date,
    min_value=minimum_date,
    max_value=maximum_date,
)

short_window = st.sidebar.slider("단기 이동평균 기간 (거래일)", 5, 60, 20)
long_window = st.sidebar.slider("장기 이동평균 기간 (거래일)", 20, 200, 60)

if start_date > end_date:
    st.error("시작 날짜는 종료 날짜보다 늦을 수 없습니다.")
    st.stop()
if short_window >= long_window:
    st.error("단기 이동평균 기간은 장기 이동평균 기간보다 짧아야 합니다.")
    st.stop()

# Calculate moving averages before applying the selected display period.
df["Short_MA"] = df["Close"].rolling(window=short_window).mean()
df["Long_MA"] = df["Close"].rolling(window=long_window).mean()

selected = df.loc[pd.Timestamp(start_date) : pd.Timestamp(end_date)].copy()
if selected.empty:
    st.warning("선택한 기간에 표시할 거래 데이터가 없습니다.")
    st.stop()

period_change = (selected["Close"].iloc[-1] / selected["Close"].iloc[0] - 1) * 100
metric_columns = st.columns(3)
metric_columns[0].metric("선택 기간 데이터", f"{len(selected):,} 거래일")
metric_columns[1].metric("기간 시작 종가", f"${selected['Close'].iloc[0]:,.2f}")
metric_columns[2].metric("선택 기간 종가 변화율", f"{period_change:+.2f}%")

st.subheader("종가와 이동평균선")
st.caption(
    f"선택 기간: {selected.index.min():%Y-%m-%d} ~ {selected.index.max():%Y-%m-%d} | "
    f"이동평균은 전체 데이터에서 계산한 뒤 선택 기간만 표시합니다."
)

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(selected.index, selected["Close"], label="종가 (Close)", color="black", alpha=0.7)
ax.plot(
    selected.index,
    selected["Short_MA"],
    label=f"{short_window}일 이동평균",
    color="royalblue",
    linestyle="--",
)
ax.plot(
    selected.index,
    selected["Long_MA"],
    label=f"{long_window}일 이동평균",
    color="firebrick",
)
ax.set_title(
    "테슬라 종가와 이동평균선\n(Tesla Closing Price and Moving Averages)",
    fontweight="bold",
    linespacing=0.9,
)
ax.set_xlabel("날짜 (Date)")
ax.set_ylabel("종가 (USD)")
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

if st.checkbox("거래량 그래프 표시"):
    st.subheader("일별 거래량")
    st.line_chart(selected[["Volume"]])

if st.checkbox("월별 수익률 그래프 표시"):
    monthly_close = df["Close"].resample("ME").last()
    monthly_returns = monthly_close.pct_change().mul(100).dropna()
    monthly_returns = monthly_returns.loc[
        (monthly_returns.index >= pd.Timestamp(start_date))
        & (monthly_returns.index <= pd.Timestamp(end_date))
    ]
    if monthly_returns.empty:
        st.info("선택 기간에는 이전 달과 비교할 수 있는 월별 수익률이 없습니다.")
    else:
        chart_data = monthly_returns.rename("월별 수익률 (%)").to_frame()
        chart_data.index = chart_data.index.strftime("%Y-%m")
        st.bar_chart(chart_data)

st.caption("과거 주가 데이터의 탐색용 화면이며, 미래 수익이나 투자 결과를 보장하지 않습니다.")
