import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from stock_analyzer import StockAnalyzer
from data_fetcher import DataFetcher
import os

# Set page configuration
st.set_page_config(
    page_title="株予想アプリ - Stock Analysis Tool",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = StockAnalyzer()
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = {}

def main():
    st.title("📈 株予想アプリ - Japanese Stock Analysis Tool")
    
    # Display disclaimer
    st.warning("""
    **投資に関する重要な注意事項 / Important Investment Disclaimer**
    
    本アプリケーションで提供される情報は参考情報のみであり、投資助言ではありません。
    投資判断は必ずご自身の責任で行ってください。投資にはリスクが伴います。
    
    This application provides reference information only and is not investment advice.
    Please make investment decisions at your own risk and responsibility.
    """)
    
    # Sidebar configuration
    st.sidebar.header("設定 / Settings")
    
    # Market selection
    market = st.sidebar.selectbox(
        "市場選択 / Market Selection",
        ["日本株 (Japanese Stocks)", "米国株 (US Stocks)", "新興国株 (Emerging Markets)"],
        index=0
    )
    
    # View mode selection
    view_mode = st.sidebar.radio(
        "表示モード / View Mode",
        ["シンプル表示 / Simple View", "詳細表示 / Detailed View"]
    )
    
    # Scoring criteria adjustment
    st.sidebar.subheader("スコア基準調整 / Scoring Criteria")
    
    per_threshold = st.sidebar.slider(
        "PER閾値 (業界平均からの乖離%) / PER Threshold (% deviation from industry avg)",
        min_value=10, max_value=50, value=20, step=5
    )
    
    pbr_threshold = st.sidebar.slider(
        "PBR閾値 / PBR Threshold",
        min_value=0.5, max_value=2.0, value=1.0, step=0.1
    )
    
    roe_threshold = st.sidebar.slider(
        "ROE閾値 (%) / ROE Threshold (%)",
        min_value=5, max_value=20, value=10, step=1
    )
    
    dividend_multiplier = st.sidebar.slider(
        "配当利回り倍率 / Dividend Yield Multiplier",
        min_value=1.0, max_value=2.0, value=1.2, step=0.1
    )
    
    # Stock symbol input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if market == "日本株 (Japanese Stocks)":
            default_symbols = ["7203.T", "6758.T", "9984.T", "8306.T", "6861.T"]
            symbol_input = st.text_input(
                "銘柄コード入力 (例: 7203.T) / Stock Symbol Input (e.g., 7203.T)",
                placeholder="7203.T, 6758.T, 9984.T"
            )
        elif market == "米国株 (US Stocks)":
            default_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
            symbol_input = st.text_input(
                "銘柄シンボル入力 (例: AAPL) / Stock Symbol Input (e.g., AAPL)",
                placeholder="AAPL, MSFT, GOOGL"
            )
        else:
            default_symbols = ["2330.TW", "005930.KS", "TSM", "BABA", "JD"]
            symbol_input = st.text_input(
                "銘柄シンボル入力 / Stock Symbol Input",
                placeholder="2330.TW, 005930.KS"
            )
    
    with col2:
        use_default = st.button("デフォルト銘柄使用 / Use Default Stocks")
    
    # Determine which symbols to analyze
    if use_default:
        symbols = default_symbols
    elif symbol_input:
        symbols = [s.strip().upper() for s in symbol_input.split(",") if s.strip()]
    else:
        symbols = default_symbols
    
    # Update data button
    if st.button("データ更新 / Update Data", type="primary"):
        update_stock_data(symbols, per_threshold, pbr_threshold, roe_threshold, dividend_multiplier)
    
    # Auto-update data if it's been more than 30 minutes
    if st.session_state.last_update is None or \
       (datetime.now() - st.session_state.last_update).seconds > 1800:  # 30 minutes
        with st.spinner("データを取得中... / Fetching data..."):
            update_stock_data(symbols, per_threshold, pbr_threshold, roe_threshold, dividend_multiplier)
    
    # Display results
    if st.session_state.stock_data:
        display_results(view_mode, market)
    else:
        st.info("データを取得するには「データ更新」ボタンをクリックしてください。\nClick 'Update Data' button to fetch stock data.")

def update_stock_data(symbols, per_threshold, pbr_threshold, roe_threshold, dividend_multiplier):
    """Update stock data and scores"""
    try:
        with st.spinner("株価データを取得中... / Fetching stock data..."):
            # Update scoring criteria
            st.session_state.analyzer.update_criteria(
                per_threshold=per_threshold,
                pbr_threshold=pbr_threshold,
                roe_threshold=roe_threshold,
                dividend_multiplier=dividend_multiplier
            )
            
            # Analyze stocks
            results = st.session_state.analyzer.analyze_stocks(symbols)
            st.session_state.stock_data = results
            st.session_state.last_update = datetime.now()
            
            # Show notification for high-scoring stocks
            high_scoring = [stock for stock in results if results[stock].get('total_score', 0) >= 80]
            if high_scoring:
                st.success(f"🚀 高スコア銘柄発見! / High-scoring stocks found: {', '.join(high_scoring)}")
            
    except Exception as e:
        st.error(f"データ取得エラー / Data fetch error: {str(e)}")

def display_results(view_mode, market):
    """Display analysis results"""
    data = st.session_state.stock_data
    
    if not data:
        st.warning("表示するデータがありません / No data to display")
        return
    
    # Convert to DataFrame for easier manipulation
    df_data = []
    for symbol, info in data.items():
        if info and 'total_score' in info:
            df_data.append({
                'Symbol': symbol,
                'Company': info.get('company_name', symbol),
                'Score': info.get('total_score', 0),
                'Recommendation': get_recommendation(info.get('total_score', 0)),
                'PER': info.get('per', 'N/A'),
                'PBR': info.get('pbr', 'N/A'),
                'ROE': info.get('roe', 'N/A'),
                'Dividend Yield': info.get('dividend_yield', 'N/A'),
                'Current Price': info.get('current_price', 'N/A')
            })
    
    if not df_data:
        st.warning("有効なデータがありません / No valid data available")
        return
    
    df = pd.DataFrame(df_data)
    df = df.sort_values('Score', ascending=False)
    
    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "分析銘柄数 / Analyzed Stocks",
            len(df),
            delta=None
        )
    
    with col2:
        buy_count = len(df[df['Score'] >= 80])
        st.metric(
            "購入推奨 / Buy Recommendations",
            buy_count,
            delta=f"{buy_count/len(df)*100:.1f}%" if len(df) > 0 else "0%"
        )
    
    with col3:
        avg_score = df['Score'].mean()
        st.metric(
            "平均スコア / Average Score",
            f"{avg_score:.1f}",
            delta=None
        )
    
    with col4:
        st.metric(
            "最終更新 / Last Update",
            st.session_state.last_update.strftime("%H:%M") if st.session_state.last_update else "N/A",
            delta=None
        )
    
    # Score distribution chart
    st.subheader("スコア分布 / Score Distribution")
    
    fig = px.histogram(
        df, 
        x='Score', 
        nbins=20,
        title="Stock Score Distribution",
        labels={'Score': 'スコア / Score', 'count': '銘柄数 / Count'}
    )
    fig.add_vline(x=80, line_dash="dash", line_color="green", annotation_text="Buy (80+)")
    fig.add_vline(x=60, line_dash="dash", line_color="orange", annotation_text="Watch (60+)")
    fig.add_vline(x=40, line_dash="dash", line_color="red", annotation_text="Neutral (40+)")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Results table
    if view_mode == "シンプル表示 / Simple View":
        display_simple_view(df)
    else:
        display_detailed_view(df, data)

def display_simple_view(df):
    """Display simple view of results"""
    st.subheader("銘柄一覧 / Stock List")
    
    # Color code the dataframe
    def color_score(val):
        if val >= 80:
            return 'background-color: #d4edda'  # Light green
        elif val >= 60:
            return 'background-color: #fff3cd'  # Light yellow
        elif val >= 40:
            return 'background-color: #f8d7da'  # Light red
        else:
            return 'background-color: #f8f9fa'  # Light gray
    
    # Display formatted table
    display_df = df[['Symbol', 'Company', 'Score', 'Recommendation', 'Current Price']].copy()
    styled_df = display_df.style.applymap(color_score, subset=['Score'])
    
    st.dataframe(styled_df, use_container_width=True, height=400)

def display_detailed_view(df, data):
    """Display detailed view of results"""
    st.subheader("詳細分析 / Detailed Analysis")
    
    # Top performers
    st.write("### 🚀 トップパフォーマー / Top Performers")
    top_stocks = df.head(3)
    
    for _, stock in top_stocks.iterrows():
        with st.expander(f"{stock['Symbol']} - {stock['Company']} (Score: {stock['Score']:.1f})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**基本情報 / Basic Info**")
                st.write(f"現在価格 / Current Price: {stock['Current Price']}")
                st.write(f"推奨 / Recommendation: {stock['Recommendation']}")
                
            with col2:
                st.write("**財務指標 / Financial Metrics**")
                st.write(f"PER: {stock['PER']}")
                st.write(f"PBR: {stock['PBR']}")
                st.write(f"ROE: {stock['ROE']}%")
                st.write(f"配当利回り / Dividend Yield: {stock['Dividend Yield']}%")
            
            # Individual score breakdown
            symbol = stock['Symbol']
            if symbol in data and 'score_breakdown' in data[symbol]:
                breakdown = data[symbol]['score_breakdown']
                st.write("**スコア内訳 / Score Breakdown**")
                
                breakdown_df = pd.DataFrame([
                    {'Metric': 'PER Score', 'Points': breakdown.get('per_score', 0)},
                    {'Metric': 'PBR Score', 'Points': breakdown.get('pbr_score', 0)},
                    {'Metric': 'ROE Score', 'Points': breakdown.get('roe_score', 0)},
                    {'Metric': 'Dividend Score', 'Points': breakdown.get('dividend_score', 0)}
                ])
                
                fig = px.bar(
                    breakdown_df, 
                    x='Metric', 
                    y='Points',
                    title=f"Score Breakdown for {symbol}"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Full detailed table
    st.write("### 📊 全銘柄詳細 / All Stocks Detail")
    st.dataframe(df, use_container_width=True, height=600)

def get_recommendation(score):
    """Get recommendation based on score"""
    if score >= 80:
        return "🚀 購入推奨 / Buy"
    elif score >= 60:
        return "👀 ウォッチ / Watch"
    elif score >= 40:
        return "➖ 中立 / Neutral"
    else:
        return "❌ 非推奨 / Not Recommended"

if __name__ == "__main__":
    main()
