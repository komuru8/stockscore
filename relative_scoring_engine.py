import logging
from typing import Dict, Any, Optional

class RelativeScoringEngine:
    """
    Relative scoring engine that compares stock metrics against baseline values
    Implements user-specified 5-tier evaluation system with proper score distribution
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Baseline values for comparison (recommended standards)
        self.baselines = {
            'pe_ratio': 15.0,           # PER baseline (lower is better)
            'pb_ratio': 1.0,            # PBR baseline (lower is better) 
            'roe': 15.0,                # ROE baseline (higher is better)
            'roa': 8.0,                 # ROA baseline (higher is better)
            'dividend_yield': 3.0,      # Dividend yield baseline (higher is better)
            'revenue_growth': 10.0,     # Revenue growth baseline (higher is better)
            'eps_growth': 10.0,         # EPS growth baseline (higher is better) 
            'operating_margin': 15.0,   # Operating margin baseline (higher is better)
            'equity_ratio': 50.0,       # Equity ratio baseline (higher is better)
            'payout_ratio': 40.0        # Payout ratio baseline (optimal range 30-50%)
        }
        
        # Define evaluation direction for each metric
        self.metric_directions = {
            'pe_ratio': 'lower_better',      # 小さい方が良い
            'pb_ratio': 'lower_better',      # 小さい方が良い
            'roe': 'higher_better',          # 大きい方が良い
            'roa': 'higher_better',          # 大きい方が良い
            'dividend_yield': 'higher_better', # 大きい方が良い
            'revenue_growth': 'higher_better', # 大きい方が良い
            'eps_growth': 'higher_better',     # 大きい方が良い
            'operating_margin': 'higher_better', # 大きい方が良い
            'equity_ratio': 'higher_better',    # 大きい方が良い
            'payout_ratio': 'optimal_range'     # 最適レンジ（30-50%）
        }
        
        # Mode configurations (exact as specified)
        self.mode_configs = {
            'beginner': {
                'metrics': ['pe_ratio', 'dividend_yield'],  # PER・配当利回り
                'max_points_per_metric': 50,
                'total_points': 100
            },
            'intermediate': {
                'metrics': ['pe_ratio', 'pb_ratio', 'roe', 'roa', 'dividend_yield', 
                           'revenue_growth', 'eps_growth', 'operating_margin', 
                           'equity_ratio', 'payout_ratio'],  # All 10 metrics
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
            direction = self.metric_directions.get(metric, 'higher_better')
            
            if baseline is None:
                return max_points * 0.5  # Fallback to normal
            
            # Convert percentage values if needed (for decimal values < 1)
            if metric in ['roe', 'roa', 'dividend_yield', 'operating_margin', 'revenue_growth', 'eps_growth', 'equity_ratio', 'payout_ratio']:
                if value < 1:  # Convert decimal to percentage
                    value = value * 100
            
            # Calculate score based on metric direction
            if direction == 'lower_better':
                # PER, PBR - lower values are better
                relative_performance = (baseline - value) / baseline
            elif direction == 'higher_better':
                # ROE, ROA, etc. - higher values are better
                relative_performance = (value - baseline) / baseline
            elif direction == 'optimal_range':
                # Payout ratio - optimal range 30-50%
                return self._calculate_payout_ratio_score(value, max_points)
            else:
                # Default to higher_better
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
    
    def _calculate_payout_ratio_score(self, value: float, max_points: int) -> float:
        """Calculate payout ratio score with optimal range logic"""
        # Optimal range: 30-50%
        if 30 <= value <= 50:
            return max_points * 1.0  # 非常に良い: 100%
        elif 25 <= value < 30 or 50 < value <= 60:
            return max_points * 0.8  # 良い: 80%
        elif 20 <= value < 25 or 60 < value <= 70:
            return max_points * 0.5  # 普通: 50%
        elif 15 <= value < 20 or 70 < value <= 80:
            return max_points * 0.2  # 悪い: 20%
        else:  # < 15% or > 80%
            return max_points * 0.0  # 非常に悪い: 0%
    
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
        """Get color code for visualization (green to red scale)"""
        if score >= 90:
            return "#2E7D32"  # Dark Green - S rank
        elif score >= 80:
            return "#4CAF50"  # Green - A rank
        elif score >= 60:
            return "#8BC34A"  # Light Green - B rank  
        elif score >= 40:
            return "#FF9800"  # Orange - C rank
        else:
            return "#F44336"  # Red - D rank
    
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