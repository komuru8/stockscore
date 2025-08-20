import logging
from typing import Dict, Any, Optional

class RelativeScoringEngine:
    """
    Relative scoring engine that compares stock metrics against baseline values
    Implements user-specified 5-tier evaluation system with proper score distribution
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Baseline values for comparison (market average values)
        self.baselines = {
            'pe_ratio': 20.0,        # Market average PER
            'pb_ratio': 1.5,         # Market average PBR
            'roe': 12.0,             # Market average ROE (%)
            'roa': 6.0,              # Market average ROA (%)
            'dividend_yield': 2.5,   # Market average dividend yield (%)
            'profit_margins': 15.0,  # Market average profit margin (%)
            'debt_to_equity': 50.0,  # Market average D/E ratio
            'current_ratio': 1.8,    # Market average current ratio
            'earnings_growth': 8.0,  # Market average earnings growth (%)
            'revenue_growth': 6.0    # Market average revenue growth (%)
        }
        
        # Mode configurations
        self.mode_configs = {
            'beginner': {
                'metrics': ['pe_ratio', 'dividend_yield'],
                'max_points_per_metric': 50,
                'total_points': 100
            },
            'intermediate': {
                'metrics': ['pe_ratio', 'pb_ratio', 'roe', 'roa', 'dividend_yield', 
                           'profit_margins', 'debt_to_equity', 'current_ratio', 
                           'earnings_growth', 'revenue_growth'],
                'max_points_per_metric': 10,
                'total_points': 100
            }
        }
    
    def calculate_score(self, stock_data: Dict, mode: str = 'intermediate') -> Dict:
        """Calculate relative score based on mode"""
        try:
            if mode not in self.mode_configs:
                mode = 'intermediate'  # Default fallback
                
            config = self.mode_configs[mode]
            metrics = config['metrics']
            max_points = config['max_points_per_metric']
            
            individual_scores = {}
            total_score = 0
            
            for metric in metrics:
                score = self._calculate_metric_score(stock_data, metric, max_points)
                individual_scores[metric] = score
                total_score += score
            
            # Generate assessment and recommendation
            assessment = self._generate_assessment(total_score)
            recommendation = self._get_investment_recommendation(total_score)
            rank = self._get_rank(total_score)
            color = self._get_color_scale(total_score)
            
            return {
                'total_score': round(total_score, 1),
                'individual_scores': individual_scores,
                'assessment': assessment,
                'recommendation': recommendation,
                'rank': rank,
                'color': color,
                'mode': mode,
                'max_possible_score': config['total_points']
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating relative score: {e}")
            return self._get_error_result()
    
    def _calculate_metric_score(self, stock_data: Dict, metric: str, max_points: int) -> float:
        """Calculate score for individual metric using relative comparison"""
        try:
            value = stock_data.get(metric)
            
            # Handle missing data - return "normal" score (5 points for 10-point max, 25 for 50-point max)
            if value is None or not isinstance(value, (int, float)):
                return max_points * 0.5  # Normal score (50% of max)
            
            baseline = self.baselines.get(metric)
            if baseline is None:
                return max_points * 0.5  # Fallback to normal
            
            # Convert percentage values if needed
            if metric in ['roe', 'roa', 'dividend_yield', 'profit_margins', 'earnings_growth', 'revenue_growth']:
                if value < 1:  # Convert decimal to percentage
                    value = value * 100
            
            # Calculate relative performance
            if metric in ['pe_ratio', 'pb_ratio', 'debt_to_equity']:
                # Lower is better metrics
                relative_performance = (baseline - value) / baseline
            else:
                # Higher is better metrics
                relative_performance = (value - baseline) / baseline
            
            # Apply 5-tier scoring system based on relative performance
            if relative_performance >= 0.20:      # +20% or better
                return max_points * 1.0          # 非常に良い: 10点 (100%) or 50点
            elif relative_performance >= 0.10:    # +10% to +20%
                return max_points * 0.8          # 良い: 8点 (80%) or 40点
            elif relative_performance >= -0.10:   # ±10%
                return max_points * 0.5          # 普通: 5点 (50%) or 25点
            elif relative_performance >= -0.20:   # -10% to -20%
                return max_points * 0.2          # 悪い: 2点 (20%) or 10点
            else:                                 # -20% or worse
                return max_points * 0.0          # 非常に悪い: 0点 or 0点
                
        except Exception as e:
            self.logger.error(f"Error calculating score for {metric}: {e}")
            return max_points * 0.5  # Return normal score on error
    
    def _generate_assessment(self, score: float) -> str:
        """Generate human-readable assessment"""
        if score >= 80:
            return "🚀 強い買い推奨 / Strong Buy - 優秀な財務指標"
        elif score >= 70:
            return "✅ 買い推奨 / Buy - 良好な投資機会"
        elif score >= 60:
            return "➖ 中立・保有 / Hold - 平均的な performance"
        elif score >= 40:
            return "⚠️ 慎重 / Caution - 慎重な検討が必要"
        else:
            return "❌ 非推奨 / Not Recommended - 投資リスクが高い"
    
    def _get_investment_recommendation(self, score: float) -> str:
        """Get investment recommendation based on score"""
        if score >= 80:
            return "🚀 強い買い推奨"
        elif score >= 70:
            return "✅ 買い推奨"  
        elif score >= 60:
            return "➖ 中立・保有"
        elif score >= 40:
            return "⚠️ 慎重"
        else:
            return "❌ 非推奨"
    
    def _get_rank(self, score: float) -> str:
        """Get rank based on score"""
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 60:
            return "B"
        elif score >= 40:
            return "C"
        else:
            return "D"
    
    def _get_color_scale(self, score: float) -> str:
        """Get color code for visualization"""
        if score >= 80:
            return "#4CAF50"  # Green - Excellent
        elif score >= 70:
            return "#8BC34A"  # Light Green - Good
        elif score >= 60:
            return "#FFC107"  # Yellow - Hold
        elif score >= 40:
            return "#FF9800"  # Orange - Caution
        else:
            return "#F44336"  # Red - Poor
    
    def _get_error_result(self) -> Dict:
        """Return error result"""
        return {
            'total_score': 0,
            'individual_scores': {},
            'assessment': "❌ データ取得エラー / Data Error",
            'recommendation': "❌ 評価不可",
            'rank': "E",
            'color': "#9E9E9E",
            'mode': 'error',
            'max_possible_score': 100
        }
    
    def update_baselines(self, **kwargs):
        """Update baseline values for comparison"""
        for key, value in kwargs.items():
            if key in self.baselines:
                self.baselines[key] = value
                self.logger.info(f"Updated baseline for {key} to {value}")