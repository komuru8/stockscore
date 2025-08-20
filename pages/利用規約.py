import streamlit as st
import sys
import os

# Add parent directory to path to import from main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set page configuration
st.set_page_config(
    page_title="利用規約 - StockScore",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'ja'
if 'user_mode' not in st.session_state:
    st.session_state.user_mode = 'beginner'

def get_text(key, lang=None):
    """Get localized text - simplified version for terms page"""
    if lang is None:
        lang = st.session_state.language
    
    texts = {
        'user_mode_selection': {
            'ja': 'ユーザーモード',
            'en': 'User Mode'
        },
        'beginner_mode': {
            'ja': '初級者',
            'en': 'Beginner'
        },
        'intermediate_mode': {
            'ja': '中級者',
            'en': 'Intermediate'
        },
        'beginner_description': {
            'ja': 'AI推奨スコア中心、直感的な「買い/見送り」判定',
            'en': 'AI-focused scoring with intuitive buy/hold decisions'
        },
        'intermediate_description': {
            'ja': '10指標によるスクリーニング、重み付け調整可能',
            'en': '10-metric screening with customizable weightings'
        },
        'terms': {
            'ja': '利用規約',
            'en': 'Terms'
        }
    }
    
    return texts.get(key, {}).get(lang, key)

def main():
    # Add sidebar menu (same as main app)
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
    
    st.sidebar.markdown("---")
    
    # Add main menu items to sidebar with consistent spacing
    st.sidebar.markdown("### " + ("メニュー" if st.session_state.language == 'ja' else "Menu"))
    st.sidebar.markdown("""
    <style>
    .stButton > button {
        margin: 4px 0 8px 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # TOP page link
    if st.sidebar.button("🏠 TOP", use_container_width=True):
        st.switch_page("TOP.py")
    
    # Terms link (current page - styled as active/disabled)
    st.sidebar.markdown(f"""
    <div style="
        background-color: #e3f2fd; 
        padding: 8px 12px; 
        border-radius: 6px; 
        border-left: 4px solid #2196f3;
        margin: 4px 0 8px 0;
        color: #1976d2;
        font-weight: 500;
    ">
        📋 {get_text('terms')}
    </div>
    """, unsafe_allow_html=True)
    
    # API Status placeholder
    if st.sidebar.button("🔧 " + ("APIステータス" if st.session_state.language == 'ja' else "API Status"), 
                        use_container_width=True):
        st.sidebar.info("メインページでご確認ください / Please check on main page")
    
    # Cache Clear placeholder
    if st.sidebar.button("🗑️ " + ("キャッシュクリア" if st.session_state.language == 'ja' else "Clear Cache"), 
                        use_container_width=True):
        st.sidebar.info("メインページでご確認ください / Please check on main page")
    
    st.sidebar.markdown("---")
    
    # Language switcher at bottom of sidebar
    current_lang = "🌐 English" if st.session_state.language == 'ja' else "🌐 日本語"
    if st.sidebar.button(current_lang, key="lang_toggle", help="Switch Language / 言語切り替え", 
                        use_container_width=True):
        st.session_state.language = 'en' if st.session_state.language == 'ja' else 'ja'
        st.rerun()

    st.title("📋 利用規約・免責事項 / Terms of Service & Disclaimer")
    
    st.markdown("---")
    
    # Investment Disclaimer Section
    st.header("⚠️ 投資に関する重要な注意事項 / Important Investment Disclaimer")
    
    st.markdown("""
    ### 日本語版
    
    **免責事項**
    
    1. **情報の性質について**
       - 本アプリケーションで提供される情報は参考情報のみであり、投資助言ではありません
       - 投資判断は必ずご自身の責任で行ってください
       - 投資にはリスクが伴い、元本が保証されるものではありません
    
    2. **データの正確性について**
       - 株価データや財務データは第三者のAPIから取得しており、データの正確性や完全性を保証するものではありません
       - リアルタイムではない場合があり、最大30分程度の遅延が生じる可能性があります
    
    3. **スコアリングについて**
       - 本アプリのスコアは独自のアルゴリズムに基づいており、投資の成果を保証するものではありません
       - スコアは参考程度にとどめ、必ず他の情報源も併用してください
    
    4. **責任の範囲**
       - 本アプリの利用により生じた損失については、一切の責任を負いかねます
       - 投資判断は必ずご自身で行い、リスクを十分理解した上で投資してください
    
    ---
    
    ### English Version
    
    **Disclaimer**
    
    1. **Nature of Information**
       - This application provides reference information only and is not investment advice
       - Please make investment decisions at your own risk and responsibility
       - Investing involves risks and principal is not guaranteed
    
    2. **Data Accuracy**
       - Stock prices and financial data are obtained from third-party APIs, and we do not guarantee the accuracy or completeness of the data
       - Data may not be real-time and may be delayed up to 30 minutes
    
    3. **Scoring System**
       - The scores in this app are based on proprietary algorithms and do not guarantee investment performance
       - Please use scores as reference only and always consult other information sources
    
    4. **Limitation of Liability**
       - We assume no responsibility for any losses incurred from using this application
       - Always make your own investment decisions and fully understand the risks before investing
    """)
    
    st.markdown("---")
    
    # Terms of Service Section
    st.header("📄 利用規約 / Terms of Service")
    
    st.markdown("""
    ### 日本語版
    
    **第1条（利用規約の適用）**
    本利用規約は、本サービスの利用に関して、利用者と当サービス提供者との間に適用されます。
    
    **第2条（利用登録）**
    本サービスは無料でご利用いただけます。利用者は本規約に同意することで、本サービスを利用できます。
    
    **第3条（禁止事項）**
    利用者は、本サービスの利用にあたり、以下の行為をしてはなりません：
    - システムに過度な負荷をかける行為
    - 不正アクセスやデータの改ざん
    - 第三者に迷惑をかける行為
    - その他、法令に違反する行為
    
    **第4条（サービスの中断・停止）**
    当サービス提供者は、システムメンテナンスやその他の理由により、予告なく本サービスを中断・停止する場合があります。
    
    **第5条（免責事項）**
    当サービス提供者は、本サービスの利用により利用者に生じた損害について、一切の責任を負いません。
    
    ---
    
    ### English Version
    
    **Article 1 (Application of Terms)**
    These Terms of Service apply to the use of this service between users and the service provider.
    
    **Article 2 (User Registration)**
    This service is available for free. Users can use this service by agreeing to these terms.
    
    **Article 3 (Prohibited Acts)**
    Users must not engage in the following acts when using this service:
    - Acts that place excessive load on the system
    - Unauthorized access or data tampering
    - Acts that cause trouble to third parties
    - Other acts that violate laws and regulations
    
    **Article 4 (Service Interruption/Suspension)**
    The service provider may interrupt or suspend this service without notice due to system maintenance or other reasons.
    
    **Article 5 (Disclaimer)**
    The service provider assumes no responsibility for any damages incurred by users through the use of this service.
    """)
    


if __name__ == "__main__":
    main()