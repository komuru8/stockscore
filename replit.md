# Stock Analysis Tool

## Overview

This is a Japanese stock analysis application built with Streamlit that provides fundamental analysis and scoring for stocks across multiple markets (Japanese, US, and Emerging Markets). The application fetches real-time stock data, calculates fundamental metrics like P/E ratio, P/B ratio, ROE, and dividend yield, then generates investment scores based on configurable criteria. It features a web-based interface with circular score visualizations, multilingual support (Japanese/English), data caching for performance optimization, and comprehensive risk disclaimers separated into a dedicated terms page.

## User Preferences

Preferred communication style: Simple, everyday language.
UI Preferences: Clean, simple main page with legal disclaimers moved to separate terms page. Action-oriented homepage with discovery methods (popularity, dividend yield, thematic search, random). No view mode selection - simple view only.
Visual Design: Circular score indicators for featured recommendations, table format for complete listings. Custom logo with emoji instead of SVG.
Language Support: Full Japanese/English bilingual interface with dropdown language selector. Japanese company names displayed when Japanese language selected.
Navigation: Simplified top navigation with only language selector and terms button. No page menu navigation.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **Layout**: Wide layout with expandable sidebar for configuration
- **Visualization**: Plotly Express and Plotly Graph Objects for interactive charts
- **Internationalization**: Bilingual interface (Japanese/English) for broader accessibility
- **State Management**: Streamlit session state for maintaining analyzer instances and cached data

### Backend Architecture
- **Modular Design**: Separated into distinct classes for different responsibilities
  - `StockAnalyzer`: Main orchestration class coordinating data fetching and scoring
  - `DataFetcher`: Handles all external data retrieval with built-in caching
  - `ScoringEngine`: Calculates investment scores using fundamental analysis metrics
- **Data Processing**: Pandas and NumPy for efficient data manipulation and calculations
- **Caching Strategy**: In-memory caching with 30-minute expiry to reduce API calls and improve performance
- **Logging**: Comprehensive logging system for debugging and monitoring

### Data Storage Solutions
- **Session-based Storage**: Streamlit session state for temporary data persistence
- **In-memory Caching**: Dictionary-based cache with time-based expiration
- **No Persistent Database**: Application relies on external APIs for real-time data

### Configuration Management
- **Configurable Scoring Criteria**: Adjustable thresholds for P/E ratio, P/B ratio, ROE, and dividend yield
- **Market Selection**: Support for multiple stock markets with different data sources
- **Weighted Scoring System**: Customizable weights for different fundamental metrics

## External Dependencies

### APIs and Data Sources
- **Yahoo Finance API**: Primary data source accessed through `yfinance` library for stock prices, historical data, and fundamental metrics
- **Real-time Data**: Live market data for current stock prices and trading information

### Python Libraries
- **Streamlit**: Web application framework for the user interface
- **yfinance**: Yahoo Finance API wrapper for stock data retrieval
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing for calculations
- **Plotly**: Interactive visualization library for charts and graphs

### Market Coverage
- **Japanese Stock Market**: Primary focus with Japanese language support
- **US Stock Market**: Secondary market support
- **Emerging Markets**: Additional market coverage for diversification

### Performance Considerations
- **Rate Limiting**: Built-in delays and caching to respect API rate limits
- **Error Handling**: Comprehensive error handling for network failures and invalid stock symbols
- **Cache Management**: Automatic cache expiry to balance performance with data freshness