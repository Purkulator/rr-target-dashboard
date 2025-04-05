import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="RR Target Dashboard", layout="wide")

# Load Excel file
target_file = st.file_uploader("Upload the RR Target Analysis Excel file", type=["xlsx"])

if target_file:
    all_data = pd.read_excel(target_file, sheet_name=None)
    df = all_data["Overall Hit Rates"]

    # Allow user to select from all filterable dimensions
    fib_df = all_data.get("By Fibonacci Level")
    range_df = all_data.get("By Range Bucket")
    ticker_df = all_data.get("By Ticker")
    tf_df = all_data.get("By Time Frame")
    time_df = all_data.get("By Time of Day")

    st.sidebar.header("Filter Setup")
    selected_tickers = st.sidebar.multiselect("Ticker(s)", ticker_df[ticker_df.columns[0]].unique(), default=ticker_df[ticker_df.columns[0]].unique())
    selected_tfs = st.sidebar.multiselect("Time Frame(s)", tf_df[tf_df.columns[0]].unique(), default=tf_df[tf_df.columns[0]].unique())
    selected_ranges = st.sidebar.multiselect("Range Bucket(s)", range_df[range_df.columns[0]].unique(), default=range_df[range_df.columns[0]].unique())
    selected_fibs = st.sidebar.multiselect("Fibonacci Bucket(s)", fib_df[fib_df.columns[0]].unique(), default=fib_df[fib_df.columns[0]].unique())
    selected_times = st.sidebar.multiselect("Time of Day", time_df[time_df.columns[0]].unique(), default=time_df[time_df.columns[0]].unique())

    # Filter each dimension dataframe
    t_df = ticker_df[ticker_df[ticker_df.columns[0]].isin(selected_tickers)]
    f_df = fib_df[fib_df[fib_df.columns[0]].isin(selected_fibs)]
    r_df = range_df[range_df[range_df.columns[0]].isin(selected_ranges)]
    tf_df = tf_df[tf_df[tf_df.columns[0]].isin(selected_tfs)]
    td_df = time_df[time_df[time_df.columns[0]].isin(selected_times)]

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

else:
    st.info("Please upload the RR Target Analysis Excel file to begin.")
