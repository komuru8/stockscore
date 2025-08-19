import pandas as pd
import numpy as np
from data_fetcher import DataFetcher
from scoring_engine import ScoringEngine
import logging

class StockAnalyzer:
    """Main class for analyzing stocks and generating scores"""
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
        self.scoring_engine = ScoringEngine()
        self.logger = logging.getLogger(__name__)
        
    def update_criteria(self, per_threshold=20, pbr_threshold=1.0, roe_threshold=10, dividend_multiplier=1.2):
        """Update scoring criteria"""
        self.scoring_engine.update_thresholds(
            per_threshold=per_threshold,
            pbr_threshold=pbr_threshold,
            roe_threshold=roe_threshold,
            dividend_multiplier=dividend_multiplier
        )
    
    def analyze_stocks(self, symbols):
        """Analyze a list of stock symbols efficiently"""
        results = {}
        
        # Use the optimized multiple stock fetcher
        self.logger.info(f"Starting analysis of {len(symbols)} symbols")
        stock_data_batch = self.data_fetcher.get_multiple_stocks(symbols)
        
        successful_analyses = 0
        
        for symbol in symbols:
            try:
                stock_data = stock_data_batch.get(symbol)
                
                if not stock_data:
                    self.logger.warning(f"No data available for {symbol}")
                    results[symbol] = None
                    continue
                
                # Calculate fundamental metrics
                metrics = self._calculate_metrics(stock_data)
                
                if not metrics:
                    self.logger.warning(f"Could not calculate metrics for {symbol}")
                    results[symbol] = None
                    continue
                
                # Generate score
                score_data = self.scoring_engine.calculate_score(metrics)
                
                # Combine all data
                result = {
                    **metrics,
                    **score_data,
                    'company_name': stock_data.get('company_name', symbol)
                }
                
                results[symbol] = result
                successful_analyses += 1
                
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {str(e)}")
                results[symbol] = None
        
        self.logger.info(f"Analysis completed: {successful_analyses}/{len(symbols)} symbols successfully analyzed")
        return results
    
    def _calculate_metrics(self, stock_data):
        """Calculate fundamental metrics from stock data"""
        try:
            metrics = {}
            
            # Basic price info
            metrics['current_price'] = stock_data.get('current_price', 0)
            
            # P/E Ratio
            earnings_per_share = stock_data.get('earnings_per_share', 0)
            if earnings_per_share and earnings_per_share > 0:
                metrics['per'] = stock_data.get('current_price', 0) / earnings_per_share
            else:
                metrics['per'] = None
            
            # P/B Ratio
            book_value_per_share = stock_data.get('book_value_per_share', 0)
            if book_value_per_share and book_value_per_share > 0:
                metrics['pbr'] = stock_data.get('current_price', 0) / book_value_per_share
            else:
                metrics['pbr'] = None
            
            # ROE (Return on Equity)
            roe = stock_data.get('return_on_equity', 0)
            if roe is not None:
                # Convert to percentage if it's in decimal form
                metrics['roe'] = roe * 100 if roe < 1 else roe
            else:
                metrics['roe'] = None
            
            # ROA (Return on Assets)
            roa = stock_data.get('return_on_assets', 0)
            if roa is not None:
                # Convert to percentage if it's in decimal form
                metrics['roa'] = roa * 100 if roa < 1 else roa
            else:
                metrics['roa'] = None
            
            # Dividend Yield
            dividend_yield = stock_data.get('dividend_yield', 0)
            if dividend_yield is not None:
                # Convert to percentage if it's in decimal form
                metrics['dividend_yield'] = dividend_yield * 100 if dividend_yield < 1 else dividend_yield
            else:
                metrics['dividend_yield'] = None
            
            # Revenue Growth (売上高成長率)
            revenue_growth = stock_data.get('revenue_growth', 0)
            if revenue_growth is not None:
                # Convert to percentage if it's in decimal form
                metrics['revenue_growth'] = revenue_growth * 100 if revenue_growth < 1 and revenue_growth > -1 else revenue_growth
            else:
                metrics['revenue_growth'] = None
            
            # EPS Growth (EPS成長率)
            eps_growth = stock_data.get('earnings_growth', 0)
            if eps_growth is not None:
                # Convert to percentage if it's in decimal form
                metrics['eps_growth'] = eps_growth * 100 if eps_growth < 1 and eps_growth > -1 else eps_growth
            else:
                metrics['eps_growth'] = None
            
            # Operating Margin (営業利益率)
            operating_margin = stock_data.get('operating_margin', 0)
            if operating_margin is not None:
                # Convert to percentage if it's in decimal form
                metrics['operating_margin'] = operating_margin * 100 if operating_margin < 1 else operating_margin
            else:
                metrics['operating_margin'] = None
            
            # Equity Ratio (自己資本比率) - calculated from debt to equity
            debt_to_equity = stock_data.get('debt_to_equity', 0)
            if debt_to_equity is not None and debt_to_equity > 0:
                # Equity ratio = 1 / (1 + debt_to_equity_ratio) * 100
                metrics['equity_ratio'] = (1 / (1 + debt_to_equity/100)) * 100 if debt_to_equity > 1 else (1 / (1 + debt_to_equity)) * 100
            else:
                metrics['equity_ratio'] = None
            
            # Payout Ratio (配当性向)
            payout_ratio = stock_data.get('payout_ratio', 0)
            if payout_ratio is not None:
                # Convert to percentage if it's in decimal form
                metrics['payout_ratio'] = payout_ratio * 100 if payout_ratio < 1 else payout_ratio
            else:
                metrics['payout_ratio'] = None
            
            # Market Cap
            metrics['market_cap'] = stock_data.get('market_cap', 0)
            
            # Sector information for industry comparison
            metrics['sector'] = stock_data.get('sector', 'Unknown')
            metrics['industry'] = stock_data.get('industry', 'Unknown')
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating metrics: {str(e)}")
            return None
    
    def get_market_averages(self, symbols, metric):
        """Calculate market averages for comparison"""
        try:
            values = []
            
            for symbol in symbols:
                stock_data = self.data_fetcher.get_stock_info(symbol)
                if stock_data:
                    metrics = self._calculate_metrics(stock_data)
                    if metrics and metrics.get(metric) is not None:
                        values.append(metrics[metric])
            
            if values:
                return {
                    'mean': np.mean(values),
                    'median': np.median(values),
                    'std': np.std(values)
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating market averages: {str(e)}")
            return None
    
    def analyze_single_stock(self, symbol):
        """Analyze a single stock in detail"""
        try:
            result = self.analyze_stocks([symbol])
            return result.get(symbol)
        except Exception as e:
            self.logger.error(f"Error analyzing single stock {symbol}: {str(e)}")
            return None
    
    def get_top_stocks(self, symbols, top_n=10):
        """Get top N stocks by score"""
        try:
            results = self.analyze_stocks(symbols)
            
            # Filter valid results and sort by score
            valid_results = {k: v for k, v in results.items() if v and 'total_score' in v}
            sorted_stocks = sorted(
                valid_results.items(),
                key=lambda x: x[1]['total_score'],
                reverse=True
            )
            
            return sorted_stocks[:top_n]
            
        except Exception as e:
            self.logger.error(f"Error getting top stocks: {str(e)}")
            return []
    
    def filter_by_score(self, symbols, min_score=60):
        """Filter stocks by minimum score"""
        try:
            results = self.analyze_stocks(symbols)
            
            filtered_stocks = {}
            for symbol, data in results.items():
                if data and data.get('total_score', 0) >= min_score:
                    filtered_stocks[symbol] = data
            
            return filtered_stocks
            
        except Exception as e:
            self.logger.error(f"Error filtering stocks by score: {str(e)}")
            return {}
