import streamlit as st
import pandas as pd
import plotly.express as px


# =========================================================
# 페이지 설정
# =========================================================
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

st.write(
    "KOBIS 영화 216편 데이터를 이용하여 "
    "영화의 분포와 변수 사이의 관계를 살펴봅니다."
)


# =========================================================
# 데이터 불러오기
# =========================================================
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/"
    "main/data/kobis_movies.csv"
)

try:
    df = pd.read_csv(DATA_URL)
except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.code(str(e))
    st.stop()


# =========================================================
# 데이터 전처리
# =========================================================

# 숫자형 데이터 변환
numeric_columns = [
    "first_scrn",
    "first_show",
    "first_week_audi",
    "total_audi",
    "days_in_top10"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# 개봉일 변환
if "openDt" in df.columns:

    df["openDt"] = (
        df["openDt"]
        .astype(str)
        .str.replace(".0", "", regex=False)
    )

    df["openDt"] = pd.to_datetime(
        df["openDt"],
        format="%Y%m%d",
        errors="coerce"
    )


# =========================================================
# 장르 전처리
# 여러 장르가 있으면 첫 번째 장르만 사용
# =========================================================
if "genre" in df.columns:

    df["genre_first"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    df.loc[
        df["genre_first"].isin(
            ["", "nan", "None"]
        ),
        "genre_first"
    ] = "미상"

else:

    df["genre_first"] = "미상"


# =========================================================
# 국가 전처리
# =========================================================
if "nation" in df.columns:

    df["nation"] = (
        df["nation"]
        .fillna("미상")
        .astype(str)
        .str.strip()
    )

    df.loc[
        df["nation"].isin(
            ["", "nan", "None"]
        ),
        "nation"
    ] = "미상"

else:

    df["nation"] = "미상"


# =========================================================
# 영화명 전처리
# =========================================================
if "movieNm" in df.columns:

    df["movieNm"] = (
        df["movieNm"]
        .fillna("영화명 없음")
        .astype(str)
    )


# =========================================================
# 그래프 1
# 장르별 영화 수 - 도넛 차트
# =========================================================
st.divider()

st.header(
    "그래프 1) 도넛 - 장르별로 영화가 얼마나 있나"
)

st.write(
    "각 영화의 첫 번째 장르를 기준으로 "
    "장르별 영화 편수를 나타냅니다."
)

genre_count = (
    df["genre_first"]
    .value_counts()
    .reset_index()
)

genre_count.columns = [
    "장르",
    "영화수"
]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화수",
    hole=0.45,
    title="장르별 영화 수"
)

fig1.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 수: %{value}편<br>"
        "비율: %{percent}"
        "<extra></extra>"
    )
)

fig1.update_layout(
    height=600
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.markdown(
    "### 💡 이 그래프로 알 수 있는 것"
)

st.text_area(
    "한 문장으로 적어 보세요.",
    placeholder=(
        "이 그래프로 알 수 있는 것을 "
        "한 문장으로 적어 보세요."
    ),
    height=100,
    key="graph1_knowledge"
)


# =========================================================
# 그래프 2
# 장르 → 영화 트리맵
# =========================================================
st.divider()

st.header(
    "그래프 2) 트리맵 - 어떤 장르의 어떤 영화가 많이 흥행했나"
)

st.write(
    "장르 안에 어떤 영화가 포함되어 있는지 나타내고, "
    "타일의 크기는 총 관객수를 의미합니다."
)

treemap_data = df[
    [
        "genre_first",
        "movieNm",
        "total_audi"
    ]
].copy()

treemap_data = treemap_data.dropna(
    subset=["total_audi"]
)

treemap_data = treemap_data[
    treemap_data["total_audi"] >= 0
]

if not treemap_data.empty:

    fig2 = px.treemap(
        treemap_data,
        path=[
            "genre_first",
            "movieNm"
        ],
        values="total_audi",
        title="장르별 영화의 총 관객수"
    )

    fig2.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "총 관객: %{value:,}명"
            "<extra></extra>"
        )
    )

    fig2.update_layout(
        height=700
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

else:

    st.warning(
        "트리맵을 만들 수 있는 데이터가 없습니다."
    )


st.markdown(
    "### 💡 이 그래프로 알 수 있는 것"
)

st.text_area(
    "한 문장으로 적어 보세요.",
    placeholder=(
        "이 그래프로 알 수 있는 것을 "
        "한 문장으로 적어 보세요."
    ),
    height=100,
    key="graph2_knowledge"
)


# =========================================================
# 그래프 3
# 총 관객수 히스토그램
# =========================================================
st.divider()

st.header(
    "그래프 3) 히스토그램 - 영화의 총 관객수는 어떻게 분포하나"
)

st.write(
    "216편 영화의 총 관객수가 "
    "어떤 구간에 많이 모여 있는지 확인합니다."
)

hist_data = df[
    [
        "movieNm",
        "total_audi"
    ]
].dropna(
    subset=["total_audi"]
)

hist_data = hist_data[
    hist_data["total_audi"] >= 0
]

if not hist_data.empty:

    fig3 = px.histogram(
        hist_data,
        x="total_audi",
        nbins=10,
        title="영화별 총 관객수 분포",
        labels={
            "total_audi": "총 관객수"
        }
    )

    fig3.update_layout(
        height=600,
        xaxis_title="총 관객수",
        yaxis_title="영화 수"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    max_movie = hist_data.loc[
        hist_data["total_audi"].idxmax()
    ]

    st.info(
        f"총 관객수가 가장 많은 영화는 "
        f"**{max_movie['movieNm']}**이며, "
        f"총 관객수는 "
        f"**{max_movie['total_audi']:,.0f}명**입니다."
    )

else:

    st.warning(
        "히스토그램을 만들 수 있는 데이터가 없습니다."
    )


st.markdown(
    "### 💡 이 그래프로 알 수 있는 것"
)

st.text_area(
    "한 문장으로 적어 보세요.",
    placeholder=(
        "이 그래프로 알 수 있는 것을 "
        "한 문장으로 적어 보세요."
    ),
    height=100,
    key="graph3_knowledge"
)


# =========================================================
# 그래프 4
# 개봉일 스크린 수 vs 총 관객수
# =========================================================
st.divider()

st.header(
    "그래프 4) 산점도 - 개봉일 스크린 수가 많으면 총 관객도 많은가"
)

st.write(
    "개봉일 스크린 수와 총 관객수의 관계를 나타냅니다."
)

scatter4_data = df[
    [
        "movieNm",
        "genre_first",
        "first_scrn",
        "total_audi"
    ]
].dropna(
    subset=[
        "first_scrn",
        "total_audi"
    ]
)

scatter4_data = scatter4_data[
    (scatter4_data["first_scrn"] >= 0)
    & (scatter4_data["total_audi"] >= 0)
]

if not scatter4_data.empty:

    fig4 = px.scatter(
        scatter4_data,
        x="first_scrn",
        y="total_audi",
        hover_name="movieNm",
        color="genre_first",
        custom_data=[
            "movieNm",
            "genre_first",
            "first_scrn",
            "total_audi"
        ],
        labels={
            "first_scrn": "개봉일 스크린 수",
            "total_audi": "총 관객",
            "genre_first": "장르"
        },
        title="개봉일 스크린 수와 총 관객수의 관계"
    )

    fig4.update_traces(
        marker=dict(
            size=10,
            opacity=0.75
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "장르: %{customdata[1]}<br>"
            "개봉일 스크린 수: "
            "%{customdata[2]:,}개<br>"
            "총 관객: "
            "%{customdata[3]:,}명"
            "<extra></extra>"
        )
    )

    fig4.update_layout(
        height=650,
        xaxis_title="개봉일 스크린 수",
        yaxis_title="총 관객"
    )

    st.plotly_chart(
        fig4,
        use_container_width=True
    )

else:

    st.warning(
        "산점도를 그릴 수 있는 데이터가 없습니다."
    )


st.markdown(
    "### 💡 이 그래프로 알 수 있는 것"
)

st.text_area(
    "한 문장으로 적어 보세요.",
    placeholder=(
        "이 그래프로 알 수 있는 것을 "
        "한 문장으로 적어 보세요."
    ),
    height=100,
    key="graph4_knowledge"
)


# =========================================================
# 그래프 5
# 장르별 총 관객수 Box Plot
# =========================================================
st.divider()

st.header(
    "그래프 5) 상자수염 - 장르별 총 관객수 분포는 어떻게 다른가"
)

st.write(
    "영화 수가 10편 이상인 장르만 대상으로 "
    "총 관객수의 분포를 비교합니다."
)

box5_data = df[
    [
        "movieNm",
        "genre_first",
        "total_audi"
    ]
].dropna(
    subset=[
        "genre_first",
        "total_audi"
    ]
)

box5_data = box5_data[
    box5_data["total_audi"] >= 0
]

genre_counts5 = (
    box5_data["genre_first"]
    .value_counts()
)

valid_genres5 = genre_counts5[
    genre_counts5 >= 10
].index

box5_data = box5_data[
    box5_data["genre_first"].isin(
        valid_genres5
    )
].copy()

if not box5_data.empty:

    fig5 = px.box(
        box5_data,
        x="genre_first",
        y="total_audi",
        points="outliers",
        hover_name="movieNm",
        custom_data=[
            "movieNm",
            "genre_first",
            "total_audi"
        ],
        labels={
            "genre_first": "장르",
            "total_audi": "총 관객"
        },
        title="장르별 총 관객수 분포"
    )

    fig5.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "장르: %{customdata[1]}<br>"
            "총 관객: %{customdata[2]:,}명"
            "<extra></extra>"
        )
    )

    fig5.update_layout(
        height=650,
        xaxis_title="장르",
        yaxis_title="총 관객"
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

else:

    st.warning(
        "10편 이상인 장르가 없어 "
        "상자수염그래프를 만들 수 없습니다."
    )


st.markdown(
    "### 💡 이 그래프로 알 수 있는 것"
)

st.text_area(
    "한 문장으로 적어 보세요.",
    placeholder=(
        "이 그래프로 알 수 있는 것을 "
        "한 문장으로 적어 보세요."
    ),
    height=100,
    key="graph5_knowledge"
)


# =========================================================
# 그래프 6
# 버블 차트
# =========================================================
st.divider()

st.header(
    "그래프 6) 버블 - 개봉일 스크린 수와 총 관객의 관계"
)

st.write(
    "가로축은 개봉일 스크린 수, "
    "세로축은 총 관객수이며 "
    "버블의 크기는 첫 주 관객수를 나타냅니다."
)

bubble_data = df[
    [
        "movieNm",
        "genre_first",
        "first_scrn",
        "first_week_audi",
        "total_audi"
    ]
].dropna(
    subset=[
        "first_scrn",
        "first_week_audi",
        "total_audi"
    ]
)

bubble_data = bubble_data[
    (bubble_data["first_scrn"] >= 0)
    & (bubble_data["first_week_audi"] >= 0)
    & (bubble_data["total_audi"] >= 0)
]

if not bubble_data.empty:

    fig6 = px.scatter(
        bubble_data,
        x="first_scrn",
        y="total_audi",
        size="first_week_audi",
        color="genre_first",
        hover_name="movieNm",
        custom_data=[
            "movieNm",
            "genre_first",
            "first_scrn",
            "first_week_audi",
            "total_audi"
        ],
        size_max=55,
        labels={
            "first_scrn": "개봉일 스크린 수",
            "total_audi": "총 관객",
            "first_week_audi": "첫 주 관객",
            "genre_first": "장르"
        },
        title="개봉일 스크린 수와 총 관객수의 관계"
    )

    fig6.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "장르: %{customdata[1]}<br>"
            "개봉일 스크린 수: "
            "%{customdata[2]:,}개<br>"
            "첫 주 관객: "
            "%{customdata[3]:,}명<br>"
            "총 관객: "
            "%{customdata[4]:,}명"
            "<extra></extra>"
        )
    )

    fig6.update_layout(
        height=700,
        xaxis_title="개봉일 스크린 수",
        yaxis_title="총 관객"
    )

    st.plotly_chart(
        fig6,
        use_container_width=True
    )

else:

    st.warning(
        "버블 차트를 그릴 수 있는 데이터가 없습니다."
    )


st.markdown(
    "### 💡 이 그래프로 알 수 있는 것"
)

st.text_area(
    "한 문장으로 적어 보세요.",
    placeholder=(
        "이 그래프로 알 수 있는 것을 "
        "한 문장으로 적어 보세요."
    ),
    height=100,
    key="graph6_knowledge"
)


# =========================================================
# 그래프 7
# 국가 → 장르 선버스트
# =========================================================
st.divider()

st.header(
    "그래프 7) 선버스트 - 국가별 장르 구성은 어떻게 다른가"
)

st.write(
    "영화를 제작한 국가와 장르의 구성을 "
    "하나의 계층 구조로 나타냅니다."
)

sunburst_data = df[
    [
        "nation",
        "genre_first"
    ]
].copy()

sunburst_data["nation"] = (
    sunburst_data["nation"]
    .fillna("미상")
    .astype(str)
)

sunburst_data["genre_first"] = (
    sunburst_data["genre_first"]
    .fillna("미상")
    .astype(str)
)

sunburst_count = (
    sunburst_data
    .groupby(
        [
            "nation",
            "genre_first"
        ],
        as_index=False
    )
    .size()
    .rename(
        columns={
            "size": "영화수"
        }
    )
)

if not sunburst_count.empty:

    fig7 = px.sunburst(
        sunburst_count,
        path=[
            "nation",
            "genre_first"
        ],
        values="영화수",
        title="제작 국가별 장르 구성"
    )

    fig7.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "영화 수: %{value}편"
            "<extra></extra>"
        )
    )

    fig7.update_layout(
        height=700
    )

    st.plotly_chart(
        fig7,
        use_container_width=True
    )

else:

    st.warning(
        "선버스트를 만들 수 있는 데이터가 없습니다."
    )


st.markdown(
    "### 💡 이 그래프로 알 수 있는 것"
)

st.text_area(
    "한 문장으로 적어 보세요.",
    placeholder=(
        "이 그래프로 알 수 있는 것을 "
        "한 문장으로 적어 보세요."
    ),
    height=100,
    key="graph7_knowledge"
)


# =========================================================
# 그래프 8
# 학생이 직접 만든 질문
# =========================================================
st.divider()

st.header(
    "그래프 8) 상자수염 - 장르에 따라 영화의 총 관객 분포가 다른가"
)

st.write(
    "질문: **장르에 따라 영화의 총 관객 분포가 다른가?**"
)

st.write(
    "장르별로 영화의 총 관객수가 어떻게 분포하는지 "
    "상자수염그래프로 비교합니다."
)


# 그래프 8 데이터 준비
box8_data = df[
    [
        "movieNm",
        "genre_first",
        "total_audi"
    ]
].copy()

box8_data["movieNm"] = (
    box8_data["movieNm"]
    .fillna("영화명 없음")
    .astype(str)
)

box8_data["genre_first"] = (
    box8_data["genre_first"]
    .fillna("미상")
    .astype(str)
)

box8_data["total_audi"] = pd.to_numeric(
    box8_data["total_audi"],
    errors="coerce"
)

box8_data = box8_data.dropna(
    subset=[
        "genre_first",
        "total_audi"
    ]
)

box8_data = box8_data[
    box8_data["total_audi"] >= 0
]


# 장르별 영화 수 확인
genre_count8 = (
    box8_data["genre_first"]
    .value_counts()
)

# 영화가 10편 이상인 장르만 비교
valid_genres8 = genre_count8[
    genre_count8 >= 10
].index

box8_data = box8_data[
    box8_data["genre_first"].isin(
        valid_genres8
    )
].copy()


if not box8_data.empty:

    fig8 = px.box(
        box8_data,
        x="genre_first",
        y="total_audi",
        points="all",
        hover_name="movieNm",
        custom_data=[
            "movieNm",
            "genre_first",
            "total_audi"
        ],
        labels={
            "genre_first": "장르",
            "total_audi": "총 관객"
        },
        title="장르에 따라 영화의 총 관객 분포가 다른가"
    )

    fig8.update_traces(
        marker=dict(
            size=6,
            opacity=0.7
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "장르: %{customdata[1]}<br>"
            "총 관객: %{customdata[2]:,}명"
            "<extra></extra>"
        )
    )

    fig8.update_layout(
        height=700,
        xaxis_title="장르",
        yaxis_title="총 관객"
    )

    st.plotly_chart(
        fig8,
        use_container_width=True
    )

else:

    st.warning(
        "비교할 수 있는 장르 데이터가 없습니다."
    )


st.markdown(
    "### 💡 이 그래프로 알 수 있는 것"
)

st.text_area(
    "한 문장으로 적어 보세요.",
    value=(
        "장르별 영화의 총 관객수 분포와 "
        "차이를 비교할 수 있다."
    ),
    height=100,
    key="graph8_knowledge"
)


# =========================================================
# 데이터 정보
# =========================================================
st.divider()

st.header("📋 데이터 정보")

st.write(
    f"전체 영화 데이터: **{len(df)}편**"
)

info_columns = [
    "movieCd",
    "movieNm",
    "openDt",
    "genre",
    "nation",
    "first_scrn",
    "first_show",
    "first_week_audi",
    "total_audi",
    "days_in_top10"
]

available_info_columns = [
    col for col in info_columns
    if col in df.columns
]

st.dataframe(
    df[available_info_columns],
    use_container_width=True,
    hide_index=True
)
