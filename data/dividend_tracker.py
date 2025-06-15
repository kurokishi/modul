# data/dividend_tracker.py
import pandas as pd

class DividendTracker:
    def __init__(self, portfolio_manager):
        self.pm = portfolio_manager
        self.dividend_data = self._load_dividends()

    def _load_dividends(self):
        """
        Contoh data dividen tahunan per saham. Bisa disambungkan ke API/data resmi
        """
        return pd.DataFrame({
            'Stock': ['AADI', 'ADRO', 'ANTM', 'BFIN', 'BJBR', 'BSSR', 'LPPF', 'PGAS', 'PTBA', 'UNVR', 'WIIM'],
            'Dividend/Share': [150, 230, 140, 90, 120, 310, 200, 210, 280, 300, 100],  # per lembar
            'Year': [2024] * 11
        })

    def calculate_portfolio_dividends(self):
        df = self.pm.df.copy()
        df = df.merge(self.dividend_data, on='Stock', how='left')
        df['Dividend/Share'].fillna(0, inplace=True)
        df['Total Shares'] = df['Balance'] * 100
        df['Dividend Income'] = df['Dividend/Share'] * df['Total Shares']
        df['Yield %'] = (df['Dividend Income'] / df['Stock Value']) * 100

        return df[['Stock', 'Balance', 'Dividend/Share', 'Dividend Income', 'Yield %']].sort_values(by='Dividend Income', ascending=False)

    def total_dividend(self):
        df = self.calculate_portfolio_dividends()
        return df['Dividend Income'].sum(), df['Yield %'].mean()
