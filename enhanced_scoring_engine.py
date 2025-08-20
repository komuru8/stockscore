import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, Optional

class EnhancedScoringEngine:
    """Enhanced scoring engine with comprehensive fundamental analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Default thresholds - can be updated
        self.thresholds = {
            'pe_ratio': {'excellent': 15, 'good': 20, 'fair': 25},
            'pb_ratio': {'excellent': 1.0, 'good': 1.5, 'fair': 2.0},
            'roe': {'excellent': 20, 'good': 15, 'fair': 10},
            'roa': {'excellent': 10, 'good': 7, 'fair': 5},
            'dividend_yield': {'excellent': 4, 'good': 3, 'fair': 2},
            'profit_margins': {'excellent': 20, 'good': 15, 'fair': 10},
            'debt_to_equity': {'excellent': 30, 'good': 50, 'fair': 70},
            'current_ratio': {'excellent': 2.0, 'good': 1.5, 'fair': 1.2},
            'earnings_growth': {'excellent': 15, 'good': 10, 'fair': 5},
            'revenue_growth': {'excellent': 10, 'good': 7, 'fair': 5}
        }
        
        # Scoring weights
        self.weights = {
            'valuation_score': 0.25,      # P/E, P/B ratios
            'profitability_score': 0.25,  # ROE, ROA, margins
            'financial_strength_score': 0.20,  # Debt ratios, current ratio
            'growth_score': 0.15,         # Earnings and revenue growth
            'dividend_score': 0.15        # Dividend yield and sustainability
        }
    
    def calculate_comprehensive_score(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive investment score with detailed breakdown"""
        try:
            # Calculate individual component scores
            valuation_score = self._calculate_valuation_score(stock_data)
            profitability_score = self._calculate_profitability_score(stock_data)
            financial_strength_score = self._calculate_financial_strength_score(stock_data)
            growth_score = self._calculate_growth_score(stock_data)
            dividend_score = self._calculate_dividend_score(stock_data)
            
            # Calculate weighted total score
            component_scores = {
                'valuation_score': valuation_score,
                'profitability_score': profitability_score,
                'financial_strength_score': financial_strength_score,
                'growth_score': growth_score,
                'dividend_score': dividend_score
            }
            
            # Only include components that have valid scores
            valid_components = {k: v for k, v in component_scores.items() if v is not None}
            
            if not valid_components:
                return self._create_score_result(0, component_scores, "Insufficient data for scoring")
            
            # Calculate weighted average of valid components
            total_weight = sum(self.weights.get(k, 0) for k in valid_components.keys())
            if total_weight == 0:
                return self._create_score_result(0, component_scores, "No valid scoring components")
            
            weighted_score = sum(
                score * self.weights.get(component, 0) 
                for component, score in valid_components.items()
            ) / total_weight * 100
            
            # Generate overall assessment
            assessment = self._generate_assessment(weighted_score, component_scores)
            
            return self._create_score_result(weighted_score, component_scores, assessment)
            
        except Exception as e:
            self.logger.error(f"Error calculating score: {e}")
            return self._create_score_result(0, {}, f"Scoring error: {str(e)}")
    
    def _calculate_valuation_score(self, data: Dict) -> Optional[float]:
        """Calculate valuation score based on P/E and P/B ratios"""
        pe_ratio = data.get('pe_ratio')
        pb_ratio = data.get('pb_ratio')
        
        scores = []
        
        # P/E Ratio scoring
        if pe_ratio is not None and pe_ratio > 0:
            if pe_ratio <= self.thresholds['pe_ratio']['excellent']:
                scores.append(100)
            elif pe_ratio <= self.thresholds['pe_ratio']['good']:
                scores.append(80)
            elif pe_ratio <= self.thresholds['pe_ratio']['fair']:
                scores.append(60)
            else:
                scores.append(30)
        
        # P/B Ratio scoring
        if pb_ratio is not None and pb_ratio > 0:
            if pb_ratio <= self.thresholds['pb_ratio']['excellent']:
                scores.append(100)
            elif pb_ratio <= self.thresholds['pb_ratio']['good']:
                scores.append(80)
            elif pb_ratio <= self.thresholds['pb_ratio']['fair']:
                scores.append(60)
            else:
                scores.append(30)
        
        return np.mean(scores) if scores else None
    
    def _calculate_profitability_score(self, data: Dict) -> Optional[float]:
        """Calculate profitability score"""
        roe = data.get('roe')
        roa = data.get('roa')
        profit_margins = data.get('profit_margins')
        
        scores = []
        
        # ROE scoring
        if roe is not None:
            roe_percent = roe * 100 if roe < 1 else roe
            if roe_percent >= self.thresholds['roe']['excellent']:
                scores.append(100)
            elif roe_percent >= self.thresholds['roe']['good']:
                scores.append(80)
            elif roe_percent >= self.thresholds['roe']['fair']:
                scores.append(60)
            else:
                scores.append(30)
        
        # ROA scoring
        if roa is not None:
            roa_percent = roa * 100 if roa < 1 else roa
            if roa_percent >= self.thresholds['roa']['excellent']:
                scores.append(100)
            elif roa_percent >= self.thresholds['roa']['good']:
                scores.append(80)
            elif roa_percent >= self.thresholds['roa']['fair']:
                scores.append(60)
            else:
                scores.append(30)
        
        # Profit margins scoring
        if profit_margins is not None:
            margins_percent = profit_margins * 100 if profit_margins < 1 else profit_margins
            if margins_percent >= self.thresholds['profit_margins']['excellent']:
                scores.append(100)
            elif margins_percent >= self.thresholds['profit_margins']['good']:
                scores.append(80)
            elif margins_percent >= self.thresholds['profit_margins']['fair']:
                scores.append(60)
            else:
                scores.append(30)
        
        return np.mean(scores) if scores else None
    
    def _calculate_financial_strength_score(self, data: Dict) -> Optional[float]:
        """Calculate financial strength score"""
        debt_to_equity = data.get('debt_to_equity')
        current_ratio = data.get('current_ratio')
        
        scores = []
        
        # Debt-to-equity scoring (lower is better)
        if debt_to_equity is not None:
            if debt_to_equity <= self.thresholds['debt_to_equity']['excellent']:
                scores.append(100)
            elif debt_to_equity <= self.thresholds['debt_to_equity']['good']:
                scores.append(80)
            elif debt_to_equity <= self.thresholds['debt_to_equity']['fair']:
                scores.append(60)
            else:
                scores.append(30)
        
        # Current ratio scoring
        if current_ratio is not None:
            if current_ratio >= self.thresholds['current_ratio']['excellent']:
                scores.append(100)
            elif current_ratio >= self.thresholds['current_ratio']['good']:
                scores.append(80)
            elif current_ratio >= self.thresholds['current_ratio']['fair']:
                scores.append(60)
            else:
                scores.append(30)
        
        return np.mean(scores) if scores else None
    
    def _calculate_growth_score(self, data: Dict) -> Optional[float]:
        """Calculate growth score"""
        earnings_growth = data.get('earnings_growth')
        revenue_growth = data.get('revenue_growth')
        
        scores = []
        
        # Earnings growth scoring
        if earnings_growth is not None:
            growth_percent = earnings_growth * 100 if earnings_growth < 1 else earnings_growth
            if growth_percent >= self.thresholds['earnings_growth']['excellent']:
                scores.append(100)
            elif growth_percent >= self.thresholds['earnings_growth']['good']:
                scores.append(80)
            elif growth_percent >= self.thresholds['earnings_growth']['fair']:
                scores.append(60)
            else:
                scores.append(30)
        
        # Revenue growth scoring
        if revenue_growth is not None:
            growth_percent = revenue_growth * 100 if revenue_growth < 1 else revenue_growth
            if growth_percent >= self.thresholds['revenue_growth']['excellent']:
                scores.append(100)
            elif growth_percent >= self.thresholds['revenue_growth']['good']:
                scores.append(80)
            elif growth_percent >= self.thresholds['revenue_growth']['fair']:
                scores.append(60)
            else:
                scores.append(30)
        
        return np.mean(scores) if scores else None
    
    def _calculate_dividend_score(self, data: Dict) -> Optional[float]:
        """Calculate dividend score"""
        dividend_yield = data.get('dividend_yield', 0)
        payout_ratio = data.get('payout_ratio')
        
        # Base dividend yield scoring
        if dividend_yield >= self.thresholds['dividend_yield']['excellent']:
            yield_score = 100
        elif dividend_yield >= self.thresholds['dividend_yield']['good']:
            yield_score = 80
        elif dividend_yield >= self.thresholds['dividend_yield']['fair']:
            yield_score = 60
        elif dividend_yield > 0:
            yield_score = 40
        else:
            yield_score = 0
        
        # Adjust for payout ratio sustainability
        if payout_ratio is not None:
            payout_percent = payout_ratio * 100 if payout_ratio < 1 else payout_ratio
            if payout_percent > 100:  # Unsustainable
                yield_score *= 0.5
            elif payout_percent > 80:  # High risk
                yield_score *= 0.7
            elif payout_percent > 60:  # Moderate
                yield_score *= 0.9
            # else: sustainable (no adjustment)
        
        return yield_score
    
    def _generate_assessment(self, score: float, components: Dict) -> str:
        """Generate human-readable assessment"""
        if score >= 80:
            grade = "Excellent"
        elif score >= 70:
            grade = "Good"
        elif score >= 60:
            grade = "Fair"
        elif score >= 40:
            grade = "Below Average"
        else:
            grade = "Poor"
        
        # Identify strongest and weakest areas
        valid_components = {k: v for k, v in components.items() if v is not None}
        if valid_components:
            strongest = max(valid_components, key=valid_components.get)
            weakest = min(valid_components, key=valid_components.get)
            
            return f"{grade} - Strongest: {strongest.replace('_', ' ').title()}, Weakest: {weakest.replace('_', ' ').title()}"
        else:
            return grade
    
    def _create_score_result(self, total_score: float, components: Dict, assessment: str) -> Dict:
        """Create standardized score result"""
        return {
            'total_score': round(total_score, 1),
            'assessment': assessment,
            'component_scores': {k: round(v, 1) if v is not None else None for k, v in components.items()},
            'score_breakdown': {
                'valuation': components.get('valuation_score'),
                'profitability': components.get('profitability_score'),
                'financial_strength': components.get('financial_strength_score'),
                'growth': components.get('growth_score'),
                'dividend': components.get('dividend_score')
            }
        }
    
    def update_thresholds(self, **kwargs):
        """Update scoring thresholds"""
        for key, value in kwargs.items():
            if key in self.thresholds:
                if isinstance(value, dict):
                    self.thresholds[key].update(value)
                else:
                    # For backward compatibility
                    if key == 'per_threshold':
                        self.thresholds['pe_ratio']['fair'] = value
                    elif key == 'pbr_threshold':
                        self.thresholds['pb_ratio']['fair'] = value
                    elif key == 'roe_threshold':
                        self.thresholds['roe']['fair'] = value