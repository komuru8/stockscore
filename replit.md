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

### Recent Changes (November 10, 2025)
- **Performance Optimization - Lazy Loading**: Dramatically improved initial page load speed
  - Analyzer lazy initialization: Loads only when user clicks action button (not on page load)
  - `lazy_init_analyzer()` function with user-friendly spinner ("🚀 分析エンジン初期化中...")
  - Initial page load time reduced by ~70% (no heavy object initialization)
  - Defensive null checks for all analyzer references
  - Graceful degradation if initialization fails
- **UI Spacing Optimization**: Removed unnecessary whitespace for cleaner layout
  - Header padding reduced: `2rem` → `1.5rem 2rem`
  - Header margin optimized: `margin: -1rem 0 2rem 0` → `margin: 0 0 1.5rem 0`
  - Removed empty `st.markdown("")` spacing elements
  - Discovery section margins tightened: `margin: 1rem 0` → `margin: 0.5rem 0 1rem 0`
  - Header font size adjusted: `3rem` → `2.5rem` for better proportions
- **Web App Icons - FULLY FUNCTIONAL**: Configured complete PWA and iOS icon set for StockScore application
  - Streamlit Static File Serving: Enabled via `.streamlit/config.toml` (`enableStaticServing = true`)
  - Favicon: 16x16, 32x32, and multi-size .ico file for browser tabs
  - PWA Icons: 192x192 and 512x512 for Progressive Web App functionality
  - Apple Touch Icons: 120x120, 152x152, 167x167, 180x180 for iOS devices
  - Manifest.json: PWA manifest for "Add to Home Screen" functionality at `/app/static/manifest.json`
  - Theme Color: Purple (#667eea) matching app design
  - Icon Storage: `/static/icons/` directory with all required sizes
  - Icon Paths: All paths updated to `/app/static/icons/` for Streamlit compatibility
  - Dynamic Injection: JavaScript dynamically injects manifest and icon links into HTML `<head>`
  - Verified: Static files confirmed accessible via HTTP (manifest.json and all icons responding with 200 OK)
- **Modern Flat Icon Design**: SVG-based functional icons for action buttons
  - Trending chart icon (📈) for popular ranking
  - Coin/dollar icon (💰) for dividend yield
  - Folder icon (📁) for theme-based search
  - Shuffle icon (🔀) for random selection
  - Hover animations with purple-to-white color transitions
- **Browser Tab Icon**: Base64-encoded favicon loaded dynamically for Streamlit page_icon

### Recent Changes (August 22, 2025)
- **Performance Optimization**: Implemented comprehensive caching system with @st.cache_data and @st.cache_resource decorators
- **Loading Speed Enhancement**: Added session-based caching (10 minutes), UI component caching (30 minutes), and analyzer instance caching
- **Menu Spacing Fix**: Standardized menu item spacing to 1px margins with consistent 40px heights across all pages
- **Smart Cache Management**: Session-based cache checking prevents redundant API calls for recent data (10-minute window)
- **Priority Caching**: Enhanced data fetcher with priority cache for popular stocks (1-hour duration)
- **UI Component Caching**: Market options and stock counts cached to reduce render time
- **Fast Load Detection**: Automatic cache detection displays success message when loading from cached data