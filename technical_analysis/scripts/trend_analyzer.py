"""
Trend Analyzer - Analyze stock trends based on technical factors.

This module provides sophisticated trend analysis using multiple technical indicators.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple


class TrendAnalyzer:
    """
    Analyze stock trends using multiple technical factors.

    Provides:
    - Overall trend direction (bullish/bearish/neutral)
    - Strength of trend
    - Key support/resistance levels
    - Trading signals
    - Risk assessment
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize TrendAnalyzer with DataFrame containing technical factors.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with columns including technical factors
            Must have at least: ['date', 'adjusted_close']
        """
        self.df = df.sort_values('date').reset_index(drop=True)
        self.latest = self.df.iloc[-1]
        self.symbol = self.df['symbol'].iloc[0] if 'symbol' in self.df.columns else 'STOCK'

    def analyze_trend_direction(self) -> Dict:
        """
        Determine overall trend direction using multiple indicators.

        Returns
        -------
        dict
            {
                'direction': 'BULLISH', 'BEARISH', or 'NEUTRAL',
                'strength': float (0-10),
                'signals': list of contributing signals,
                'score': int (bullish signals - bearish signals)
            }
        """
        bullish_signals = []
        bearish_signals = []
        score = 0

        # 1. Price vs SMAs
        if 'dist_sma_200' in self.df.columns and pd.notna(self.latest['dist_sma_200']):
            dist_200 = self.latest['dist_sma_200']
            if dist_200 > 0.05:  # >5% above SMA(200)
                bullish_signals.append(f"Price {dist_200*100:.1f}% above SMA(200)")
                score += 2
            elif dist_200 < -0.05:
                bearish_signals.append(f"Price {-dist_200*100:.1f}% below SMA(200)")
                score -= 2

        if 'dist_sma_50' in self.df.columns and pd.notna(self.latest['dist_sma_50']):
            dist_50 = self.latest['dist_sma_50']
            if dist_50 > 0.03:
                bullish_signals.append(f"Price {dist_50*100:.1f}% above SMA(50)")
                score += 1
            elif dist_50 < -0.03:
                bearish_signals.append(f"Price {-dist_50*100:.1f}% below SMA(50)")
                score -= 1

        # 2. SMA alignment (Golden/Death Cross)
        if 'sma_dist_20_50' in self.df.columns and pd.notna(self.latest['sma_dist_20_50']):
            sma_dist = self.latest['sma_dist_20_50']
            if sma_dist > 0.02:
                bullish_signals.append(f"SMA(20) {sma_dist*100:.1f}% above SMA(50) (Golden Cross)")
                score += 2
            elif sma_dist < -0.02:
                bearish_signals.append(f"SMA(20) {-sma_dist*100:.1f}% below SMA(50) (Death Cross)")
                score -= 2

        # 3. Momentum
        if 'momentum_score' in self.df.columns and pd.notna(self.latest['momentum_score']):
            mom = self.latest['momentum_score']
            if mom > 0.5:
                bullish_signals.append(f"Strong positive momentum ({mom:.2f})")
                score += 2
            elif mom < -0.5:
                bearish_signals.append(f"Strong negative momentum ({mom:.2f})")
                score -= 2

        # 4. MACD
        if 'macd_hist_12_26_9' in self.df.columns and pd.notna(self.latest['macd_hist_12_26_9']):
            macd = self.latest['macd_hist_12_26_9']
            if macd > 0:
                bullish_signals.append("MACD histogram positive")
                score += 1
            elif macd < 0:
                bearish_signals.append("MACD histogram negative")
                score -= 1

        # 5. RSI (overbought/oversold)
        if 'rsi_14' in self.df.columns and pd.notna(self.latest['rsi_14']):
            rsi = self.latest['rsi_14']
            if rsi < 30:
                bullish_signals.append(f"RSI oversold ({rsi:.1f}) - potential bounce")
                score += 1
            elif rsi > 70:
                bearish_signals.append(f"RSI overbought ({rsi:.1f}) - potential pullback")
                score -= 1

        # 6. ADX (trend strength)
        if 'adx_14' in self.df.columns and pd.notna(self.latest['adx_14']):
            adx = self.latest['adx_14']
            if adx > 25:
                # Strong trend, check direction
                if 'plus_di_14' in self.df.columns and 'minus_di_14' in self.df.columns:
                    plus_di = self.latest['plus_di_14']
                    minus_di = self.latest['minus_di_14']
                    if plus_di > minus_di:
                        bullish_signals.append(f"Strong uptrend (ADX {adx:.1f})")
                        score += 2
                    else:
                        bearish_signals.append(f"Strong downtrend (ADX {adx:.1f})")
                        score -= 2

        # Determine overall direction and strength
        if score >= 3:
            direction = "BULLISH"
            strength = min(10, score)
        elif score <= -3:
            direction = "BEARISH"
            strength = min(10, abs(score))
        else:
            direction = "NEUTRAL"
            strength = 5

        return {
            'direction': direction,
            'strength': strength,
            'score': score,
            'bullish_signals': bullish_signals,
            'bearish_signals': bearish_signals
        }

    def analyze_volatility(self) -> Dict:
        """
        Analyze current volatility conditions.

        Returns
        -------
        dict
            Volatility analysis including level, squeeze conditions, etc.
        """
        result = {
            'level': 'UNKNOWN',
            'annualized_pct': None,
            'percentile': None,
            'squeeze': False,
            'expansion': False
        }

        # Current volatility
        if 'volatility' in self.df.columns and pd.notna(self.latest['volatility']):
            vol = self.latest['volatility']
            result['annualized_pct'] = vol * 100

            # Calculate percentile
            vol_series = self.df['volatility'].dropna()
            if len(vol_series) > 0:
                percentile = (vol_series < vol).sum() / len(vol_series)
                result['percentile'] = percentile * 100

                if percentile < 0.2:
                    result['level'] = 'LOW'
                elif percentile > 0.8:
                    result['level'] = 'HIGH'
                else:
                    result['level'] = 'NORMAL'

        # Bollinger squeeze
        if 'bb_squeeze' in self.df.columns and pd.notna(self.latest['bb_squeeze']):
            result['squeeze'] = bool(self.latest['bb_squeeze'])

        # Check for volatility expansion (BB width increasing)
        if 'bb_width' in self.df.columns and len(self.df) >= 5:
            recent_width = self.df['bb_width'].tail(5)
            if recent_width.iloc[-1] > recent_width.iloc[0]:
                result['expansion'] = True

        return result

    def analyze_volume(self) -> Dict:
        """
        Analyze volume patterns.

        Returns
        -------
        dict
            Volume analysis including relative volume, trends, etc.
        """
        result = {
            'relative': None,
            'level': 'UNKNOWN',
            'trend': 'UNKNOWN',
            'signals': []
        }

        # Relative volume
        if 'relative_volume' in self.df.columns and pd.notna(self.latest['relative_volume']):
            rvol = self.latest['relative_volume']
            result['relative'] = rvol

            if rvol > 2.0:
                result['level'] = 'VERY HIGH'
                result['signals'].append(f"Volume {rvol:.1f}x average - significant activity")
            elif rvol > 1.5:
                result['level'] = 'HIGH'
                result['signals'].append(f"Volume {rvol:.1f}x average - elevated interest")
            elif rvol < 0.5:
                result['level'] = 'LOW'
                result['signals'].append(f"Volume {rvol:.1f}x average - low participation")
            else:
                result['level'] = 'NORMAL'

        # Volume trend (increasing or decreasing)
        if 'volume' in self.df.columns and len(self.df) >= 5:
            recent_vol = self.df['volume'].tail(5)
            if recent_vol.iloc[-1] > recent_vol.mean():
                result['trend'] = 'INCREASING'
            elif recent_vol.iloc[-1] < recent_vol.mean():
                result['trend'] = 'DECREASING'
            else:
                result['trend'] = 'STABLE'

        return result

    def identify_key_levels(self) -> Dict:
        """
        Identify key support and resistance levels.

        Returns
        -------
        dict
            Support and resistance levels based on SMAs and recent highs/lows
        """
        levels = {
            'current_price': self.latest['adjusted_close'],
            'support': [],
            'resistance': []
        }

        price = self.latest['adjusted_close']

        # SMAs as support/resistance
        # Note: We need to calculate SMA values from dist_sma_X columns since actual SMAs were dropped
        dist_sma_cols = [col for col in self.df.columns if col.startswith('dist_sma_')]
        for col in dist_sma_cols:
            if pd.notna(self.latest[col]):
                dist_pct = self.latest[col]  # This is the % distance (e.g., 0.60 = 60% above)
                sma_val = price / (1 + dist_pct)  # Back-calculate the SMA value
                window = col.split('_')[-1]

                if sma_val < price:
                    levels['support'].append({
                        'level': sma_val,
                        'type': f'SMA({window})',
                        'distance_pct': (price - sma_val) / price * 100
                    })
                elif sma_val > price:
                    levels['resistance'].append({
                        'level': sma_val,
                        'type': f'SMA({window})',
                        'distance_pct': (sma_val - price) / price * 100
                    })

        # Recent highs/lows (last 30 days)
        if len(self.df) >= 30:
            recent_30 = self.df.tail(30)
            high_30 = recent_30['high'].max() if 'high' in self.df.columns else recent_30['adjusted_close'].max()
            low_30 = recent_30['low'].min() if 'low' in self.df.columns else recent_30['adjusted_close'].min()

            if high_30 > price:
                levels['resistance'].append({
                    'level': high_30,
                    'type': '30-day High',
                    'distance_pct': (high_30 - price) / price * 100
                })

            if low_30 < price:
                levels['support'].append({
                    'level': low_30,
                    'type': '30-day Low',
                    'distance_pct': (price - low_30) / price * 100
                })

        # Sort by distance from current price
        levels['support'] = sorted(levels['support'], key=lambda x: x['distance_pct'])
        levels['resistance'] = sorted(levels['resistance'], key=lambda x: x['distance_pct'])

        return levels

    def generate_trading_signals(self) -> List[Dict]:
        """
        Generate technical setup indicators based on technical factors.

        Note: These are analytical observations, not trading recommendations.

        Returns
        -------
        list of dict
            Technical setup indicators with pattern, confidence, and context
        """
        signals = []

        # Get trend analysis
        trend = self.analyze_trend_direction()

        # Strong bullish setup indicator
        if trend['direction'] == 'BULLISH' and trend['strength'] >= 7:
            signals.append({
                'action': 'STRONG BULLISH PATTERN',
                'confidence': 'HIGH',
                'reason': f"Technical indicators show strong bullish alignment (score: {trend['score']})",
                'details': trend['bullish_signals']
            })

        # Strong bearish setup indicator
        elif trend['direction'] == 'BEARISH' and trend['strength'] >= 7:
            signals.append({
                'action': 'STRONG BEARISH PATTERN',
                'confidence': 'HIGH',
                'reason': f"Technical indicators show strong bearish alignment (score: {trend['score']})",
                'details': trend['bearish_signals']
            })

        # Oversold bounce pattern
        if 'rsi_14' in self.df.columns and pd.notna(self.latest['rsi_14']):
            rsi = self.latest['rsi_14']
            if rsi < 30 and 'macd_hist_12_26_9' in self.df.columns:
                macd = self.latest['macd_hist_12_26_9']
                if pd.notna(macd) and macd > 0:
                    signals.append({
                        'action': 'OVERSOLD REVERSAL PATTERN',
                        'confidence': 'MEDIUM',
                        'reason': 'Indicators suggest potential oversold reversal pattern',
                        'details': [f'RSI in oversold territory ({rsi:.1f})', 'MACD showing positive divergence']
                    })

        # Overbought pullback pattern
        if 'rsi_14' in self.df.columns and pd.notna(self.latest['rsi_14']):
            rsi = self.latest['rsi_14']
            if rsi > 70 and 'macd_hist_12_26_9' in self.df.columns:
                macd = self.latest['macd_hist_12_26_9']
                if pd.notna(macd) and macd < 0:
                    signals.append({
                        'action': 'OVERBOUGHT PULLBACK PATTERN',
                        'confidence': 'MEDIUM',
                        'reason': 'Indicators suggest potential overbought pullback pattern',
                        'details': [f'RSI in overbought territory ({rsi:.1f})', 'MACD showing negative divergence']
                    })

        # Bollinger squeeze breakout pattern
        vol_analysis = self.analyze_volatility()
        if vol_analysis['squeeze'] and vol_analysis['expansion']:
            direction = trend['direction']
            if direction != 'NEUTRAL':
                signals.append({
                    'action': f'VOLATILITY BREAKOUT PATTERN ({direction})',
                    'confidence': 'MEDIUM',
                    'reason': f'Bollinger squeeze breakout pattern observed with {direction.lower()} bias',
                    'details': ['Low volatility squeeze expanding', f'Trend direction: {direction}']
                })

        # No clear pattern
        if not signals:
            signals.append({
                'action': 'NEUTRAL - NO CLEAR PATTERN',
                'confidence': 'LOW',
                'reason': 'No clear technical pattern identified',
                'details': ['Mixed signals or neutral trend conditions']
            })

        return signals

    def generate_report(self) -> str:
        """
        Generate a comprehensive text report of the technical analysis.

        Returns
        -------
        str
            Formatted report text
        """
        # Get all analyses
        trend = self.analyze_trend_direction()
        vol = self.analyze_volatility()
        volume = self.analyze_volume()
        levels = self.identify_key_levels()
        signals = self.generate_trading_signals()

        # Build report
        report = []
        report.append("=" * 80)
        report.append(f"TECHNICAL ANALYSIS REPORT - {self.symbol}")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Analysis Period: {self.df['date'].min().date()} to {self.df['date'].max().date()}")
        report.append(f"Current Price: ${self.latest['adjusted_close']:.2f}")
        report.append("")

        # Trend Analysis
        report.append("=" * 80)
        report.append("TREND ANALYSIS")
        report.append("=" * 80)
        report.append(f"Direction: {trend['direction']}")
        report.append(f"Strength: {trend['strength']}/10")
        report.append(f"Score: {trend['score']:+d}")
        report.append("")

        if trend['bullish_signals']:
            report.append("Bullish Signals:")
            for signal in trend['bullish_signals']:
                report.append(f"  + {signal}")
            report.append("")

        if trend['bearish_signals']:
            report.append("Bearish Signals:")
            for signal in trend['bearish_signals']:
                report.append(f"  - {signal}")
            report.append("")

        # Volatility Analysis
        report.append("=" * 80)
        report.append("VOLATILITY ANALYSIS")
        report.append("=" * 80)
        report.append(f"Level: {vol['level']}")
        if vol['annualized_pct']:
            report.append(f"Annualized Volatility: {vol['annualized_pct']:.2f}%")
        if vol['percentile']:
            report.append(f"Historical Percentile: {vol['percentile']:.1f}th")
        report.append(f"Bollinger Squeeze: {'YES' if vol['squeeze'] else 'NO'}")
        report.append(f"Volatility Expanding: {'YES' if vol['expansion'] else 'NO'}")
        report.append("")

        # Volume Analysis
        report.append("=" * 80)
        report.append("VOLUME ANALYSIS")
        report.append("=" * 80)
        if volume['relative']:
            report.append(f"Relative Volume: {volume['relative']:.2f}x ({volume['level']})")
        report.append(f"Volume Trend: {volume['trend']}")
        if volume['signals']:
            for sig in volume['signals']:
                report.append(f"  * {sig}")
        report.append("")

        # Key Levels
        report.append("=" * 80)
        report.append("KEY LEVELS")
        report.append("=" * 80)
        report.append(f"Current Price: ${levels['current_price']:.2f}")
        report.append("")

        if levels['resistance']:
            report.append("Resistance Levels:")
            for r in levels['resistance'][:3]:  # Top 3
                report.append(f"  ${r['level']:.2f} ({r['type']}) - {r['distance_pct']:.2f}% above")
            report.append("")

        if levels['support']:
            report.append("Support Levels:")
            for s in levels['support'][:3]:  # Top 3
                report.append(f"  ${s['level']:.2f} ({s['type']}) - {s['distance_pct']:.2f}% below")
            report.append("")

        # Technical Patterns & Setups
        report.append("=" * 80)
        report.append("TECHNICAL PATTERNS & SETUPS")
        report.append("=" * 80)

        for i, signal in enumerate(signals, 1):
            report.append(f"Pattern #{i}:")
            report.append(f"  Type: {signal['action']}")
            report.append(f"  Confidence: {signal['confidence']}")
            report.append(f"  Observation: {signal['reason']}")
            if signal['details']:
                report.append("  Details:")
                for detail in signal['details']:
                    report.append(f"    - {detail}")
            report.append("")

        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)

        return "\n".join(report)


if __name__ == '__main__':
    # Example usage
    print("TrendAnalyzer module loaded.")
    print("Usage: from trend_analyzer import TrendAnalyzer")
    print("       analyzer = TrendAnalyzer(df)")
    print("       report = analyzer.generate_report()")
