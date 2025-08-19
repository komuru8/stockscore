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
        
    def get_stock_info(self, symbol):
        """Get comprehensive stock information"""
        try:
            # Check cache first
            if self._is_cached(symbol):
                self.logger.info(f"Using cached data for {symbol}")
                return self.cache[symbol]
            
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
    
    def _is_cached(self, symbol):
        """Check if symbol data is cached and still valid"""
        if symbol not in self.cache or symbol not in self.cache_expiry:
            return False
        
        return datetime.now() < self.cache_expiry[symbol]
    
    def clear_cache(self):
        """Clear the data cache"""
        self.cache.clear()
        self.cache_expiry.clear()
    
    def get_multiple_stocks(self, symbols):
        """Get data for multiple stocks efficiently"""
        try:
            results = {}
            
            # Process in larger batches for better performance
            batch_size = 20  # Increased batch size
            total_batches = (len(symbols) + batch_size - 1) // batch_size
            
            self.logger.info(f"Processing {len(symbols)} symbols in {total_batches} batches")
            
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                self.logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} symbols)")
                
                # Process symbols in parallel within batch
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    # Submit all symbols in the batch
                    future_to_symbol = {executor.submit(self.get_stock_info, symbol): symbol for symbol in batch}
                    
                    # Collect results
                    for future in concurrent.futures.as_completed(future_to_symbol):
                        symbol = future_to_symbol[future]
                        try:
                            result = future.result(timeout=30)  # 30 second timeout per symbol
                            results[symbol] = result
                        except Exception as exc:
                            self.logger.warning(f"Error fetching {symbol}: {exc}")
                            results[symbol] = None
                
                # Shorter wait between batches
                if i + batch_size < len(symbols):
                    time.sleep(0.5)  # Reduced wait time
            
            # Log summary
            successful = len([r for r in results.values() if r is not None])
            self.logger.info(f"Successfully fetched data for {successful}/{len(symbols)} symbols")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error fetching multiple stocks: {str(e)}")
            return {}
    
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
