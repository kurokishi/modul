# analysis/stock_scorer.py
import pandas as pd

class StockScorer:
    def __init__(self, df):
        self.df = df.copy()

    def apply_scoring(self):
        if self.df.empty:
            return pd.DataFrame()

        df = self.df.copy()

        # Normalisasi dan Skor
        df['PER Score'] = self._inverse_score(df['PER'])
        df['PBV Score'] = self._inverse_score(df['PBV'])
        df['Dividend Score'] = self._direct_score(df['Yield'])
        df['ROE Score'] = self._direct_score(df['ROE'])

        # Bobot (bisa disesuaikan)
        weights = {
            'PER Score': 0.25,
            'PBV Score': 0.25,
            'Dividend Score': 0.25,
            'ROE Score': 0.25
        }

        df['Final Score'] = (
            df['PER Score'] * weights['PER Score'] +
            df['PBV Score'] * weights['PBV Score'] +
            df['Dividend Score'] * weights['Dividend Score'] +
            df['ROE Score'] * weights['ROE Score']
        )

        return df.sort_values(by='Final Score', ascending=False).reset_index(drop=True)

    def _inverse_score(self, series):
        norm = (series.max() - series) / (series.max() - series.min() + 1e-9)
        return (norm * 100).fillna(0)

    def _direct_score(self, series):
        norm = (series - series.min()) / (series.max() - series.min() + 1e-9)
        return (norm * 100).fillna(0)
