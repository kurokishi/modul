# analysis/allocation_helper.py
import pandas as pd

class AllocationHelper:
    def __init__(self, recommendations_df):
        self.df = recommendations_df.copy()

    def simulate_allocation(self, total_budget, method="equal"):
        df = self.df.copy()
        if df.empty or total_budget <= 0:
            return pd.DataFrame()

        # Estimasi harga (pakai kolom PBV atau Yield jika tidak ada harga langsung)
        if 'Current Price' not in df.columns:
            df['Current Price'] = 1000  # asumsi default jika harga tak tersedia

        if method == "equal":
            alloc_per_stock = total_budget / len(df)
            df['Lot Allocated'] = (alloc_per_stock // (df['Current Price'] * 100)).astype(int)
            df['Allocated Rp'] = df['Lot Allocated'] * df['Current Price'] * 100
        elif method == "weighted":
            df['Weight'] = df['Final Score'] / df['Final Score'].sum()
            df['Allocated Rp'] = (df['Weight'] * total_budget).round(0)
            df['Lot Allocated'] = (df['Allocated Rp'] // (df['Current Price'] * 100)).astype(int)
            df['Allocated Rp'] = df['Lot Allocated'] * df['Current Price'] * 100
        else:
            return pd.DataFrame()

        return df[['Stock', 'Ticker', 'Current Price', 'Lot Allocated', 'Allocated Rp']]
