import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="利用規約 - StockScore",
    page_icon="📋",
    layout="wide"
)

def main():
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
    
    st.markdown("---")
    
    # Contact Information
    st.header("📞 お問い合わせ / Contact Information")
    
    st.markdown("""
    本サービスに関するお問い合わせは、以下までご連絡ください：
    
    For inquiries about this service, please contact:
    
    **Email**: support@stockanalysis.app (例)
    **Website**: https://stockanalysis.app (例)
    """)
    
    # Back to main page button
    st.markdown("---")
    if st.button("🏠 TOPに戻る / Back to TOP", type="primary"):
        st.switch_page("app.py")

if __name__ == "__main__":
    main()