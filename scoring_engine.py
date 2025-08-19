import numpy as np
import logging
from datetime import datetime

class ScoringEngine:
    """Engine for calculating stock investment scores based on fundamental analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Default scoring thresholds
        self.thresholds = {
            'per_threshold': 20,        # PER should be 20% below industry average
            'pbr_threshold': 1.0,       # PBR should be below 1.0
            'roe_threshold': 10,        # ROE should be above 10%
            'dividend_multiplier': 1.2  # Dividend yield should be 1.2x market average
        }
        
        # Scoring weights (total should be 100)
        self.weights = {
            'per_weight': 30,
            'pbr_weight': 25,
            'roe_weight': 25,
            'dividend_weight': 20
        }
        
        # Market averages for comparison (will be updated dynamically)
        self.market_averages = {
            'per_average': 15.0,
            'pbr_average': 1.5,
            'roe_average': 8.0,
            'dividend_average': 2.0
        }
    
    def update_thresholds(self, **kwargs):
        """Update scoring thresholds"""
        for key, value in kwargs.items():
            if key in self.thresholds:
                self.thresholds[key] = value
                self.logger.info(f"Updated {key} to {value}")
    
    def update_market_averages(self, **kwargs):
        """Update market averages for comparison"""
        for key, value in kwargs.items():
            if key in self.market_averages:
                self.market_averages[key] = value
    
    def calculate_score(self, metrics):
        """Calculate comprehensive investment score for a stock using all 10 metrics"""
        try:
            scores = {}
            
            # Calculate individual metric scores for all 10 indicators
            scores['per_score'] = self._calculate_per_score(metrics.get('per'))
            scores['pbr_score'] = self._calculate_pbr_score(metrics.get('pbr'))
            scores['roe_score'] = self._calculate_roe_score(metrics.get('roe'))
            scores['roa_score'] = self._calculate_roa_score(metrics.get('roa'))
            scores['dividend_score'] = self._calculate_dividend_score(metrics.get('dividend_yield'))
            scores['revenue_growth_score'] = self._calculate_revenue_growth_score(metrics.get('revenue_growth'))
            scores['eps_growth_score'] = self._calculate_eps_growth_score(metrics.get('eps_growth'))
            scores['operating_margin_score'] = self._calculate_operating_margin_score(metrics.get('operating_margin'))
            scores['equity_ratio_score'] = self._calculate_equity_ratio_score(metrics.get('equity_ratio'))
            scores['payout_ratio_score'] = self._calculate_payout_ratio_score(metrics.get('payout_ratio'))
            
            # Updated weights for 10 metrics (total = 100)
            weights = {
                'per_weight': 15,           # PER
                'pbr_weight': 10,           # PBR
                'roe_weight': 15,           # ROE
                'roa_weight': 10,           # ROA
                'dividend_weight': 10,      # Dividend Yield
                'revenue_growth_weight': 10, # Revenue Growth
                'eps_growth_weight': 10,    # EPS Growth
                'operating_margin_weight': 10, # Operating Margin
                'equity_ratio_weight': 5,   # Equity Ratio
                'payout_ratio_weight': 5    # Payout Ratio
            }
            
            # Calculate weighted total score
            total_score = (
                scores['per_score'] * weights['per_weight'] / 100 +
                scores['pbr_score'] * weights['pbr_weight'] / 100 +
                scores['roe_score'] * weights['roe_weight'] / 100 +
                scores['roa_score'] * weights['roa_weight'] / 100 +
                scores['dividend_score'] * weights['dividend_weight'] / 100 +
                scores['revenue_growth_score'] * weights['revenue_growth_weight'] / 100 +
                scores['eps_growth_score'] * weights['eps_growth_weight'] / 100 +
                scores['operating_margin_score'] * weights['operating_margin_weight'] / 100 +
                scores['equity_ratio_score'] * weights['equity_ratio_weight'] / 100 +
                scores['payout_ratio_score'] * weights['payout_ratio_weight'] / 100
            )
            
            # Additional quality adjustments
            quality_adjustment = self._calculate_quality_adjustment(metrics)
            total_score += quality_adjustment
            
            # Ensure score is within 0-100 range
            total_score = max(0, min(100, total_score))
            
            # Generate recommendation
            recommendation = self._get_recommendation(total_score)
            
            # Prepare detailed explanation
            explanation = self._generate_explanation(metrics, scores, total_score)
            
            result = {
                'total_score': round(total_score, 1),
                'score_breakdown': scores,
                'recommendation': recommendation,
                'explanation': explanation,
                'quality_adjustment': quality_adjustment
            }
            
            self.logger.info(f"Calculated score: {total_score:.1f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating score: {str(e)}")
            return {
                'total_score': 0,
                'score_breakdown': {},
                'recommendation': 'Error',
                'explanation': f"Error calculating score: {str(e)}",
                'quality_adjustment': 0
            }
    
    def _calculate_per_score(self, per):
        """Calculate PER-based score (0-100)"""
        if per is None or per <= 0:
            return 0
        
        try:
            # Good PER is typically between 10-20 for most stocks
            # Lower PER (undervalued) gets higher score
            if per <= 10:
                return 100  # Very undervalued
            elif per <= 15:
                return 80   # Undervalued
            elif per <= 20:
                return 60   # Fair value
            elif per <= 30:
                return 30   # Slightly overvalued
            else:
                return 10   # Overvalued
                
        except Exception as e:
            self.logger.error(f"Error calculating PER score: {str(e)}")
            return 0
    
    def _calculate_pbr_score(self, pbr):
        """Calculate PBR-based score (0-100)"""
        if pbr is None or pbr <= 0:
            return 0
        
        try:
            # Good PBR is typically below 1.5
            # Lower PBR indicates potential undervaluation
            if pbr <= 0.5:
                return 100  # Significantly undervalued
            elif pbr <= 1.0:
                return 80   # Undervalued (meeting our threshold)
            elif pbr <= 1.5:
                return 60   # Fair value
            elif pbr <= 2.0:
                return 30   # Slightly overvalued
            else:
                return 10   # Overvalued
                
        except Exception as e:
            self.logger.error(f"Error calculating PBR score: {str(e)}")
            return 0
    
    def _calculate_roe_score(self, roe):
        """Calculate ROE-based score (0-100)"""
        if roe is None:
            return 0
        
        try:
            # Higher ROE indicates better profitability
            if roe >= 20:
                return 100  # Excellent profitability
            elif roe >= 15:
                return 80   # Very good profitability
            elif roe >= 10:
                return 60   # Good profitability (meets our threshold)
            elif roe >= 5:
                return 30   # Average profitability
            elif roe > 0:
                return 10   # Low profitability
            else:
                return 0    # Negative ROE
                
        except Exception as e:
            self.logger.error(f"Error calculating ROE score: {str(e)}")
            return 0
    
    def _calculate_dividend_score(self, dividend_yield):
        """Calculate dividend yield-based score (0-100)"""
        if dividend_yield is None or dividend_yield < 0:
            return 0
        
        try:
            # Higher dividend yield is generally better for income investors
            market_avg = self.market_averages['dividend_average']
            target_yield = market_avg * self.thresholds['dividend_multiplier']
            
            if dividend_yield >= target_yield * 1.5:
                return 100  # Excellent dividend
            elif dividend_yield >= target_yield:
                return 80   # Good dividend (meets our threshold)
            elif dividend_yield >= market_avg:
                return 60   # Above market average
            elif dividend_yield >= market_avg * 0.5:
                return 30   # Below average but positive
            elif dividend_yield > 0:
                return 10   # Low dividend
            else:
                return 5    # No dividend (still gets some points for growth potential)
                
        except Exception as e:
            self.logger.error(f"Error calculating dividend score: {str(e)}")
            return 0
    
    def _calculate_roa_score(self, roa):
        """Calculate ROA-based score (0-100)"""
        if roa is None:
            return 0
        
        try:
            # Higher ROA indicates better asset efficiency
            if roa >= 15:
                return 100  # Excellent asset efficiency
            elif roa >= 10:
                return 80   # Very good asset efficiency
            elif roa >= 5:
                return 60   # Good asset efficiency
            elif roa >= 2:
                return 30   # Average asset efficiency
            elif roa > 0:
                return 10   # Low asset efficiency
            else:
                return 0    # Negative ROA
        except Exception as e:
            self.logger.error(f"Error calculating ROA score: {str(e)}")
            return 0
    
    def _calculate_revenue_growth_score(self, revenue_growth):
        """Calculate revenue growth-based score (0-100)"""
        if revenue_growth is None:
            return 0
        
        try:
            # Higher revenue growth indicates business expansion
            if revenue_growth >= 20:
                return 100  # Excellent growth
            elif revenue_growth >= 10:
                return 80   # Very good growth
            elif revenue_growth >= 5:
                return 60   # Good growth
            elif revenue_growth >= 0:
                return 30   # Stable/slow growth
            elif revenue_growth >= -5:
                return 10   # Slight decline
            else:
                return 0    # Significant decline
        except Exception as e:
            self.logger.error(f"Error calculating revenue growth score: {str(e)}")
            return 0
    
    def _calculate_eps_growth_score(self, eps_growth):
        """Calculate EPS growth-based score (0-100)"""
        if eps_growth is None:
            return 0
        
        try:
            # Higher EPS growth indicates improving profitability
            if eps_growth >= 25:
                return 100  # Excellent EPS growth
            elif eps_growth >= 15:
                return 80   # Very good EPS growth
            elif eps_growth >= 10:
                return 60   # Good EPS growth
            elif eps_growth >= 0:
                return 30   # Stable EPS
            elif eps_growth >= -10:
                return 10   # Declining EPS
            else:
                return 0    # Significant EPS decline
        except Exception as e:
            self.logger.error(f"Error calculating EPS growth score: {str(e)}")
            return 0
    
    def _calculate_operating_margin_score(self, operating_margin):
        """Calculate operating margin-based score (0-100)"""
        if operating_margin is None:
            return 0
        
        try:
            # Higher operating margin indicates better operational efficiency
            if operating_margin >= 20:
                return 100  # Excellent operational efficiency
            elif operating_margin >= 15:
                return 80   # Very good operational efficiency
            elif operating_margin >= 10:
                return 60   # Good operational efficiency
            elif operating_margin >= 5:
                return 30   # Average operational efficiency
            elif operating_margin > 0:
                return 10   # Low operational efficiency
            else:
                return 0    # Negative operating margin
        except Exception as e:
            self.logger.error(f"Error calculating operating margin score: {str(e)}")
            return 0
    
    def _calculate_equity_ratio_score(self, equity_ratio):
        """Calculate equity ratio-based score (0-100)"""
        if equity_ratio is None:
            return 0
        
        try:
            # Higher equity ratio indicates better financial stability
            if equity_ratio >= 60:
                return 100  # Excellent financial stability
            elif equity_ratio >= 50:
                return 80   # Very good financial stability
            elif equity_ratio >= 40:
                return 60   # Good financial stability
            elif equity_ratio >= 30:
                return 30   # Average financial stability
            elif equity_ratio >= 20:
                return 10   # Low financial stability
            else:
                return 0    # Poor financial stability
        except Exception as e:
            self.logger.error(f"Error calculating equity ratio score: {str(e)}")
            return 0
    
    def _calculate_payout_ratio_score(self, payout_ratio):
        """Calculate payout ratio-based score (0-100)"""
        if payout_ratio is None:
            return 50  # Neutral score for companies with no dividends
        
        try:
            # Optimal payout ratio is typically 30-60%
            if 30 <= payout_ratio <= 60:
                return 100  # Optimal payout ratio
            elif 20 <= payout_ratio <= 70:
                return 80   # Good payout ratio
            elif 10 <= payout_ratio <= 80:
                return 60   # Acceptable payout ratio
            elif payout_ratio <= 90:
                return 30   # High payout ratio (sustainability risk)
            elif payout_ratio > 100:
                return 0    # Unsustainable payout ratio
            else:
                return 50   # Low/no payout (growth company)
        except Exception as e:
            self.logger.error(f"Error calculating payout ratio score: {str(e)}")
            return 0

    def _calculate_quality_adjustment(self, metrics):
        """Calculate quality-based adjustments to the score"""
        try:
            adjustment = 0
            
            # Financial health adjustments
            debt_to_equity = metrics.get('debt_to_equity', 0)
            if debt_to_equity and debt_to_equity < 0.3:
                adjustment += 2  # Low debt is good
            elif debt_to_equity and debt_to_equity > 1.0:
                adjustment -= 3  # High debt is concerning
            
            # Profitability consistency
            profit_margins = metrics.get('profit_margins', 0)
            if profit_margins and profit_margins > 0.15:
                adjustment += 2  # High profit margins
            elif profit_margins and profit_margins < 0:
                adjustment -= 5  # Negative margins
            
            # Growth potential
            earnings_growth = metrics.get('earnings_growth', 0)
            if earnings_growth and earnings_growth > 0.1:
                adjustment += 1  # Positive earnings growth
            elif earnings_growth and earnings_growth < -0.1:
                adjustment -= 2  # Declining earnings
            
            # Market position
            market_cap = metrics.get('market_cap', 0)
            if market_cap and market_cap > 10e9:  # Large cap (>10B)
                adjustment += 1  # Large cap stability
            
            # Volatility consideration
            volatility = metrics.get('volatility', 0)
            if volatility and volatility < 0.2:
                adjustment += 1  # Low volatility is good for value investing
            elif volatility and volatility > 0.5:
                adjustment -= 1  # High volatility increases risk
            
            return min(5, max(-10, adjustment))  # Cap adjustments
            
        except Exception as e:
            self.logger.error(f"Error calculating quality adjustment: {str(e)}")
            return 0
    
    def _get_recommendation(self, score):
        """Get investment recommendation based on score"""
        if score >= 80:
            return "🚀 購入推奨 / Strong Buy"
        elif score >= 60:
            return "👀 ウォッチ / Watch"
        elif score >= 40:
            return "➖ 中立 / Hold"
        else:
            return "❌ 売却検討 / Consider Selling"
    
    def _generate_explanation(self, metrics, scores, total_score):
        """Generate detailed explanation of the scoring"""
        try:
            explanation = []
            
            # Overall assessment
            if total_score >= 80:
                explanation.append("この銘柄は優れた投資機会を示しています。")
                explanation.append("This stock shows excellent investment potential.")
            elif total_score >= 60:
                explanation.append("この銘柄は注目に値する投資候補です。")
                explanation.append("This stock is worth watching as an investment candidate.")
            elif total_score >= 40:
                explanation.append("この銘柄は適正価格で取引されています。")
                explanation.append("This stock appears to be fairly valued.")
            else:
                explanation.append("この銘柄は現在推奨されません。")
                explanation.append("This stock is not currently recommended.")
            
            explanation.append("")  # Empty line
            
            # Detailed breakdown
            per = metrics.get('per')
            if per and per > 0:
                explanation.append(f"PER: {per:.2f} (スコア: {scores['per_score']:.1f}/100)")
                if per <= 15:
                    explanation.append("  ✓ 低PERで割安の可能性 / Low PER suggests potential undervaluation")
                elif per > 25:
                    explanation.append("  ⚠ 高PERで割高の可能性 / High PER suggests potential overvaluation")
            
            pbr = metrics.get('pbr')
            if pbr and pbr > 0:
                explanation.append(f"PBR: {pbr:.2f} (スコア: {scores['pbr_score']:.1f}/100)")
                if pbr <= 1.0:
                    explanation.append("  ✓ PBR 1.0以下で資産価値での割安 / PBR below 1.0 suggests asset undervaluation")
                elif pbr > 2.0:
                    explanation.append("  ⚠ 高PBRで割高の可能性 / High PBR suggests potential overvaluation")
            
            roe = metrics.get('roe')
            if roe is not None:
                explanation.append(f"ROE: {roe:.1f}% (スコア: {scores['roe_score']:.1f}/100)")
                if roe >= 15:
                    explanation.append("  ✓ 高ROEで優れた収益性 / High ROE indicates excellent profitability")
                elif roe >= 10:
                    explanation.append("  ✓ 良好なROE / Good ROE")
                elif roe < 5:
                    explanation.append("  ⚠ 低ROEで収益性に懸念 / Low ROE raises profitability concerns")
            
            dividend_yield = metrics.get('dividend_yield')
            if dividend_yield is not None:
                explanation.append(f"配当利回り: {dividend_yield:.1f}% (スコア: {scores['dividend_score']:.1f}/100)")
                if dividend_yield >= 3:
                    explanation.append("  ✓ 高配当利回り / High dividend yield")
                elif dividend_yield >= 2:
                    explanation.append("  ✓ 適度な配当利回り / Moderate dividend yield")
                elif dividend_yield == 0:
                    explanation.append("  - 無配当（成長投資型の可能性）/ No dividend (possible growth stock)")
            
            return "\n".join(explanation)
            
        except Exception as e:
            self.logger.error(f"Error generating explanation: {str(e)}")
            return f"スコア計算完了 / Score calculation completed: {total_score:.1f}"
    
    def compare_stocks(self, stock_data_list):
        """Compare multiple stocks and rank them"""
        try:
            results = []
            
            for symbol, data in stock_data_list:
                if data and 'total_score' in data:
                    results.append({
                        'symbol': symbol,
                        'score': data['total_score'],
                        'recommendation': data['recommendation']
                    })
            
            # Sort by score (highest first)
            results.sort(key=lambda x: x['score'], reverse=True)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error comparing stocks: {str(e)}")
            return []
    
    def get_score_distribution(self, scores):
        """Get distribution analysis of scores"""
        try:
            if not scores:
                return {}
            
            scores_array = np.array(scores)
            
            return {
                'mean': np.mean(scores_array),
                'median': np.median(scores_array),
                'std': np.std(scores_array),
                'min': np.min(scores_array),
                'max': np.max(scores_array),
                'buy_count': len([s for s in scores if s >= 80]),
                'watch_count': len([s for s in scores if 60 <= s < 80]),
                'hold_count': len([s for s in scores if 40 <= s < 60]),
                'sell_count': len([s for s in scores if s < 40])
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating score distribution: {str(e)}")
            return {}
