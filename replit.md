# Stock Analysis Tool

## Overview

This is a Japanese stock analysis application built with Streamlit that provides fundamental analysis and scoring for stocks across multiple markets (Japanese, US, and Emerging Markets). The application features three user modes (beginner, intermediate, advanced) to accommodate different investment experience levels. It fetches real-time stock data, calculates fundamental metrics, and generates investment scores based on configurable criteria. The app includes a web-based interface with circular score visualizations, multilingual support (Japanese/English), data caching for performance optimization, and comprehensive risk disclaimers separated into a dedicated terms page.

## User Preferences

Preferred communication style: Simple, everyday language.
UI Preferences: Clean, simple main page with legal disclaimers moved to separate terms page. Action-oriented homepage with discovery methods (popularity, dividend yield, thematic search, random). Three-tier user mode system (beginner/intermediate/advanced).
Visual Design: Circular score indicators for featured recommendations, table format for complete listings. Custom logo with emoji instead of SVG.
Language Support: Full Japanese/English bilingual interface with dropdown language selector. Japanese company names displayed when Japanese language selected.
Navigation: Simplified top navigation with only language selector and terms button. No page menu navigation.
User Modes: 👶 Beginner (simplified AI scoring), 🧑‍💼 Intermediate (10-metric analysis).
Performance Priorities: Remove stock count limitations, implement intelligent caching and random request intervals to handle server load efficiently rather than restricting functionality.

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
- **Enhanced In-memory Caching**: 30-minute cache with timestamp-based expiration to reduce API calls
- **Intelligent Request Control**: Random 1.5-3 second intervals between API requests to prevent rate limiting
- **Cache-First Processing**: Prioritizes cached data over new API requests for improved performance
- **No Persistent Database**: Application relies on external APIs for real-time data

### Configuration Management
- **Configurable Scoring Criteria**: Adjustable thresholds for P/E ratio, P/B ratio, ROE, and dividend yield
- **Market Selection**: Support for multiple stock markets with different data sources
- **Weighted Scoring System**: Customizable weights for different fundamental metrics

## Deployment Configuration

### File Structure
- **Main Application**: `TOP.py` - Contains the primary Streamlit application logic (development version)
- **Deployment Entry Point**: `app.py` - Complete copy of TOP.py for production deployments
- **Configuration**: `.streamlit/config.toml` - Server configuration for deployments

### Deployment Settings
- **Port**: 5000 (configured for Replit deployment compatibility)
- **Server Configuration**: Headless mode with CORS disabled for production
- **Entry Point**: Uses `app.py` as deployment entry point (complete application copy for 100% compatibility)
- **Deployment Fix**: August 2025 - Resolved production white screen issue by ensuring app.py contains complete application code

## External Dependencies

### APIs and Data Sources  
- **Yahoo Finance API**: Primary data source accessed through `yfinance` library for stock prices, historical data, and fundamental metrics
- **Finnhub API**: Secondary/failover data source for enhanced reliability when Yahoo Finance experiences 502 errors
- **Real-time Data**: Live market data for current stock prices and trading information
- **Failover Configuration**: Automatic switching from Yahoo Finance to Finnhub when primary source fails, with 1-hour cooldown before retry

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
- **Intelligent Caching**: 30-minute cache system eliminates redundant API calls for recently fetched stocks
- **Request Interval Control**: Random 1.5-3 second delays between API requests prevent bot detection and rate limiting
- **Failover Architecture**: Automatic Yahoo Finance → Finnhub switching when primary API fails (1-hour cooldown)
- **Batch Optimization**: Cache-first processing prioritizes local data over API requests
- **Error Handling**: Comprehensive error handling for network failures and invalid stock symbols
- **Cache Management**: Manual cache clearing option and automatic 30-minute expiry for data freshness

## Current Status (August 2025)

### System Requirements Compliance
**✅ Fully Implemented**
- Yahoo Finance + Finnhub failover configuration with 502 error detection
- 30-minute caching system with timestamp-based expiration
- Random 1.5-3 second request intervals for bot detection avoidance
- Complete fundamental analysis data collection (10+ metrics)
- Comprehensive stock data: price, volume, market cap, historical data
- Full fundamental metrics: PER, PBR, ROE, ROA, dividend yield, growth rates, margins, ratios
- **NEW**: Relative scoring system with proper score distribution and 5-tier evaluation

### Technical Implementation
- **Basic Analyzer**: StockAnalyzer with DataFetcher - Proven stable, handles all required data
- **Enhanced Analyzer**: EnhancedStockAnalyzer with EnhancedDataFetcher - Advanced features, may have integration complexity
- **Relative Scoring Engine**: New system implementing user-specified requirements:
  - Mode-based evaluation: Beginner (2 metrics x 50 points), Intermediate (10 metrics x 10 points)
  - 5-tier scoring: 非常に悪い(0点), 悪い(2点), 普通(5点), 良い(8点), 非常に良い(10点)
  - Relative comparison against baseline values with ±20%, ±10% thresholds
  - Missing data handling: "normal" score (50% of max points)
  - Visual enhancements: S/A/B/C/D ranks, color coding, progress bars with time estimation

### Recent Changes (August 20, 2025)
- **Progress Enhancement**: Added percentage display and real-time remaining time estimation for 50+ stock analysis
- **NoneType Error Resolution**: Complete type safety implementation across all comparison operations
- **Score Distribution Fix**: Eliminated uniform 100-point scores, implemented proper relative evaluation
- **Investment Recommendations**: 🚀強い買い推奨(80+), ✅買い推奨(70+), ➖中立(60+), ⚠️慎重(40+), ❌非推奨(<40)
- **UI Improvements**: Rank display with color coding, enhanced featured recommendations section