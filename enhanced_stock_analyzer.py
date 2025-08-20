import pandas as pd
import numpy as np
from enhanced_data_fetcher import EnhancedDataFetcher
from enhanced_scoring_engine import EnhancedScoringEngine
import logging
from typing import Dict, List, Optional, Any

class EnhancedStockAnalyzer:
    """Enhanced stock analyzer with comprehensive analysis and failover data sources"""
    
    def __init__(self):
        self.data_fetcher = EnhancedDataFetcher()
        self.scoring_engine = EnhancedScoringEngine()
        self.logger = logging.getLogger(__name__)
        
    def analyze_stocks(self, symbols: List[str]) -> Dict[str, Optional[Dict]]:
        """Analyze multiple stocks with enhanced metrics"""
        self.logger.info(f"Starting enhanced analysis of {len(symbols)} symbols")
        
        # Get raw data
        raw_data = self.data_fetcher.get_multiple_stocks(symbols)
        
        # Process each stock
        results = {}
        successful_analyses = 0
        
        for symbol in symbols:
            try:
                stock_data = raw_data.get(symbol)
                
                if not stock_data:
                    self.logger.warning(f"No data available for {symbol}")
                    results[symbol] = None
                    continue
                
                # Calculate enhanced metrics
                enhanced_data = self._enhance_stock_data(stock_data)
                
                # Calculate comprehensive score
                score_data = self.scoring_engine.calculate_comprehensive_score(enhanced_data)
                
                # Combine all data
                result = {
                    **enhanced_data,
                    **score_data
                }
                
                results[symbol] = result
                successful_analyses += 1
                
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {str(e)}")
                results[symbol] = None
        
        self.logger.info(f"Enhanced analysis completed: {successful_analyses}/{len(symbols)} symbols")
        return results
    
    def _enhance_stock_data(self, stock_data: Dict) -> Dict:
        """Enhance stock data with additional calculated metrics"""
        enhanced = stock_data.copy()
        
        try:
            # Calculate additional metrics if historical data is available
            price_history = stock_data.get('price_history', [])
            if price_history and len(price_history) > 1:
                try:
                    enhanced.update(self._calculate_technical_metrics(price_history))
                except Exception as e:
                    self.logger.error(f"Error calculating technical metrics: {e}")
            
            # Calculate financial ratios and scores
            try:
                enhanced.update(self._calculate_financial_ratios(stock_data))
            except Exception as e:
                self.logger.error(f"Error calculating financial ratios: {e}")
            
            # Risk assessment
            try:
                enhanced['risk_level'] = self._assess_risk_level(stock_data)
            except Exception as e:
                self.logger.error(f"Error assessing risk level: {e}")
                enhanced['risk_level'] = 'Unknown'
            
            # Investment recommendation
            try:
                enhanced['recommendation'] = self._generate_recommendation(stock_data)
            except Exception as e:
                self.logger.error(f"Error generating recommendation: {e}")
                enhanced['recommendation'] = 'Analysis incomplete'
            
        except Exception as e:
            self.logger.error(f"Error enhancing stock data: {e}")
        
        return enhanced
    
    def _calculate_technical_metrics(self, price_history: List[float]) -> Dict:
        """Calculate technical analysis metrics"""
        if len(price_history) < 20:
            return {}
        
        prices = np.array(price_history)
        
        # Price changes
        price_change_1d = ((prices[-1] - prices[-2]) / prices[-2] * 100) if len(prices) >= 2 else 0
        price_change_1w = ((prices[-1] - prices[-5]) / prices[-5] * 100) if len(prices) >= 5 else 0
        price_change_1m = ((prices[-1] - prices[-21]) / prices[-21] * 100) if len(prices) >= 21 else 0
        price_change_1y = ((prices[-1] - prices[0]) / prices[0] * 100) if len(prices) >= 252 else 0
        
        # Moving averages
        ma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else prices[-1]
        ma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else prices[-1]
        ma_200 = np.mean(prices[-200:]) if len(prices) >= 200 else prices[-1]
        
        # Volatility (standard deviation of returns)
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns) * np.sqrt(252) * 100  # Annualized volatility
        
        return {
            'price_change_1d': round(price_change_1d, 2),
            'price_change_1w': round(price_change_1w, 2),
            'price_change_1m': round(price_change_1m, 2),
            'price_change_1y': round(price_change_1y, 2),
            'moving_average_20': round(ma_20, 2),
            'moving_average_50': round(ma_50, 2),
            'moving_average_200': round(ma_200, 2),
            'volatility': round(volatility, 2),
            'price_vs_ma20': round((prices[-1] - ma_20) / ma_20 * 100, 2),
            'price_vs_ma50': round((prices[-1] - ma_50) / ma_50 * 100, 2)
        }
    
    def _calculate_financial_ratios(self, stock_data: Dict) -> Dict:
        """Calculate additional financial ratios"""
        ratios = {}
        
        # Price metrics
        current_price = stock_data.get('current_price', 0)
        market_cap = stock_data.get('market_cap', 0)
        
        # EPS-based calculations
        eps = stock_data.get('eps')
        if eps and eps > 0:
            ratios['earnings_yield'] = round((eps / current_price) * 100, 2) if current_price > 0 else 0
        
        # Dividend calculations
        dividend_rate = stock_data.get('dividend_rate', 0)
        if dividend_rate and current_price > 0:
            ratios['dividend_yield_calculated'] = round((dividend_rate / current_price) * 100, 2)
        
        # Market cap classification
        if market_cap > 0:
            if market_cap >= 10_000_000_000:  # $10B+
                ratios['market_cap_category'] = 'Large Cap'
            elif market_cap >= 2_000_000_000:  # $2B-$10B
                ratios['market_cap_category'] = 'Mid Cap'
            else:
                ratios['market_cap_category'] = 'Small Cap'
        
        return ratios
    
    def _assess_risk_level(self, stock_data: Dict) -> str:
        """Assess overall risk level"""
        risk_factors = []
        
        # Volatility risk
        volatility = stock_data.get('volatility', 0)
        if volatility > 40:
            risk_factors.append('high_volatility')
        elif volatility > 25:
            risk_factors.append('medium_volatility')
        
        # Valuation risk
        pe_ratio = stock_data.get('pe_ratio')
        if pe_ratio and pe_ratio > 30:
            risk_factors.append('high_pe')
        
        # Financial strength risk
        debt_to_equity = stock_data.get('debt_to_equity')
        if debt_to_equity and debt_to_equity > 70:
            risk_factors.append('high_debt')
        
        current_ratio = stock_data.get('current_ratio')
        if current_ratio and current_ratio < 1.0:
            risk_factors.append('liquidity_concern')
        
        # Determine overall risk
        if len(risk_factors) >= 3:
            return 'High Risk'
        elif len(risk_factors) >= 2:
            return 'Medium Risk'
        elif len(risk_factors) >= 1:
            return 'Low-Medium Risk'
        else:
            return 'Low Risk'
    
    def _generate_recommendation(self, stock_data: Dict) -> str:
        """Generate investment recommendation"""
        # This is a simplified recommendation engine
        # In practice, this would be much more sophisticated
        
        pe_ratio = stock_data.get('pe_ratio')
        roe = stock_data.get('roe', 0)
        dividend_yield = stock_data.get('dividend_yield', 0)
        debt_to_equity = stock_data.get('debt_to_equity', 100)
        
        positive_factors = 0
        negative_factors = 0
        
        # Valuation
        if pe_ratio and pe_ratio < 20:
            positive_factors += 1
        elif pe_ratio and pe_ratio > 30:
            negative_factors += 1
        
        # Profitability
        roe_percent = roe * 100 if roe and roe < 1 else roe if roe else 0
        if roe_percent > 15:
            positive_factors += 1
        elif roe_percent < 5:
            negative_factors += 1
        
        # Dividend
        if dividend_yield > 3:
            positive_factors += 1
        
        # Financial strength
        if debt_to_equity < 50:
            positive_factors += 1
        elif debt_to_equity > 100:
            negative_factors += 1
        
        # Generate recommendation
        if positive_factors >= 3 and negative_factors == 0:
            return 'Strong Buy'
        elif positive_factors >= 2 and negative_factors <= 1:
            return 'Buy'
        elif positive_factors >= 1 and negative_factors <= 1:
            return 'Hold'
        elif negative_factors >= 2:
            return 'Sell'
        else:
            return 'Neutral'
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get current API status"""
        return self.data_fetcher.get_api_status()
    
    def clear_cache(self):
        """Clear data cache"""
        self.data_fetcher.clear_cache()
    
    def update_scoring_criteria(self, **kwargs):
        """Update scoring criteria"""
        self.scoring_engine.update_thresholds(**kwargs)