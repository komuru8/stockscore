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
    page_title="StockScore - Advanced Stock Analysis",
    page_icon="🎯",
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

def create_stock_logo():
    """Create custom StockScore logo SVG inspired by the provided design"""
    return """
    <div style="display: inline-block; margin-right: 10px; vertical-align: middle;">
        <svg width="40" height="40" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <!-- Background gradient -->
            <defs>
                <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#2563eb;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#0f172a;stop-opacity:1" />
                </linearGradient>
                <linearGradient id="chartGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#22d3ee;stop-opacity:1" />
                </linearGradient>
            </defs>
            
            <!-- Rounded background -->
            <rect x="5" y="5" width="90" height="90" rx="20" ry="20" fill="url(#bgGrad)" />
            
            <!-- Chart bars -->
            <rect x="20" y="65" width="12" height="20" rx="2" fill="url(#chartGrad)" opacity="0.9"/>
            <rect x="35" y="55" width="12" height="30" rx="2" fill="url(#chartGrad)" opacity="0.9"/>
            <rect x="50" y="45" width="12" height="40" rx="2" fill="url(#chartGrad)" opacity="0.9"/>
            <rect x="65" y="35" width="12" height="50" rx="2" fill="url(#chartGrad)" opacity="0.9"/>
            
            <!-- Trend line -->
            <path d="M 20 70 Q 35 60 50 50 Q 65 40 80 30" stroke="#10b981" stroke-width="3" fill="none" opacity="0.8"/>
            
            <!-- Data points -->
            <circle cx="26" cy="70" r="4" fill="#10b981"/>
            <circle cx="41" cy="60" r="4" fill="#10b981"/>
            <circle cx="56" cy="50" r="4" fill="#10b981"/>
            <circle cx="71" cy="40" r="4" fill="#10b981"/>
            <circle cx="80" cy="30" r="4" fill="#10b981"/>
            
            <!-- Checkmark -->
            <path d="M 70 75 L 75 80 L 85 70" stroke="#10b981" stroke-width="3" fill="none" stroke-linecap="round"/>
        </svg>
    </div>
    """

def get_text(key, lang=None):
    """Get localized text"""
    if lang is None:
        lang = st.session_state.language
    
    texts = {
        'title': {
            'ja': 'StockScore',
            'en': 'StockScore'
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

def handle_action_buttons(popularity_button, dividend_button, theme_button, random_button, market):
    """Handle action button clicks and return selected symbols"""
    import random
    
    selected_symbols = None
    
    if popularity_button:
        # Popular/high market cap stocks by market
        if market == get_text('japanese_stocks'):
            selected_symbols = [
                "7203.T", "6758.T", "9984.T", "8306.T", "6861.T", "9434.T", "4063.T", "6098.T",
                "8035.T", "9432.T", "4519.T", "6367.T", "7267.T", "8031.T", "4568.T", "9020.T",
                "6954.T", "8028.T", "6902.T", "7974.T", "4507.T", "9022.T", "6326.T", "6971.T"
            ][:20]  # Top 20 popular Japanese stocks
        elif market == get_text('us_stocks'):
            selected_symbols = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "UNH", "XOM",
                "JNJ", "JPM", "V", "PG", "HD", "CVX", "MA", "BAC", "ABBV", "PFE"
            ]  # Top 20 popular US stocks
        else:
            selected_symbols = [
                "2330.TW", "005930.KS", "TSM", "BABA", "JD", "PDD", "BIDU", "ASML", "NIO", "XPEV",
                "LI", "SHOP", "SE", "GRAB", "VALE", "PBR", "ITUB", "BBD", "EWZ", "FMX"
            ]  # Top 20 emerging market stocks
        
        st.success("人気ランキング上位銘柄を選択しました" if st.session_state.language == 'ja' else "Selected top popular stocks")
        
    elif dividend_button:
        # High dividend yield stocks by market
        if market == get_text('japanese_stocks'):
            selected_symbols = [
                "8306.T", "8411.T", "8316.T", "8591.T", "8604.T", "8630.T", "8725.T", "8732.T",
                "8766.T", "8795.T", "8830.T", "9501.T", "9613.T", "9962.T", "9983.T", "8001.T",
                "8028.T", "8031.T", "8053.T", "8058.T"
            ]  # High dividend Japanese stocks (banks, utilities, etc.)
        elif market == get_text('us_stocks'):
            selected_symbols = [
                "T", "VZ", "XOM", "CVX", "KO", "PEP", "JNJ", "PG", "MO", "PM",
                "IBM", "VTI", "SCHD", "DVY", "HDV", "NOBL", "DGRO", "VYM", "SPYD", "USMV"
            ]  # High dividend US stocks
        else:
            selected_symbols = [
                "PBR", "VALE", "ITUB", "BBD", "ABEV", "SID", "UGP", "EWZ", "FMX", "CIG",
                "ERJ", "GOL", "AZUL", "BRFS", "JBS", "CACC", "PAC", "TV", "WIT", "005930.KS"
            ]  # High dividend emerging market stocks
            
        st.success("高配当利回り銘柄を選択しました" if st.session_state.language == 'ja' else "Selected high dividend yield stocks")
        
    elif theme_button:
        # Show theme selection modal
        with st.expander("テーマを選択してください" if st.session_state.language == 'ja' else "Select a Theme", expanded=True):
            theme_options = get_theme_options(market)
            selected_theme = st.selectbox(
                "投資テーマ" if st.session_state.language == 'ja' else "Investment Theme",
                list(theme_options.keys()),
                index=0
            )
            
            if st.button("このテーマで分析開始" if st.session_state.language == 'ja' else "Start Analysis with This Theme"):
                selected_symbols = theme_options[selected_theme]
                st.success(f"テーマ「{selected_theme}」の銘柄を選択しました" if st.session_state.language == 'ja' else f"Selected stocks for theme: {selected_theme}")
                
    elif random_button:
        # Random selection from all available stocks
        if market == get_text('japanese_stocks'):
            all_symbols = [
                "7203.T", "6758.T", "9984.T", "8306.T", "6861.T", "9434.T", "4063.T", "6098.T",
                "8035.T", "9432.T", "4519.T", "6367.T", "7267.T", "8031.T", "4568.T", "9020.T",
                "6954.T", "8028.T", "6902.T", "7974.T", "4507.T", "9022.T", "6326.T", "6971.T",
                "6504.T", "8766.T", "4502.T", "7751.T", "6981.T", "8802.T", "4503.T", "9301.T",
                "7269.T", "6178.T", "8001.T", "4661.T", "3382.T", "4755.T", "7762.T", "6273.T",
                "8309.T", "6758.T", "8058.T", "4523.T", "6869.T", "7735.T", "4543.T", "6503.T"
            ]
        elif market == get_text('us_stocks'):
            all_symbols = [
                "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "UNH",
                "XOM", "JNJ", "JPM", "V", "PG", "HD", "CVX", "MA", "BAC", "ABBV",
                "PFE", "AVGO", "KO", "MRK", "PEP", "TMO", "COST", "WMT", "DHR", "LIN",
                "ABT", "ACN", "VZ", "MCD", "ADBE", "CRM", "TXN", "NEE", "PM", "NFLX"
            ]
        else:
            all_symbols = [
                "2330.TW", "005930.KS", "TSM", "BABA", "JD", "PDD", "BIDU", "ASML", "NIO", "XPEV",
                "LI", "SHOP", "SE", "GRAB", "VALE", "PBR", "ITUB", "BBD", "EWZ", "FMX",
                "WIT", "ABEV", "SID", "UGP", "CIG", "ERJ", "GOL", "AZUL", "BRFS", "JBS"
            ]
            
        selected_symbols = random.sample(all_symbols, min(25, len(all_symbols)))
        st.success("ランダムに銘柄を選択しました" if st.session_state.language == 'ja' else "Randomly selected stocks")
        
    return selected_symbols

def get_theme_options(market):
    """Get theme-based stock selections by market"""
    if market == get_text('japanese_stocks'):
        return {
            "高配当株 / High Dividend": ["8306.T", "8411.T", "8316.T", "8591.T", "8604.T", "8630.T", "8725.T", "9501.T"],
            "成長株 / Growth": ["9984.T", "6098.T", "4063.T", "6367.T", "4568.T", "6178.T", "4755.T", "3659.T"],
            "防衛関連 / Defense": ["7203.T", "6902.T", "7267.T", "7269.T", "6113.T", "6770.T", "6645.T", "6301.T"],
            "テクノロジー / Technology": ["6758.T", "9984.T", "4063.T", "6367.T", "4568.T", "6861.T", "4324.T", "4689.T"],
            "バイオ・製薬 / Biotech & Pharma": ["4519.T", "4568.T", "4507.T", "4523.T", "4502.T", "4503.T", "4661.T", "4543.T"],
            "エネルギー / Energy": ["5020.T", "1605.T", "5019.T", "1662.T", "9501.T", "9502.T", "9503.T", "9531.T"]
        }
    elif market == get_text('us_stocks'):
        return {
            "高配当株 / High Dividend": ["T", "VZ", "XOM", "CVX", "KO", "PEP", "JNJ", "PG", "MO", "IBM"],
            "成長株 / Growth": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "NFLX", "CRM", "ADBE"],
            "防衛関連 / Defense": ["BA", "LMT", "RTX", "GD", "NOC", "HII", "LDOS", "TXT", "KTOS", "AJRD"],
            "テクノロジー / Technology": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "ORCL", "IBM", "CSCO", "INTC"],
            "バイオ・製薬 / Biotech & Pharma": ["JNJ", "PFE", "ABBV", "MRK", "BMY", "AMGN", "GILD", "BIIB", "VRTX", "REGN"],
            "エネルギー / Energy": ["XOM", "CVX", "COP", "EOG", "SLB", "MPC", "VLO", "PSX", "OXY", "KMI"]
        }
    else:
        return {
            "高配当株 / High Dividend": ["PBR", "VALE", "ITUB", "BBD", "ABEV", "SID", "UGP", "EWZ"],
            "成長株 / Growth": ["BABA", "JD", "PDD", "BIDU", "NIO", "XPEV", "LI", "SE"],
            "テクノロジー / Technology": ["2330.TW", "TSM", "BABA", "JD", "PDD", "BIDU", "ASML", "SHOP"],
            "エネルギー / Energy": ["PBR", "VALE", "SID", "UGP", "CIG", "ERJ", "005930.KS", "2330.TW"],
            "消費財 / Consumer": ["ABEV", "BRFS", "JBS", "FMX", "CACC", "PAC", "TV", "BBD"],
            "金融 / Financial": ["ITUB", "BBD", "EWZ", "WIT", "CACC", "PAC", "TV", "005930.KS"]
        }

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
    
    # Display title with custom logo
    logo_html = create_stock_logo()
    title_html = f"""
    <div style="display: flex; align-items: center; margin-bottom: 20px;">
        {logo_html}
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #2563eb 0%, #10b981 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            {get_text('title')}
        </h1>
    </div>
    """
    st.markdown(title_html, unsafe_allow_html=True)
    
    # Sidebar configuration (moved up to define market first)
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
    
    # Action buttons section with enhanced styling
    st.markdown("---")
    st.subheader("📍 " + ("株式検索方法を選択" if st.session_state.language == 'ja' else "Choose Stock Discovery Method"))
    
    # Add custom CSS for enhanced button styling
    st.markdown("""
    <style>
    div[data-testid="column"] > div > div > div > button {
        height: 120px;
        border-radius: 15px;
        border: 2px solid #e1e5e9;
        background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
        transition: all 0.3s ease;
        font-size: 14px !important;
        font-weight: 600;
        text-align: center;
    }
    div[data-testid="column"] > div > div > div > button:hover {
        border-color: #2563eb;
        background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create action buttons in a grid layout
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        popularity_button = st.button(
            "📈\n\n人気ランキング\nから探す" if st.session_state.language == 'ja' else "📈\n\nPopular\nRanking",
            use_container_width=True,
            help="市場で人気の銘柄を表示" if st.session_state.language == 'ja' else "Show popular stocks in the market"
        )
    
    with col2:
        dividend_button = st.button(
            "💰\n\n配当利回り\nから探す" if st.session_state.language == 'ja' else "💰\n\nHigh\nDividend",
            use_container_width=True,
            help="高配当利回りの銘柄を表示" if st.session_state.language == 'ja' else "Show high dividend yield stocks"
        )
    
    with col3:
        theme_button = st.button(
            "🎯\n\nテーマ別\nに探す" if st.session_state.language == 'ja' else "🎯\n\nBy\nTheme",
            use_container_width=True,
            help="特定のテーマやセクターの銘柄を表示" if st.session_state.language == 'ja' else "Show stocks by specific themes or sectors"
        )
    
    with col4:
        random_button = st.button(
            "🎲\n\nランダム\nに探す" if st.session_state.language == 'ja' else "🎲\n\nRandom\nPick",
            use_container_width=True,
            help="ランダムに選択された銘柄を表示" if st.session_state.language == 'ja' else "Show randomly selected stocks"
        )
    
    # Handle action button clicks
    selected_method = handle_action_buttons(popularity_button, dividend_button, theme_button, random_button, market)
    
    # Determine which symbols to analyze based on selected method
    if selected_method:
        symbols = selected_method
    else:
        # Manual stock symbol input (fallback)
        st.markdown("---")
        st.subheader("手動銘柄入力" if st.session_state.language == 'ja' else "Manual Stock Input")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if market == get_text('japanese_stocks'):
                default_symbols = ["7203.T", "6758.T", "9984.T", "8306.T", "6861.T", "9434.T", "4063.T", "6098.T"]
                symbol_input = st.text_input(
                    "銘柄コード入力 (例: 7203.T) / Stock Symbol Input (e.g., 7203.T)",
                    placeholder="7203.T, 6758.T, 9984.T"
                )
            elif market == get_text('us_stocks'):
                default_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B"]
                symbol_input = st.text_input(
                    "銘柄シンボル入力 (例: AAPL) / Stock Symbol Input (e.g., AAPL)",
                    placeholder="AAPL, MSFT, GOOGL"
                )
            else:
                default_symbols = ["2330.TW", "005930.KS", "TSM", "BABA", "JD", "PDD", "BIDU", "ASML"]
                symbol_input = st.text_input(
                    "銘柄シンボル入力 / Stock Symbol Input",
                    placeholder="2330.TW, 005930.KS"
                )
        
        with col2:
            use_default = st.button("デフォルト銘柄使用 / Use Default Stocks")
        
        # Set symbols based on user input
        if use_default:
            symbols = default_symbols
        elif symbol_input:
            symbols = [s.strip().upper() for s in symbol_input.split(",") if s.strip()]
        else:
            symbols = default_symbols
    
    # Update data button
    if st.button(get_text('update_data'), type="primary"):
        update_stock_data(symbols, per_threshold, pbr_threshold, roe_threshold, dividend_multiplier)
    
    # Auto-update data if it's been more than 30 minutes (only for smaller datasets)
    if len(symbols) <= 20 and (st.session_state.last_update is None or \
       (datetime.now() - st.session_state.last_update).seconds > 1800):  # 30 minutes
        st.info(f"自動更新中... / Auto-updating {len(symbols)} stocks...")
        update_stock_data(symbols, per_threshold, pbr_threshold, roe_threshold, dividend_multiplier)
    
    # Display results
    if st.session_state.stock_data:
        display_results(view_mode, market)
    else:
        st.info("データを取得するには「データ更新」ボタンをクリックしてください。\nClick 'Update Data' button to fetch stock data.")

def update_stock_data(symbols, per_threshold, pbr_threshold, roe_threshold, dividend_multiplier):
    """Update stock data and scores"""
    progress_bar = None
    status_text = None
    
    try:
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Update scoring criteria
        status_text.text("設定を更新中... / Updating criteria...")
        st.session_state.analyzer.update_criteria(
            per_threshold=per_threshold,
            pbr_threshold=pbr_threshold,
            roe_threshold=roe_threshold,
            dividend_multiplier=dividend_multiplier
        )
        progress_bar.progress(10)
        
        # Analyze stocks with progress updates
        status_text.text(f"株価データを取得中... / Fetching data for {len(symbols)} stocks...")
        progress_bar.progress(20)
        
        results = st.session_state.analyzer.analyze_stocks(symbols)
        progress_bar.progress(90)
        
        # Store results
        st.session_state.stock_data = results
        st.session_state.last_update = datetime.now()
        progress_bar.progress(100)
        
        # Show summary
        valid_results = [r for r in results.values() if r and 'total_score' in r]
        status_text.text(f"分析完了: {len(valid_results)}/{len(symbols)} 銘柄 / Analysis complete: {len(valid_results)}/{len(symbols)} stocks")
        
        # Show notification for high-scoring stocks
        high_scoring = [stock for stock in results if results.get(stock) and results[stock].get('total_score', 0) >= 80]
        if high_scoring:
            st.success(f"🚀 高スコア銘柄発見! / High-scoring stocks found: {len(high_scoring)} stocks")
            
        # Clear progress indicators after a moment
        time.sleep(2)
        if progress_bar:
            progress_bar.empty()
        if status_text:
            status_text.empty()
        
    except Exception as e:
        st.error(f"データ取得エラー / Data fetch error: {str(e)}")
        if progress_bar:
            progress_bar.empty()
        if status_text:
            status_text.empty()

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
    
    # Featured Recommendations Section
    st.subheader("🌟 " + ("推奨銘柄ピックアップ" if st.session_state.language == 'ja' else "Featured Recommendations"))
    
    # Get top 3 recommendations
    top_recommendations = df.head(3)
    
    if len(top_recommendations) > 0:
        # Display in 1 row of 3 columns
        cols = st.columns(3)
        for col_idx, col in enumerate(cols):
            if col_idx < len(top_recommendations):
                stock = top_recommendations.iloc[col_idx]
                
                with col:
                    # Create card-like container
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            border: 2px solid {'#28a745' if stock['Score'] >= 80 else '#fd7e14' if stock['Score'] >= 60 else '#ffc107'};
                            border-radius: 15px;
                            padding: 20px;
                            margin-bottom: 15px;
                            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            text-align: center;
                        ">
                        """, unsafe_allow_html=True)
                        
                        # Stock header
                        st.markdown(f"**{stock['Symbol']}**")
                        st.markdown(f"<div style='font-size: 0.9em; color: #666;'>{stock['Company']}</div>", unsafe_allow_html=True)
                        
                        # Circular score
                        circular_svg = create_circular_score(stock['Score'], 100)
                        st.markdown(circular_svg, unsafe_allow_html=True)
                        
                        # Price and recommendation
                        st.markdown(f"**{stock['Current Price']}**")
                        st.markdown(f"<div style='font-size: 0.9em; font-weight: bold;'>{stock['Recommendation']}</div>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
    
    # Results table
    if view_mode == get_text('simple_view'):
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
    """Display simple table view of results"""
    st.subheader("銘柄一覧" if st.session_state.language == 'ja' else "Stock List")
    
    # Enhanced table with better formatting and styling
    display_columns = ['Symbol', 'Company', 'Score', 'Recommendation', 'Current Price', 'PER', 'PBR', 'ROE', 'Dividend Yield']
    table_df = df[display_columns].copy()
    
    # Format numerical columns
    for col in ['PER', 'PBR', 'ROE', 'Dividend Yield']:
        table_df[col] = pd.to_numeric(table_df[col], errors='coerce')
        if col in ['ROE', 'Dividend Yield']:
            table_df[col] = table_df[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
        else:
            table_df[col] = table_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
    
    # Color coding function for scores
    def highlight_scores(row):
        score = row['Score']
        if score >= 80:
            return ['background-color: #d4edda'] * len(row)  # Light green
        elif score >= 60:
            return ['background-color: #fff3cd'] * len(row)  # Light yellow
        elif score >= 40:
            return ['background-color: #f8d7da'] * len(row)  # Light red
        else:
            return ['background-color: #f8f9fa'] * len(row)  # Light gray
    
    # Apply styling
    styled_df = table_df.style.apply(highlight_scores, axis=1)
    
    # Display the styled dataframe
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=600,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score",
                help="Investment score (0-100)",
                min_value=0,
                max_value=100,
                format="%.1f",
            ),
            "Symbol": st.column_config.TextColumn(
                "Symbol" if st.session_state.language == 'en' else "銘柄",
                width="small",
            ),
            "Company": st.column_config.TextColumn(
                "Company" if st.session_state.language == 'en' else "企業名",
                width="medium",
            ),
            "Current Price": st.column_config.TextColumn(
                "Price" if st.session_state.language == 'en' else "価格",
                width="small",
            ),
            "Recommendation": st.column_config.TextColumn(
                "Rec." if st.session_state.language == 'en' else "推奨",
                width="medium",
            )
        }
    )

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
