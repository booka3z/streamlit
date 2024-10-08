import streamlit as st
import pandas as pd
import io

@st.cache_data
def load_ticker_data(ticker_file):
    return pd.read_excel(ticker_file)

def generate_holdings_summary(df_tickers, ww_file):
    # Read the Whalewisdom export excel file
    df_ww_export = pd.read_excel(ww_file, skiprows=3)

    # Perform left join on df_tickers and df_ww_export
    df_merged = pd.merge(df_tickers, df_ww_export, left_on='Ticker', right_on='Symbol', how='left')

    # Convert 'Market Value' to integer
    df_merged['Market Value'] = df_merged['Market Value'].fillna(0).astype(int)
    
    # Slice df_merged to show Ticker and Market Value
    df_sliced = df_merged[['Ticker', 'Market Value']].dropna()

    # Drop rows where Market Value is zero
    df_sliced = df_sliced[df_sliced['Market Value'] != 0]

    df_sliced = df_sliced.sort_values(by='Market Value', ascending=False)
    df_sliced['Market Value'] = df_sliced['Market Value'].apply(lambda x: "{:,}".format(x))
    
    # Create a new column 'Text' that combines 'Ticker' and 'Market Value'
    df_sliced['Text'] = df_sliced['Ticker'] + ' $' + df_sliced['Market Value']

    # Join all elements in the 'Text' column into a single string, separated by newlines
    text_chunk = '\n'.join(df_sliced['Text'])

    return text_chunk

st.title("Holdings Summary Generator")
st.write("""
Purpose: This page extracts the relevant holdings information from 13F (via Whale Wisdom exports) and outputs a text summary.

Steps:
1. Upload the tickers that you are interested in. This first Excel file needs to include a column named 'Ticker' that has the tickers you want to filter for.
2. Upload an unmodified Excel export from Whale Wisdom.
3. Click 'Generate Summary' to process the data and view the results.
4. To extract the summary for the next spreadsheet, click "X" and upload another Whalewisdom export.
""")

# Master ticker file upload
if 'ticker_data' not in st.session_state:
    ticker_file = st.file_uploader("Upload Master ETF Data Pull Excel file", type=["xlsx"])
    if ticker_file:
        st.session_state.ticker_data = load_ticker_data(ticker_file)
        st.success("Master ETF Data Pull file loaded successfully!")

# Whalewisdom file upload
ww_file = st.file_uploader("Upload Whalewisdom Export Excel file", type=["xlsx"])

if 'ticker_data' in st.session_state and ww_file:
    if st.button("Generate Summary"):
        try:
            result = generate_holdings_summary(st.session_state.ticker_data, ww_file)
            st.text_area("Holdings Summary", result, height=400)
            st.download_button("Download Summary", result, "holdings_summary.txt")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
elif 'ticker_data' not in st.session_state:
    st.info("Please upload the Master ETF Data Pull file first.")
else:
    st.info("Please upload a Whalewisdom Export file to generate the summary.")
