# visualization/portfolio_visualizer.py
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


class PortfolioVisualizer:
    @staticmethod
    def portfolio_pie(df):
        fig = px.pie(df, values='Market Value', names='Stock',
                     title='Portfolio Composition', hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig

    @staticmethod
    def performance_bar(df):
        df = df.copy()
        df['Color'] = df['Unrealized'].apply(lambda x: 'green' if x >= 0 else 'red')
        fig = px.bar(df, x='Stock', y='Unrealized', color='Color',
                     title='Unrealized Gain/Loss by Stock',
                     labels={'Unrealized': 'Gain/Loss (Rp)'})
        fig.update_layout(showlegend=False)
        return fig

    @staticmethod
    def price_prediction_plot(history, forecast, stock):
        history = history.rename(columns={'Price': 'Value'})
        history['Type'] = 'Historical'

        forecast_df = pd.DataFrame({
            'Date': forecast['dates'],
            'Value': forecast['predictions'],
            'Type': 'Forecast'
        })

        combined = pd.concat([history, forecast_df])

        fig = px.line(combined, x='Date', y='Value', color='Type',
                      title=f"Price Forecast for {stock}",
                      labels={'Value': 'Price (Rp)'})

        if 'confidence' in forecast:
            fig.add_trace(go.Scatter(
                x=forecast_df['Date'].tolist() + forecast_df['Date'].tolist()[::-1],
                y=forecast['upper'] + forecast['lower'][::-1],
                fill='toself',
                fillcolor='rgba(100, 150, 255, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Confidence Interval'
            ))

        return fig
