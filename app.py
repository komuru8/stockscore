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
if 'language' not in st.session_state:
    st.session_state.language = 'ja'  # Default to Japanese

def get_text(key, lang=None):
    """Get localized text"""
    if lang is None:
        lang = st.session_state.language
    
    texts = {
        'title': {
            'ja': '📈 株予想アプリ - Japanese Stock Analysis Tool',
            'en': '📈 Stock Analysis Tool - Japanese Stock Prediction App'
        },
        'terms': {
            'ja': '📋 利用規約',
            'en': '📋 Terms'
        },
        'terms_help': {
            'ja': '利用規約・免責事項を確認',
            'en': 'Terms of Service & Disclaimer'
        },
        'language_toggle': {
            'ja': '🌐 Language: 日本語',
            'en': '🌐 Language: English'
        },
        'market_selection': {
            'ja': '市場選択 / Market Selection',
            'en': 'Market Selection / 市場選択'
        },
        'japanese_stocks': {
            'ja': '日本株 (Japanese Stocks)',
            'en': 'Japanese Stocks (日本株)'
        },
        'us_stocks': {
            'ja': '米国株 (US Stocks)',
            'en': 'US Stocks (米国株)'
        },
        'emerging_stocks': {
            'ja': '新興国株 (Emerging Markets)',
            'en': 'Emerging Markets (新興国株)'
        },
        'view_mode': {
            'ja': '表示モード / View Mode',
            'en': 'View Mode / 表示モード'
        },
        'simple_view': {
            'ja': 'シンプル表示 / Simple View',
            'en': 'Simple View / シンプル表示'
        },
        'detailed_view': {
            'ja': '詳細表示 / Detailed View',
            'en': 'Detailed View / 詳細表示'
        },
        'scoring_criteria': {
            'ja': 'スコア基準調整 / Scoring Criteria',
            'en': 'Scoring Criteria / スコア基準調整'
        },
        'portfolio_overview': {
            'ja': 'ポートフォリオ概要 / Portfolio Overview',
            'en': 'Portfolio Overview / ポートフォリオ概要'
        },
        'analyzed_stocks': {
            'ja': '分析銘柄数 / Analyzed Stocks',
            'en': 'Analyzed Stocks / 分析銘柄数'
        },
        'buy_recommendations': {
            'ja': '購入推奨 / Buy Recommendations',
            'en': 'Buy Recommendations / 購入推奨'
        },
        'average_score': {
            'ja': '平均スコア / Average Score',
            'en': 'Average Score / 平均スコア'
        },
        'last_update': {
            'ja': '最終更新 / Last Update',
            'en': 'Last Update / 最終更新'
        },
        'update_data': {
            'ja': 'データ更新 / Update Data',
            'en': 'Update Data / データ更新'
        }
    }
    
    return texts.get(key, {}).get(lang, key)

def main():
    # Language toggle in top right
    col1, col2, col3 = st.columns([6, 2, 2])
    with col2:
        if st.button(get_text('language_toggle'), help="Switch language"):
            st.session_state.language = 'en' if st.session_state.language == 'ja' else 'ja'
            st.rerun()
    with col3:
        if st.button(get_text('terms'), help=get_text('terms_help')):
            st.switch_page("pages/terms.py")
    
    st.title(get_text('title'))
    
    # Sidebar configuration
    st.sidebar.header("設定" if st.session_state.language == 'ja' else "Settings")
    
    # Market selection
    market_options = [
        get_text('japanese_stocks'),
        get_text('us_stocks'),
        get_text('emerging_stocks')
    ]
    market = st.sidebar.selectbox(
        get_text('market_selection'),
        market_options,
        index=0
    )
    
    # View mode selection
    view_mode = st.sidebar.radio(
        get_text('view_mode'),
        [get_text('simple_view'), get_text('detailed_view')]
    )
    
    # Scoring criteria adjustment
    st.sidebar.subheader(get_text('scoring_criteria'))
    
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
    if st.button(get_text('update_data'), type="primary"):
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
    st.subheader(get_text('portfolio_overview'))
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            get_text('analyzed_stocks'),
            len(df),
            delta=None
        )
    
    with col2:
        buy_count = len(df[df['Score'] >= 80])
        st.metric(
            get_text('buy_recommendations'),
            buy_count,
            delta=f"{buy_count/len(df)*100:.1f}%" if len(df) > 0 else "0%"
        )
    
    with col3:
        avg_score = df['Score'].mean()
        st.metric(
            get_text('average_score'),
            f"{avg_score:.1f}",
            delta=None
        )
    
    with col4:
        st.metric(
            get_text('last_update'),
            st.session_state.last_update.strftime("%H:%M") if st.session_state.last_update else "N/A",
            delta=None
        )
    
    # Investment recommendations overview
    st.subheader("投資推奨レベル別銘柄数" if st.session_state.language == 'ja' else "Stock Count by Recommendation Level")
    
    recommendation_counts = {
        "🚀 強い買い" if st.session_state.language == 'ja' else "🚀 Strong Buy": len(df[df['Score'] >= 80]),
        "👀 ウォッチ" if st.session_state.language == 'ja' else "👀 Watch": len(df[(df['Score'] >= 60) & (df['Score'] < 80)]),
        "➖ 中立" if st.session_state.language == 'ja' else "➖ Neutral": len(df[(df['Score'] >= 40) & (df['Score'] < 60)]),
        "❌ 非推奨" if st.session_state.language == 'ja' else "❌ Not Recommended": len(df[df['Score'] < 40])
    }
    
    # Create horizontal bar chart for recommendation levels
    rec_data = []
    for level, count in recommendation_counts.items():
        rec_data.append({'Level': level, 'Count': count})
    rec_df = pd.DataFrame(rec_data)
    
    fig = px.bar(
        rec_df,
        x='Count',
        y='Level',
        orientation='h',
        color='Count',
        color_continuous_scale=['#ff4444', '#ff8800', '#ffaa00', '#00aa00'],
        title="投資推奨レベル別分析" if st.session_state.language == 'ja' else "Investment Recommendation Analysis"
    )
    fig.update_layout(
        showlegend=False,
        yaxis={'categoryorder': 'array', 'categoryarray': list(recommendation_counts.keys())[::-1]}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Results table
    if view_mode == "シンプル表示 / Simple View":
        display_simple_view(df)
    else:
        display_detailed_view(df, data)

def create_circular_score(score, size=100):
    """Create circular score visualization using SVG"""
    # Determine color based on score
    if score >= 80:
        color = "#28a745"  # Green
        stroke_color = "#28a745"
    elif score >= 60:
        color = "#fd7e14"  # Orange
        stroke_color = "#fd7e14"
    elif score >= 40:
        color = "#ffc107"  # Yellow
        stroke_color = "#ffc107"
    else:
        color = "#dc3545"  # Red
        stroke_color = "#dc3545"
    
    # Calculate circle parameters
    radius = size // 3
    circumference = 2 * 3.14159 * radius
    stroke_dasharray = circumference
    stroke_dashoffset = circumference - (circumference * score / 100)
    
    svg = f"""
    <div style="display: flex; justify-content: center; align-items: center; width: {size}px; height: {size}px;">
        <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
            <!-- Background circle -->
            <circle 
                cx="{size//2}" 
                cy="{size//2}" 
                r="{radius}" 
                stroke="#e9ecef" 
                stroke-width="8" 
                fill="none"
            />
            <!-- Progress circle -->
            <circle 
                cx="{size//2}" 
                cy="{size//2}" 
                r="{radius}" 
                stroke="{stroke_color}" 
                stroke-width="8" 
                fill="none"
                stroke-dasharray="{stroke_dasharray}"
                stroke-dashoffset="{stroke_dashoffset}"
                stroke-linecap="round"
                transform="rotate(-90 {size//2} {size//2})"
                style="transition: stroke-dashoffset 0.3s ease-in-out;"
            />
            <!-- Score text -->
            <text 
                x="{size//2}" 
                y="{size//2 + 5}" 
                text-anchor="middle" 
                font-family="Arial, sans-serif"
                font-size="{size//4}" 
                font-weight="bold" 
                fill="{color}"
            >
                {int(score)}
            </text>
        </svg>
    </div>
    """
    return svg

def display_simple_view(df):
    """Display simple view of results"""
    st.subheader("銘柄一覧" if st.session_state.language == 'ja' else "Stock List")
    
    # Display stocks in a grid format with circular scores
    for i in range(0, len(df), 2):
        cols = st.columns(2)
        
        for j, col in enumerate(cols):
            if i + j < len(df):
                stock = df.iloc[i + j]
                with col:
                    with st.container():
                        # Create card-like container
                        st.markdown(f"""
                        <div style="
                            border: 1px solid #ddd;
                            border-radius: 10px;
                            padding: 20px;
                            margin-bottom: 20px;
                            background-color: white;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        ">
                        """, unsafe_allow_html=True)
                        
                        # Stock header
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**{stock['Symbol']}**")
                            st.markdown(f"<small>{stock['Company']}</small>", unsafe_allow_html=True)
                            st.markdown(f"価格: {stock['Current Price']}" if st.session_state.language == 'ja' else f"Price: {stock['Current Price']}")
                        
                        with col2:
                            # Display circular score
                            circular_svg = create_circular_score(stock['Score'], 80)
                            st.markdown(circular_svg, unsafe_allow_html=True)
                        
                        # Recommendation
                        st.markdown(f"**{stock['Recommendation']}**")
                        
                        st.markdown("</div>", unsafe_allow_html=True)

def display_detailed_view(df, data):
    """Display detailed view of results"""
    st.subheader("詳細分析" if st.session_state.language == 'ja' else "Detailed Analysis")
    
    # Top performers
    st.write("### 🚀 " + ("トップパフォーマー" if st.session_state.language == 'ja' else "Top Performers"))
    top_stocks = df.head(3)
    
    for _, stock in top_stocks.iterrows():
        with st.expander(f"{stock['Symbol']} - {stock['Company']} (Score: {stock['Score']:.1f})"):
            # Main stock info with circular score
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write("**" + ("基本情報" if st.session_state.language == 'ja' else "Basic Info") + "**")
                st.write(("現在価格" if st.session_state.language == 'ja' else "Current Price") + f": {stock['Current Price']}")
                st.write(("推奨" if st.session_state.language == 'ja' else "Recommendation") + f": {stock['Recommendation']}")
                
            with col2:
                st.write("**" + ("財務指標" if st.session_state.language == 'ja' else "Financial Metrics") + "**")
                st.write(f"PER: {stock['PER']}")
                st.write(f"PBR: {stock['PBR']}")
                st.write(f"ROE: {stock['ROE']}%")
                st.write(("配当利回り" if st.session_state.language == 'ja' else "Dividend Yield") + f": {stock['Dividend Yield']}%")
            
            with col3:
                st.write("**" + ("スコア" if st.session_state.language == 'ja' else "Score") + "**")
                circular_svg = create_circular_score(stock['Score'], 100)
                st.markdown(circular_svg, unsafe_allow_html=True)
            
            # Individual score breakdown with circular indicators
            symbol = stock['Symbol']
            if symbol in data and 'score_breakdown' in data[symbol]:
                breakdown = data[symbol]['score_breakdown']
                st.write("**" + ("スコア内訳" if st.session_state.language == 'ja' else "Score Breakdown") + "**")
                
                # Display breakdown scores with mini circular indicators
                col1, col2, col3, col4 = st.columns(4)
                
                scores_data = [
                    ('PER', breakdown.get('per_score', 0)),
                    ('PBR', breakdown.get('pbr_score', 0)),
                    ('ROE', breakdown.get('roe_score', 0)),
                    (('配当' if st.session_state.language == 'ja' else 'Dividend'), breakdown.get('dividend_score', 0))
                ]
                
                for i, (metric, score) in enumerate(scores_data):
                    with [col1, col2, col3, col4][i]:
                        st.markdown(f"**{metric}**")
                        mini_circular_svg = create_circular_score(score, 60)
                        st.markdown(mini_circular_svg, unsafe_allow_html=True)
    
    # Full detailed table
    st.write("### 📊 " + ("全銘柄詳細" if st.session_state.language == 'ja' else "All Stocks Detail"))
    
    # Enhanced table with better formatting
    display_columns = ['Symbol', 'Company', 'Score', 'Recommendation', 'Current Price', 'PER', 'PBR', 'ROE', 'Dividend Yield']
    enhanced_df = df[display_columns].copy()
    
    # Format numerical columns
    for col in ['PER', 'PBR', 'ROE', 'Dividend Yield']:
        enhanced_df[col] = pd.to_numeric(enhanced_df[col], errors='coerce')
        enhanced_df[col] = enhanced_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
    
    st.dataframe(
        enhanced_df,
        use_container_width=True,
        height=600,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score",
                help="Investment score (0-100)",
                min_value=0,
                max_value=100,
            ),
        }
    )

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
