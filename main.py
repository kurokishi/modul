# main.py
import streamlit as st
import pandas as pd
import numpy as np
from data.portfolio_manager import PortfolioManager
from data.portfolio_crud import PortfolioCRUD
from data.dividend_tracker import DividendTracker
from data.input_loader import InputLoader
from analysis.portfolio_analyzer import PortfolioAnalyzer
from analysis.risk_analyzer import RiskAnalyzer
from analysis.benchmark import BenchmarkAnalyzer
from analysis.optimizer import PortfolioOptimizer
from analysis.stock_scorer import StockScorer
from analysis.stock_recommender import StockRecommender
from analysis.allocation_helper import AllocationHelper
from visualization.portfolio_visualizer import PortfolioVisualizer
from utils.formatter import format_rupiah, format_percentage, color_negative_red

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
    loader = InputLoader()

    st.title("📊 Advanced Portfolio Analysis Dashboard")

    # ===== Upload Data Analisis Awal =====
    loader.upload_interface()
    uploaded_df = loader.get_analysis_data()
    if not uploaded_df.empty:
        st.subheader("📋 Data Saham Watchlist")
        st.dataframe(uploaded_df, use_container_width=True)

        scorer = StockScorer(uploaded_df)
        scored_df = scorer.apply_scoring()
        st.subheader("🏅 Skor Saham Berdasarkan Valuasi & Kinerja")
        st.dataframe(scored_df[['Stock', 'PER', 'PBV', 'Yield', 'ROE', 'Final Score']], use_container_width=True)

        recommender = StockRecommender(scored_df, pm.df)
        recommendations = recommender.recommend_additions(top_n=5)
        if not recommendations.empty:
            st.subheader("🧠 Rekomendasi Penambahan Saham (Belum Dimiliki)")
            st.dataframe(recommendations, use_container_width=True)

            st.subheader("💸 Simulasi Alokasi Dana untuk Rekomendasi")
            budget = st.number_input("Masukkan total dana (Rp)", min_value=0, value=5000000)
            method = st.selectbox("Metode Alokasi", ["equal", "weighted"])
            allocator = AllocationHelper(recommendations)
            alloc_df = allocator.simulate_allocation(budget, method)
            if not alloc_df.empty:
                st.dataframe(alloc_df, use_container_width=True)

    # ===== CRUD Interaktif =====
    crud.display_editor()

    # ===== Update Harga Pasar =====
    st.header("🔄 Real-time Market Data")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Update Market Prices", type="primary"):
            if pm.update_real_time_prices():
                st.success("Market prices updated successfully!")
                st.session_state.portfolio = pm
                st.rerun()
    with col2:
        st.caption(f"Last update: {pm.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
        st.progress(100, text="Data Siap")

    # ===== Ringkasan Portofolio =====
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

    # ===== Tabel Real-time Saham =====
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

    # ===== Rekomendasi Trading =====
    st.header("💡 Trading Recommendations")
    rec_df = analyzer.generate_recommendations()
    rec_colors = {'Sell': 'red', 'Buy More': 'green', 'Hold/Buy': 'lightgreen', 'Hold/Sell': 'orange', 'Hold': 'gray'}
    styled_rec = rec_df.style.apply(lambda x: [f"background-color: {rec_colors.get(v, 'white')}" for v in x], subset=['Recommendation'])
    st.dataframe(styled_rec, use_container_width=True)

    # ===== Analisis Risiko =====
    with st.expander("🔍 Analisis Risiko"):
        risk_data = risk.risk_report()
        st.dataframe(risk_data['sector_distribution'], use_container_width=True)
        st.metric("Skor Konsentrasi (0-100)", risk_data['concentration_score'])
        st.dataframe(risk_data['volatility_table'], use_container_width=True)

    # ===== Benchmark IHSG =====
    with st.expander("📊 Benchmarking vs IHSG"):
        bench_df = bench.compare_vs_index()
        metrics = bench.performance_metrics(bench_df)
        st.line_chart(bench_df.set_index('Date'), use_container_width=True)
        col1, col2 = st.columns(2)
        col1.metric("Alpha", f"{metrics['Alpha']}%")
        col2.metric("Korelasi β Proxy", metrics['Correlation (β proxy)'])

    # ===== Dividen =====
    with st.expander("💰 Pendapatan Dividen"):
        div_df = div_tracker.calculate_portfolio_dividends()
        total_div, avg_yield = div_tracker.total_dividend()
        st.dataframe(div_df, use_container_width=True)
        col1, col2 = st.columns(2)
        col1.metric("Total Dividen Tahunan", f"Rp {total_div:,.0f}")
        col2.metric("Rata-rata Yield", f"{avg_yield:.2f}%")

    # ===== Optimasi Portofolio =====
    with st.expander("📈 Optimasi Alokasi Portofolio"):
        rebalance_df, opt_risk = opt.rebalance_recommendation()
        st.dataframe(rebalance_df, use_container_width=True)
        st.caption(f"Volatilitas optimal portofolio: {opt_risk:.2%}")

if __name__ == '__main__':
    main()
