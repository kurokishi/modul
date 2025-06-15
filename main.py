# main.py
import streamlit as st
from data.portfolio_manager import PortfolioManager
from analysis.portfolio_analyzer import PortfolioAnalyzer
from analysis.risk_analyzer import RiskAnalyzer
from analysis.benchmark import BenchmarkAnalyzer
from analysis.optimizer import PortfolioOptimizer
from data.dividend_tracker import DividendTracker
from data.portfolio_crud import PortfolioCRUD
from visualization.portfolio_visualizer import PortfolioVisualizer
from utils.formatter import format_rupiah, format_percentage, color_negative_red
import numpy as np
import pandas as pd

def main():
    st.set_page_config(page_title="📊 Portfolio Dashboard", layout="wide")

    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = PortfolioManager()

    pm = st.session_state.portfolio
    analyzer = PortfolioAnalyzer(pm)
    visualizer = PortfolioVisualizer()
    risk = RiskAnalyzer(pm)
    bench = BenchmarkAnalyzer(pm)
    opt = PortfolioOptimizer(pm)
    div_tracker = DividendTracker(pm)
    crud = PortfolioCRUD(pm)

    st.title("📊 Advanced Portfolio Analysis Dashboard")
    st.caption("Monitor, analisis, dan kelola portofolio saham Anda secara interaktif")

    # Update Harga
    st.header("🔄 Real-time Market Data")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Update Market Prices", type="primary"):
            if pm.update_real_time_prices():
                st.success("Market prices updated successfully!")
                st.session_state.portfolio = pm
                st.rerun()
    with col2:
        update_time = pm.last_update.strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"Last update: {update_time}")
        st.progress(100, text="Data Siap")

    # Summary
    st.header("📈 Portfolio Summary")
    summary = analyzer.portfolio_summary()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Invested", format_rupiah(summary['total_invested']))
    col2.metric("Current Value", format_rupiah(summary['total_market_value']), format_percentage(summary['return_pct']))
    col3.metric("Unrealized P&L", format_rupiah(summary['total_unrealized']), format_percentage(summary['return_pct']), delta_color="inverse")

    col1, col2 = st.columns([3, 2])
    with col1:
        st.plotly_chart(visualizer.portfolio_pie(pm.df), use_container_width=True)
    with col2:
        st.plotly_chart(visualizer.performance_bar(pm.df), use_container_width=True)

    # Detail Saham
    st.header("📋 Real-time Stock Details")
    pm.df['Unrealized %'] = (pm.df['Unrealized'] / pm.df['Stock Value']) * 100
    pm.df['Daily Change'] = (pm.df['Market Price'] / pm.df['Avg Price'] - 1) * 100
    pm.df['Current Value'] = pm.df['Balance'] * pm.df['Market Price']

    view_df = pm.df[['Stock', 'Balance', 'Avg Price', 'Market Price', 'Daily Change', 'Current Value', 'Unrealized', 'Unrealized %']].copy()
    for col in ['Avg Price', 'Market Price', 'Current Value', 'Unrealized']:
        view_df[col] = view_df[col].apply(format_rupiah)
    view_df['Daily Change'] = view_df['Daily Change'].apply(format_percentage)
    view_df['Unrealized %'] = view_df['Unrealized %'].apply(format_percentage)
    styled_df = view_df.style.map(color_negative_red, subset=['Daily Change', 'Unrealized', 'Unrealized %'])
    st.dataframe(styled_df, use_container_width=True)

    # Prediksi Harga
    st.header("🔮 AI Price Prediction")
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_stock = st.selectbox("Pilih Saham", pm.df['Stock'])
        days = st.slider("Periode Prediksi (hari)", 7, 90, 30)
    with col2:
        if selected_stock:
            with st.spinner("Menghitung prediksi..."):
                dates, predictions, last_pred = analyzer.predict_price(selected_stock, days)
                if predictions is not None:
                    current_price = pm.df[pm.df['Stock'] == selected_stock]['Market Price'].iloc[0]
                    change_pct = (last_pred / current_price - 1) * 100
                    st.metric(f"Harga Prediksi dalam {days} hari", format_rupiah(last_pred), format_percentage(change_pct))
                    volatility = current_price * 0.15 * np.sqrt(days/365)
                    upper = [p + volatility * (i/len(predictions)) for i, p in enumerate(predictions)]
                    lower = [p - volatility * (i/len(predictions)) for i, p in enumerate(predictions)]
                    forecast_data = {
                        'dates': dates,
                        'predictions': predictions,
                        'upper': upper,
                        'lower': lower,
                        'confidence': True
                    }
                    history = pm.simulated_data[selected_stock].tail(60)
                    st.plotly_chart(visualizer.price_prediction_plot(history, forecast_data, selected_stock), use_container_width=True)

    # What-If
    st.header("🎮 What If Scenario Analysis")
    col1, col2 = st.columns(2)
    with col1:
        sim_stock = st.selectbox("Pilih Saham", pm.df['Stock'], key='sim_stock')
        price_change = st.slider("Perubahan Harga (%)", -50.0, 50.0, 10.0, key='price_slider')
    with col2:
        if sim_stock:
            result = analyzer.what_if_simulation(sim_stock, price_change)
            if result:
                current_value = pm.df['Market Value'].sum()
                new_value = result['new_total_market']
                change = (new_value - current_value) / current_value * 100
                st.metric("Dampak Total Nilai Portofolio", format_rupiah(new_value), format_percentage(change))
                st.metric("Unrealized Baru", format_rupiah(result['new_unrealized']), format_percentage((result['new_unrealized'] - summary['total_unrealized']) / summary['total_invested'] * 100))

    # Rekomendasi
    st.header("💡 Trading Recommendations")
    rec_df = analyzer.generate_recommendations()
    rec_colors = {'Sell': 'red', 'Buy More': 'green', 'Hold/Buy': 'lightgreen', 'Hold/Sell': 'orange', 'Hold': 'gray'}
    styled_rec = rec_df.style.apply(lambda x: [f"background-color: {rec_colors.get(v, 'white')}" for v in x], subset=['Recommendation'])
    st.dataframe(styled_rec, use_container_width=True)

    # Risiko
    with st.expander("🔍 Analisis Risiko"):
        risk_data = risk.risk_report()
        st.subheader("Distribusi Sektor (%)")
        st.dataframe(risk_data['sector_distribution'], use_container_width=True)
        st.metric("Skor Konsentrasi (0-100)", risk_data['concentration_score'])
        st.subheader("Volatilitas Saham (%)")
        st.dataframe(risk_data['volatility_table'], use_container_width=True)

    # Benchmark
    with st.expander("📊 Benchmarking vs IHSG"):
        bench_df = bench.compare_vs_index()
        metrics = bench.performance_metrics(bench_df)
        st.line_chart(bench_df.set_index('Date'), use_container_width=True)
        col1, col2 = st.columns(2)
        col1.metric("Alpha", f"{metrics['Alpha']}%")
        col2.metric("Korelasi β Proxy", metrics['Correlation (β proxy)'])

    # Dividen
    with st.expander("💰 Pendapatan Dividen"):
        div_df = div_tracker.calculate_portfolio_dividends()
        total_div, avg_yield = div_tracker.total_dividend()
        st.dataframe(div_df, use_container_width=True)
        col1, col2 = st.columns(2)
        col1.metric("Total Dividen Tahunan", f"Rp {total_div:,.0f}")
        col2.metric("Rata-rata Yield", f"{avg_yield:.2f}%")

    # Optimasi
    with st.expander("📈 Optimasi Alokasi Portofolio"):
        rebalance_df, opt_risk = opt.rebalance_recommendation()
        st.dataframe(rebalance_df, use_container_width=True)
        st.caption(f"Volatilitas optimal portofolio: {opt_risk:.2%}")

    # CRUD
    crud.display_editor()
        if st.button("🔁 Refresh Data & Rekomendasi"):
                    st.rerun()

if __name__ == "__main__":
    main()
