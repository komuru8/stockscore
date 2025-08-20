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
        """Calculate score for individual metric using linear interpolation"""
        try:
            value = stock_data.get(metric)
            
            # Handle missing data - return neutral score (5 points for 10-point max, 25 for 50-point max)
            if value is None or not isinstance(value, (int, float)):
                return max_points * 0.5  # Neutral score (50% of max)
            
            # Convert percentage values if needed (for decimal values < 1)
            if metric in ['roe', 'roa', 'dividend_yield', 'operating_margin', 'revenue_growth', 'eps_growth', 'equity_ratio', 'payout_ratio']:
                if value < 1:  # Convert decimal to percentage
                    value = value * 100
            
            # Calculate score based on specific metric rules
            if metric == 'pe_ratio':
                return self._calculate_per_score(value, max_points)
            elif metric == 'pb_ratio':
                return self._calculate_pbr_score(value, max_points)
            elif metric == 'dividend_yield':
                return self._calculate_dividend_yield_score(value, max_points)
            elif metric in ['revenue_growth', 'eps_growth']:
                return self._calculate_growth_score(value, max_points)
            elif metric in ['roe', 'roa', 'operating_margin', 'equity_ratio']:
                return self._calculate_ratio_score(value, max_points, metric)
            elif metric == 'payout_ratio':
                return self._calculate_payout_ratio_score(value, max_points)
            else:
                # Fallback to baseline comparison
                baseline = self.baselines.get(metric, 0)
                if value >= baseline:
                    return max_points
                else:
                    return max_points * (value / baseline) if baseline > 0 else max_points * 0.5
                
        except Exception as e:
            self.logger.error(f"Error calculating score for {metric}: {e}")
            return max_points * 0.5  # Return neutral score on error
    
    def _calculate_per_score(self, value: float, max_points: int) -> float:
        """Calculate PER score with linear interpolation"""
        baseline = 15.0  # PER baseline
        if value <= baseline:
            return max_points  # Full points for PER <= baseline
        elif value >= baseline * 2:  # PER >= 30
            return 0  # Zero points for PER >= 2x baseline
        else:
            # Linear interpolation between baseline and 2x baseline
            ratio = (baseline * 2 - value) / baseline
            return max_points * ratio
    
    def _calculate_pbr_score(self, value: float, max_points: int) -> float:
        """Calculate PBR score with linear interpolation"""
        if value <= 1.0:
            return max_points  # Full points for PBR <= 1.0
        elif value >= 3.0:  # Upper limit
            return 0  # Zero points for PBR >= 3.0
        else:
            # Linear interpolation between 1.0 and 3.0
            ratio = (3.0 - value) / 2.0
            return max_points * ratio
    
    def _calculate_dividend_yield_score(self, value: float, max_points: int) -> float:
        """Calculate dividend yield score"""
        baseline = 2.0  # 2% baseline
        upper_limit = 5.0  # 5% upper limit
        if value < baseline:
            return 0  # Zero points below baseline
        elif value >= upper_limit:
            return max_points  # Full points at 5% or above
        else:
            # Linear interpolation between baseline and upper limit
            ratio = (value - baseline) / (upper_limit - baseline)
            return max_points * ratio
    
    def _calculate_growth_score(self, value: float, max_points: int) -> float:
        """Calculate growth score (EPS/Revenue growth)"""
        baseline = 5.0  # 5% baseline growth
        if value < 0:  # Negative growth
            return 0
        elif value == 0:  # No growth
            return max_points * 0.5  # 50% of max points
        elif value >= baseline:
            return max_points  # Full points for baseline growth or better
        else:
            # Linear interpolation between 0% and baseline
            ratio = value / baseline
            return max_points * (0.5 + 0.5 * ratio)  # Scale from 50% to 100%
    
    def _calculate_ratio_score(self, value: float, max_points: int, metric: str) -> float:
        """Calculate score for ratio metrics (ROE, ROA, Operating Margin, Equity Ratio)"""
        baseline = self.baselines.get(metric, 10.0)
        if value >= baseline:
            return max_points  # Full points for meeting baseline
        elif value <= 0:
            return 0  # Zero points for non-positive values
        else:
            # Linear interpolation from 0 to baseline
            ratio = value / baseline
            return max_points * ratio
    
    def _calculate_payout_ratio_score(self, value: float, max_points: int) -> float:
        """Calculate payout ratio score with optimal range logic"""
        # Optimal range: 30-50%
        if 30 <= value <= 50:
            return max_points  # Full points for optimal range
        elif value < 30:
            # Linear scale from 0 to 30%
            if value <= 0:
                return max_points * 0.5  # Neutral for no dividends
            else:
                ratio = value / 30.0
                return max_points * (0.5 + 0.5 * ratio)  # Scale from 50% to 100%
        else:  # value > 50
            # Linear decline from 50% to 100%
            if value >= 100:
                return 0  # Unsustainable
            else:
                ratio = (100 - value) / 50.0
                return max_points * ratio
    
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
        """Get rank based on score (updated boundaries)"""
        if score >= 90:
            return "S"  # 90-100点（非常に優秀）
        elif score >= 75:
            return "A"  # 75-89点（優秀）
        elif score >= 60:
            return "B"  # 60-74点（平均以上）
        elif score >= 40:
            return "C"  # 40-59点（平均以下）
        else:
            return "D"  # 0-39点（推奨度低い）
    
    def _get_color_scale(self, score: float) -> str:
        """Get color code for visualization (green to red scale)"""
        if score >= 90:
            return "#1B5E20"  # 濃い緑 - S rank
        elif score >= 75:
            return "#4CAF50"  # 緑 - A rank
        elif score >= 60:
            return "#FFEB3B"  # 黄色 - B rank  
        elif score >= 40:
            return "#FF9800"  # オレンジ - C rank
        else:
            return "#F44336"  # 赤 - D rank
    
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