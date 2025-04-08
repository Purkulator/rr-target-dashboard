import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="RR Target Dashboard", layout="wide")

# Load Excel file
target_file = st.file_uploader("Upload the RR Target Analysis Excel file", type=["xlsx"])

if target_file:
    all_data = pd.read_excel(target_file, sheet_name=None)
    df = all_data["Overall Hit Rates"]

    # Rename columns if they have placeholder names
    def rename_dim_column(df, preferred_name):
        col = df.columns[0]
        if preferred_name.lower() not in col.lower():
            df = df.rename(columns={col: preferred_name})
        return df

    fib_df = rename_dim_column(all_data.get("By Fibonacci Level"), "Fibonacci Bucket")
    range_df = rename_dim_column(all_data.get("By Range Bucket"), "Range Bucket")
    ticker_df = rename_dim_column(all_data.get("By Ticker"), "Ticker")
    tf_df = rename_dim_column(all_data.get("By Time Frame"), "Time Frame")
    time_df = rename_dim_column(all_data.get("By Time of Day"), "Time of Day")

    st.sidebar.header("Filter Setup")
    if st.sidebar.button("Reset Filters"):
        selected_tickers = ticker_df["Ticker"].unique()
        selected_tfs = tf_df["Time Frame"].unique()
        selected_ranges = range_df["Range Bucket"].unique()
        selected_fibs = fib_df["Fibonacci Bucket"].unique()
        selected_times = time_df["Time of Day"].unique()
    else:
        selected_tickers = st.sidebar.multiselect("Ticker(s)", ticker_df["Ticker"].unique(), default=ticker_df["Ticker"].unique())
        selected_tfs = st.sidebar.multiselect("Time Frame(s)", tf_df["Time Frame"].unique(), default=tf_df["Time Frame"].unique())
        selected_ranges = st.sidebar.multiselect("Range Bucket(s)", range_df["Range Bucket"].unique(), default=range_df["Range Bucket"].unique())
        selected_fibs = st.sidebar.multiselect("Fibonacci Bucket(s)", fib_df["Fibonacci Bucket"].unique(), default=fib_df["Fibonacci Bucket"].unique())
        selected_times = st.sidebar.multiselect("Time of Day", time_df["Time of Day"].unique(), default=time_df["Time of Day"].unique())

    # Filter each dimension dataframe
    t_df = ticker_df[ticker_df["Ticker"].isin(selected_tickers)]
    f_df = fib_df[fib_df["Fibonacci Bucket"].isin(selected_fibs)]
    r_df = range_df[range_df["Range Bucket"].isin(selected_ranges)]
    tf_df = tf_df[tf_df["Time Frame"].isin(selected_tfs)]
    td_df = time_df[time_df["Time of Day"].isin(selected_times)]

    # Merge on RR Target
    merged = t_df.merge(f_df, on="RR Target", suffixes=("", "_fib"))
    merged = merged.merge(r_df, on="RR Target", suffixes=("", "_range"))
    merged = merged.merge(tf_df, on="RR Target", suffixes=("", "_tf"))
    merged = merged.merge(td_df, on="RR Target", suffixes=("", "_time"))

    # Filter RR Target range to 1.5–3.5 to avoid overlapping
    merged = merged[(merged["RR Target"] >= 1.5) & (merged["RR Target"] <= 3.5)]

    # Calculate combined hit rate across all matching filters
    merged["Average Hit Rate"] = merged[["Hit Rate", "Hit Rate_fib", "Hit Rate_range", "Hit Rate_tf", "Hit Rate_time"]].mean(axis=1)

    st.header("🎯 Filtered Hit Rate Curve")
    fig, ax = plt.subplots()
    ax.plot(merged["RR Target"], merged["Average Hit Rate"]*100, marker='o', color='green')
    ax.set_title("Filtered Average Hit Rate vs RR Target")
    ax.set_xlabel("RR Target")
    ax.set_ylabel("Hit Rate (%)")
    ax.set_xticks(merged["RR Target"])
    ax.grid(True)
    st.pyplot(fig)

    # Total RR Attained Simulation (based on trade logic)
    st.header("📈 Total RR Attained Simulation")
    rr_targets = np.round(np.arange(1.8, 2.5, 0.1), 1)
    total_rr = []

    for target in rr_targets:
        result = []
        for _, row in merged.iterrows():
            if row["Average Hit Rate"] >= target / 10:  # simulate hit as successful outcome
                result.append(target)
            elif row["Average Hit Rate"] > 0:  # simulate partial profit
                result.append(round(row["Average Hit Rate"] * target, 2))
            else:  # losing trade
                result.append(-1.0)
        total_rr.append(sum(result))

    rr_df = pd.DataFrame({"RR Target": rr_targets, "Total RR Attained": total_rr})
    fig2, ax2 = plt.subplots()
    ax2.plot(rr_df["RR Target"], rr_df["Total RR Attained"], marker='o', color='blue')
    ax2.set_title("Total RR Attained by RR Target (1.8 to 2.4)")
    ax2.set_xlabel("RR Target")
    ax2.set_ylabel("Total RR Attained")
    ax2.grid(True)
    st.pyplot(fig2)

else:
    st.info("Please upload the RR Target Analysis Excel file to begin.")
