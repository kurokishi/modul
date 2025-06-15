# analysis/risk_analyzer.py
import pandas as pd
import numpy as np


class RiskAnalyzer:
    def __init__(self, portfolio_manager):
        self.pm = portfolio_manager

    def sector_distribution(self):
        """
        Menghitung distribusi sektor berdasarkan jumlah saham atau nilai pasar
        """
        # Jika sektor tidak tersedia, fallback ke dummy sektor
        if 'Sector' not in self.pm.df.columns:
            self.pm.df['Sector'] = self.pm.df['Stock'].map(self._mock_sector_map())

        sector_counts = self.pm.df.groupby('Sector')['Market Value'].sum()
        total_value = sector_counts.sum()
        distribution = (sector_counts / total_value * 100).sort_values(ascending=False)
        return distribution.reset_index(name='Percentage')

    def concentration_score(self):
        """
        Menghitung indeks konsentrasi sederhana (HHI-like index)
        """
        sector_data = self.sector_distribution()
        percentages = sector_data['Percentage'] / 100
        hhi = np.sum(percentages ** 2)
        return round(hhi * 100, 2)  # Semakin tinggi, semakin terkonsentrasi

    def volatility_estimation(self):
        """
        Menghitung volatilitas harga untuk masing-masing saham
        """
        vol_data = []
        for stock, df in self.pm.simulated_data.items():
            std_dev = np.std(df['Price'].pct_change().dropna())
            vol_data.append({
                'Stock': stock,
                'Volatility (σ)': round(std_dev * 100, 2)
            })
        return pd.DataFrame(vol_data).sort_values(by='Volatility (σ)', ascending=False)

    def risk_report(self):
        """
        Menggabungkan distribusi sektor, konsentrasi, dan volatilitas menjadi 1 ringkasan risiko
        """
        sector_dist = self.sector_distribution()
        score = self.concentration_score()
        volatility_df = self.volatility_estimation()

        return {
            'sector_distribution': sector_dist,
            'concentration_score': score,
            'volatility_table': volatility_df
        }

    def _mock_sector_map(self):
        return {
            'AADI': 'Automotive', 'ADRO': 'Energy', 'ANTM': 'Mining', 'BFIN': 'Finance',
            'BJBR': 'Banking', 'BSSR': 'Energy', 'LPPF': 'Retail', 'PGAS': 'Energy',
            'PTBA': 'Mining', 'UNVR': 'Consumer', 'WIIM': 'Tobacco'
        }
