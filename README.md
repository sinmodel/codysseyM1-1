# Tesla (TSLA) Stock Analysis

테슬라(TSLA) 2024~2025년 주가 데이터를 수집하고, 이동평균·월별 수익률·변동성을 분석하는 교육 과제입니다. Streamlit 대시보드에서 기간과 이동평균 조건을 바꿔가며 결과를 탐색할 수 있습니다.

## 준비 사항

- Python 3.10 이상
- 인터넷 연결 (Yahoo Finance에서 데이터를 처음 수집할 때 필요)

## Windows에서 실행하기

PowerShell에서 프로젝트 폴더로 이동한 뒤 아래 명령을 차례로 실행합니다.

```powershell
python -m pip install -r requirements.txt
python collect_data.py
python analysis.py
streamlit run streamlit_app.py
```

대시보드가 실행되면 브라우저에서 표시되는 로컬 주소를 엽니다. 대시보드 왼쪽에서 시작·종료 날짜와 단기·장기 이동평균 기간을 조정할 수 있습니다. 거래량과 월별 수익률 그래프는 각 체크박스로 표시합니다.

월별 평균 종가 그래프를 추가로 만들려면 프로젝트 폴더에서 다음을 실행합니다.

```powershell
python monthly_analysis.py
python monthly_line_chart.py
```

## 프로젝트 구성

```text
tesla-stock-analysis/
├── analysis.py                 # 데이터 확인, 이동평균·월별 수익률, 그래프 생성
├── collect_data.py             # Yahoo Finance에서 TSLA 데이터 수집
├── monthly_analysis.py         # 월별 평균 종가 막대 그래프
├── monthly_line_chart.py       # 월별 평균 종가 선 그래프
├── summary_report.py           # 요약 통계 텍스트 출력
├── streamlit_app.py            # 기간·이동평균 조건을 바꿀 수 있는 대시보드
├── requirements.txt            # Python 패키지와 버전
├── REPORT.md                   # 분석 질문, 결과, 해석, 한계점, AI 사용 로그
├── data/                       # 데이터 수집 시 CSV가 저장되는 폴더
└── images/                     # 분석 그래프와 대시보드 캡처
```

## 데이터 출처 및 이용 시 주의

`collect_data.py`는 Yahoo Finance에서 TSLA의 2024-01-01 이상, 2026-01-01 미만 데이터를 받아 `data/tesla_stock_data.csv`로 저장합니다. 수집 시점이나 제공처의 변경에 따라 데이터가 달라질 수 있습니다. 데이터를 재배포하거나 상업적으로 이용하기 전에 Yahoo Finance의 최신 이용 약관을 확인하세요.

CSV 원본은 저장소에 포함하지 않습니다. 복제한 뒤 위 실행 방법대로 `python collect_data.py`를 실행해 생성하세요.

## 대시보드 보너스 과제 캡처

대시보드를 실행한 뒤 `Win+Shift+S`로 화면을 캡처해 다음 이름으로 `images/`에 저장하면 제출용 탐색 시나리오가 준비됩니다.

- `05_dashboard_default.png`: 기본 기간과 MA20·MA60
- `06_dashboard_date_range.png`: 종료 날짜를 2025-06-30으로 변경
- `07_dashboard_ma_changed.png`: 같은 기간에서 MA30·MA100으로 변경

## 재현 관련 참고

분석 기간은 CSV의 실제 관측 범위인 2024-01-02~2025-12-31이며 총 502 거래일입니다. 분석 방법, 수치 근거, 그래프와 한계점은 [REPORT.md](REPORT.md)를 참고하세요.
