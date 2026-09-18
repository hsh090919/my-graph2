import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

st.write(
    "216편의 영화 데이터를 이용하여 영화의 분포와 변수 사이의 관계를 살펴봅니다."
)


# =========================================================
# 데이터 불러오기
# =========================================================
URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"

df = pd.read_csv(URL)


# =========================================================
# 데이터 전처리
# =========================================================

# 장르가 여러 개일 경우 첫 번째 장르만 사용
df["genre_first"] = (
    df["genre"]
    .fillna("미상")
    .astype(str)
    .str.split("|")
    .str[0]
)

# 국가 결측값 처리
df["nation"] = df["nation"].fillna("미상")

# 숫자로 사용해야 하는 열 변환
numeric_columns = [
    "first_scrn",
    "first_show",
    "first_week_audi",
    "total_audi",
    "days_in_top10"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# 개봉일을 날짜 형식으로 변환
df["openDt"] = pd.to_datetime(
    df["openDt"].astype(str),
    format="%Y%m%d",
    errors="coerce"
)


# =========================================================
# 그래프 1
# =========================================================
st.header("그래프1) 도넛 - 장르별 영화는 얼마나 있나")

genre_count = (
    df["genre_first"]
    .value_counts()
    .reset_index()
)

genre_count.columns = [
    "genre",
    "count"
]

fig1 = px.pie(
    genre_count,
    names="genre",
    values="count",
    hole=0.45,
    title="장르별 영화 수"
)

fig1.update_traces(
    hovertemplate=
    "장르: %{label}<br>"
    "영화 수: %{value}편<br>"
    "비율: %{percent}<extra></extra>"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.subheader("💡 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프1 설명",
    placeholder="이 그래프로 알 수 있는 것을 입력하세요.",
    key="graph1_explanation"
)


# =========================================================
# 그래프 2
# =========================================================
st.header("그래프2) 트리맵 - 어떤 장르의 영화가 관객을 많이 모았나")

treemap_df = df[
    [
        "genre_first",
        "movieNm",
        "total_audi"
    ]
].dropna()

fig2 = px.treemap(
    treemap_df,
    path=[
        "genre_first",
        "movieNm"
    ],
    values="total_audi",
    title="장르 → 영화별 총 관객수"
)

fig2.update_traces(
    hovertemplate=
    "영화: %{label}<br>"
    "총 관객수: %{value:,}명<extra></extra>"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.subheader("💡 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프2 설명",
    placeholder="이 그래프로 알 수 있는 것을 입력하세요.",
    key="graph2_explanation"
)


# =========================================================
# 그래프 3
# =========================================================
st.header("그래프3) 히스토그램 - 영화들의 총 관객수는 어떻게 분포하나")

hist_df = df[
    [
        "movieNm",
        "total_audi"
    ]
].dropna()

fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=10,
    title="영화별 총 관객수 분포"
)

fig3.update_layout(
    xaxis_title="총 관객수",
    yaxis_title="영화 수"
)

fig3.update_traces(
    hovertemplate=
    "총 관객수 구간: %{x}<br>"
    "영화 수: %{y}편<extra></extra>"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# 총 관객수가 가장 많은 영화
max_movie = df.loc[
    df["total_audi"].idxmax()
]

st.info(
    f"🏆 총 관객수가 가장 많은 영화: "
    f"**{max_movie['movieNm']}** "
    f"({max_movie['total_audi']:,.0f}명)"
)

st.subheader("💡 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프3 설명",
    placeholder="이 그래프로 알 수 있는 것을 입력하세요.",
    key="graph3_explanation"
)


# =========================================================
# 그래프 4
# =========================================================
st.header("그래프4) 산점도 - 개봉일 스크린 수가 많으면 총 관객도 많은가")

scatter_df = df[
    [
        "movieNm",
        "genre_first",
        "first_scrn",
        "total_audi"
    ]
].dropna()

fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre_first",
    hover_name="movieNm",
    title="개봉일 스크린 수와 총 관객수의 관계",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객수",
        "genre_first": "장르"
    },
    custom_data=[
        "movieNm",
        "genre_first",
        "first_scrn",
        "total_audi"
    ]
)

fig4.update_traces(
    hovertemplate=
    "<b>%{customdata[0]}</b><br>"
    "장르: %{customdata[1]}<br>"
    "개봉일 스크린 수: %{customdata[2]:,}개<br>"
    "총 관객수: %{customdata[3]:,}명"
    "<extra></extra>"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.subheader("💡 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프4 설명",
    placeholder="이 그래프로 알 수 있는 것을 입력하세요.",
    key="graph4_explanation"
)


# =========================================================
# 그래프 5
# =========================================================
st.header("그래프5) 상자수염 - 장르별 총 관객수 분포는 다른가")

# 장르별 영화 수 계산
genre_10 = (
    df["genre_first"]
    .value_counts()
)

# 영화가 10편 이상인 장르만 선택
valid_genres = genre_10[
    genre_10 >= 10
].index

box_df = df[
    df["genre_first"].isin(valid_genres)
][
    [
        "movieNm",
        "genre_first",
        "total_audi"
    ]
].dropna()

fig5 = px.box(
    box_df,
    x="genre_first",
    y="total_audi",

    # ⭐ 그래프 4와 동일하게 장르별 색상
    color="genre_first",

    points="outliers",

    title="영화가 10편 이상인 장르의 총 관객수 분포",

    labels={
        "genre_first": "장르",
        "total_audi": "총 관객수"
    },

    custom_data=[
        "movieNm",
        "genre_first",
        "total_audi"
    ]
)

fig5.update_traces(
    hovertemplate=
    "<b>%{customdata[0]}</b><br>"
    "장르: %{customdata[1]}<br>"
    "총 관객수: %{customdata[2]:,}명"
    "<extra></extra>"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.subheader("💡 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프5 설명",
    placeholder="이 그래프로 알 수 있는 것을 입력하세요.",
    key="graph5_explanation"
)


# =========================================================
# 그래프 6
# =========================================================
st.header("그래프6) 버블 - 첫 주 관객수가 많으면 총 관객도 많은가")

bubble_df = df[
    [
        "movieNm",
        "genre_first",
        "first_scrn",
        "first_week_audi",
        "total_audi"
    ]
].dropna()

fig6 = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",

    # 장르별 색상
    color="genre_first",

    # 첫 주 관객수에 따라 원 크기
    size="first_week_audi",

    hover_name="movieNm",

    title="개봉일 스크린 수 × 총 관객수 × 첫 주 관객수",

    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객수",
        "first_week_audi": "첫 주 관객수",
        "genre_first": "장르"
    },

    custom_data=[
        "movieNm",
        "genre_first",
        "first_scrn",
        "first_week_audi",
        "total_audi"
    ]
)

fig6.update_traces(
    hovertemplate=
    "<b>%{customdata[0]}</b><br>"
    "장르: %{customdata[1]}<br>"
    "개봉일 스크린 수: %{customdata[2]:,}개<br>"
    "첫 주 관객수: %{customdata[3]:,}명<br>"
    "총 관객수: %{customdata[4]:,}명"
    "<extra></extra>"
)

st.plotly_chart(
    fig6,
    use_container_width=True
)

st.subheader("💡 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프6 설명",
    placeholder="이 그래프로 알 수 있는 것을 입력하세요.",
    key="graph6_explanation"
)


# =========================================================
# 그래프 7
# =========================================================
st.header("그래프7) 선버스트 - 국가와 장르에 따라 영화는 어떻게 구성되어 있나")

sunburst_df = df[
    [
        "nation",
        "genre_first"
    ]
].copy()

sunburst_df["nation"] = (
    sunburst_df["nation"]
    .fillna("미상")
)

sunburst_df["genre_first"] = (
    sunburst_df["genre_first"]
    .fillna("미상")
)

sunburst_df = (
    sunburst_df
    .groupby(
        [
            "nation",
            "genre_first"
        ]
    )
    .size()
    .reset_index(
        name="count"
    )
)

fig7 = px.sunburst(
    sunburst_df,
    path=[
        "nation",
        "genre_first"
    ],
    values="count",
    title="국가 → 장르별 영화 구성"
)

fig7.update_traces(
    hovertemplate=
    "항목: %{label}<br>"
    "영화 수: %{value}편<extra></extra>"
)

st.plotly_chart(
    fig7,
    use_container_width=True
)

st.subheader("💡 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프7 설명",
    placeholder="이 그래프로 알 수 있는 것을 입력하세요.",
    key="graph7_explanation"
)


# =========================================================
# 그래프 8
# =========================================================
st.header("그래프8) 산점도 - 개봉일 스크린 수가 많으면 상영 횟수도 많은가")

st.write(
    "가로축은 개봉일 스크린 수, "
    "세로축은 개봉일 상영 횟수입니다. "
    "점 하나는 영화 한 편을 나타냅니다."
)

graph8_df = df[
    [
        "movieNm",
        "genre_first",
        "first_scrn",
        "first_show"
    ]
].dropna()

fig8 = px.scatter(
    graph8_df,

    x="first_scrn",
    y="first_show",

    # 장르별 색상
    color="genre_first",

    hover_name="movieNm",

    title="개봉일 스크린 수와 상영 횟수의 관계",

    labels={
        "first_scrn": "개봉일 스크린 수",
        "first_show": "개봉일 상영 횟수",
        "genre_first": "장르"
    },

    custom_data=[
        "movieNm",
        "genre_first",
        "first_scrn",
        "first_show"
    ]
)

fig8.update_traces(
    hovertemplate=
    "<b>%{customdata[0]}</b><br>"
    "장르: %{customdata[1]}<br>"
    "개봉일 스크린 수: %{customdata[2]:,}개<br>"
    "개봉일 상영 횟수: %{customdata[3]:,}회"
    "<extra></extra>"
)

fig8.update_layout(
    xaxis_title="개봉일 스크린 수",
    yaxis_title="개봉일 상영 횟수"
)

st.plotly_chart(
    fig8,
    use_container_width=True
)

st.subheader("💡 이 그래프로 알 수 있는 것")

st.text_area(
    "그래프8 설명",
    placeholder="예: 개봉일 스크린 수와 상영 횟수 사이의 관계를 알 수 있다.",
    key="graph8_explanation"
)


# =========================================================
# 마무리
# =========================================================
st.divider()

st.success(
    "그래프 8은 직접 만든 질문을 산점도로 표현한 그래프입니다."
)
