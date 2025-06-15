# analysis/optimizer.py
import pandas as pd
import numpy as np
from scipy.optimize import minimize

class PortfolioOptimizer:
    def __init__(self, portfolio_manager):
        self.pm = portfolio_manager
        self.sim_data = self.pm.simulated_data

    def get_returns_cov_matrix(self):
        returns_df = pd.DataFrame()
        for stock, data in self.sim_data.items():
            if stock not in self.pm.df['Stock'].values:
                continue
            prices = data.set_index('Date')['Price']
            returns_df[stock] = prices.pct_change()
        returns_df = returns_df.dropna()
        mean_returns = returns_df.mean()
        cov_matrix = returns_df.cov()
        return mean_returns, cov_matrix

    def portfolio_performance(self, weights, mean_returns, cov_matrix):
        ret = np.dot(weights, mean_returns)
        vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return ret, vol

    def optimize_weights(self):
        stocks = list(self.pm.df['Stock'])
        mean_returns, cov_matrix = self.get_returns_cov_matrix()

        num_assets = len(stocks)
        args = (mean_returns, cov_matrix)
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(num_assets))
        initial_weights = num_assets * [1. / num_assets, ]

        result = minimize(
            lambda x: self.portfolio_performance(x, *args)[1],  # minimize volatility
            initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)

        return dict(zip(stocks, result.x)), result.fun

    def current_weights(self):
        total_mv = self.pm.df['Market Value'].sum()
        return dict(zip(self.pm.df['Stock'], self.pm.df['Market Value'] / total_mv))

    def rebalance_recommendation(self):
        current = self.current_weights()
        optimal, opt_risk = self.optimize_weights()
        df = pd.DataFrame({
            'Stock': list(current.keys()),
            'Current Weight': list(current.values()),
            'Optimal Weight': [optimal[s] for s in current.keys()]
        })
        df['Change %'] = (df['Optimal Weight'] - df['Current Weight']) * 100
        return df.sort_values(by='Change %', ascending=False), opt_risk
