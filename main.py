import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)


# --------------------------------------------------
# 제목
# --------------------------------------------------
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

st.markdown(
    """
    1년간 박스오피스 10위권에 들었던 영화 중
    이 기간에 개봉한 216편의 데이터를 살펴봅니다.
    """
)


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일: 8자리 숫자 → 날짜
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 숫자로 사용해야 하는 열
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.exception(e)
    st.stop()


# --------------------------------------------------
# 그래프 1
# --------------------------------------------------
st.divider()

st.header("그래프 1) 도넛 - 어떤 장르의 영화가 많았나")

st.markdown(
    """
    **장르별 영화 편수의 분포**를 도넛 그래프로 나타냅니다.
    여러 장르가 세로막대(|)로 표시된 경우에는 첫 번째 장르만 사용합니다.
    """
)


# 장르가 여러 개이면 첫 번째 장르만 사용
df["대표장르"] = (
    df["genre"]
    .fillna("미상")
    .astype(str)
    .str.split("|")
    .str[0]
    .str.strip()
)

# 빈 값 처리
df.loc[
    df["대표장르"].isin(["", "nan", "None"]),
    "대표장르"
] = "미상"


# 장르별 영화 편수
genre_counts = (
    df["대표장르"]
    .value_counts()
    .reset_index()
)

genre_counts.columns = ["장르", "영화편수"]


# 도넛 그래프
fig = px.pie(
    genre_counts,
    names="장르",
    values="영화편수",
    hole=0.5,
    title="장르별 영화 편수"
)

fig.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig.update_layout(
    height=550,
    legend_title_text="장르"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# 그래프로 알 수 있는 것
# --------------------------------------------------
st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "내용을 입력하세요.",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    height=100,
    key="graph1_answer"
)


# --------------------------------------------------
# 원본 데이터 확인
# --------------------------------------------------
st.divider()

st.subheader("📋 데이터 확인")

st.write(f"전체 영화 수: **{len(df)}편**")

st.dataframe(
    df[
        [
            "movieCd",
            "movieNm",
            "openDt",
            "대표장르",
            "nation",
            "first_scrn",
            "first_show",
            "first_week_audi",
            "total_audi",
            "days_in_top10"
        ]
    ],
    use_container_width=True,
    hide_index=True
)
