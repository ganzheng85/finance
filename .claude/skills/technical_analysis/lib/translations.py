"""
Translations for Technical Analysis Reports
Supports English and Chinese languages
"""

TRANSLATIONS = {
    'en': {
        # Report sections
        'technical_analysis': 'Technical Analysis',
        'executive_summary': 'Executive Summary',
        'trend_analysis': 'Trend Analysis',
        'summary': 'Summary',
        'key_indicators': 'Key Technical Indicators',
        'volatility_analysis': 'Volatility Analysis',
        'volume_analysis': 'Volume Analysis',
        'support_resistance': 'Key Support & Resistance Levels',
        'trading_zones': 'Trading Zones',
        'technical_patterns': 'Technical Patterns & Setups',
        'recent_price_action': 'Recent Price Action (Last 10 Days)',

        # Trend section
        'trend_direction': 'Trend Direction',
        'primary_pattern': 'Primary Pattern',
        'volatility_level': 'Volatility Level',
        'volume_level': 'Volume Level',
        'overall_direction': 'Overall Direction',
        'strength': 'Strength',
        'technical_score': 'Technical Score',
        'price_trend': 'Price Trend',
        'volume_trend': 'Volume Trend',
        'bullish_signals': 'Bullish Signals',
        'bearish_signals': 'Bearish Signals',
        'confidence': 'confidence',

        # Table headers
        'indicator': 'Indicator',
        'value': 'Value',
        'signal': 'Signal',
        'level': 'Level',
        'type': 'Type',
        'distance': 'Distance',
        'date': 'Date',
        'close': 'Close',
        'volume': 'Volume',

        # Indicators
        'rsi': 'RSI(14)',
        'macd_histogram': 'MACD Histogram',
        'atr': 'ATR(14)',
        'adx': 'ADX(14)',
        'price_vs_sma200': 'Price vs SMA(200)',
        'bollinger_b': 'Bollinger %B',

        # Signals
        'oversold': 'OVERSOLD',
        'overbought': 'OVERBOUGHT',
        'neutral': 'NEUTRAL',
        'bullish': 'BULLISH',
        'bearish': 'BEARISH',
        'strong_trend': 'STRONG TREND',
        'weak_trend': 'WEAK TREND',
        'above': 'ABOVE',
        'below': 'BELOW',
        'within_bands': 'WITHIN BANDS',
        'above_bands': 'ABOVE BANDS',
        'below_bands': 'BELOW BANDS',
        'high_volatility': 'HIGH VOLATILITY',
        'normal': 'NORMAL',
        'low_volatility': 'LOW VOLATILITY',

        # Volatility
        'level': 'Level',
        'annualized_volatility': 'Annualized Volatility',
        'historical_percentile': 'Historical Percentile',
        'bollinger_squeeze': 'Bollinger Squeeze',
        'yes': 'YES',
        'no': 'NO',
        'percentile': 'percentile',

        # Volume
        'volume_trend': 'Volume Trend',
        'average_volume': 'Average Volume',
        'relative_volume': 'Relative Volume',
        'increasing': 'INCREASING',
        'decreasing': 'DECREASING',
        'stable': 'STABLE',

        # Support/Resistance
        'current_price': 'Current Price',
        'resistance_levels': 'Resistance Levels (Above Current Price)',
        'support_levels': 'Support Levels (Below Current Price)',
        'support_zone': 'Support Zone',
        'near_term_pivot': 'Near-term Pivot',
        'resistance_zone': 'Resistance Zone',
        'higher_resistance': 'Higher Resistance (from earlier period)',
        'roughly': 'roughly',
        'around': 'around',

        # Patterns
        'pattern': 'Pattern',
        'confidence_level': 'Confidence Level',
        'observation': 'Observation',
        'technical_details': 'Technical Details',
        'no_clear_pattern': 'NO CLEAR PATTERN',
        'low': 'LOW',
        'medium': 'MEDIUM',
        'high': 'HIGH',
        'no_pattern_identified': 'No clear technical pattern identified',
        'mixed_signals': 'Mixed signals or neutral trend conditions',

        # Price action
        'change': 'Change',

        # Misc
        'generated_on': 'Generated on',
        'ticker': 'Ticker',
        'atr_description': 'useful for stop-loss/position sizing',
        'as_percent_of_price': 'as % of price',

        # Disclaimer
        'disclaimer': 'Note: This report provides technical indicators and data analysis for research purposes. It does not constitute investment advice or personalized recommendations.',

        # Bottom Disclaimer Section
        'disclaimer.title': 'Important Disclaimer',
        'disclaimer.subtitle': 'RESEARCH TOOL - NOT INVESTMENT ADVICE',
        'disclaimer.intro1': 'This technical analysis report is provided as a research tool and data summary for educational purposes only.',
        'disclaimer.intro2': 'It presents technical indicators, historical patterns, and statistical analysis based on publicly available market data.',
        'disclaimer.not.title': 'This report does NOT:',
        'disclaimer.not.1': 'Constitute personalized investment advice or recommendations',
        'disclaimer.not.2': 'Consider your individual financial situation, objectives, or risk tolerance',
        'disclaimer.not.3': 'Guarantee future performance or predict market outcomes',
        'disclaimer.not.4': 'Replace the need for consultation with licensed financial professionals',
        'disclaimer.notes.title': 'Important Notes:',
        'disclaimer.notes.1': 'Technical patterns are historical observations and may not repeat',
        'disclaimer.notes.2': 'Past performance does not indicate future results',
        'disclaimer.notes.3': 'Markets can change rapidly and unexpectedly',
        'disclaimer.notes.4': 'All investment decisions carry risk of loss',
        'disclaimer.responsibility': 'You are solely responsible for your own investment decisions. Always conduct thorough research and consult with qualified financial advisors before making any investment or trading decisions.',
        'disclaimer.generated': 'Report Generated By:',
        'disclaimer.tool': 'Technical Analysis Research Tool',
        'disclaimer.timestamp': 'Timestamp:',
    },
    'zh': {
        # Report sections
        'technical_analysis': '技术分析',
        'executive_summary': '执行摘要',
        'trend_analysis': '趋势分析',
        'summary': '摘要',
        'key_indicators': '关键技术指标',
        'volatility_analysis': '波动性分析',
        'volume_analysis': '成交量分析',
        'support_resistance': '主要支撑与阻力位',
        'trading_zones': '交易区间',
        'technical_patterns': '技术形态与设置',
        'recent_price_action': '近期价格走势（最近10天）',

        # Trend section
        'trend_direction': '趋势方向',
        'primary_pattern': '主要形态',
        'volatility_level': '波动水平',
        'volume_level': '成交量水平',
        'overall_direction': '整体方向',
        'strength': '强度',
        'technical_score': '技术评分',
        'price_trend': '价格趋势',
        'volume_trend': '成交量趋势',
        'bullish_signals': '看涨信号',
        'bearish_signals': '看跌信号',
        'confidence': '置信度',

        # Table headers
        'indicator': '指标',
        'value': '数值',
        'signal': '信号',
        'level': '水平',
        'type': '类型',
        'distance': '距离',
        'date': '日期',
        'close': '收盘价',
        'volume': '成交量',

        # Indicators
        'rsi': 'RSI(14)',
        'macd_histogram': 'MACD柱状图',
        'atr': 'ATR(14)',
        'adx': 'ADX(14)',
        'price_vs_sma200': '价格相对SMA(200)',
        'bollinger_b': '布林带%B',

        # Signals
        'oversold': '超卖',
        'overbought': '超买',
        'neutral': '中性',
        'bullish': '看涨',
        'bearish': '看跌',
        'strong_trend': '强趋势',
        'weak_trend': '弱趋势',
        'above': '之上',
        'below': '之下',
        'within_bands': '区间内',
        'above_bands': '区间上方',
        'below_bands': '区间下方',
        'high_volatility': '高波动',
        'normal': '正常',
        'low_volatility': '低波动',

        # Volatility
        'level': '水平',
        'annualized_volatility': '年化波动率',
        'historical_percentile': '历史百分位',
        'bollinger_squeeze': '布林带收窄',
        'yes': '是',
        'no': '否',
        'percentile': '百分位',

        # Volume
        'volume_trend': '成交量趋势',
        'average_volume': '平均成交量',
        'relative_volume': '相对成交量',
        'increasing': '增加',
        'decreasing': '减少',
        'stable': '稳定',

        # Support/Resistance
        'current_price': '当前价格',
        'resistance_levels': '阻力位（高于当前价格）',
        'support_levels': '支撑位（低于当前价格）',
        'support_zone': '支撑区间',
        'near_term_pivot': '短期枢纽',
        'resistance_zone': '阻力区间',
        'higher_resistance': '更高阻力位（来自早期）',
        'roughly': '大约',
        'around': '约',

        # Patterns
        'pattern': '形态',
        'confidence_level': '置信度',
        'observation': '观察',
        'technical_details': '技术细节',
        'no_clear_pattern': '无明确形态',
        'low': '低',
        'medium': '中',
        'high': '高',
        'no_pattern_identified': '未识别出明确的技术形态',
        'mixed_signals': '混合信号或中性趋势条件',

        # Price action
        'change': '变化',

        # Misc
        'generated_on': '生成时间',
        'ticker': '股票代码',
        'atr_description': '用于止损/仓位管理',
        'as_percent_of_price': '占价格百分比',

        # Disclaimer
        'disclaimer': '注意：本报告仅提供技术指标和数据分析用于研究目的。它不构成投资建议或个性化推荐。',

        # Bottom Disclaimer Section
        'disclaimer.title': '重要免责声明',
        'disclaimer.subtitle': '研究工具 - 非投资建议',
        'disclaimer.intro1': '本技术分析报告仅作为研究工具和数据摘要供教育目的使用。',
        'disclaimer.intro2': '它基于公开市场数据呈现技术指标、历史形态和统计分析。',
        'disclaimer.not.title': '本报告不提供：',
        'disclaimer.not.1': '个性化投资建议或推荐',
        'disclaimer.not.2': '考虑您个人财务状况、目标或风险承受能力',
        'disclaimer.not.3': '保证未来表现或预测市场结果',
        'disclaimer.not.4': '替代持牌金融专业人士咨询的需要',
        'disclaimer.notes.title': '重要提示：',
        'disclaimer.notes.1': '技术形态是历史观察，可能不会重复',
        'disclaimer.notes.2': '过去的表现不代表未来结果',
        'disclaimer.notes.3': '市场可能迅速且意外地变化',
        'disclaimer.notes.4': '所有投资决策都承担损失风险',
        'disclaimer.responsibility': '您对自己的投资决策负全部责任。在做出任何投资或交易决策之前，请务必进行全面研究并咨询合格的财务顾问。',
        'disclaimer.generated': '报告生成工具：',
        'disclaimer.tool': '技术分析研究工具',
        'disclaimer.timestamp': '时间戳：',
    }
}


def get_text(key: str, lang: str = 'en') -> str:
    """
    Get translated text for a given key

    Args:
        key: Translation key
        lang: Language code ('en' or 'zh')

    Returns:
        Translated text, or key if not found
    """
    if lang not in TRANSLATIONS:
        lang = 'en'

    return TRANSLATIONS[lang].get(key, key)


def translate(key: str, lang: str = 'en') -> str:
    """Alias for get_text"""
    return get_text(key, lang)
