import os
import pandas as pd
import streamlit as st

def get_path(*path_parts):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, '..', *path_parts)

@st.cache_data
def load_files():
    df_group = pd.read_parquet(get_path('data', 'df_group.parquet'))
    df_unique = pd.read_parquet(get_path('data', 'df_unique.parquet'))
    df_positions = pd.read_parquet(get_path('data', 'df_positions.parquet'))
    return df_group, df_unique, df_positions
