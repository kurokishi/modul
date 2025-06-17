# data/portfolio_manager.py

import pandas as pd
from datetime import datetime

class PortfolioManager:
    def __init__(self):
        # DataFrame portofolio kosong, diisi setelah upload CSV
        self.df = pd.DataFrame()
        self.simulated_data = {}
        self.new_stocks = pd.DataFrame()
        self.last_update = datetime.now()

    def load_from_csv(self, df):
        """
        Mengisi portofolio dari DataFrame (hasil upload CSV user).
        Diharapkan kolom: 'Stock', 'Ticker', 'Lot Balance', 'Avg Price'
        """
        self.df = df.copy()

        # Hitung otomatis kolom penting
        self.df['Balance'] = self.df['Lot Balance'] * 100
        self.df['Stock Value'] = self.df['Balance'] * self.df['Avg Price']
        self.df['Market Price'] = self.df['Avg Price']  # awalnya dianggap sama
        self.df['Market Value'] = self.df['Balance'] * self.df['Market Price']
        self.df['Unrealized'] = self.df['Market Value'] - self.df['Stock Value']

    def update_real_time_prices(self):
        """
        Simulasi pembaruan harga saham (secara acak ±1%)
        """
        if self.df.empty:
            return False

        # Simulasi fluktuasi harga
        self.df['Market Price'] = self.df['Market Price'] * (
            1 + pd.Series([0.01] * len(self.df)).sample(frac=1).values
        )
        self.df['Market Value'] = self.df['Balance'] * self.df['Market Price']
        self.df['Unrealized'] = self.df['Market Value'] - self.df['Stock Value']
        self.last_update = datetime.now()
        return True
