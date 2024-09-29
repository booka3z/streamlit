import streamlit as st
import pandas as pd

def format_dollar_amount(amount):
    formatted_absolute_amount = '${:,.2f}'.format(abs(amount))
    if round(amount, 2) < 0:
        return f'-{formatted_absolute_amount}'
    return formatted_absolute_amount

@st.cache_data(ttl=21*24*3600)
def load_data(url):
    # Read in the data
    df = pd.read_excel(url, engine='xlrd', skiprows=0, usecols=[
        'Initiating Firm Name',
        'Client Defined Category Name',
        'AUM',
        'Industry AUM',
        'NNA',
        'Industry NNA'
    ])
    return df
st.set_page_config(page_title="Industry AUM Lookup", page_icon="📈", layout="wide")

# Title
st.title("Industry AUM Lookup")
st.write("""
This page extracts Industry AUM from the Cohort Analyzer output. 
""")
st.write("""
!! This page takes about 30 seconds to load the first time. !!
""")
# Load data
url = st.secrets["mf_analyzer_url"]
df = load_data(url)

# Get unique list of Initiating Firm Names
unique_firm_names = sorted(df['Initiating Firm Name'].unique())

# Create an autocomplete input for Firm Name
firm_name = st.selectbox(
    "Enter or Select Firm Name",
    options=[""] + unique_firm_names,
    index=0,
    key="firm_name_input"
)

# Filter the dataframe based on Firm Name
if firm_name:
    filtered_df = df[df['Initiating Firm Name'] == firm_name]
    category_mapping = {
        'BUIGX': 'Buffer10/Hedged Equity',
        'KNGIX': 'Covered Call',
        'ENGIX': 'Buffer20/Innovator',
        'RYSE': 'IR Hedge',
        'BTCVX': 'Crypto'
    }
    filtered_df.loc[filtered_df['Client Defined Category Name'].isin(category_mapping), 'Client Defined Category Name'] = filtered_df['Client Defined Category Name'].map(category_mapping)
    filtered_df = filtered_df.groupby(['Client Defined Category Name'])[['Industry AUM', 'AUM']].sum().reset_index()
    filtered_df['Industry AUM'] = filtered_df['Industry AUM'].apply(format_dollar_amount)
    filtered_df = filtered_df.rename(columns={'AUM': 'Vest AUM'})
    filtered_df['Vest AUM'] = filtered_df['Vest AUM'].apply(format_dollar_amount)

# Display the filtered data
if firm_name:
    st.dataframe(filtered_df)