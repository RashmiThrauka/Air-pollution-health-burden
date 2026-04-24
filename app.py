import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="Air Pollution Health Burden Dashboard",
    page_icon="🌫️",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(BASE_DIR, "DataExtract.csv"))
    aggregates = ["All Countries", "European Environment Agency Member Countries", "European Union Countries"]
    df = df[~df["Country Or Territory"].isin(aggregates)].copy()
    country = df[df["NUTS Code"].str.len() == 2].copy()
    return df, country

full_data, country_data = load_data()

st.title("🌫️ Air Pollution Health Burden in Europe")
st.caption("Burden of disease attributable to air pollution (2022) · Source: European Environment Agency")
st.divider()

st.sidebar.header("Filters")

all_countries = sorted(country_data["Country Or Territory"].unique())
selected_countries = st.sidebar.multiselect("Country", all_countries, default=all_countries)

pollutants = sorted(country_data["Air Pollutant"].unique())
selected_pollutant = st.sidebar.selectbox("Air Pollutant", pollutants, index=pollutants.index("PM2.5") if "PM2.5" in pollutants else 0)

categories = sorted(country_data["Category"].unique())
selected_category = st.sidebar.selectbox("Category", categories, index=categories.index("Mortality") if "Mortality" in categories else 0)

indicators = sorted(country_data["Health Indicator"].unique())
selected_indicator = st.sidebar.selectbox("Health Indicator", indicators)

filtered = country_data[
    (country_data["Country Or Territory"].isin(selected_countries)) &
    (country_data["Air Pollutant"] == selected_pollutant) &
    (country_data["Category"] == selected_category) &
    (country_data["Health Indicator"] == selected_indicator)
]

if filtered.empty:
    st.warning("No data matches the current filters. Adjust the sidebar filters.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Countries", filtered["Country Or Territory"].nunique())
with col2:
    total_value = filtered["Value"].sum()
    st.metric("Total Burden", f"{total_value:,.0f}")
with col3:
    avg_rate = filtered["Value for 100k Of Affected Population"].mean()
    st.metric("Avg per 100k", f"{avg_rate:.1f}")
with col4:
    avg_pollution = filtered["Air Pollution Population Weighted Average [ug/m3]"].mean()
    st.metric("Avg Pollution (µg/m³)", f"{avg_pollution:.1f}")

st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ Map", "📊 Country Ranking", "🔬 Analysis", "🔄 Comparison", "📋 Data"])

with tab1:
    map_data = filtered.copy()
    fig_map = px.choropleth(
        map_data,
        locations="NUTS Code",
        locationmode="ISO-3166-1 alpha-2",
        color="Value for 100k Of Affected Population",
        hover_name="Country Or Territory",
        hover_data={
            "Value": ":,.0f",
            "Air Pollution Population Weighted Average [ug/m3]": ":.1f",
            "NUTS Code": False
        },
        color_continuous_scale="YlOrRd",
        labels={
            "Value for 100k Of Affected Population": "Per 100k",
            "Air Pollution Population Weighted Average [ug/m3]": "Pollution (µg/m³)"
        },
        scope="europe"
    )
    fig_map.update_layout(
        height=550,
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor="lightgray"),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_map, use_container_width=True)

    top_col, bottom_col = st.columns(2)
    with top_col:
        st.markdown("**Highest Burden (per 100k)**")
        top10 = map_data.nlargest(10, "Value for 100k Of Affected Population")[
            ["Country Or Territory", "Value for 100k Of Affected Population", "Value"]
        ].reset_index(drop=True)
        top10.index = top10.index + 1
        top10.columns = ["Country", "Per 100k", "Total"]
        top10["Per 100k"] = top10["Per 100k"].round(1)
        top10["Total"] = top10["Total"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(top10, use_container_width=True)
    with bottom_col:
        st.markdown("**Lowest Burden (per 100k)**")
        bottom10 = map_data.nsmallest(10, "Value for 100k Of Affected Population")[
            ["Country Or Territory", "Value for 100k Of Affected Population", "Value"]
        ].reset_index(drop=True)
        bottom10.index = bottom10.index + 1
        bottom10.columns = ["Country", "Per 100k", "Total"]
        bottom10["Per 100k"] = bottom10["Per 100k"].round(1)
        bottom10["Total"] = bottom10["Total"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(bottom10, use_container_width=True)

with tab2:
    st.subheader("Country Ranking by Health Burden")
    rank_data = filtered[["Country Or Territory", "Value for 100k Of Affected Population", "Value"]].sort_values(
        "Value for 100k Of Affected Population", ascending=True
    )
    fig_rank = px.bar(
        rank_data,
        x="Value for 100k Of Affected Population",
        y="Country Or Territory",
        orientation="h",
        color="Value for 100k Of Affected Population",
        color_continuous_scale="YlOrRd",
        labels={"Value for 100k Of Affected Population": "Per 100k", "Country Or Territory": ""},
        hover_data={"Value": ":,.0f"}
    )
    fig_rank.update_layout(height=max(400, len(rank_data) * 22), showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig_rank, use_container_width=True)

with tab3:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Distribution of Burden per 100k")
        fig_hist = px.histogram(
            filtered, x="Value for 100k Of Affected Population", nbins=15,
            labels={"Value for 100k Of Affected Population": "Per 100k", "count": "Number of Countries"},
            color_discrete_sequence=["#E74C3C"]
        )
        fig_hist.update_layout(height=400, bargap=0.05)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_right:
        st.subheader("Pollution Level vs Health Burden")
        fig_scatter = px.scatter(
            filtered,
            x="Air Pollution Population Weighted Average [ug/m3]",
            y="Value for 100k Of Affected Population",
            hover_name="Country Or Territory",
            size="Affected Population",
            size_max=40,
            labels={
                "Air Pollution Population Weighted Average [ug/m3]": "Pollution (µg/m³)",
                "Value for 100k Of Affected Population": "Burden per 100k"
            },
            color_discrete_sequence=["#E74C3C"]
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Burden by Health Outcome")
    outcome_data = country_data[
        (country_data["Country Or Territory"].isin(selected_countries)) &
        (country_data["Air Pollutant"] == selected_pollutant) &
        (country_data["Category"] == selected_category) &
        (country_data["Health Indicator"] == selected_indicator)
    ]
    if not outcome_data.empty:
        outcome_agg = outcome_data.groupby("Outcome")["Value"].sum().reset_index().sort_values("Value", ascending=True)
        fig_outcome = px.bar(
            outcome_agg, x="Value", y="Outcome", orientation="h",
            labels={"Value": "Total Burden", "Outcome": ""},
            color_discrete_sequence=["#3498DB"]
        )
        fig_outcome.update_layout(height=max(250, len(outcome_agg) * 40))
        st.plotly_chart(fig_outcome, use_container_width=True)

with tab4:
    st.subheader("Compare Countries")
    compare_countries = st.multiselect(
        "Select countries to compare (max 10)",
        all_countries,
        default=all_countries[:3] if len(all_countries) >= 3 else all_countries,
        max_selections=10
    )

    if compare_countries:
        compare_data = country_data[
            (country_data["Country Or Territory"].isin(compare_countries)) &
            (country_data["Air Pollutant"] == selected_pollutant) &
            (country_data["Category"] == selected_category) &
            (country_data["Health Indicator"] == selected_indicator)
        ]

        if not compare_data.empty:
            fig_compare = px.bar(
                compare_data.sort_values("Value for 100k Of Affected Population"),
                x="Value for 100k Of Affected Population",
                y="Country Or Territory",
                orientation="h",
                color="Country Or Territory",
                labels={"Value for 100k Of Affected Population": "Per 100k", "Country Or Territory": ""}
            )
            fig_compare.update_layout(height=max(300, len(compare_countries) * 40), showlegend=False)
            st.plotly_chart(fig_compare, use_container_width=True)

            st.subheader("Summary Table")
            summary = compare_data[["Country Or Territory", "Value", "Value for 100k Of Affected Population",
                                     "Air Pollution Population Weighted Average [ug/m3]", "Affected Population"]].copy()
            summary.columns = ["Country", "Total Burden", "Per 100k", "Pollution (µg/m³)", "Affected Population"]
            summary["Total Burden"] = summary["Total Burden"].apply(lambda x: f"{x:,.0f}")
            summary["Per 100k"] = summary["Per 100k"].round(1)
            summary["Pollution (µg/m³)"] = summary["Pollution (µg/m³)"].round(1)
            summary["Affected Population"] = summary["Affected Population"].apply(lambda x: f"{x:,.0f}")
            summary = summary.sort_values("Per 100k", ascending=False).reset_index(drop=True)
            summary.index = summary.index + 1
            st.dataframe(summary, use_container_width=True)

    st.subheader("Compare Across Pollutants")
    pollutant_compare = country_data[
        (country_data["Country Or Territory"].isin(compare_countries if compare_countries else all_countries[:5])) &
        (country_data["Category"] == selected_category) &
        (country_data["Health Indicator"] == selected_indicator) &
        (country_data["Outcome"] == "All causes")
    ]
    if not pollutant_compare.empty:
        fig_poll = px.bar(
            pollutant_compare,
            x="Country Or Territory",
            y="Value for 100k Of Affected Population",
            color="Air Pollutant",
            barmode="group",
            labels={"Value for 100k Of Affected Population": "Per 100k", "Country Or Territory": "", "Air Pollutant": "Pollutant"}
        )
        fig_poll.update_layout(height=450, xaxis_tickangle=-30)
        st.plotly_chart(fig_poll, use_container_width=True)

with tab5:
    st.subheader("Filtered Data")
    display_data = filtered[[
        "Country Or Territory", "NUTS Code", "Air Pollutant", "Category",
        "Outcome", "Health Indicator", "Value", "Value for 100k Of Affected Population",
        "Air Pollution Population Weighted Average [ug/m3]"
    ]].copy()
    display_data.columns = ["Country", "Code", "Pollutant", "Category", "Outcome",
                            "Indicator", "Value", "Per 100k", "Pollution (µg/m³)"]
    display_data = display_data.sort_values("Country").reset_index(drop=True)

    search = st.text_input("Search by country name")
    if search:
        display_data = display_data[display_data["Country"].str.contains(search, case=False)]

    st.dataframe(display_data, use_container_width=True, height=500)
    st.download_button(
        "Download filtered data as CSV",
        display_data.to_csv(index=False),
        "filtered_data.csv",
        "text/csv"
    )
