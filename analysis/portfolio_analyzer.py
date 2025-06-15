# analysis/portfolio_analyzer.py
import pandas as pd
import numpy as np
from datetime import timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline


class PortfolioAnalyzer:
    def __init__(self, portfolio_manager):
        self.pm = portfolio_manager

    def portfolio_summary(self):
        df = self.pm.df
        total_stock_value = df['Stock Value'].sum()
        total_market_value = df['Market Value'].sum()
        total_unrealized = df['Unrealized'].sum()
        return_pct = (total_unrealized / total_stock_value) * 100 if total_stock_value else 0

        return {
            'total_invested': total_stock_value,
            'total_market_value': total_market_value,
            'total_unrealized': total_unrealized,
            'return_pct': return_pct
        }

    def predict_price(self, stock, days=30):
        if stock not in self.pm.simulated_data:
            return None, None, None

        data = self.pm.simulated_data[stock].copy()
        data['Days'] = (data['Date'] - data['Date'].min()).dt.days
        data['MA7'] = data['Price'].rolling(window=7).mean()
        data['MA30'] = data['Price'].rolling(window=30).mean()
        data = data.dropna()

        X = data[['Days', 'MA7', 'MA30']]
        y = data['Price']

        model = make_pipeline(StandardScaler(), RandomForestRegressor(n_estimators=100, random_state=42))
        model.fit(X, y)

        last_date = data['Date'].iloc[-1]
        future_dates = [last_date + timedelta(days=i) for i in range(1, days + 1)]
        future_days = [(fd - data['Date'].min()).days for fd in future_dates]

        last_ma7 = data['MA7'].iloc[-1]
        last_ma30 = data['MA30'].iloc[-1]
        future_ma7 = [last_ma7] * days
        future_ma30 = [last_ma30] * days

        future_X = pd.DataFrame({
            'Days': future_days,
            'MA7': future_ma7,
            'MA30': future_ma30
        })
        predictions = model.predict(future_X)

        return future_dates, predictions, predictions[-1]

    def what_if_simulation(self, stock, price_change_pct):
        sim_df = self.pm.df.copy()
        idx = sim_df[sim_df['Stock'] == stock].index

        if not idx.empty:
            original_price = sim_df.loc[idx, 'Market Price'].values[0]
            new_price = original_price * (1 + price_change_pct / 100)
            sim_df.loc[idx, 'Market Price'] = new_price
            sim_df['Market Value'] = sim_df['Balance'] * sim_df['Market Price']
            sim_df['Unrealized'] = sim_df['Market Value'] - sim_df['Stock Value']

            return {
                'new_total_market': sim_df['Market Value'].sum(),
                'new_unrealized': sim_df['Unrealized'].sum(),
                'sim_df': sim_df
            }
        return None

    def generate_recommendations(self):
        recommendations = []

        for _, row in self.pm.df.iterrows():
            stock = row['Stock']
            unrealized_pct = (row['Unrealized'] / row['Stock Value']) * 100 if row['Stock Value'] else 0
            trend = 0

            if stock in self.pm.simulated_data and len(self.pm.simulated_data[stock]) > 10:
                data = self.pm.simulated_data[stock]
                trend = (data['Price'].iloc[-1] / data['Price'].iloc[-10] - 1) * 100

            if unrealized_pct < -15 or trend < -5:
                rec, reason, urgency = 'Sell', 'Significant loss & downward trend', 'High'
            elif unrealized_pct > 20 or trend > 8:
                rec, reason, urgency = 'Buy More', 'Strong performance & upward trend', 'Medium'
            elif unrealized_pct > 5 or trend > 3:
                rec, reason, urgency = 'Hold/Buy', 'Positive performance', 'Low'
            elif unrealized_pct < -5:
                rec, reason, urgency = 'Hold/Sell', 'Mild underperformance', 'Monitor'
            else:
                rec, reason, urgency = 'Hold', 'Stable performance', 'Low'

            recommendations.append({
                'Stock': stock,
                'Recommendation': rec,
                'Reason': reason,
                'Urgency': urgency,
                'Unrealized %': f"{unrealized_pct:.1f}%",
                '30d Trend %': f"{trend:.1f}%"
            })

        return pd.DataFrame(recommendations)
