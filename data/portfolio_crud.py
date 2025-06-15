# data/portfolio_crud.py
import streamlit as st
import pandas as pd

class PortfolioCRUD:
    def __init__(self, portfolio_manager):
        self.pm = portfolio_manager

    def display_editor(self):
        st.subheader("✏️ Edit Data Saham (CRUD)")

        with st.expander("➕ Tambah Saham Baru"):
            new_stock = st.text_input("Kode Saham (e.g. TLKM)", max_chars=5)
            new_ticker = st.text_input("Kode Ticker (e.g. TLKM.JK)")
            new_lot = st.number_input("Jumlah Lot", min_value=0, step=1)
            new_price = st.number_input("Harga Beli per Lembar", min_value=0)

            if st.button("Tambah ke Portofolio") and new_stock and new_ticker:
                self.add_stock(new_stock, new_ticker, new_lot, new_price)
                st.success(f"Saham {new_stock} ditambahkan.")
                st.rerun()

        with st.expander("📝 Edit / Hapus Saham yang Ada"):
            df = self.pm.df.copy()
            edited_df = st.data_editor(
                df[['Stock', 'Ticker', 'Lot Balance', 'Avg Price']],
                num_rows="dynamic",
                key="edit_table"
            )
            if st.button("Simpan Perubahan"):
                self.update_from_editor(edited_df)
                st.success("Portofolio diperbarui.")
                st.rerun()

        # Tombol Refresh Manual
        st.markdown("---")
        if st.button("🔁 Refresh Data & Tampilan"):
            st.rerun()

    def add_stock(self, stock, ticker, lot, avg_price):
        balance = lot * 100
        new_row = {
            'Stock': stock,
            'Ticker': ticker,
            'Lot Balance': float(lot),
            'Balance': balance,
            'Avg Price': avg_price,
            'Stock Value': balance * avg_price,
            'Market Price': avg_price,
            'Market Value': balance * avg_price,
            'Unrealized': 0
        }
        self.pm.df = pd.concat([self.pm.df, pd.DataFrame([new_row])], ignore_index=True)

    def update_from_editor(self, edited_df):
        for _, row in edited_df.iterrows():
            mask = self.pm.df['Stock'] == row['Stock']
            self.pm.df.loc[mask, 'Ticker'] = row['Ticker']
            self.pm.df.loc[mask, 'Lot Balance'] = row['Lot Balance']
            self.pm.df.loc[mask, 'Balance'] = row['Lot Balance'] * 100
            self.pm.df.loc[mask, 'Avg Price'] = row['Avg Price']
            self.pm.df.loc[mask, 'Stock Value'] = self.pm.df.loc[mask, 'Balance'] * row['Avg Price']
            self.pm.df.loc[mask, 'Market Price'] = row['Avg Price']

        self.pm.df['Market Value'] = self.pm.df['Balance'] * self.pm.df['Market Price']
        self.pm.df['Unrealized'] = self.pm.df['Market Value'] - self.pm.df['Stock Value']
