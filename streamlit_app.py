from pathlib import Path
import os
import subprocess
import sys

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


PROJECT_DIR = Path(__file__).resolve().parent
os.chdir(PROJECT_DIR)
DATA_PATH = PROJECT_DIR / "data" / "tesla_stock_data.csv"
REQUIRED_COLUMNS = {"Close", "Volume"}

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

st.set_page_config(page_title="테슬라 주가 탐색 대시보드", layout="wide")
st.title("테슬라 주가 탐색 대시보드")
st.caption("Tesla Stock Explorer")

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] .main-menu-title,
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {
        font-size: 1.2rem;
        font-weight: 700;
    }
    [data-testid="stSidebar"] .dashboard-menu-item {
        font-size: 0.95rem;
        font-weight: 600;
        margin: 0.25rem 0;
    }
    [data-testid="stSidebar"] .dashboard-title {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        font-size: 0.95rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }
    [data-testid="stSidebar"] .dashboard-fixed-check {
        display: inline-flex;
        width: 1.25rem;
        height: 1.25rem;
        align-items: center;
        justify-content: center;
        border-radius: 0.25rem;
        background: #ff4b4b;
        color: white;
        font-size: 1rem;
        font-weight: 700;
        line-height: 1;
    }
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        font-size: 0.95rem;
        font-weight: 600;
    }
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label p {
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown('<div class="main-menu-title">메인 메뉴</div>', unsafe_allow_html=True)
if "show_deployment_page" not in st.session_state:
    st.session_state.show_deployment_page = False


def return_to_main_menu() -> None:
    st.session_state.show_deployment_page = False


page = st.sidebar.radio(
    "페이지 선택",
    ["홈", "데이터 수집", "분석 실행", "대시보드"],
    key="main_menu_selection",
    on_change=return_to_main_menu,
    label_visibility="collapsed",
)

if st.session_state.show_deployment_page:
    page = "배포"


def render_sidebar_footer() -> None:
    if st.sidebar.button("배포", key="deployment_menu"):
        st.session_state.show_deployment_page = True
        st.rerun()

    if st.sidebar.button("종료", key="exit_app"):
        shutdown_file = os.environ.get("TESLA_STOCK_SHUTDOWN_FILE")
        if shutdown_file:
            Path(shutdown_file).write_text("exit", encoding="utf-8")
            st.html(
                "<script>window.location.replace('about:blank');</script>",
                unsafe_allow_javascript=True,
            )
        else:
            st.info("PowerShell에서 실행한 앱을 종료하려면 프로젝트의 `python main.py`로 실행하세요.")
        st.stop()


def run_script(script_name: str) -> bool:
    result = subprocess.run(
        [sys.executable, str(PROJECT_DIR / script_name)],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        check=False,
    )

    if result.stdout:
        st.code(result.stdout)
    if result.stderr:
        st.code(result.stderr, language="text")
    if result.returncode != 0:
        st.error(f"{script_name} 실행에 실패했습니다 (종료 코드: {result.returncode}).")
        return False

    st.success(f"{script_name} 실행이 완료되었습니다.")
    return True


if page == "홈":
    render_sidebar_footer()
    st.header("과제 실행 메뉴")
    st.write(
        "왼쪽 메뉴에서 데이터를 수집하고 분석을 실행한 뒤, "
        "대시보드에서 기간과 이동평균 조건을 바꿔가며 결과를 확인할 수 있습니다."
    )
    if DATA_PATH.is_file():
        st.success("주가 데이터 파일이 준비되어 있습니다.")
    else:
        st.info("먼저 왼쪽의 '데이터 수집' 메뉴에서 TSLA 데이터를 수집하세요.")
    st.markdown(
        """
        1. **데이터 수집**에서 Yahoo Finance 데이터를 내려받습니다.
        2. **분석 실행**에서 필수·월별 분석과 요약 리포트를 생성합니다.
        3. **대시보드**에서 날짜 범위와 이동평균을 조정해 결과를 탐색합니다.
        """
    )
    st.stop()

if page == "데이터 수집":
    render_sidebar_footer()
    st.header("TSLA 데이터 수집")
    st.write("Yahoo Finance에서 2024~2025년 TSLA 주가 데이터를 내려받습니다.")
    if st.button("데이터 수집 실행", type="primary"):
        with st.spinner("데이터를 수집하고 있습니다..."):
            run_script("collect_data.py")
    st.stop()

if page == "분석 실행":
    render_sidebar_footer()
    st.header("분석 및 결과물 생성")
    if not DATA_PATH.is_file():
        st.warning("먼저 '데이터 수집' 메뉴에서 주가 데이터를 수집하세요.")
        st.stop()

    st.write(
        "이동평균·거래량·월별 수익률 분석, 월별 평균 종가 그래프, "
        "월별 추이 그래프와 요약 리포트를 차례대로 생성합니다."
    )
    if st.button("전체 분석 실행", type="primary"):
        scripts = [
            "analysis.py",
            "monthly_analysis.py",
            "monthly_line_chart.py",
            "summary_report.py",
        ]
        for script_name in scripts:
            with st.spinner(f"{script_name} 실행 중..."):
                if not run_script(script_name):
                    st.warning("오류가 발생해 나머지 분석은 실행하지 않았습니다.")
                    break
    st.stop()

if page == "배포":
    render_sidebar_footer()
    st.header("앱 배포 안내")
    st.write(
        "대시보드를 온라인에서 사용하려면 프로젝트 파일을 GitHub에 올린 뒤 "
        "Streamlit Community Cloud에 연결하세요."
    )
    st.markdown(
        """
        1. 프로젝트 전체를 GitHub 저장소에 푸시합니다. `requirements.txt`가 저장소에 있어야 합니다.
        2. [Streamlit Community Cloud](https://share.streamlit.io/)에 로그인하고 **Create app**을 선택합니다.
        3. 저장소와 브랜치를 선택하고 앱 파일 경로를 `streamlit_app.py`로 지정합니다.
        4. **Deploy**를 누릅니다. 배포 후 앱에서 **데이터 수집** 메뉴를 실행해 데이터를 준비합니다.

        이 프로젝트는 Yahoo Finance에서 데이터를 가져오므로 배포 환경에서도 인터넷 연결이 필요합니다.
        """
    )
    st.info("로컬 PC에서 실행할 때는 프로젝트 폴더에서 `python main.py`를 사용하세요.")
    st.stop()

if not DATA_PATH.is_file():
    render_sidebar_footer()
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

start_date = st.sidebar.date_input("시작 날짜", value=minimum_date, min_value=minimum_date, max_value=maximum_date)
end_date = st.sidebar.date_input("종료 날짜", value=maximum_date, min_value=minimum_date, max_value=maximum_date)
short_window = st.sidebar.slider("단기 이동평균 기간 (거래일)", 5, 60, 20)
long_window = st.sidebar.slider("장기 이동평균 기간 (거래일)", 20, 200, 60)
st.sidebar.markdown(
    '<div class="dashboard-title"><span class="dashboard-fixed-check">✓</span>'
    '종가와 이동평균선</div>',
    unsafe_allow_html=True,
)
show_volume = st.sidebar.checkbox("거래량 그래프 표시")
show_monthly_returns = st.sidebar.checkbox("월별 수익률 그래프 표시")
render_sidebar_footer()

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
    "종가와 이동평균선",
    fontweight="bold",
)
ax.set_xlabel("날짜 (Date)")
ax.set_ylabel("종가 (USD)")
ax.legend()
ax.grid(True, alpha=0.3)
fig.tight_layout()
st.pyplot(fig)
plt.close(fig)

if show_volume:
    st.subheader("거래량 그래프 표시")
    st.line_chart(selected[["Volume"]])

if show_monthly_returns:
    st.subheader("월별 수익률 그래프 표시")
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
