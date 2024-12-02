import pandas as pd
import streamlit as st

@st.cache_data
def load_files():
    df_group = pd.read_parquet('data/df_group.parquet')
    df_unique = pd.read_parquet('data/df_unique.parquet')
    df_positions = pd.read_parquet('data/df_positions.parquet')
    
    return df_group, df_unique, df_positions