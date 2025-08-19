import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
import os

class DataFetcher:
    """Class responsible for fetching stock data from various sources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 1800  # 30 minutes in seconds
        
    def _get_cached_result(self, symbol):
        """Get cached result if still valid"""
        if symbol in self.cache and symbol in self.cache_expiry:
            if datetime.now() < self.cache_expiry[symbol]:
                return self.cache[symbol]
            else:
                # Remove expired cache
                del self.cache[symbol]
                del self.cache_expiry[symbol]
        return None
        
    def _cache_result(self, symbol, result):
        """Cache the result with expiry time"""
        self.cache[symbol] = result
        self.cache_expiry[symbol] = datetime.now() + timedelta(seconds=self.cache_duration)
        
    def _is_cached(self, symbol):
        """Check if symbol data is cached and still valid"""
        if symbol in self.cache and symbol in self.cache_expiry:
            return datetime.now() < self.cache_expiry[symbol]
        return False
    
    def get_stock_info(self, symbol):
        """Get comprehensive stock information"""
        try:
            # Check cache first
            cached_result = self._get_cached_result(symbol)
            if cached_result:
                self.logger.info(f"Using cached data for {symbol}")
                return cached_result
            
            self.logger.info(f"Fetching fresh data for {symbol}")
            
            # Create yfinance ticker object
            ticker = yf.Ticker(symbol)
            
            # Get basic info
            info = ticker.info
            
            if not info or not info.get('regularMarketPrice'):
                self.logger.warning(f"No valid info data for {symbol}")
                return None
            
            # Get historical data for additional calculations
            hist = ticker.history(period="1y")
            
            if hist.empty:
                self.logger.warning(f"No historical data for {symbol}")
                return None
            
            # Prepare comprehensive stock data
            stock_data = self._extract_stock_data(info, hist)
            
            # Cache the result
            self.cache[symbol] = stock_data
            self.cache_expiry[symbol] = datetime.now() + timedelta(seconds=self.cache_duration)
            
            return stock_data
            
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def _extract_stock_data(self, info, hist):
        """Extract and clean stock data from yfinance response"""
        try:
            stock_data = {}
            
            # Basic company information
            stock_data['company_name'] = info.get('longName', info.get('shortName', 'Unknown'))
            stock_data['sector'] = info.get('sector', 'Unknown')
            stock_data['industry'] = info.get('industry', 'Unknown')
            stock_data['country'] = info.get('country', 'Unknown')
            
            # Price information
            stock_data['current_price'] = info.get('regularMarketPrice', info.get('currentPrice', 0))
            stock_data['previous_close'] = info.get('previousClose', 0)
            stock_data['market_cap'] = info.get('marketCap', 0)
            
            # Financial metrics - All 10 indicators
            stock_data['earnings_per_share'] = info.get('trailingEps', info.get('forwardEps', 0))
            stock_data['book_value_per_share'] = info.get('bookValue', 0)
            stock_data['return_on_equity'] = info.get('returnOnEquity', 0)
            stock_data['return_on_assets'] = info.get('returnOnAssets', 0)
            stock_data['dividend_yield'] = info.get('dividendYield', 0)
            stock_data['revenue_growth'] = info.get('revenueGrowth', 0)
            stock_data['earnings_growth'] = info.get('earningsGrowth', 0)
            stock_data['operating_margin'] = info.get('operatingMargins', 0)
            stock_data['debt_to_equity'] = info.get('debtToEquity', 0)
            stock_data['payout_ratio'] = info.get('payoutRatio', 0)
            
            # Additional financial data
            stock_data['dividend_rate'] = info.get('dividendRate', 0)
            stock_data['pe_ratio'] = info.get('trailingPE', info.get('forwardPE', 0))
            stock_data['pb_ratio'] = info.get('priceToBook', 0)
            stock_data['current_ratio'] = info.get('currentRatio', 0)
            stock_data['quick_ratio'] = info.get('quickRatio', 0)
            stock_data['profit_margins'] = info.get('profitMargins', 0)
            
            # Calculate additional metrics from historical data
            if not hist.empty:
                stock_data.update(self._calculate_historical_metrics(hist))
            
            # Clean and validate the data
            stock_data = self._clean_data(stock_data)
            
            return stock_data
            
        except Exception as e:
            self.logger.error(f"Error extracting stock data: {str(e)}")
            return None
    
    def _calculate_historical_metrics(self, hist):
        """Calculate additional metrics from historical price data"""
        try:
            metrics = {}
            
            if len(hist) < 2:
                return metrics
            
            # Price volatility (standard deviation of returns)
            returns = hist['Close'].pct_change().dropna()
            if len(returns) > 0:
                metrics['volatility'] = returns.std() * np.sqrt(252)  # Annualized
                metrics['avg_daily_return'] = returns.mean()
            
            # Price performance
            if len(hist) >= 252:  # 1 year of data
                metrics['year_return'] = (hist['Close'].iloc[-1] / hist['Close'].iloc[-252] - 1)
            
            if len(hist) >= 63:  # 3 months of data
                metrics['quarter_return'] = (hist['Close'].iloc[-1] / hist['Close'].iloc[-63] - 1)
            
            if len(hist) >= 21:  # 1 month of data
                metrics['month_return'] = (hist['Close'].iloc[-1] / hist['Close'].iloc[-21] - 1)
            
            # Trading volume metrics
            metrics['avg_volume'] = hist['Volume'].mean()
            metrics['volume_trend'] = hist['Volume'].tail(10).mean() / hist['Volume'].head(10).mean()
            
            # Price range metrics
            metrics['high_52w'] = hist['High'].max()
            metrics['low_52w'] = hist['Low'].min()
            current_price = hist['Close'].iloc[-1]
            metrics['distance_from_high'] = (current_price - metrics['high_52w']) / metrics['high_52w']
            metrics['distance_from_low'] = (current_price - metrics['low_52w']) / metrics['low_52w']
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating historical metrics: {str(e)}")
            return {}
    
    def _clean_data(self, data):
        """Clean and validate stock data"""
        try:
            cleaned_data = {}
            
            for key, value in data.items():
                # Handle None values
                if value is None:
                    cleaned_data[key] = 0
                    continue
                
                # Handle infinity and NaN values
                if isinstance(value, (int, float)):
                    if np.isnan(value) or np.isinf(value):
                        cleaned_data[key] = 0
                    else:
                        cleaned_data[key] = value
                else:
                    cleaned_data[key] = value
            
            return cleaned_data
            
        except Exception as e:
            self.logger.error(f"Error cleaning data: {str(e)}")
            return data
    

    
    def clear_cache(self):
        """Clear the data cache"""
        self.cache.clear()
        self.cache_expiry.clear()
    
    def get_multiple_stocks(self, symbols):
        """Get data for multiple stocks with improved error handling and caching"""
        try:
            results = {}
            
            # Much smaller batches to prevent server overload
            batch_size = 2  # Only 2 stocks at a time
            total_batches = (len(symbols) + batch_size - 1) // batch_size
            
            self.logger.info(f"Processing {len(symbols)} symbols in {total_batches} batches of {batch_size}")
            
            for batch_idx in range(total_batches):
                start_idx = batch_idx * batch_size
                end_idx = min(start_idx + batch_size, len(symbols))
                batch_symbols = symbols[start_idx:end_idx]
                
                self.logger.info(f"Processing batch {batch_idx + 1}/{total_batches}: {batch_symbols}")
                
                # Process each symbol in the batch
                for symbol in batch_symbols:
                    try:
                        # Check cache first before making API call
                        cached_result = self._get_cached_result(symbol)
                        if cached_result is not None:
                            self.logger.info(f"Using cached data for {symbol}")
                            results[symbol] = cached_result
                            continue
                        
                        # Fetch fresh data with retry logic
                        stock_data = self._fetch_with_retry(symbol, max_retries=2)
                        if stock_data:
                            results[symbol] = stock_data
                            self._cache_result(symbol, stock_data)
                        else:
                            results[symbol] = None
                            
                    except Exception as symbol_error:
                        self.logger.error(f"Error processing {symbol}: {str(symbol_error)}")
                        results[symbol] = None
                
                # Longer delay between batches to prevent server overload
                if batch_idx < total_batches - 1:
                    time.sleep(3.0)  # 3 second delay between batches
                    
            return results
            
        except Exception as e:
            self.logger.error(f"Error in get_multiple_stocks: {str(e)}")
            return {}
    
    def _fetch_with_retry(self, symbol, max_retries=2):
        """Fetch data with retry logic and error handling"""
        for attempt in range(max_retries + 1):
            try:
                self.logger.info(f"Fetching {symbol} (attempt {attempt + 1})")
                
                # Create yfinance ticker object
                ticker = yf.Ticker(symbol)
                
                # Get basic info with timeout
                info = ticker.info
                
                if not info or not info.get('regularMarketPrice'):
                    self.logger.warning(f"No valid info data for {symbol}")
                    if attempt < max_retries:
                        time.sleep(1.0)  # Wait before retry
                        continue
                    return None
                
                # Get historical data
                hist = ticker.history(period="6mo")  # Reduced to 6 months for faster processing
                
                if hist.empty:
                    self.logger.warning(f"No historical data for {symbol}")
                    if attempt < max_retries:
                        time.sleep(1.0)
                        continue
                    return None
                
                # Extract stock data
                stock_data = self._extract_stock_data(info, hist)
                return stock_data
                
            except Exception as e:
                self.logger.error(f"Error fetching {symbol} on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries:
                    time.sleep(2.0)  # Wait longer before retry
                    continue
                return None
        
        return None
    
    def validate_symbol(self, symbol):
        """Validate if a stock symbol exists and has data"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Check if we have basic required information
            if info and info.get('regularMarketPrice'):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error validating symbol {symbol}: {str(e)}")
            return False
    
    def get_market_data(self, market_index):
        """Get market index data for comparison"""
        try:
            # Map market names to index symbols
            index_mapping = {
                'japanese': '^N225',  # Nikkei 225
                'us': '^GSPC',        # S&P 500
                'emerging': 'EEM'     # iShares MSCI Emerging Markets ETF
            }
            
            symbol = index_mapping.get(market_index.lower())
            if not symbol:
                return None
            
            return self.get_stock_info(symbol)
            
        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            return None
