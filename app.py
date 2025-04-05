
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="RR Target Dashboard", layout="wide")

# Load data (this assumes the user will upload the Excel file generated earlier)
uploaded_file = st.file_uploader("Upload the RR Target Analysis Excel file", type=["xlsx"])

if uploaded_file:
    # Read all sheets into a dictionary
    all_data = pd.read_excel(uploaded_file, sheet_name=None)

    # Sidebar filters
    st.sidebar.header("Filters")
    sheet_options = list(all_data.keys())[1:]  # skip 'Overall Hit Rates'
    selected_sheets = st.sidebar.multiselect("Select Dimensions to Compare", sheet_options, default=sheet_options)

    # Display overall hit rates
    st.header("Overall Hit Rate vs RR Target")
    overall_df = all_data["Overall Hit Rates"]
    fig, ax = plt.subplots()
    ax.plot(overall_df["RR Target"], overall_df["Hit Rate (%)"], marker='o')
    ax.set_title("Overall Hit Rate vs RR Target")
    ax.set_xlabel("RR Target")
    ax.set_ylabel("Hit Rate (%)")
    ax.grid(True)
    st.pyplot(fig)

    # Plot selected breakdowns
    for sheet in selected_sheets:
        st.subheader(f"Hit Rate by RR Target - {sheet}")
        df = all_data[sheet]
        pivot_df = df.pivot(index="RR Target", columns=df.columns[0], values="Hit Rate")

        fig, ax = plt.subplots()
        for column in pivot_df.columns:
            ax.plot(pivot_df.index, pivot_df[column]*100, label=column)
        ax.set_title(f"{sheet} Breakdown")
        ax.set_xlabel("RR Target")
        ax.set_ylabel("Hit Rate (%)")
        ax.legend(title=df.columns[0], bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True)
        st.pyplot(fig)
else:
    st.info("Please upload the RR Target Analysis Excel file to begin.")
