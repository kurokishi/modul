# data/input_loader.py
import pandas as pd
import streamlit as st

class InputLoader:
    def __init__(self):
        self.analysis_df = pd.DataFrame()

    def upload_interface(self):
        st.subheader("📂 Upload Data Analisis Awal")
        uploaded_file = st.file_uploader("Unggah file CSV (data screening atau watchlist)", type=["csv"])

        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                clean_df = self._clean_df(df)
                if not clean_df.empty:
                    self.analysis_df = clean_df
                    st.success("File berhasil diproses dan dimuat.")
                    st.dataframe(self.analysis_df.head(), use_container_width=True)
                else:
                    st.warning("File tidak memiliki kolom yang sesuai.")
            except Exception as e:
                st.error(f"Gagal membaca file: {str(e)}")

    def _clean_df(self, df):
        required_cols = {'Stock', 'Ticker'}
        df.columns = [col.strip() for col in df.columns]  # bersihkan spasi
        if not required_cols.issubset(set(df.columns)):
            return pd.DataFrame()

        df = df.copy()
        numeric_cols = [col for col in df.columns if col not in ['Stock', 'Ticker', 'Sector']]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df.dropna(subset=['Ticker']).reset_index(drop=True)

    def get_analysis_data(self):
        return self.analysis_df
