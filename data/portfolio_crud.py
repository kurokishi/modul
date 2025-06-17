# data/portfolio_crud.py

import streamlit as st
import pandas as pd

class PortfolioCRUD:
    def __init__(self, portfolio_manager):
        self.pm = portfolio_manager

    def display_editor(self):
        st.subheader("✏️ Edit Data Saham (CRUD)")

        # ===== Upload Portofolio dari CSV =====
        with st.expander("📂 Upload File Portofolio (CSV)"):
            uploaded_file = st.file_uploader("Unggah file CSV", type=["csv"])
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    self.import_dataframe(df)
                    self.pm.load_from_csv(self.pm.df)
                    st.session_state.portfolio = self.pm
                    st.success("Data CSV berhasil dimuat.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal membaca file: {str(e)}")

        # ===== Tambah Saham Manual =====
        with st.expander("➕ Tambah Saham Baru"):
            new_stock = st.text_input("Kode Saham (e.g. TLKM)", max_chars=5)
            new_ticker = st.text_input("Kode Ticker (e.g. TLKM.JK)")
            new_lot = st.number_input("Jumlah Lot", min_value=0, step=1)
            new_price = st.number_input("Harga Beli per Lembar", min_value=0)

            if st.button("Tambah ke Portofolio") and new_stock and new_ticker:
                self.add_stock(new_stock, new_ticker, new_lot, new_price)
                self.pm.load_from_csv(self.pm.df)
                st.session_state.portfolio = self.pm
                st.success(f"Saham {new_stock} ditambahkan.")
                st.rerun()

        # ===== Edit / Hapus Saham =====
        with st.expander("📝 Edit / Hapus Saham yang Ada"):
            df = self.pm.df.copy()
            df.columns = [col.strip() for col in df.columns]  # Bersihkan spasi

            required_cols = ['Stock', 'Ticker', 'Lot Balance', 'Avg Price']
            if not all(col in df.columns for col in required_cols):
                st.warning(f"❗ Data tidak valid. Diperlukan kolom: {', '.join(required_cols)}")
                return

            edited_df = st.data_editor(
                df[required_cols],
                num_rows="dynamic",
                key="edit_table"
            )

            if st.button("Simpan Perubahan"):
                self.update_from_editor(edited_df)
                self.pm.load_from_csv(self.pm.df)
                st.session_state.portfolio = self.pm
                st.success("Portofolio diperbarui.")
                st.rerun()

        st.markdown("---")
        if st.button("🔁 Refresh Data & Tampilan"):
            st.rerun()

    def add_stock(self, stock, ticker, lot, avg_price):
        new_row = {
            'Stock': stock,
            'Ticker': ticker,
            'Lot Balance': float(lot),
            'Avg Price': avg_price,
        }
        self.pm.df = pd.concat([self.pm.df, pd.DataFrame([new_row])], ignore_index=True)

    def update_from_editor(self, edited_df):
        current_stocks = set(self.pm.df['Stock'])
        edited_stocks = set(edited_df['Stock'])
        removed_stocks = current_stocks - edited_stocks
        self.pm.df = self.pm.df[~self.pm.df['Stock'].isin(removed_stocks)]

        for _, row in edited_df.iterrows():
            mask = self.pm.df['Stock'] == row['Stock']
            self.pm.df.loc[mask, 'Ticker'] = row['Ticker']
            self.pm.df.loc[mask, 'Lot Balance'] = row['Lot Balance']
            self.pm.df.loc[mask, 'Avg Price'] = row['Avg Price']

    def import_dataframe(self, df):
        required_cols = {'Stock', 'Ticker', 'Lot Balance', 'Avg Price'}
        df.columns = [col.strip() for col in df.columns]
        if not required_cols.issubset(df.columns):
            st.warning("Kolom CSV harus mengandung: Stock, Ticker, Lot Balance, Avg Price")
            return

        self.pm.df = pd.DataFrame()
        for _, row in df.iterrows():
            self.add_stock(row['Stock'], row['Ticker'], row['Lot Balance'], row['Avg Price'])
