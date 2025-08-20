import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from stock_analyzer import StockAnalyzer

try:
    from enhanced_stock_analyzer import EnhancedStockAnalyzer
    from relative_scoring_engine import RelativeScoringEngine
    ENHANCED_ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"Enhanced analyzer import failed: {e}")
    ENHANCED_ANALYZER_AVAILABLE = False
from data_fetcher import DataFetcher
import os

# Set page configuration
st.set_page_config(
    page_title="TOP - StockScore",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state with proper error handling
if 'analyzer' not in st.session_state:
    try:
        if ENHANCED_ANALYZER_AVAILABLE:
            st.session_state.analyzer = EnhancedStockAnalyzer()
            st.session_state.using_enhanced = True
            print("✅ Enhanced analyzer initialized")
        else:
            st.session_state.analyzer = StockAnalyzer()
            st.session_state.using_enhanced = False
            print("✅ Basic analyzer initialized")
    except Exception as init_error:
        print(f"Analyzer initialization error: {init_error}")
        # Fallback to basic analyzer
        st.session_state.analyzer = StockAnalyzer()
        st.session_state.using_enhanced = False

# Initialize relative scoring engine
if 'relative_scorer' not in st.session_state:
    st.session_state.relative_scorer = RelativeScoringEngine()
if 'last_update' not in st.session_state:
    st.session_state.last_update = None
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = {}
if 'language' not in st.session_state:
    st.session_state.language = 'ja'  # Default to Japanese
if 'user_mode' not in st.session_state:
    st.session_state.user_mode = 'beginner'  # Default to beginner mode



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
            'ja': '利用規約',
            'en': 'Terms'
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
        'all_markets': {
            'ja': '全て (All Markets)',
            'en': 'All Markets (全て)'
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
        },
        'user_mode_selection': {
            'ja': 'ユーザーモード',
            'en': 'User Mode'
        },
        'beginner_mode': {
            'ja': '👶 初級者',
            'en': '👶 Beginner'
        },
        'intermediate_mode': {
            'ja': '🧑‍💼 中級者',
            'en': '🧑‍💼 Intermediate'
        },
        'advanced_mode': {
            'ja': '🧑‍🔬 上級者',
            'en': '🧑‍🔬 Advanced'
        },
        'beginner_description': {
            'ja': 'AI推奨スコア中心、直感的な「買い/見送り」判定',
            'en': 'AI-focused scoring with intuitive buy/hold decisions'
        },
        'intermediate_description': {
            'ja': '10指標によるスクリーニング、重み付け調整可能',
            'en': '10-metric screening with customizable weightings'
        },
        'advanced_description': {
            'ja': '高度なフィルタリング・カスタム条件設定（開発中）',
            'en': 'Advanced filtering & custom conditions (in development)'
        }
    }
    
    return texts.get(key, {}).get(lang, key)

def handle_action_buttons(popularity_button, dividend_button, theme_button, random_button, market, stock_count=20):
    """Handle action button clicks and return selected symbols"""
    import random
    
    selected_symbols = None
    
    if popularity_button:
        # Popular/high market cap stocks by market
        if market == get_text('all_markets'):
            # Combine stocks from all markets to support larger counts
            japanese_stocks = [
                "7203.T", "6758.T", "9984.T", "8306.T", "6861.T", "9434.T", "4063.T", "6098.T", "8035.T", "9432.T", 
                "4519.T", "6367.T", "7267.T", "8031.T", "4568.T", "9020.T", "6954.T", "1605.T", "6902.T", "7974.T",
                "4507.T", "9022.T", "6326.T", "6971.T", "8766.T", "4502.T", "7751.T", "6981.T", "8802.T", "4503.T",
                "9301.T", "7269.T", "6178.T", "8001.T", "4661.T", "3382.T", "4755.T", "7762.T", "6273.T", "8309.T",
                "8058.T", "4523.T", "6869.T", "7735.T", "4543.T", "6503.T", "9613.T", "9962.T", "9983.T", "8411.T",
                "8316.T", "8591.T", "8604.T", "8630.T", "8725.T", "5020.T", "4385.T", "6501.T", "7013.T", "9101.T",
                "2914.T", "1605.T", "3659.T", "4021.T", "4042.T", "4183.T", "4188.T", "4324.T", "4689.T", "4704.T"
            ]
            us_stocks = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "UNH", "XOM", "JNJ", "JPM", 
                "V", "PG", "HD", "CVX", "MA", "BAC", "ABBV", "PFE", "KO", "MRK", "TMO", "COST", "WMT", "DHR", 
                "LIN", "ABT", "ACN", "VZ", "MCD", "ADBE", "CRM", "TXN", "NEE", "PM", "NFLX", "BMY", "T", "CMCSA", 
                "NKE", "HON", "UPS", "SBUX", "LOW", "QCOM", "AMD", "IBM", "GS", "MS", "BLK", "CAT", "RTX", "GE", 
                "INTC", "ORCL", "CSCO", "DIS", "F", "GM", "PYPL", "UBER", "ABNB", "ROKU", "ZM", "SNOW", "CRM", 
                "DDOG", "PLTR", "SQ", "TWTR", "SNAP", "PINS"
            ]
            emerging_stocks = [
                "2330.TW", "005930.KS", "TSM", "BABA", "JD", "PDD", "BIDU", "ASML", "NIO", "XPEV", "LI", "SHOP", 
                "SE", "GRAB", "VALE", "PBR", "ITUB", "BBD", "PETR4.SA", "WEGE3.SA", "MGLU3.SA", "B3SA3.SA", 
                "RENT3.SA", "FLRY3.SA", "HAPV3.SA", "LREN3.SA", "NTCO3.SA", "RADL3.SA", "GGBR4.SA", "USIM5.SA",
                "CSNA3.SA", "GOAU4.SA", "SUZB3.SA", "CMIG4.SA", "ELET3.SA", "TAEE11.SA", "VIVT3.SA", "TIMS3.SA",
                "TOTS3.SA", "BRDT3.SA", "KLBN11.SA", "SUZB3.SA", "CIEL3.SA", "COGN3.SA", "YDUQ3.SA", "ARZZ3.SA",
                "MRFG3.SA", "JBSS3.SA", "BEEF3.SA", "SMTO3.SA", "CAML3.SA", "MULT3.SA", "PCAR3.SA", "RAIZ4.SA"
            ]
            all_combined = japanese_stocks + us_stocks + emerging_stocks
            selected_symbols = all_combined[:stock_count]
        elif market == get_text('japanese_stocks'):
            all_japanese_stocks = [
                "7203.T", "6758.T", "9984.T", "8306.T", "6861.T", "9434.T", "4063.T", "6098.T",
                "8035.T", "9432.T", "4519.T", "6367.T", "7267.T", "8031.T", "4568.T", "9020.T",
                "6954.T", "1605.T", "6902.T", "7974.T", "4507.T", "9022.T", "6326.T", "6971.T",
                "8766.T", "4502.T", "7751.T", "6981.T", "8802.T", "4503.T", "9301.T", "7269.T",
                "6178.T", "8001.T", "4661.T", "3382.T", "4755.T", "7762.T", "6273.T", "8309.T",
                "8058.T", "4523.T", "6869.T", "7735.T", "4543.T", "6503.T", "9613.T", "9962.T",
                "9983.T", "8411.T", "8316.T", "8591.T", "8604.T", "8630.T", "8725.T", "5020.T",
                "4385.T", "6501.T", "7013.T", "9101.T", "2914.T", "1605.T", "3659.T", "4021.T",
                "4042.T", "4183.T", "4188.T", "4324.T", "4689.T", "4704.T", "4708.T", "4751.T",
                "4768.T", "4812.T", "4816.T", "4901.T", "4911.T", "4912.T", "4967.T", "4968.T",
                "5020.T", "5101.T", "5108.T", "5201.T", "5202.T", "5232.T", "5301.T", "5332.T",
                "5401.T", "5411.T", "5541.T", "5631.T", "5703.T", "5706.T", "5707.T", "5711.T",
                "5714.T", "5802.T", "5803.T", "5901.T", "5902.T", "5938.T", "5947.T", "5991.T",
                "6028.T", "6103.T", "6113.T", "6146.T", "6305.T", "6324.T", "6361.T", "6366.T",
                "6370.T", "6448.T", "6460.T", "6471.T", "6473.T", "6506.T", "6594.T", "6674.T",
                "6701.T", "6702.T", "6723.T", "6724.T", "6728.T", "6752.T", "6762.T", "6770.T",
                "6806.T", "6841.T", "6856.T", "6857.T", "6952.T", "6976.T", "7003.T", "7004.T",
                "7011.T", "7012.T", "7105.T", "7201.T", "7202.T", "7205.T", "7211.T", "7240.T",
                "7261.T", "7270.T", "7272.T", "7282.T", "7309.T", "7731.T", "7733.T", "7752.T",
                "7832.T", "7951.T", "7956.T", "7988.T", "8002.T", "8015.T", "8020.T", "8053.T"
            ]
            selected_symbols = all_japanese_stocks[:stock_count]
        elif market == get_text('us_stocks'):
            all_us_stocks = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "UNH", "XOM",
                "JNJ", "JPM", "V", "PG", "HD", "CVX", "MA", "BAC", "ABBV", "PFE", "KO", "MRK",
                "TMO", "COST", "WMT", "DHR", "LIN", "ABT", "ACN", "VZ", "MCD", "ADBE", "CRM",
                "TXN", "NEE", "PM", "NFLX", "BMY", "T", "CMCSA", "NKE", "HON", "UPS", "SBUX",
                "LOW", "QCOM", "AMD", "IBM", "GS", "MS", "BLK", "CAT", "RTX", "GE", "INTC",
                "ORCL", "CSCO", "DIS", "F", "GM", "PYPL", "UBER", "ABNB", "ROKU", "ZM", "SNOW",
                "DDOG", "PLTR", "SQ", "TWTR", "SNAP", "PINS", "DOCU", "OKTA", "CRWD", "ZS",
                "NET", "TEAM", "NOW", "WDAY", "VEEV", "PANW", "SPLK", "ESTC", "MDB", "WORK",
                "SPOT", "TWLO", "PTON", "CHWY", "ETSY", "W", "SHOP", "SQ", "PYPL", "ROKU",
                "NFLX", "DIS", "CMCSA", "T", "VZ", "TMUS", "CHTR", "DISH", "SIRI", "FOXA",
                "CBS", "VIAC", "DISCA", "DISCK", "WBD", "PARA", "AMC", "CNK", "IMAX", "LGF-A"
            ]
            selected_symbols = all_us_stocks[:stock_count]
        else:
            all_emerging_stocks = [
                "2330.TW", "005930.KS", "TSM", "BABA", "JD", "PDD", "BIDU", "ASML", "NIO", "XPEV",
                "LI", "SHOP", "SE", "GRAB", "VALE", "PBR", "ITUB", "BBD", "EWZ", "FMX", "ABEV",
                "SID", "UGP", "CIG", "ERJ", "GOL", "AZUL", "BRFS", "JBS", "CACC", "PAC", "TV",
                "WIT", "000001.SS", "000002.SS", "600036.SS", "600519.SS", "000858.SZ", "002594.SZ",
                "600887.SS", "601318.SS", "000725.SZ", "002415.SZ", "600276.SS", "601166.SS",
                "PETR4.SA", "WEGE3.SA", "MGLU3.SA", "B3SA3.SA", "RENT3.SA", "FLRY3.SA", "HAPV3.SA",
                "LREN3.SA", "NTCO3.SA", "RADL3.SA", "GGBR4.SA", "USIM5.SA", "CSNA3.SA", "GOAU4.SA",
                "SUZB3.SA", "CMIG4.SA", "ELET3.SA", "TAEE11.SA", "VIVT3.SA", "TIMS3.SA", "TOTS3.SA",
                "BRDT3.SA", "KLBN11.SA", "CIEL3.SA", "COGN3.SA", "YDUQ3.SA", "ARZZ3.SA", "MRFG3.SA",
                "JBSS3.SA", "BEEF3.SA", "SMTO3.SA", "CAML3.SA", "MULT3.SA", "PCAR3.SA", "RAIZ4.SA",
                "KEPL3.SA", "LWSA3.SA", "MTRE3.SA", "RRRP3.SA", "SBSP3.SA", "SAPR11.SA", "SANB11.SA",
                "BPAC11.SA", "CCRO3.SA", "CMIN3.SA", "CPFE3.SA", "CRFB3.SA", "CSAN3.SA", "CVCB3.SA"
            ]
            selected_symbols = all_emerging_stocks[:stock_count]
        
        st.success("人気ランキング上位銘柄を選択しました" if st.session_state.language == 'ja' else "Selected top popular stocks")
        
    elif dividend_button:
        # High dividend yield stocks by market
        if market == get_text('all_markets'):
            # Combine high dividend stocks from all markets
            japanese_dividend = ["8306.T", "8411.T", "8316.T", "8591.T", "8604.T", "8630.T", "8725.T", "8766.T", "8795.T", "8830.T", "9501.T", "9613.T", "9962.T", "9983.T", "8001.T", "8031.T", "8053.T", "8058.T", "5020.T", "1605.T"]
            us_dividend = ["T", "VZ", "XOM", "CVX", "KO", "PEP", "JNJ", "PG", "MO", "PM", "IBM", "MMM", "CAT", "GE", "F", "GM", "C", "BAC", "JPM", "WFC", "O", "MAIN", "STAG", "EPD", "ET", "KMI", "ENB", "TRP", "SPG", "REG"]
            emerging_dividend = ["VALE", "PBR", "ITUB", "BBD", "ABEV", "SID", "UGP", "EWZ", "FMX", "CIG", "ERJ", "GOL", "AZUL", "BRFS", "JBS", "CACC", "PAC", "TV", "WIT", "005930.KS"]
            all_dividend = japanese_dividend + us_dividend + emerging_dividend
            selected_symbols = all_dividend[:stock_count]
        elif market == get_text('japanese_stocks'):
            all_dividend_japanese = [
                "8306.T", "8411.T", "8316.T", "8591.T", "8604.T", "8630.T", "8725.T", "5020.T",
                "8766.T", "8795.T", "8830.T", "9501.T", "9613.T", "9962.T", "9983.T", "8001.T",
                "1605.T", "8031.T", "8053.T", "8058.T", "9502.T", "9503.T", "9531.T", "9532.T",
                "8802.T", "8804.T", "8601.T", "8628.T", "8771.T", "8772.T", "8773.T", "3405.T",
                "5201.T", "5202.T", "5333.T", "5401.T", "5406.T", "5408.T", "5713.T", "5714.T",
                "6502.T", "6503.T", "6504.T", "6506.T", "6841.T", "6857.T", "6971.T", "6976.T"
            ]
            selected_symbols = all_dividend_japanese[:stock_count]
        elif market == get_text('us_stocks'):
            all_dividend_us = [
                "T", "VZ", "XOM", "CVX", "KO", "PEP", "JNJ", "PG", "MO", "PM",
                "IBM", "MMM", "CAT", "GE", "F", "GM", "C", "BAC", "JPM", "WFC",
                "O", "MAIN", "STAG", "EPD", "ET", "KMI", "ENB", "TRP", "SPG", "REG",
                "DUK", "NEE", "SO", "D", "AEP", "EXC", "SRE", "PCG", "ED", "WEC",
                "MDT", "ABBV", "MRK", "PFE", "BMY", "LLY", "UNH", "CVS", "WBA", "GILD"
            ]
            selected_symbols = all_dividend_us[:stock_count]
        else:
            # Expanded high dividend emerging market stocks
            all_dividend_emerging = [
                "PBR", "VALE", "ITUB", "BBD", "ABEV", "SID", "UGP", "EWZ", "FMX", "CIG",
                "ERJ", "GOL", "AZUL", "BRFS", "JBS", "CACC", "PAC", "TV", "WIT", "005930.KS",
                "PETR4.SA", "WEGE3.SA", "MGLU3.SA", "B3SA3.SA", "RENT3.SA", "FLRY3.SA", "HAPV3.SA",
                "LREN3.SA", "NTCO3.SA", "RADL3.SA", "GGBR4.SA", "USIM5.SA", "CSNA3.SA", "GOAU4.SA",
                "SUZB3.SA", "CMIG4.SA", "ELET3.SA", "TAEE11.SA", "VIVT3.SA", "TIMS3.SA", "TOTS3.SA",
                "BRDT3.SA", "KLBN11.SA", "CIEL3.SA", "COGN3.SA", "YDUQ3.SA", "ARZZ3.SA", "MRFG3.SA"
            ]
            selected_symbols = all_dividend_emerging[:stock_count]
            
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
                theme_stocks = theme_options[selected_theme]
                selected_symbols = theme_stocks[:stock_count]  # Use user-selected stock count
                st.success(f"テーマ「{selected_theme}」から{len(selected_symbols)}銘柄を選択しました" if st.session_state.language == 'ja' else f"Selected {len(selected_symbols)} stocks for theme: {selected_theme}")
                
    elif random_button:
        # Random selection from all available stocks using the expanded lists
        if market == get_text('all_markets'):
            # Use the same expanded lists from popularity search
            japanese_all = [
                "7203.T", "6758.T", "9984.T", "8306.T", "6861.T", "9434.T", "4063.T", "6098.T", "8035.T", "9432.T", 
                "4519.T", "6367.T", "7267.T", "8031.T", "4568.T", "9020.T", "6954.T", "1605.T", "6902.T", "7974.T",
                "4507.T", "9022.T", "6326.T", "6971.T", "8766.T", "4502.T", "7751.T", "6981.T", "8802.T", "4503.T",
                "9301.T", "7269.T", "6178.T", "8001.T", "4661.T", "3382.T", "4755.T", "7762.T", "6273.T", "8309.T",
                "8058.T", "4523.T", "6869.T", "7735.T", "4543.T", "6503.T", "9613.T", "9962.T", "9983.T", "8411.T",
                "8316.T", "8591.T", "8604.T", "8630.T", "8725.T", "5020.T", "4385.T", "6501.T", "7013.T", "9101.T"
            ]
            us_all = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "UNH", "XOM", "JNJ", "JPM", 
                "V", "PG", "HD", "CVX", "MA", "BAC", "ABBV", "PFE", "KO", "MRK", "TMO", "COST", "WMT", "DHR", 
                "LIN", "ABT", "ACN", "VZ", "MCD", "ADBE", "CRM", "TXN", "NEE", "PM", "NFLX", "BMY", "T", "CMCSA", 
                "NKE", "HON", "UPS", "SBUX", "LOW", "QCOM", "AMD", "IBM", "GS", "MS", "BLK", "CAT", "RTX", "GE", 
                "INTC", "ORCL", "CSCO", "DIS", "F", "GM", "PYPL", "UBER", "ABNB", "ROKU", "ZM", "SNOW"
            ]
            emerging_all = [
                "2330.TW", "005930.KS", "TSM", "BABA", "JD", "PDD", "BIDU", "ASML", "NIO", "XPEV", "LI", "SHOP", 
                "SE", "GRAB", "VALE", "PBR", "ITUB", "BBD", "PETR4.SA", "WEGE3.SA", "MGLU3.SA", "B3SA3.SA", 
                "RENT3.SA", "FLRY3.SA", "HAPV3.SA", "LREN3.SA", "NTCO3.SA", "RADL3.SA", "GGBR4.SA", "USIM5.SA",
                "CSNA3.SA", "GOAU4.SA", "SUZB3.SA", "CMIG4.SA", "ELET3.SA", "TAEE11.SA", "VIVT3.SA", "TIMS3.SA"
            ]
            all_symbols = japanese_all + us_all + emerging_all
            selected_symbols = random.sample(all_symbols, min(stock_count, len(all_symbols)))
        elif market == get_text('japanese_stocks'):
            # Use the expanded Japanese stock list
            all_symbols = [
                "7203.T", "6758.T", "9984.T", "8306.T", "6861.T", "9434.T", "4063.T", "6098.T",
                "8035.T", "9432.T", "4519.T", "6367.T", "7267.T", "8031.T", "4568.T", "9020.T",
                "6954.T", "1605.T", "6902.T", "7974.T", "4507.T", "9022.T", "6326.T", "6971.T",
                "8766.T", "4502.T", "7751.T", "6981.T", "8802.T", "4503.T", "9301.T", "7269.T",
                "6178.T", "8001.T", "4661.T", "3382.T", "4755.T", "7762.T", "6273.T", "8309.T",
                "8058.T", "4523.T", "6869.T", "7735.T", "4543.T", "6503.T", "9613.T", "9962.T",
                "9983.T", "8411.T", "8316.T", "8591.T", "8604.T", "8630.T", "8725.T", "5020.T",
                "4385.T", "6501.T", "7013.T", "9101.T", "2914.T", "1605.T", "3659.T", "4021.T",
                "4042.T", "4183.T", "4188.T", "4324.T", "4689.T", "4704.T", "4708.T", "4751.T",
                "4768.T", "4812.T", "4816.T", "4901.T", "4911.T", "4912.T", "4967.T", "4968.T"
            ]
            selected_symbols = random.sample(all_symbols, min(stock_count, len(all_symbols)))
        elif market == get_text('us_stocks'):
            # Use the expanded US stock list
            all_symbols = [
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "UNH", "XOM",
                "JNJ", "JPM", "V", "PG", "HD", "CVX", "MA", "BAC", "ABBV", "PFE", "KO", "MRK",
                "TMO", "COST", "WMT", "DHR", "LIN", "ABT", "ACN", "VZ", "MCD", "ADBE", "CRM",
                "TXN", "NEE", "PM", "NFLX", "BMY", "T", "CMCSA", "NKE", "HON", "UPS", "SBUX",
                "LOW", "QCOM", "AMD", "IBM", "GS", "MS", "BLK", "CAT", "RTX", "GE", "INTC",
                "ORCL", "CSCO", "DIS", "F", "GM", "PYPL", "UBER", "ABNB", "ROKU", "ZM", "SNOW",
                "DDOG", "PLTR", "SQ", "TWTR", "SNAP", "PINS", "DOCU", "OKTA", "CRWD", "ZS"
            ]
            selected_symbols = random.sample(all_symbols, min(stock_count, len(all_symbols)))
        else:
            # Use the expanded emerging market list
            all_symbols = [
                "2330.TW", "005930.KS", "TSM", "BABA", "JD", "PDD", "BIDU", "ASML", "NIO", "XPEV",
                "LI", "SHOP", "SE", "GRAB", "VALE", "PBR", "ITUB", "BBD", "EWZ", "FMX", "ABEV",
                "SID", "UGP", "CIG", "ERJ", "GOL", "AZUL", "BRFS", "JBS", "CACC", "PAC", "TV",
                "WIT", "000001.SS", "000002.SS", "600036.SS", "600519.SS", "000858.SZ", "002594.SZ",
                "600887.SS", "601318.SS", "000725.SZ", "002415.SZ", "600276.SS", "601166.SS",
                "PETR4.SA", "WEGE3.SA", "MGLU3.SA", "B3SA3.SA", "RENT3.SA", "FLRY3.SA", "HAPV3.SA"
            ]
            selected_symbols = random.sample(all_symbols, min(stock_count, len(all_symbols)))
            
        st.success("ランダムに銘柄を選択しました" if st.session_state.language == 'ja' else "Randomly selected stocks")
        
    return selected_symbols

def generate_stock_analysis(stock):
    """Generate detailed stock analysis based on fundamentals and market position"""
    symbol = stock['Symbol']
    score = stock['Score']
    company = stock['Company']
    
    # Get language preference
    is_japanese = st.session_state.language == 'ja'
    
    # Analysis templates based on symbol patterns and scores
    analyses = {
        # Japanese stocks
        "7203.T": {
            'ja': "トヨタは特にROE（自己資本利益率）15%超、営業利益率8%台という優秀な収益性指標を維持しています。電動化技術への年間1兆円規模の投資により、2030年までに電動車販売比率50%を目指し、収益の多角化を図っています。今後5年間で売上高年平均3-5%成長、営業利益率10%台への向上が予想され、脱炭素社会移行のリーダーとして持続的な収益拡大が期待されます。",
            'en': "Toyota excels particularly in ROE (Return on Equity) exceeding 15% and operating margin around 8%. With annual investments of over 1 trillion yen in electrification technology, the company aims for 50% electrified vehicle sales ratio by 2030, diversifying revenue streams. Over the next 5 years, we expect average annual revenue growth of 3-5% and operating margin improvement to over 10%, positioning Toyota for sustained revenue expansion as a leader in the carbon-neutral transition."
        },
        "6758.T": {
            'ja': "ソニーは特にイメージセンサー事業で世界シェア50%超、営業利益率20%台という突出した収益性を誇ります。PlayStation事業の継続的成長（年売上2.7兆円）とコンテンツIP活用により、今後3年間で売上高年平均5-7%成長が見込まれます。メタバース・AI技術への投資により、2027年頃には新規事業からの収益が全体の15%に達し、総合的な収益性向上が予想されます。",
            'en': "Sony excels particularly with over 50% global market share in image sensors and operating margins exceeding 20%. Continued growth in PlayStation business (annual revenue of 2.7 trillion yen) and content IP utilization are expected to drive 5-7% average annual revenue growth over the next 3 years. Investments in metaverse and AI technologies are projected to generate 15% of total revenue from new businesses by 2027, enhancing overall profitability."
        },
        "9984.T": {
            'ja': "ソフトバンクグループは世界最大級のテクノロジー投資会社として、AI・IoT・フィンテック分野のユニコーン企業への戦略的投資を展開。Vision Fundを通じた投資ポートフォリオの価値向上と、国内通信事業の安定収益が企業価値を支えています。テクノロジー革新の恩恵を受けやすい投資構造により、長期的な成長性が期待されます。",
            'en': "SoftBank Group operates as one of the world's largest technology investment companies, strategically investing in AI, IoT, and fintech unicorns. Portfolio value appreciation through Vision Fund and stable domestic telecom revenue support corporate value. The investment structure positioned to benefit from technology innovation offers strong long-term growth potential."
        },
        # US stocks
        "AAPL": {
            'ja': "アップルは営業利益率30%超、ROE180%という圧倒的な収益効率を実現しています。特にサービス事業の粗利率70%が際立ち、今後5年でサービス収益は年平均10-15%成長が予想されます。Vision ProやApple Car等の新事業展開により、2028年頃には売上高5000億ドル突破、総売上に占めるサービス比率30%到達が見込まれ、更なる高収益体質の強化が期待されます。",
            'en': "Apple achieves exceptional profitability with operating margins exceeding 30% and ROE of 180%. The Services business particularly stands out with gross margins of 70%, expected to grow 10-15% annually over the next 5 years. With new ventures like Vision Pro and Apple Car, revenue is projected to surpass $500 billion by 2028, with Services comprising 30% of total revenue, further strengthening the high-margin business structure."
        },
        "MSFT": {
            'ja': "マイクロソフトはクラウドコンピューティング分野でAzureを中心とした急成長により、企業向けソフトウェアの盟主的地位を確立。AI技術への先行投資、サブスクリプション型ビジネスモデルの浸透、企業のデジタルトランスフォーメーション需要の拡大が成長を牽引しています。",
            'en': "Microsoft has established dominance in enterprise software through rapid growth centered on Azure cloud computing. Leading AI technology investments, subscription business model penetration, and expanding enterprise digital transformation demand drive sustained growth in the cloud-first era."
        },
        "GOOGL": {
            'ja': "グーグル（アルファベット）は世界最大の検索エンジン・デジタル広告プラットフォームとして、膨大なデータ資産を活用したAI・機械学習技術で競争優位を構築。YouTube・クラウド事業の成長、自動運転Waymo等の未来技術への投資により、デジタル経済の発展とともに成長が期待されます。",
            'en': "Google (Alphabet) leverages its position as the world's largest search engine and digital advertising platform, building competitive advantages through AI and machine learning technologies powered by massive data assets. Growth in YouTube and cloud services, plus investments in future technologies like autonomous driving Waymo, position the company for continued expansion alongside the digital economy."
        }
    }
    
    # Generic analysis for stocks not in the specific list
    generic_analysis = {
        'ja': f"{company}は当社の分析において{score}点という{'優秀な' if score >= 80 else '良好な' if score >= 60 else '標準的な'}評価を獲得しました。特に{'ROEと営業利益率' if score >= 80 else 'PERと配当利回り' if score >= 60 else '財務安定性'}の指標で良好な数値を示しています。現在の業界トレンドと企業の競争優位性を考慮すると、今後2-3年で{'売上高5-10%成長と利益率改善' if score >= 80 else '安定した業績維持と配当継続' if score >= 60 else '業績回復の兆しと構造改革効果'}が期待されます。",
        'en': f"{company} achieved a {'excellent' if score >= 80 else 'good' if score >= 60 else 'moderate'} score of {score} points in our analysis. The company particularly excels in {'ROE and operating margins' if score >= 80 else 'P/E ratio and dividend yield' if score >= 60 else 'financial stability'} metrics. Considering current industry trends and competitive advantages, we expect {'5-10% revenue growth and margin improvement' if score >= 80 else 'stable performance and dividend sustainability' if score >= 60 else 'signs of recovery and structural reform benefits'} over the next 2-3 years."
    }
    
    # Return specific analysis if available, otherwise use generic
    if symbol in analyses:
        return analyses[symbol]['ja' if is_japanese else 'en']
    else:
        return generic_analysis['ja' if is_japanese else 'en']

def get_market_type(symbol):
    """Determine market type based on symbol pattern"""
    if symbol.endswith('.T'):
        return "日本株" if st.session_state.language == 'ja' else "Japanese"
    elif any(symbol.endswith(suffix) for suffix in ['.SS', '.SZ', '.HK', '.TW', '.KS']):
        return "新興国株" if st.session_state.language == 'ja' else "Emerging"
    elif symbol in ['TSM', 'BABA', 'JD', 'PDD', 'BIDU', 'NIO', 'XPEV', 'LI', 'SHOP', 'SE', 'GRAB', 
                   'VALE', 'PBR', 'ITUB', 'BBD', 'EWZ', 'FMX', 'ABEV', 'SID', 'ASML']:
        return "新興国株" if st.session_state.language == 'ja' else "Emerging"
    else:
        return "米国株" if st.session_state.language == 'ja' else "US"

def get_japanese_company_name(symbol, original_name):
    """Get Japanese company name for display when language is Japanese"""
    japanese_names = {
        "7203.T": "トヨタ自動車",
        "6758.T": "ソニーグループ", 
        "9984.T": "ソフトバンクグループ",
        "8306.T": "三菱UFJフィナンシャル・グループ",
        "6861.T": "キーエンス",
        "9434.T": "ソフトバンク",
        "4063.T": "信越化学工業",
        "6098.T": "リクルートホールディングス",
        "8035.T": "東京エレクトロン",
        "9432.T": "日本電信電話",
        "4519.T": "中外製薬",
        "6367.T": "ダイキン工業",
        "7267.T": "ホンダ",
        "8031.T": "三井物産",
        "4568.T": "第一三共",
        "9020.T": "東日本旅客鉄道",
        "6954.T": "ファナック",
        "1605.T": "富士商事",
        "6902.T": "デンソー",
        "7974.T": "任天堂",
        "4507.T": "塩野義製薬",
        "9022.T": "東海旅客鉄道",
        "6326.T": "クボタ",
        "6971.T": "京セラ",
        "8411.T": "みずほフィナンシャルグループ",
        "8316.T": "三井住友フィナンシャルグループ",
        "8591.T": "オリックス",
        "8604.T": "野村ホールディングス",
        "8630.T": "SOMPOホールディングス",
        "8725.T": "MS&ADインシュアランスグループホールディングス",
        "5020.T": "マネーパートナーズグループ",
        "8766.T": "東京海上ホールディングス",
        "8795.T": "T&Dホールディングス",
        "8830.T": "住友不動産",
        "9501.T": "東京電力ホールディングス",
        "9613.T": "エヌ・ティ・ティ・データ",
        "9962.T": "ミスミグループ本社",
        "9983.T": "ファーストリテイリング"
    }
    
    return japanese_names.get(symbol, original_name)

def get_theme_options(market):
    """Get theme-based stock selections by market with expanded lists"""
    if market == get_text('all_markets'):
        return {
            "高配当株 / High Dividend": [
                "8306.T", "8411.T", "8316.T", "8591.T", "8604.T", "8630.T", "8725.T", "5020.T", "8766.T", "8795.T",
                "T", "VZ", "XOM", "CVX", "KO", "PEP", "JNJ", "PG", "MO", "PM", "IBM", "MMM", "CAT", "GE", "F",
                "PBR", "VALE", "ITUB", "BBD", "ABEV", "SID", "UGP", "EWZ", "FMX", "CIG", "ERJ", "GOL", "AZUL",
                "BRFS", "JBS", "CACC", "PAC", "TV", "WIT", "005930.KS", "PETR4.SA", "WEGE3.SA", "MGLU3.SA"
            ],
            "成長株 / Growth": [
                "9984.T", "4063.T", "6758.T", "6861.T", "9434.T", "6098.T", "8035.T", "9432.T", "4519.T", "6367.T",
                "NVDA", "TSLA", "AMZN", "META", "GOOGL", "AAPL", "MSFT", "NFLX", "ADBE", "CRM", "UBER", "ABNB",
                "BABA", "JD", "PDD", "BIDU", "NIO", "XPEV", "LI", "TSM", "2330.TW", "SE", "GRAB", "SHOP",
                "ROKU", "ZM", "SNOW", "DDOG", "PLTR", "SQ", "PYPL", "SPOT", "TWLO", "PTON", "CHWY", "ETSY"
            ],
            "テクノロジー / Technology": [
                "6758.T", "9984.T", "9434.T", "4063.T", "6861.T", "6098.T", "8035.T", "9432.T", "6367.T", "7267.T",
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "NFLX", "ADBE", "CRM", "ORCL", "CSCO",
                "2330.TW", "TSM", "BABA", "JD", "PDD", "BIDU", "NIO", "XPEV", "LI", "ASML", "005930.KS", "SE",
                "GRAB", "SHOP", "ROKU", "ZM", "SNOW", "DDOG", "PLTR", "SQ", "NET", "TEAM", "NOW", "WDAY"
            ],
            "金融 / Financial": [
                "8306.T", "8411.T", "8316.T", "8591.T", "8604.T", "8630.T", "8725.T", "5020.T", "8766.T", "8795.T",
                "JPM", "BAC", "WFC", "C", "GS", "MS", "BLK", "USB", "PNC", "TFC", "COF", "AXP", "V", "MA",
                "ITUB", "BBD", "PETR4.SA", "B3SA3.SA", "ABEV", "SID", "UGP", "005930.KS", "VALE", "PBR",
                "BRFS", "JBS", "CACC", "PAC", "TV", "WIT", "EWZ", "FMX", "CIG", "ERJ", "GOL", "AZUL"
            ],
            "エネルギー / Energy": [
                "5020.T", "1605.T", "3659.T", "5101.T", "5108.T", "5201.T", "5202.T", "5232.T", "5301.T", "5332.T",
                "XOM", "CVX", "COP", "EOG", "SLB", "MPC", "VLO", "PSX", "KMI", "OKE", "EPD", "ET", "ENB", "TRP",
                "PBR", "VALE", "PETR4.SA", "WEGE3.SA", "GGBR4.SA", "USIM5.SA", "CSNA3.SA", "GOAU4.SA", "SID",
                "UGP", "CIG", "ERJ", "CMIG4.SA", "ELET3.SA", "TAEE11.SA", "VIVT3.SA", "TIMS3.SA", "TOTS3.SA"
            ],
            "大型優良株 / Blue Chips": [
                "7203.T", "6758.T", "9984.T", "8306.T", "6861.T", "9434.T", "4063.T", "6098.T", "8035.T", "9432.T",
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "BRK-B", "UNH", "JNJ", "JPM", "V", "PG",
                "2330.TW", "005930.KS", "TSM", "BABA", "JD", "PDD", "ASML", "VALE", "PBR", "ITUB", "BBD", "EWZ",
                "HD", "CVX", "MA", "BAC", "ABBV", "PFE", "KO", "MRK", "TMO", "COST", "WMT", "DHR", "LIN"
            ]
        }
    elif market == get_text('japanese_stocks'):
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
    # Language selection and terms button in top right
    col1, col2, col3 = st.columns([6, 2, 2])
    with col2:
        # Language dropdown
        language_options = {
            '🌐 日本語': 'ja',
            '🌐 English': 'en'
        }
        current_lang_display = '🌐 日本語' if st.session_state.language == 'ja' else '🌐 English'
        selected_lang = st.selectbox(
            "Language",
            options=list(language_options.keys()),
            index=list(language_options.keys()).index(current_lang_display),
            label_visibility="collapsed"
        )
        if language_options[selected_lang] != st.session_state.language:
            st.session_state.language = language_options[selected_lang]
            st.rerun()
    with col3:
        if st.button(get_text('terms'), help=get_text('terms_help')):
            st.switch_page("pages/利用規約.py")
    
    # Display title with emoji icon instead of SVG - reduced top spacing
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-top: -20px; margin-bottom: 15px;">
        <div style="font-size: 3rem; margin-right: 15px;">🎯</div>
        <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, #2563eb 0%, #10b981 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            {get_text('title')}
        </h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    st.sidebar.header("" if st.session_state.language == 'ja' else "")
    
    # User mode selection
    st.sidebar.subheader(get_text('user_mode_selection'))
    mode_options = {
        get_text('beginner_mode'): 'beginner',
        get_text('intermediate_mode'): 'intermediate'
    }
    
    current_mode_display = next(k for k, v in mode_options.items() if v == st.session_state.user_mode)
    selected_mode = st.sidebar.selectbox(
        "モード選択" if st.session_state.language == 'ja' else "Mode Selection",
        options=list(mode_options.keys()),
        index=list(mode_options.keys()).index(current_mode_display),
        help="投資経験に応じてモードを選択してください" if st.session_state.language == 'ja' else "Select mode based on your investment experience"
    )
    
    if mode_options[selected_mode] != st.session_state.user_mode:
        st.session_state.user_mode = mode_options[selected_mode]
        st.rerun()
    
    # Mode description
    if st.session_state.user_mode == 'beginner':
        st.sidebar.info(get_text('beginner_description'))
    elif st.session_state.user_mode == 'intermediate':
        st.sidebar.info(get_text('intermediate_description'))
    
    # Always use simple view
    view_mode = get_text('simple_view')
    
    # Conditional scoring criteria adjustment based on user mode
    # Initialize default values for all thresholds
    per_threshold = 15
    pbr_threshold = 1.0
    roe_threshold = 10
    dividend_threshold = 3.0
    dividend_multiplier = 1.2
    roa_threshold = 5
    sales_growth_threshold = 5
    eps_growth_threshold = 10
    operating_margin_threshold = 10
    equity_ratio_threshold = 40
    payout_ratio_threshold = 30
    
    if st.session_state.user_mode == 'beginner':
        # Simplified criteria for beginners
        st.sidebar.subheader("🎯 簡易設定")
        
        per_threshold = st.sidebar.slider(
            "PER基準" if st.session_state.language == 'ja' else "PER Standard",
            min_value=10, max_value=30, value=15, step=5,
            help="低いほど割安" if st.session_state.language == 'ja' else "Lower is better value"
        )
        
        dividend_threshold = st.sidebar.slider(
            "配当利回り基準 (%)" if st.session_state.language == 'ja' else "Dividend Yield Standard (%)",
            min_value=2.0, max_value=6.0, value=3.5, step=0.5,
            help="この値以上の配当利回りを評価" if st.session_state.language == 'ja' else "Evaluate dividend yields above this value"
        )
        
        # Convert to multiplier for backward compatibility with analyzer
        dividend_multiplier = 1.5
        
    elif st.session_state.user_mode == 'intermediate':
        # Full 10 indicators for intermediate users
        st.sidebar.subheader(get_text('scoring_criteria'))
        
        # Core valuation metrics
        per_threshold = st.sidebar.slider(
            "PER閾値" if st.session_state.language == 'ja' else "PER Threshold",
            min_value=5, max_value=50, value=15, step=5
        )
        
        pbr_threshold = st.sidebar.slider(
            "PBR閾値" if st.session_state.language == 'ja' else "PBR Threshold",
            min_value=0.5, max_value=3.0, value=1.0, step=0.1
        )
        
        roe_threshold = st.sidebar.slider(
            "ROE閾値 (%)" if st.session_state.language == 'ja' else "ROE Threshold (%)",
            min_value=5, max_value=25, value=10, step=1
        )
        
        roa_threshold = st.sidebar.slider(
            "ROA閾値 (%)" if st.session_state.language == 'ja' else "ROA Threshold (%)",
            min_value=2, max_value=15, value=5, step=1
        )
        
        dividend_threshold = st.sidebar.slider(
            "配当利回り閾値 (%)" if st.session_state.language == 'ja' else "Dividend Yield Threshold (%)",
            min_value=1.0, max_value=8.0, value=3.0, step=0.5
        )
        
        # Convert to multiplier for backward compatibility with analyzer
        dividend_multiplier = 1.2
        
        # Growth metrics
        sales_growth_threshold = st.sidebar.slider(
            "売上成長率閾値 (%)" if st.session_state.language == 'ja' else "Sales Growth Threshold (%)",
            min_value=0, max_value=20, value=5, step=1
        )
        
        eps_growth_threshold = st.sidebar.slider(
            "EPS成長率閾値 (%)" if st.session_state.language == 'ja' else "EPS Growth Threshold (%)",
            min_value=0, max_value=25, value=10, step=1
        )
        
        # Profitability metrics
        operating_margin_threshold = st.sidebar.slider(
            "営業利益率閾値 (%)" if st.session_state.language == 'ja' else "Operating Margin Threshold (%)",
            min_value=5, max_value=30, value=10, step=1
        )
        
        # Financial health metrics
        equity_ratio_threshold = st.sidebar.slider(
            "自己資本比率閾値 (%)" if st.session_state.language == 'ja' else "Equity Ratio Threshold (%)",
            min_value=20, max_value=80, value=40, step=5
        )
        
        payout_ratio_threshold = st.sidebar.slider(
            "配当性向閾値 (%)" if st.session_state.language == 'ja' else "Payout Ratio Threshold (%)",
            min_value=10, max_value=80, value=30, step=5
        )
    
    # Stock discovery section with market selection
    st.markdown("---")
    st.subheader("📍 " + ("株式検索方法を選択" if st.session_state.language == 'ja' else "Choose Stock Discovery Method"))
    
    # Market selection integrated into discovery section
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        market_options = [
            get_text('all_markets'),
            get_text('japanese_stocks'),
            get_text('us_stocks'),
            get_text('emerging_stocks')
        ]
        market = st.selectbox(
            "🌍 " + ("市場選択 / Market" if st.session_state.language == 'ja' else "Market / 市場選択"),
            market_options,
            index=0,
            help="分析したい市場を選択してください / Select the market to analyze"
        )
    
    with col2:
        # Number of stocks selection
        stock_count_options = ["20", "50", "100", "200", "任意入力 / Custom"]
        selected_count_option = st.selectbox(
            "📊 " + ("検索銘柄数" if st.session_state.language == 'ja' else "Number of Stocks"),
            stock_count_options,
            index=0,
            help="分析する銘柄数を選択してください / Select number of stocks to analyze"
        )
        
        # Handle custom input
        if selected_count_option == "任意入力 / Custom":
            stock_count = st.number_input(
                "銘柄数を入力 / Enter number",
                min_value=1,
                max_value=500,
                value=20,
                step=1
            )
        else:
            stock_count = int(selected_count_option)
    
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
    st.markdown("") # Add some spacing
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    
    with col1:
        popularity_button = st.button(
            "📈\n\n人気から\n探す" if st.session_state.language == 'ja' else "📈\n\nPopular\nRanking",
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
    
    # Handle action button clicks with auto-execution
    selected_method = handle_action_buttons(popularity_button, dividend_button, theme_button, random_button, market, stock_count)
    
    # Auto-execute data fetching when action button is pressed
    if selected_method:
        symbols = selected_method
        st.success(f"✅ {len(symbols)}銘柄を自動取得中... / Auto-fetching {len(symbols)} stocks...")
        
        # Automatically trigger data update
        with st.spinner("データを取得中... / Fetching data..."):
            update_stock_data(symbols, per_threshold, pbr_threshold, roe_threshold, dividend_multiplier)
        
    else:
        # Show message to select an action button
        st.info("上記のアクションボタンから検索方法を選択してください。\nPlease select a discovery method from the action buttons above.")
        symbols = []
    
    # Enhanced API test button showing failover status
    if st.sidebar.button("🔧 " + ("APIステータス" if st.session_state.language == 'ja' else "API Status"), type="secondary"):
        st.sidebar.write("📊 データソースの接続状況を確認中... / Checking data source connections...")
        
        # Test Yahoo Finance API
        st.sidebar.markdown("**Yahoo Finance API:**")
        test_symbols = ["7203.T", "AAPL"]
        yahoo_status = True
        for symbol in test_symbols:
            try:
                import yfinance as yf
                ticker = yf.Ticker(symbol)
                info = ticker.info
                if info and info.get('regularMarketPrice'):
                    st.sidebar.success(f"✅ {symbol}: 正常 / Normal")
                else:
                    st.sidebar.error(f"❌ {symbol}: データ取得失敗 / Data fetch failed")
                    yahoo_status = False
            except Exception as e:
                st.sidebar.error(f"❌ {symbol}: エラー / Error - {str(e)[:50]}...")
                yahoo_status = False
        
        # Overall Yahoo Finance status
        if yahoo_status:
            st.sidebar.success("🟢 Yahoo Finance API: 正常動作 / Working Normally")
        else:
            st.sidebar.error("🔴 Yahoo Finance API: 問題あり / Issues Detected")
        
        # Test Finnhub API if available
        if hasattr(st.session_state, 'analyzer') and hasattr(st.session_state.analyzer, 'data_fetcher'):
            st.sidebar.markdown("**Finnhub API:**")
            try:
                # Check if Finnhub is configured
                import os
                if os.getenv('FINNHUB_API_KEY'):
                    st.sidebar.success("✅ Finnhub API Key: 設定済み / Configured")
                    st.sidebar.info("🔄 Finnhub API: フェイルオーバー対応 / Failover Ready")
                else:
                    st.sidebar.warning("⚠️ Finnhub API Key: 未設定 / Not configured")
            except Exception as e:
                st.sidebar.error(f"❌ Finnhub: {str(e)[:50]}...")
        
        # Show analyzer status
        st.sidebar.markdown("**アナライザー状態 / Analyzer Status:**")
        if hasattr(st.session_state, 'using_enhanced') and st.session_state.using_enhanced:
            st.sidebar.success("🔧 Enhanced Analyzer: アクティブ / Active")
            if hasattr(st.session_state.analyzer, 'get_api_status'):
                status = st.session_state.analyzer.get_api_status()
                for api, stat in status.items():
                    if stat == "healthy":
                        st.sidebar.success(f"✅ {api}: 正常 / Healthy")
                    else:
                        st.sidebar.error(f"❌ {api}: {stat}")
        else:
            st.sidebar.info("🔧 Basic Analyzer: アクティブ / Active")
        
        # Show cache status
        if hasattr(st.session_state, 'stock_data') and st.session_state.stock_data:
            cache_count = len(st.session_state.stock_data)
            st.sidebar.info(f"💾 キャッシュ済み銘柄数: {cache_count} / Cached stocks: {cache_count}")
    
    # Manual update button for additional control (optional)
    if symbols and not selected_method:  # Only show manual button if no auto-execution happened
        # Show analyzer status
        st.info("🔧 Basic Analyzer使用中: 安定性重視でシンプル処理 / Using Basic Analyzer with stability focus")
        
        # Show cache status if available  
        if hasattr(st.session_state.analyzer, 'data_fetcher') and hasattr(st.session_state.analyzer.data_fetcher, 'cache'):
            cache_size = len(st.session_state.analyzer.data_fetcher.cache)
            if cache_size > 0:
                st.success(f"📊 キャッシュ済み: {cache_size} 銘柄 / Cached: {cache_size} stocks")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(get_text('update_data'), type="primary"):
                update_stock_data(symbols, per_threshold, pbr_threshold, roe_threshold, dividend_multiplier)
                    
        with col2:
            if st.button("🗑️ キャッシュクリア / Clear Cache", type="secondary"):
                if hasattr(st.session_state.analyzer, 'clear_cache'):
                    st.session_state.analyzer.clear_cache()
                    st.success("キャッシュをクリアしました / Cache cleared")
                else:
                    st.info("キャッシュ機能は利用できません / Cache not available")
    
    # Additional controls for cached data
    elif symbols:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 再取得 / Re-fetch", type="secondary"):
                update_stock_data(symbols, per_threshold, pbr_threshold, roe_threshold, dividend_multiplier)
        with col2:
            if st.button("🗑️ キャッシュクリア / Clear Cache", type="secondary"):
                if hasattr(st.session_state.analyzer, 'clear_cache'):
                    st.session_state.analyzer.clear_cache()
                    st.success("キャッシュをクリアしました / Cache cleared")
                else:
                    st.info("キャッシュ機能は利用できません / Cache not available")
        
        # Disable auto-update to prevent server overload issues
        # Auto-update disabled due to server stability concerns
        
        # Clean interface without test buttons
        
        # Display results cleanly
        if st.session_state.stock_data:
            valid_data = {k: v for k, v in st.session_state.stock_data.items() if v is not None}
            
            if valid_data:
                display_results(view_mode, market)
            else:
                st.warning("有効なデータが取得できませんでした。別の銘柄をお試しください。/ No valid data found. Please try different stocks.")
        else:
            st.info("データを取得するには「データ更新」ボタンをクリックしてください。\nClick 'Update Data' button to fetch stock data.")
    else:
        # Show placeholder when no action is selected
        st.markdown("---")
        st.markdown("**" + ("アクションボタンを選択すると、ここに分析結果が表示されます。" if st.session_state.language == 'ja' else "Select an action button above to see analysis results here.") + "**")

def update_stock_data(symbols, per_threshold, pbr_threshold, roe_threshold, dividend_multiplier):
    """Update stock data and scores with batch processing to prevent server overload"""
    progress_bar = None
    status_text = None
    
    try:
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Clean UI - removed debug output
        st.info(f"📊 {len(symbols)} 銘柄の分析を開始 / Starting analysis of {len(symbols)} stocks")
        status_text.text(f"処理開始: {', '.join(symbols[:5])}" + ("..." if len(symbols) > 5 else ""))
        
        # Update scoring criteria with method compatibility
        status_text.text("設定を更新中... / Updating criteria...")
        try:
            # Check which method is available and use appropriate one
            if hasattr(st.session_state.analyzer, 'update_scoring_criteria'):
                # Enhanced Analyzer method
                st.session_state.analyzer.update_scoring_criteria(
                    per_threshold=per_threshold,
                    pbr_threshold=pbr_threshold,
                    roe_threshold=roe_threshold,
                    dividend_multiplier=dividend_multiplier
                )

            elif hasattr(st.session_state.analyzer, 'update_criteria'):
                # Basic Analyzer method
                st.session_state.analyzer.update_criteria(
                    per_threshold=per_threshold,
                    pbr_threshold=pbr_threshold,
                    roe_threshold=roe_threshold,
                    dividend_multiplier=dividend_multiplier
                )

            else:
                st.warning("⚠️ スコア更新メソッドが見つかりません / Score update method not found")
        except Exception as criteria_error:
            st.error(f"❌ スコア設定エラー / Criteria error: {str(criteria_error)}")
            st.write(f"Available methods: {[m for m in dir(st.session_state.analyzer) if 'update' in m.lower()]}")
            return
        
        progress_bar.progress(5)
        
        # Intelligent batch processing with cache optimization
        total_symbols = len(symbols)
        all_results = {}
        

        
        # Use Enhanced analyzer if properly initialized, fallback to Basic
        if not hasattr(st.session_state.analyzer, 'analyze_stocks'):
            st.error("Analyzer missing analyze_stocks method - reinitializing with Enhanced")
            try:
                from enhanced_stock_analyzer import EnhancedStockAnalyzer
                st.session_state.analyzer = EnhancedStockAnalyzer()
                st.session_state.using_enhanced = True
                st.success("✅ Enhanced Analyzer再初期化成功")
            except Exception as e:
                st.warning(f"Enhanced Analyzer initialization failed: {e}")
                st.session_state.analyzer = StockAnalyzer()
                st.session_state.using_enhanced = False
        
        try:
            analyzer_type = "Enhanced" if st.session_state.using_enhanced else "Basic"
            status_text.text(f"{analyzer_type} Analyzer でバッチ処理開始... / Starting {analyzer_type} batch processing...")
            
            # Use the analyzer's batch processing with error catching
            status_text.text("データ分析中... / Analyzing data...")
            all_results = st.session_state.analyzer.analyze_stocks(symbols)
            
            # Apply relative scoring to all results
            for symbol, result in all_results.items():
                if result and result is not None:
                    # Use relative scoring engine for consistent evaluation
                    current_mode = st.session_state.get('user_mode', '中級者')
                    relative_score = st.session_state.relative_scorer.calculate_score(
                        result, 
                        mode='beginner' if current_mode == '👶 初級者' else 'intermediate'
                    )
                    
                    # Update result with relative scoring data
                    result.update({
                        'relative_score': relative_score,
                        'total_score': relative_score['total_score'],
                        'recommendation': relative_score['recommendation'],
                        'rank': relative_score['rank'],
                        'color': relative_score['color']
                    })
            
            # Simple progress feedback without debug details
            
            # Calculate estimated time (2-3 seconds per stock on average)
            estimated_time_per_stock = 2.5
            total_estimated_time = len(symbols) * estimated_time_per_stock
            start_time = time.time()
            
            # Update progress with time estimation
            for idx in range(total_symbols):
                current_progress = 5 + (85 * (idx + 1) // total_symbols)
                progress_bar.progress(current_progress)
                
                # Calculate remaining time
                elapsed_time = time.time() - start_time
                if idx > 0:
                    avg_time_per_stock = elapsed_time / idx
                    remaining_stocks = total_symbols - idx
                    estimated_remaining = remaining_stocks * avg_time_per_stock
                else:
                    estimated_remaining = total_estimated_time
                
                # Format time display
                if estimated_remaining > 60:
                    time_display = f"{estimated_remaining/60:.1f}分"
                else:
                    time_display = f"{estimated_remaining:.0f}秒"
                
                status_text.text(f"進捗 {current_progress}% | 残り約{time_display} | {idx + 1}/{total_symbols}銘柄")
                time.sleep(0.1)
            
        except Exception as batch_error:
            st.error(f"❌ バッチ処理エラー / Batch processing error: {str(batch_error)}")
            st.write(f"Error details: {type(batch_error).__name__}: {str(batch_error)}")
            import traceback
            st.text(traceback.format_exc())
            
            # Fallback to individual processing
            st.info("🔄 個別処理にフォールバック / Falling back to individual processing")
            all_results = {}
            
            for idx, symbol in enumerate(symbols):
                status_text.text(f"個別処理 {idx + 1}/{total_symbols}: {symbol}")
                st.write(f"処理中: {symbol}")
                
                try:
                    # Try single stock analysis first
                    single_result = st.session_state.analyzer.analyze_stocks([symbol])
                    if single_result and symbol in single_result and single_result[symbol]:
                        all_results[symbol] = single_result[symbol]
                        st.write(f"✅ {symbol}: 成功")
                    else:
                        # Try direct data fetcher as backup
                        if hasattr(st.session_state.analyzer, 'data_fetcher'):
                            data = st.session_state.analyzer.data_fetcher.get_stock_info(symbol)
                            if data:
                                all_results[symbol] = {
                                    **data,
                                    'total_score': 50,
                                    'assessment': 'Basic Analysis'
                                }
                                st.write(f"✅ {symbol}: データフェッチャーで成功")
                            else:
                                all_results[symbol] = None
                                st.write(f"❌ {symbol}: データなし")
                        else:
                            all_results[symbol] = None
                            st.write(f"❌ {symbol}: データフェッチャーなし")
                    
                    progress = 5 + (85 * (idx + 1) // total_symbols)
                    progress_bar.progress(progress)
                    
                except Exception as stock_error:
                    st.error(f"❌ {symbol} 個別処理エラー: {str(stock_error)}")
                    all_results[symbol] = None
        
        progress_bar.progress(90)
        
        # Store results
        st.session_state.stock_data = all_results
        st.session_state.last_update = datetime.now()
        progress_bar.progress(100)
        
        # Show summary
        valid_results = [r for r in all_results.values() if r and 'total_score' in r]
        status_text.text(f"分析完了: {len(valid_results)}/{total_symbols} 銘柄 / Analysis complete: {len(valid_results)}/{total_symbols} stocks")
        
        # Clean status display
        if len(valid_results) == 0:
            st.warning("データの取得に失敗しました。しばらく時間を置いてから再試行してください。/ Data fetch failed. Please try again later.")
        else:
            st.success(f"✅ {len(valid_results)} 銘柄のデータを取得しました / Successfully fetched {len(valid_results)} stocks")
        
        # Show notification for high-scoring stocks
        high_scoring = [stock for stock in all_results if all_results.get(stock) and all_results[stock].get('total_score', 0) >= 80]
        if high_scoring:
            st.success(f"🚀 高スコア銘柄発見! / High-scoring stocks found: {len(high_scoring)} stocks")
        
        # Show warning if many stocks failed to process
        failed_count = total_symbols - len(valid_results)
        if failed_count > total_symbols * 0.3:  # More than 30% failed
            st.warning(f"⚠️ {failed_count} 銘柄のデータ取得に失敗しました。サーバー負荷が原因の可能性があります。/ {failed_count} stocks failed to process. This may be due to server load.")
            
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
    """Display analysis results based on user mode"""
    data = st.session_state.stock_data
    
    if not data:
        st.warning("表示するデータがありません / No data to display")
        return
    
    # Convert to DataFrame for easier manipulation - columns depend on user mode
    df_data = []
    for symbol, info in data.items():
        if info and 'total_score' in info:
            # Get appropriate company name based on language setting
            company_name = info.get('company_name', symbol)
            if st.session_state.language == 'ja' and symbol.endswith('.T'):
                company_name = get_japanese_company_name(symbol, company_name)
            
            # Get relative score data
            relative_data = info.get('relative_score', {})
            rank = info.get('rank', 'N/A')
            
            if st.session_state.get('user_mode', '中級者') == '👶 初級者':
                # Simplified data for beginners (2 metrics only)
                df_data.append({
                    'Symbol': symbol,
                    'Company': company_name,
                    'Score': info.get('total_score', 0),
                    'Rank': rank,
                    'Recommendation': info.get('recommendation', 'N/A'),
                    'PER': info.get('pe_ratio', 'N/A'),
                    'Dividend Yield': format_percentage(info.get('dividend_yield', 'N/A')),
                    'Current Price': info.get('current_price', 'N/A')
                })
            else:
                # Full data for intermediate users with all 10 metrics
                df_data.append({
                    'Symbol': symbol,
                    'Company': company_name,
                    'Score': info.get('total_score', 0),
                    'Rank': rank,
                    'Recommendation': info.get('recommendation', 'N/A'),
                    'Current Price': info.get('current_price', 'N/A'),
                    'PER': info.get('pe_ratio', 'N/A'),
                    'PBR': info.get('pb_ratio', 'N/A'),
                    'ROE': format_percentage(info.get('roe', 'N/A')),
                    'ROA': format_percentage(info.get('roa', 'N/A')),
                    'Dividend Yield': format_percentage(info.get('dividend_yield', 'N/A')),
                    'Revenue Growth': format_percentage(info.get('revenue_growth', 'N/A')),
                    'EPS Growth': format_percentage(info.get('eps_growth', 'N/A')),
                    'Operating Margin': format_percentage(info.get('operating_margin', 'N/A')),
                    'Equity Ratio': format_percentage(info.get('equity_ratio', 'N/A')),
                    'Payout Ratio': format_percentage(info.get('payout_ratio', 'N/A'))
                })
    
    if not df_data:
        st.warning("有効なデータがありません / No valid data available")
        return
    
    df = pd.DataFrame(df_data)
    df = df.sort_values('Score', ascending=False)
    
    # Show investment decision results first
    st.subheader("💡 " + ("投資判定結果" if st.session_state.language == 'ja' else "Investment Decision Results"))
    
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
    
    # Simple recommendation summary
    if st.session_state.user_mode == 'beginner':
        recommendation_counts = {
            "🟢 おすすめ" if st.session_state.language == 'ja' else "🟢 Recommended": len(df[df['Score'] >= 80]),
            "🟡 様子見" if st.session_state.language == 'ja' else "🟡 Wait & See": len(df[(df['Score'] >= 60) & (df['Score'] < 80)]),
            "🔴 見送り" if st.session_state.language == 'ja' else "🔴 Skip": len(df[df['Score'] < 60])
        }
    else:
        recommendation_counts = {
            "🚀 強い買い" if st.session_state.language == 'ja' else "🚀 Strong Buy": len(df[df['Score'] >= 80]),
            "👀 ウォッチ" if st.session_state.language == 'ja' else "👀 Watch": len(df[(df['Score'] >= 60) & (df['Score'] < 80)]),
            "➖ 中立" if st.session_state.language == 'ja' else "➖ Neutral": len(df[(df['Score'] >= 40) & (df['Score'] < 60)]),
            "❌ 非推奨" if st.session_state.language == 'ja' else "❌ Not Recommended": len(df[df['Score'] < 40])
        }
    
    # Display as simple text summary instead of large chart
    st.markdown("**推奨レベル別銘柄数:**" if st.session_state.language == 'ja' else "**Stock Count by Recommendation Level:**")
    rec_cols = st.columns(len(recommendation_counts))
    for i, (level, count) in enumerate(recommendation_counts.items()):
        with rec_cols[i]:
            st.metric(level, count, label_visibility="visible")
    
    # Featured Recommendations Section
    st.subheader("🌟 " + ("推奨銘柄ピックアップ" if st.session_state.language == 'ja' else "Featured Recommendations"))
    
    # Get top 3 recommendations
    top_recommendations = df.head(3)
    
    if len(top_recommendations) > 0:
        # Display only the columns we need (no empty boxes)
        num_stocks = min(len(top_recommendations), 3)
        cols = st.columns(num_stocks)
        
        for col_idx in range(num_stocks):
            stock = top_recommendations.iloc[col_idx]
            
            with cols[col_idx]:
                # Create card-like container
                with st.container():
                    # Remove the bordered container - use simple layout instead
                    
                    # Stock header
                    st.markdown(f"**{stock['Symbol']}**")
                    st.markdown(f"<div style='font-size: 0.9em; color: #666;'>{stock['Company']}</div>", unsafe_allow_html=True)
                    
                    # Circular score
                    circular_svg = create_circular_score(stock['Score'], 100)
                    st.markdown(circular_svg, unsafe_allow_html=True)
                    
                    # Price and recommendation
                    st.markdown(f"**{stock['Current Price']}**")
                    # Display rank and recommendation with color
                    rank = data[stock['Symbol']].get('rank', 'N/A') if stock['Symbol'] in data else 'N/A'
                    st.markdown(f"<div style='font-size: 1.2em; font-weight: bold; color: black;'>ランク {rank}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size: 0.9em; font-weight: bold;'>{stock['Recommendation']}</div>", unsafe_allow_html=True)
                    
                    # Stock analysis explanation - only show in expander
                    analysis = generate_stock_analysis(stock)
                    with st.expander("詳細分析を見る" if st.session_state.language == 'ja' else "See Detailed Analysis"):
                        st.write(analysis)

    # Now show the full stock list below featured recommendations
    st.markdown("---")
    st.subheader("📊 " + ("銘柄一覧" if st.session_state.language == 'ja' else "Stock List"))
    
    # Results table - show after featured recommendations
    if view_mode == get_text('simple_view'):
        if st.session_state.get('user_mode', '初級者') == '中級者':
            display_intermediate_view(df)
        else:
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

def format_percentage(value):
    """Format percentage values correctly"""
    if value == 'N/A' or value is None:
        return 'N/A'
    try:
        # Convert to float
        num_val = float(value)
        # If value is greater than 1, assume it's already a percentage
        if num_val > 1:
            return f"{num_val:.1f}%"
        else:
            # If value is less than 1, convert decimal to percentage
            return f"{num_val * 100:.1f}%"
    except (ValueError, TypeError):
        return 'N/A'

def display_simple_view(df):
    """Display simple table view of results"""
    st.subheader("銘柄一覧" if st.session_state.language == 'ja' else "Stock List")
    
    # Add market type column
    df_with_market = df.copy()
    df_with_market['Market'] = df_with_market['Symbol'].apply(get_market_type)
    
    # Enhanced table with better formatting and styling - only use columns that exist
    available_columns = ['Symbol', 'Market', 'Company', 'Score', 'Recommendation', 'Current Price']
    # All 10 financial metrics now available
    optional_columns = ['PER', 'PBR', 'ROE', 'ROA', 'Dividend Yield', 'Revenue Growth', 'EPS Growth', 'Operating Margin', 'Equity Ratio', 'Payout Ratio']
    
    # Add only the columns that exist in the DataFrame
    for col in optional_columns:
        if col in df_with_market.columns:
            available_columns.append(col)
    
    table_df = df_with_market[available_columns].copy()
    
    # Format numerical columns - only format columns that exist
    numerical_cols = ['PER', 'PBR', 'ROE', 'ROA', 'Dividend Yield', 'Revenue Growth', 'EPS Growth', 'Operating Margin', 'Equity Ratio', 'Payout Ratio']
    for col in numerical_cols:
        if col in table_df.columns:
            table_df[col] = pd.to_numeric(table_df[col], errors='coerce')
            if col in ['ROE', 'ROA', 'Dividend Yield', 'Revenue Growth', 'EPS Growth', 'Operating Margin', 'Equity Ratio', 'Payout Ratio']:
                # Apply proper percentage formatting that handles both decimal and percentage values
                table_df[col] = table_df[col].apply(
                    lambda x: f"{x * 100:.1f}%" if pd.notna(x) and x <= 1.0 else f"{x:.1f}%" if pd.notna(x) else "N/A"
                )
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
            "Market": st.column_config.TextColumn(
                "Market" if st.session_state.language == 'en' else "市場",
                width="small",
            ),
            "Company": st.column_config.TextColumn(
                "Company" if st.session_state.language == 'en' else "企業名",
                width="medium",
            ),
            "PER": st.column_config.TextColumn(
                "PER" if st.session_state.language == 'en' else "PER",
                width="small",
            ),
            "PBR": st.column_config.TextColumn(
                "PBR" if st.session_state.language == 'en' else "PBR", 
                width="small",
            ),
            "ROE": st.column_config.TextColumn(
                "ROE" if st.session_state.language == 'en' else "ROE",
                width="small",
            ),
            "ROA": st.column_config.TextColumn(
                "ROA" if st.session_state.language == 'en' else "ROA",
                width="small",
            ),
            "Dividend Yield": st.column_config.TextColumn(
                "Dividend Yield" if st.session_state.language == 'en' else "配当利回り",
                width="small",
            ),
            "Revenue Growth": st.column_config.TextColumn(
                "Revenue Growth" if st.session_state.language == 'en' else "売上高成長率",
                width="small",
            ),
            "EPS Growth": st.column_config.TextColumn(
                "EPS Growth" if st.session_state.language == 'en' else "EPS成長率",
                width="small",
            ),
            "Operating Margin": st.column_config.TextColumn(
                "Operating Margin" if st.session_state.language == 'en' else "営業利益率",
                width="small",
            ),
            "Equity Ratio": st.column_config.TextColumn(
                "Equity Ratio" if st.session_state.language == 'en' else "自己資本比率",
                width="small",
            ),
            "Payout Ratio": st.column_config.TextColumn(
                "Payout Ratio" if st.session_state.language == 'en' else "配当性向",
                width="small",
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

def get_metric_color(metric_name, value, score_contribution):
    """Get color for metric based on whether it contributes positively to the score"""
    if pd.isna(value) or value == "N/A":
        return "color: gray;"
    
    # Determine if metric contributes positively or negatively to score
    # Higher is better: ROE, ROA, Dividend Yield, Revenue Growth, Free Cash Flow Yield
    # Lower is better: PER, PBR, Debt to Equity, Current Ratio (but not too low)
    
    higher_is_better = ['ROE', 'ROA', 'Dividend Yield', 'Revenue Growth', 'Free Cash Flow Yield', 'Operating Margin']
    lower_is_better = ['PER', 'PBR', 'Debt to Equity']
    
    if score_contribution > 50:  # Positive contribution
        return "color: green; font-weight: bold;"
    elif score_contribution < 50:  # Negative contribution  
        return "color: red; font-weight: bold;"
    else:  # Neutral
        return "color: orange; font-weight: bold;"

def display_intermediate_view(df):
    """Display intermediate mode view with all 10 metrics and color coding"""
    st.subheader("銘柄一覧（中級者モード）" if st.session_state.language == 'ja' else "Stock List (Intermediate Mode)")
    
    # Add market type column
    df_with_market = df.copy()
    df_with_market['Market'] = df_with_market['Symbol'].apply(get_market_type)
    
    # All 10 metrics for intermediate mode - ensure all are available
    all_columns = ['Symbol', 'Market', 'Company', 'Score', 'Recommendation', 'Current Price', 
                  'PER', 'PBR', 'ROE', 'ROA', 'Dividend Yield', 'Revenue Growth', 
                  'EPS Growth', 'Operating Margin', 'Equity Ratio', 'Payout Ratio']
    
    # Add missing columns with N/A values to ensure all 10 metrics are displayed
    for col in all_columns:
        if col not in df_with_market.columns:
            df_with_market[col] = "N/A"
    
    available_columns = all_columns
    
    table_df = df_with_market[available_columns].copy()
    
    # Format numerical columns
    numerical_cols = ['PER', 'PBR', 'ROE', 'ROA', 'Dividend Yield', 'Revenue Growth', 
                     'EPS Growth', 'Operating Margin', 'Equity Ratio', 'Payout Ratio']
    
    for col in numerical_cols:
        if col in table_df.columns:
            table_df[col] = pd.to_numeric(table_df[col], errors='coerce')
            if col in ['ROE', 'ROA', 'Dividend Yield', 'Revenue Growth', 'EPS Growth', 'Operating Margin', 'Equity Ratio', 'Payout Ratio']:
                # Apply proper percentage formatting that handles both decimal and percentage values
                table_df[col] = table_df[col].apply(
                    lambda x: f"{x * 100:.1f}%" if pd.notna(x) and x <= 1.0 else f"{x:.1f}%" if pd.notna(x) else "N/A"
                )
            else:
                table_df[col] = table_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
    
    # Color coding function with metric evaluation
    def highlight_metrics(row):
        styles = []
        for col in row.index:
            if col == 'Score':
                score = row[col]
                if score >= 80:
                    styles.append('background-color: #d4edda')
                elif score >= 60:
                    styles.append('background-color: #fff3cd')
                else:
                    styles.append('background-color: #f8d7da')
            elif col in numerical_cols and col in row.index:
                # Simple scoring logic for color coding
                try:
                    value_str = str(row[col]).replace('%', '').replace('N/A', '')
                    if value_str:
                        value = float(value_str)
                        if col == 'PER':
                            color = 'color: green; font-weight: bold;' if 10.0 <= value <= 20.0 else 'color: red; font-weight: bold;'
                        elif col == 'PBR':
                            color = 'color: green; font-weight: bold;' if 0.5 <= value <= 2.0 else 'color: red; font-weight: bold;'
                        elif col in ['ROE', 'ROA']:
                            color = 'color: green; font-weight: bold;' if value >= 15.0 else 'color: red; font-weight: bold;'
                        elif col == 'Dividend Yield':
                            color = 'color: green; font-weight: bold;' if value >= 3.0 else 'color: red; font-weight: bold;'
                        elif col == 'Revenue Growth':
                            color = 'color: green; font-weight: bold;' if value >= 5.0 else 'color: red; font-weight: bold;'
                        elif col == 'EPS Growth':
                            color = 'color: green; font-weight: bold;' if value >= 10.0 else 'color: red; font-weight: bold;'
                        elif col == 'Operating Margin':
                            color = 'color: green; font-weight: bold;' if value >= 10.0 else 'color: red; font-weight: bold;'
                        elif col == 'Equity Ratio':
                            color = 'color: green; font-weight: bold;' if value >= 40.0 else 'color: red; font-weight: bold;'
                        elif col == 'Payout Ratio':
                            color = 'color: green; font-weight: bold;' if 20.0 <= value <= 60.0 else 'color: red; font-weight: bold;'
                        else:
                            color = 'color: green; font-weight: bold;' if value > 0.0 else 'color: red; font-weight: bold;'
                        styles.append(color)
                    else:
                        styles.append('color: gray;')
                except (ValueError, TypeError):
                    styles.append('color: gray;')
            else:
                styles.append('')
        return styles
    
    # Apply styling
    styled_df = table_df.style.apply(highlight_metrics, axis=1)
    
    # Display the styled dataframe with all metrics
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
            "Market": st.column_config.TextColumn(
                "Market" if st.session_state.language == 'en' else "市場",
                width="small",
            ),
            "Company": st.column_config.TextColumn(
                "Company" if st.session_state.language == 'en' else "企業名",
                width="medium",
            ),
            "PER": st.column_config.TextColumn(
                "PER" if st.session_state.language == 'en' else "PER",
                width="small",
            ),
            "PBR": st.column_config.TextColumn(
                "PBR" if st.session_state.language == 'en' else "PBR",
                width="small",
            ),
            "ROE": st.column_config.TextColumn(
                "ROE" if st.session_state.language == 'en' else "ROE",
                width="small",
            ),
            "ROA": st.column_config.TextColumn(
                "ROA" if st.session_state.language == 'en' else "ROA",
                width="small",
            ),
            "Dividend Yield": st.column_config.TextColumn(
                "Dividend Yield" if st.session_state.language == 'en' else "配当利回り",
                width="small",
            ),
            "Revenue Growth": st.column_config.TextColumn(
                "Revenue Growth" if st.session_state.language == 'en' else "売上高成長率",
                width="small",
            ),
            "EPS Growth": st.column_config.TextColumn(
                "EPS Growth" if st.session_state.language == 'en' else "EPS成長率",
                width="small",
            ),
            "Operating Margin": st.column_config.TextColumn(
                "Operating Margin" if st.session_state.language == 'en' else "営業利益率",
                width="small",
            ),
            "Equity Ratio": st.column_config.TextColumn(
                "Equity Ratio" if st.session_state.language == 'en' else "自己資本比率",
                width="small",
            ),
            "Payout Ratio": st.column_config.TextColumn(
                "Payout Ratio" if st.session_state.language == 'en' else "配当性向",
                width="small",
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

def get_simple_recommendation(score):
    """Get simplified recommendation for beginners"""
    if score >= 80:
        return "🟢 おすすめ / Recommended" if st.session_state.language == 'ja' else "🟢 Recommended"
    elif score >= 60:
        return "🟡 様子見 / Wait & See" if st.session_state.language == 'ja' else "🟡 Wait & See"
    else:
        return "🔴 見送り / Skip" if st.session_state.language == 'ja' else "🔴 Skip"

if __name__ == "__main__":
    main()
