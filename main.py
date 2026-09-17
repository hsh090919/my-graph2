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

st.write(
    "1년간 박스오피스 10위권에 든 영화 가운데 "
    "이 기간에 개봉한 영화들의 분포와 관계를 살펴봅니다."
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

    # 여러 장르가 있으면 첫 번째 장르만 사용
    df["genre_first"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 빈 장르 처리
    df.loc[
        df["genre_first"].isin(["", "nan", "None"]),
        "genre_first"
    ] = "미상"

    # 숫자형 열 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # 개봉일 변환
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    return df


try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.error(str(e))
    st.stop()


# ==================================================
# 그래프 1
# ==================================================

st.divider()

st.header("그래프 1) 도넛 - 장르별 영화 편수")

st.write(
    "여러 장르가 세로막대(|)로 표시된 영화는 "
    "첫 번째 장르만 사용했습니다."
)

genre_count = (
    df["genre_first"]
    .value_counts()
    .reset_index()
)

genre_count.columns = [
    "장르",
    "영화편수"
]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="영화편수",
    hole=0.5
)

fig1.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig1.update_layout(
    title="장르별 영화 편수",
    height=550,
    legend_title="장르"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 적어 보세요.",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    height=100,
    key="graph1_knowledge"
)


# ==================================================
# 그래프 2
# ==================================================

st.divider()

st.header("그래프 2) 트리맵 - 장르 안에는 어떤 영화가 들어 있나")

st.write(
    "장르 안에 영화를 배치하고, "
    "칸의 크기를 총 관객 수에 비례하여 나타냅니다."
)

treemap_data = df[
    [
        "genre_first",
        "movieNm",
        "total_audi"
    ]
].copy()

treemap_data["movieNm"] = (
    treemap_data["movieNm"]
    .fillna("영화명 없음")
    .astype(str)
)

treemap_data = treemap_data.dropna(
    subset=["total_audi"]
)

treemap_data = treemap_data[
    treemap_data["total_audi"] >= 0
]

fig2 = px.treemap(
    treemap_data,
    path=["genre_first", "movieNm"],
    values="total_audi",
    custom_data=["movieNm", "total_audi"]
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "총 관객: %{customdata[1]:,}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    title="장르별 영화와 총 관객",
    height=700,
    margin=dict(
        t=60,
        l=10,
        r=10,
        b=10
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 적어 보세요.",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    height=100,
    key="graph2_knowledge"
)


# ==================================================
# 그래프 3
# ==================================================

st.divider()

st.header("그래프 3) 히스토그램 - 영화의 총 관객은 어느 구간에 몰려 있나")

st.write(
    "각 영화의 총 관객 수가 어느 구간에 많이 분포하는지 "
    "히스토그램으로 확인합니다."
)

hist_data = df[
    ["movieNm", "total_audi"]
].copy()

hist_data["movieNm"] = (
    hist_data["movieNm"]
    .fillna("영화명 없음")
    .astype(str)
)

hist_data = hist_data.dropna(
    subset=["total_audi"]
)

hist_data = hist_data[
    hist_data["total_audi"] >= 0
]

if not hist_data.empty:

    max_movie_row = hist_data.loc[
        hist_data["total_audi"].idxmax()
    ]

    max_movie_name = max_movie_row["movieNm"]
    max_movie_audience = int(max_movie_row["total_audi"])

    hist_data["관객구간"] = pd.cut(
        hist_data["total_audi"],
        bins=10,
        include_lowest=True
    )

    bin_counts = (
        hist_data["관객구간"]
        .value_counts()
        .sort_index()
    )

    most_common_bin = bin_counts.idxmax()
    most_common_count = int(bin_counts.max())

    bin_start = most_common_bin.left
    bin_end = most_common_bin.right

    fig3 = px.histogram(
        hist_data,
        x="total_audi",
        nbins=10,
        labels={
            "total_audi": "총 관객 수",
            "count": "영화 편수"
        },
        title="영화별 총 관객 수 분포"
    )

    fig3.update_traces(
        hovertemplate=(
            "총 관객 구간: %{x}<br>"
            "영화 편수: %{y}편"
            "<extra></extra>"
        )
    )

    fig3.update_layout(
        height=550,
        xaxis_title="총 관객 수",
        yaxis_title="영화 편수"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    st.markdown("### 📌 히스토그램에서 확인할 수 있는 내용")

    st.info(
        f"🎬 **대부분의 영화가 몰려 있는 구간:** "
        f"약 {bin_start:,.0f}명 ~ {bin_end:,.0f}명 "
        f"(이 구간에 {most_common_count}편)"
    )

    st.info(
        f"🏆 **총 관객이 가장 많은 영화:** "
        f"**{max_movie_name}** "
        f"({max_movie_audience:,}명)"
    )

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 적어 보세요.",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    height=100,
    key="graph3_knowledge"
)


# ==================================================
# 그래프 4
# ==================================================

st.divider()

st.header("그래프 4) 산점도 - 개봉일 스크린수가 많으면 총 관객도 많을까")

st.write(
    "개봉일 스크린수와 총 관객의 관계를 산점도로 나타냅니다. "
    "각 점은 하나의 영화이며, 장르에 따라 색을 다르게 표시합니다."
)

scatter_data = df[
    [
        "movieNm",
        "genre_first",
        "first_scrn",
        "total_audi"
    ]
].copy()

scatter_data["movieNm"] = (
    scatter_data["movieNm"]
    .fillna("영화명 없음")
    .astype(str)
)

scatter_data = scatter_data.dropna(
    subset=[
        "first_scrn",
        "total_audi"
    ]
)

scatter_data = scatter_data[
    (scatter_data["first_scrn"] >= 0)
    & (scatter_data["total_audi"] >= 0)
]

fig4 = px.scatter(
    scatter_data,
    x="first_scrn",
    y="total_audi",
    color="genre_first",
    hover_name="movieNm",
    custom_data=[
        "movieNm",
        "genre_first",
        "first_scrn",
        "total_audi"
    ],
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "genre_first": "장르"
    },
    title="개봉일 스크린수와 총 관객의 관계"
)

fig4.update_traces(
    marker=dict(
        size=10,
        opacity=0.75
    ),
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "장르: %{customdata[1]}<br>"
        "개봉일 스크린수: %{customdata[2]:,}개<br>"
        "총 관객: %{customdata[3]:,}명"
        "<extra></extra>"
    )
)

fig4.update_layout(
    height=650,
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객",
    legend_title="장르"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 적어 보세요.",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    height=100,
    key="graph4_knowledge"
)


# ==================================================
# 그래프 5
# ==================================================

st.divider()

st.header("그래프 5) 상자 그림 - 장르별 총 관객 분포는 어떻게 다른가")

st.write(
    "영화가 10편 이상인 장르만 골라 "
    "장르별 총 관객 수의 분포를 상자 그림으로 비교합니다."
)

# --------------------------------------------------
# 장르별 영화 수 계산
# --------------------------------------------------

genre_counts_for_box = (
    df["genre_first"]
    .value_counts()
)

# 영화가 10편 이상인 장르만 선택
valid_genres = genre_counts_for_box[
    genre_counts_for_box >= 10
].index.tolist()

box_data = df[
    df["genre_first"].isin(valid_genres)
].copy()

box_data = box_data[
    [
        "genre_first",
        "movieNm",
        "total_audi"
    ]
].dropna(
    subset=["total_audi"]
)

box_data = box_data[
    box_data["total_audi"] >= 0
]

# --------------------------------------------------
# 박스플롯
# --------------------------------------------------

if not box_data.empty:

    fig5 = px.box(
        box_data,
        x="genre_first",
        y="total_audi",
        color="genre_first",
        points="outliers",
        custom_data=[
            "movieNm",
            "genre_first",
            "total_audi"
        ],
        labels={
            "genre_first": "장르",
            "total_audi": "총 관객"
        },
        title="영화 10편 이상인 장르의 총 관객 분포"
    )

    # 이상치에 마우스를 올렸을 때 영화명 표시
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
        yaxis_title="총 관객",
        showlegend=False
    )

    st.plotly_chart(
        fig5,
        use_container_width=True
    )

    st.caption(
        "※ 상자 밖에 표시되는 점은 해당 장르의 일반적인 분포에서 "
        "상대적으로 멀리 떨어진 값(이상치)입니다. "
        "점에 마우스를 올리면 영화명을 확인할 수 있습니다."
    )

else:

    st.warning(
        "영화가 10편 이상인 장르가 없어 "
        "상자 그림을 그릴 수 없습니다."
    )


# --------------------------------------------------
# 그래프 5 설명
# --------------------------------------------------

st.markdown("### 💡 이 그래프로 알 수 있는 것")

st.text_area(
    "한 문장으로 적어 보세요.",
    placeholder="이 그래프로 알 수 있는 것을 한 문장으로 적어 보세요.",
    height=100,
    key="graph5_knowledge"
)


# ==================================================
# 데이터 기본 정보
# ==================================================

st.divider()

st.subheader("📊 데이터 기본 정보")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "분석한 영화 수",
        f"{len(df)}편"
    )

with col2:
    st.metric(
        "장르 종류",
        f"{genre_count['장르'].nunique()}개"
    )


# ==================================================
# 장르별 영화 편수
# ==================================================

st.subheader("장르별 영화 편수")

st.dataframe(
    genre_count,
    use_container_width=True,
    hide_index=True
)
