# analysis/benchmark.py
import yfinance as yf
import pandas as pd
import numpy as np


class BenchmarkAnalyzer:
    def __init__(self, portfolio_manager):
        self.pm = portfolio_manager

    def get_index_data(self, symbol="^JKSE", period="3mo"):
        """
        Mengambil data historis indeks (default: IHSG)
        """
        idx = yf.Ticker(symbol)
        hist = idx.history(period=period)
        hist = hist[['Close']].rename(columns={"Close": "Index"})
        hist.reset_index(inplace=True)
        return hist

    def get_portfolio_history(self):
        """
        Membuat histori nilai portofolio dari data simulasi harga saham
        """
        daily_value = None
        for stock, df in self.pm.simulated_data.items():
            if stock not in self.pm.df['Stock'].values:
                continue
            lot = self.pm.df[self.pm.df['Stock'] == stock]['Balance'].iloc[0]
            df = df.copy()
            df['Value'] = df['Price'] * lot
            if daily_value is None:
                daily_value = df[['Date', 'Value']].rename(columns={'Value': stock})
            else:
                daily_value = daily_value.merge(df[['Date', 'Value']].rename(columns={'Value': stock}),
                                                on='Date', how='outer')

        daily_value = daily_value.fillna(method='ffill')
        daily_value['Portfolio'] = daily_value.drop(columns='Date').sum(axis=1)
        return daily_value[['Date', 'Portfolio']]

    def compare_vs_index(self, symbol="^JKSE"):
        """
        Membandingkan pertumbuhan portofolio dengan indeks tertentu
        """
        index_df = self.get_index_data(symbol)
        portfolio_df = self.get_portfolio_history()
        df = pd.merge(index_df, portfolio_df, on='Date', how='inner')

        df['Index %'] = df['Index'].pct_change().fillna(0).cumsum() * 100
        df['Portfolio %'] = df['Portfolio'].pct_change().fillna(0).cumsum() * 100
        return df[['Date', 'Index %', 'Portfolio %']]

    def performance_metrics(self, df):
        """
        Hitung alpha (selisih performa), beta dummy (perbandingan regresi sederhana)
        """
        if len(df) < 2:
            return {'Alpha': 0, 'Beta': 0}

        returns_index = df['Index %'].diff().dropna()
        returns_port = df['Portfolio %'].diff().dropna()

        # Korelasi (bukan beta sesungguhnya, tapi sebagai estimasi sederhana)
        correlation = np.corrcoef(returns_index, returns_port)[0, 1]
        alpha = df['Portfolio %'].iloc[-1] - df['Index %'].iloc[-1]

        return {
            'Alpha': round(alpha, 2),
            'Correlation (β proxy)': round(correlation, 2)
        }
