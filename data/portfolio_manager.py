# data/portfolio_manager.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
import streamlit as st

class PortfolioManager:
    def __init__(self):
        self.df = self.load_portfolio()
        self.simulated_data = self.generate_historical_data()
        self.new_stocks = self.get_new_stocks()
        self.last_update = datetime.now()

    @staticmethod
    def load_portfolio():
        return pd.DataFrame({
            'Stock': ['AADI', 'ADRO', 'ANTM', 'BFIN', 'BJBR', 'BSSR', 'LPPF', 'PGAS', 'PTBA', 'UNVR', 'WIIM'],
            'Ticker': ['AADI.JK', 'ADRO.JK', 'ANTM.JK', 'BFIN.JK', 'BJBR.JK', 'BSSR.JK', 'LPPF.JK', 'PGAS.JK', 'PTBA.JK', 'UNVR.JK', 'WIIM.JK'],
            'Lot Balance': [5.0, 17.0, 15.0, 30.0, 23.0, 11.0, 5.0, 10.0, 4.0, 60.0, 5.0],
            'Balance': [500, 1700, 1500, 3000, 2300, 1100, 500, 1000, 400, 6000, 500],
            'Avg Price': [7300, 2605, 1423, 1080, 1145, 4489, 1700, 1600, 2400, 1860, 871],
            'Stock Value': [3650000, 4428500, 2135000, 3240000, 2633500, 4938000, 850000, 1600000, 960000, 11162500, 435714],
            'Market Price': [7225, 2200, 3110, 905, 850, 4400, 1745, 1820, 2890, 1730, 835],
            'Unrealized': [-37500, -688500, 2530000, -525000, -678500, -98000, 22500, 220000, 196000, -782500, -18215]
        })

    def generate_historical_data(self):
        np.random.seed(42)
        dates = pd.date_range(end='2025-05-31', periods=100, freq='D')
        data = {}

        for stock in self.df['Stock']:
            base_price = self.df[self.df['Stock'] == stock]['Market Price'].iloc[0]
            volatility = base_price * 0.02
            prices = [base_price]

            for _ in range(1, len(dates)):
                change = np.random.normal(0, volatility)
                if stock in ['ANTM', 'PTBA', 'PGAS']:
                    change += volatility * 0.1
                prices.append(prices[-1] + change)

            data[stock] = pd.DataFrame({'Date': dates, 'Price': prices})
        return data

    @staticmethod
    def get_new_stocks():
        return pd.DataFrame({
            'Stock': ['TLKM', 'BBCA', 'BMRI', 'ASII'],
            'Ticker': ['TLKM.JK', 'BBCA.JK', 'BMRI.JK', 'ASII.JK'],
            'Sector': ['Telecom', 'Banking', 'Banking', 'Automotive'],
            'Dividend Yield': [4.5, 3.2, 3.8, 2.9],
            'Growth Rate': [8.0, 10.0, 9.5, 7.0],
            'Current Price': [3500, 9500, 6000, 4500],
            'Risk Level': ['Low', 'Medium', 'Medium', 'High']
        })

    def update_real_time_prices(self):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            all_tickers = list(self.df['Ticker']) + list(self.new_stocks['Ticker'])
            prices = {}

            for i, ticker in enumerate(all_tickers):
                status_text.text(f"Fetching data for {ticker}...")
                progress_bar.progress((i + 1) / len(all_tickers))
                try:
                    stock_data = yf.Ticker(ticker)
                    hist = stock_data.history(period='1d')
                    if not hist.empty:
                        prices[ticker] = hist['Close'].iloc[-1]
                    else:
                        prices[ticker] = self.get_fallback_price(ticker)
                except Exception as e:
                    st.warning(f"Error fetching data for {ticker}: {str(e)}")
                    prices[ticker] = self.get_fallback_price(ticker)

            self.apply_prices(prices)
            self.last_update = datetime.now()
            return True
        except Exception as e:
            st.error(f"Error updating prices: {str(e)}")
            return False
        finally:
            progress_bar.empty()
            status_text.empty()

    def get_fallback_price(self, ticker):
        if ticker in self.df['Ticker'].values:
            return self.df[self.df['Ticker'] == ticker]['Market Price'].iloc[0]
        elif ticker in self.new_stocks['Ticker'].values:
            return self.new_stocks[self.new_stocks['Ticker'] == ticker]['Current Price'].iloc[0]
        return 0

    def apply_prices(self, prices):
        for idx, row in self.df.iterrows():
            ticker = row['Ticker']
            if ticker in prices:
                self.df.at[idx, 'Market Price'] = prices[ticker]

        for idx, row in self.new_stocks.iterrows():
            ticker = row['Ticker']
            if ticker in prices:
                self.new_stocks.at[idx, 'Current Price'] = prices[ticker]

        self.df['Market Value'] = self.df['Balance'] * self.df['Market Price']
        self.df['Unrealized'] = self.df['Market Value'] - self.df['Stock Value']
