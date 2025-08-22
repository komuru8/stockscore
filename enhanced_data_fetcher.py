import yfinance as yf
import pandas as pd
import numpy as np
import logging
import time
import random
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests

try:
    import finnhub
    FINNHUB_AVAILABLE = True
except ImportError:
    FINNHUB_AVAILABLE = False
    finnhub = None

class EnhancedDataFetcher:
    """Enhanced data fetcher with Yahoo Finance + Finnhub failover configuration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize APIs
        self.finnhub_client = None
        self._init_finnhub()
        
        # Enhanced cache configuration
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 30 * 60  # 30 minutes
        self.priority_cache = {}  # High-priority cache for popular stocks
        self.priority_cache_duration = 60 * 60  # 1 hour for popular stocks
        
        # API status tracking
        self.yahoo_failures = 0
        self.max_yahoo_failures = 3
        self.last_yahoo_failure = None
        self.yahoo_cooldown = 3600  # 1 hour cooldown after repeated failures
        
        # Request control
        self.last_request_time = {}
        self.min_request_interval = (1, 3)  # Random 1-3 seconds between requests
        
    def _init_finnhub(self):
        """Initialize Finnhub client"""
        try:
            if not FINNHUB_AVAILABLE:
                self.logger.warning("Finnhub library not available")
                return
                
            api_key = os.getenv('FINNHUB_API_KEY')
            if api_key and finnhub:
                self.finnhub_client = finnhub.Client(api_key=api_key)
                self.logger.info("Finnhub client initialized successfully")
            else:
                self.logger.warning("FINNHUB_API_KEY not found")
        except Exception as e:
            self.logger.error(f"Failed to initialize Finnhub client: {e}")
            
    def _should_use_yahoo(self) -> bool:
        """Determine if we should try Yahoo Finance first"""
        if self.yahoo_failures < self.max_yahoo_failures:
            return True
            
        # Check if cooldown period has passed
        if self.last_yahoo_failure:
            time_since_failure = datetime.now() - self.last_yahoo_failure
            if time_since_failure.total_seconds() > self.yahoo_cooldown:
                # Reset failure count after cooldown
                self.yahoo_failures = 0
                self.last_yahoo_failure = None
                return True
                
        return False
    
    def _record_yahoo_failure(self):
        """Record a Yahoo Finance failure"""
        self.yahoo_failures += 1
        self.last_yahoo_failure = datetime.now()
        self.logger.warning(f"Yahoo Finance failure #{self.yahoo_failures}")
        
    def _wait_between_requests(self, symbol: str):
        """Implement random delay between requests"""
        now = time.time()
        if symbol in self.last_request_time:
            time_since_last = now - self.last_request_time[symbol]
            min_interval = random.uniform(*self.min_request_interval)
            if time_since_last < min_interval:
                sleep_time = min_interval - time_since_last
                time.sleep(sleep_time)
        
        self.last_request_time[symbol] = now
    
    def _is_cached(self, symbol: str) -> bool:
        """Check if symbol data is cached and not expired"""
        if symbol not in self.cache:
            return False
            
        if symbol not in self.cache_expiry:
            return False
            
        return datetime.now() < self.cache_expiry[symbol]
    
    def _get_cached_result(self, symbol: str) -> Optional[Dict]:
        """Get cached result if available and not expired"""
        if self._is_cached(symbol):
            self.logger.info(f"Using cached data for {symbol}")
            return self.cache[symbol]
        return None
    
    def _cache_result(self, symbol: str, data: Dict):
        """Cache the result with expiry time and priority handling"""
        self.cache[symbol] = data
        self.cache_expiry[symbol] = datetime.now() + timedelta(seconds=self.cache_duration)
        
        # Cache popular stocks with longer duration
        popular_symbols = ['7203.T', '6758.T', '9984.T', 'AAPL', 'MSFT', 'GOOGL', 'TSLA']
        if symbol in popular_symbols:
            self.priority_cache[symbol] = data
    
    def get_stock_data(self, symbol: str) -> Optional[Dict]:
        """Get comprehensive stock data with failover"""
        self._wait_between_requests(symbol)
        
        # Check cache first
        cached_data = self._get_cached_result(symbol)
        if cached_data:
            return cached_data
        
        # Try data sources in order
        data = None
        
        if self._should_use_yahoo():
            try:
                data = self._fetch_yahoo_data(symbol)
                if data:
                    self.logger.info(f"Successfully fetched {symbol} from Yahoo Finance")
                    self._cache_result(symbol, data)
                    return data
                else:
                    self._record_yahoo_failure()
            except Exception as e:
                self.logger.error(f"Yahoo Finance error for {symbol}: {e}")
                self._record_yahoo_failure()
        
        # Fallback to Finnhub
        if self.finnhub_client:
            try:
                data = self._fetch_finnhub_data(symbol)
                if data:
                    self.logger.info(f"Successfully fetched {symbol} from Finnhub")
                    self._cache_result(symbol, data)
                    return data
            except Exception as e:
                self.logger.error(f"Finnhub error for {symbol}: {e}")
        
        self.logger.error(f"Failed to fetch data for {symbol} from all sources")
        return None
    
    def _fetch_yahoo_data(self, symbol: str) -> Optional[Dict]:
        """Fetch comprehensive data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get basic info
            info = ticker.info
            if not info or not info.get('regularMarketPrice'):
                return None
            
            # Get historical data for chart and calculations
            hist = ticker.history(period="1y")  # Extended to 1 year for better analysis
            if hist.empty:
                return None
            
            # Get financial data
            financials = ticker.financials
            balance_sheet = ticker.balance_sheet
            
            # Extract comprehensive data
            stock_data = {
                # Basic Info
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                
                # Price Data
                'current_price': info.get('regularMarketPrice', 0),
                'previous_close': info.get('previousClose', 0),
                'volume': info.get('volume', 0),
                'market_cap': info.get('marketCap', 0),
                
                # Fundamental Metrics
                'pe_ratio': info.get('trailingPE', None),
                'pb_ratio': info.get('priceToBook', None),
                'roe': info.get('returnOnEquity', None),
                'roa': info.get('returnOnAssets', None),
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                'dividend_rate': info.get('dividendRate', 0),
                'payout_ratio': info.get('payoutRatio', None),
                
                # Growth Metrics
                'earnings_growth': info.get('earningsGrowth', None),
                'revenue_growth': info.get('revenueGrowth', None),
                'eps': info.get('trailingEps', None),
                
                # Profitability
                'profit_margins': info.get('profitMargins', None),
                'operating_margins': info.get('operatingMargins', None),
                'gross_margins': info.get('grossMargins', None),
                
                # Financial Strength
                'debt_to_equity': info.get('debtToEquity', None),
                'current_ratio': info.get('currentRatio', None),
                'book_value': info.get('bookValue', None),
                
                # Historical Data for Charts
                'price_history': hist['Close'].tolist()[-252:] if len(hist) >= 252 else hist['Close'].tolist(),
                'volume_history': hist['Volume'].tolist()[-252:] if len(hist) >= 252 else hist['Volume'].tolist(),
                'dates': [d.strftime('%Y-%m-%d') for d in hist.index[-252:]] if len(hist) >= 252 else [d.strftime('%Y-%m-%d') for d in hist.index],
                
                # Data source
                'data_source': 'Yahoo Finance',
                'last_updated': datetime.now().isoformat()
            }
            
            return stock_data
            
        except Exception as e:
            self.logger.error(f"Error fetching Yahoo data for {symbol}: {e}")
            return None
    
    def _fetch_finnhub_data(self, symbol: str) -> Optional[Dict]:
        """Fetch data from Finnhub API"""
        try:
            # Convert symbol format for Finnhub (remove .T for Japanese stocks)
            finnhub_symbol = symbol.replace('.T', '') if symbol.endswith('.T') else symbol
            
            # Get basic quote
            if not self.finnhub_client:
                return None
                
            quote = self.finnhub_client.quote(finnhub_symbol)
            if not quote or quote.get('c') == 0:  # 'c' is current price
                return None
            
            # Get company profile
            profile = self.finnhub_client.company_profile2(symbol=finnhub_symbol)
            
            # Get basic financial metrics
            metrics = self.finnhub_client.company_basic_financials(finnhub_symbol, 'all')
            
            # Extract data
            stock_data = {
                # Basic Info
                'symbol': symbol,
                'company_name': profile.get('name', symbol) if profile else symbol,
                'sector': profile.get('finnhubIndustry', 'Unknown') if profile else 'Unknown',
                'industry': profile.get('finnhubIndustry', 'Unknown') if profile else 'Unknown',
                
                # Price Data
                'current_price': quote.get('c', 0),
                'previous_close': quote.get('pc', 0),
                'volume': 0,  # Not available in basic quote
                'market_cap': profile.get('marketCapitalization', 0) * 1000000 if profile and profile.get('marketCapitalization') else 0,
                
                # Fundamental Metrics (from metrics if available)
                'pe_ratio': metrics.get('metric', {}).get('peBasicExclExtraTTM') if metrics else None,
                'pb_ratio': metrics.get('metric', {}).get('pbAnnual') if metrics else None,
                'roe': metrics.get('metric', {}).get('roeRfy') if metrics else None,
                'roa': metrics.get('metric', {}).get('roaRfy') if metrics else None,
                'dividend_yield': metrics.get('metric', {}).get('dividendYieldIndicatedAnnual') if metrics else 0,
                
                # Limited data from Finnhub free tier
                'eps': metrics.get('metric', {}).get('epsExclExtraItemsTTM') if metrics else None,
                'profit_margins': metrics.get('metric', {}).get('netProfitMarginTTM') if metrics else None,
                
                # Historical data placeholder (would need separate API calls)
                'price_history': [],
                'volume_history': [],
                'dates': [],
                
                # Data source
                'data_source': 'Finnhub',
                'last_updated': datetime.now().isoformat()
            }
            
            return stock_data
            
        except Exception as e:
            self.logger.error(f"Error fetching Finnhub data for {symbol}: {e}")
            return None
    
    def get_multiple_stocks(self, symbols: List[str]) -> Dict[str, Optional[Dict]]:
        """Get data for multiple stocks with intelligent caching and request control"""
        results = {}
        cache_hits = 0
        api_requests = 0
        
        self.logger.info(f"Processing {len(symbols)} symbols with cache optimization")
        
        # Process each symbol with cache-first approach
        for i, symbol in enumerate(symbols):
            try:
                # Check cache first
                cached_data = self._get_cached_result(symbol)
                if cached_data:
                    results[symbol] = cached_data
                    cache_hits += 1
                    self.logger.info(f"Cache hit for {symbol} ({i+1}/{len(symbols)})")
                    continue
                
                # Make API request for uncached data
                self.logger.info(f"API request for {symbol} ({i+1}/{len(symbols)})")
                stock_data = self.get_stock_data(symbol)
                results[symbol] = stock_data
                api_requests += 1
                
                # Intelligent delay: longer for API requests, shorter for cache hits
                if i < len(symbols) - 1:
                    if stock_data:  # Successful API request
                        delay = random.uniform(1.5, 3.0)  # 1.5-3 seconds for API calls
                    else:  # Failed request - shorter delay
                        delay = random.uniform(0.5, 1.0)  # 0.5-1 second for failures
                    
                    time.sleep(delay)
                    
            except Exception as e:
                self.logger.error(f"Error processing {symbol}: {e}")
                results[symbol] = None
        
        # Log comprehensive summary
        successful = len([r for r in results.values() if r is not None])
        self.logger.info(f"Batch complete: {successful}/{len(symbols)} successful, {cache_hits} cache hits, {api_requests} API requests")
        
        return results
    
    def clear_cache(self):
        """Clear the data cache"""
        self.cache.clear()
        self.cache_expiry.clear()
        self.logger.info("Cache cleared")
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get current API status information"""
        return {
            'yahoo_failures': self.yahoo_failures,
            'yahoo_available': self._should_use_yahoo(),
            'finnhub_available': self.finnhub_client is not None,
            'cache_size': len(self.cache),
            'last_yahoo_failure': self.last_yahoo_failure.isoformat() if self.last_yahoo_failure else None
        }