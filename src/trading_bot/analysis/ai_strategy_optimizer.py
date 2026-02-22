import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from ai.ai_client_factory import AIClientFactory

logger = logging.getLogger(__name__)


class AIStrategyOptimizer:
    """
    基于大模型的品种智能配置引擎
    根据品种画像自动生成最优交易策略参数
    """

    def __init__(self, model_name: str = "qwen"):
        self.ai_factory = AIClientFactory()
        self.llm_client = self.ai_factory.create_client(model_name)
        self.system_prompt = self._build_system_prompt()
        self.parameter_templates = self._load_parameter_templates()

    def optimize_strategy(self, symbol_profile: Dict[str, Any], 
                         historical_performance: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        根据品种画像优化交易策略参数
        
        Args:
            symbol_profile: 品种画像数据
            historical_performance: 历史表现数据（可选）
            
        Returns:
            优化后的策略参数
        """
        symbol = symbol_profile.get('symbol', 'UNKNOWN')
        logger.info(f"Optimizing strategy for {symbol} using AI...")
        
        prompt = self._build_optimization_prompt(symbol_profile, historical_performance)
        
        try:
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000,
                "stream": False
            }
            
            response = self.llm_client._call_api("chat/completions", payload, symbol=symbol)
            
            if response and 'choices' in response and len(response['choices']) > 0:
                content = response['choices'][0]['message']['content']
                optimized_params = self._parse_ai_response(content, symbol)
                
                logger.info(f"AI optimization completed for {symbol}")
                return optimized_params
            else:
                logger.warning(f"AI response empty for {symbol}, using fallback")
                return self._generate_fallback_params(symbol_profile)
                
        except Exception as e:
            logger.error(f"AI optimization failed for {symbol}: {e}, using fallback")
            return self._generate_fallback_params(symbol_profile)

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """你是一个专业的量化交易策略优化专家，擅长根据市场品种特征自动配置最优交易参数。

你的任务是：
1. 分析品种的市场特征（波动性、流动性、交易时段等）
2. 根据历史表现调整参数（如果有）
3. 生成该品种的最优交易参数配置

请严格按照JSON格式返回结果，包含以下参数：
- position_size: 仓位大小（基于风险百分比）
- stop_loss_atr_multiplier: 止损ATR倍数
- take_profit_atr_multiplier: 止盈ATR倍数
- risk_per_trade: 单笔风险百分比
- max_daily_trades: 每日最大交易次数
- min_profit_target: 最小止盈目标（ATR倍数）
- trailing_stop_atr: 移动止损ATR倍数
- break_even_atr: 盈亏平衡ATR倍数
- confluence_threshold: 汇聚信号阈值
- position_multiplier: 仓位乘数
- optimal_timeframe: 最优交易周期
- volatility_adjustment: 波动性调整因子
- session_filters: 交易时段过滤器
- trend_following_mode: 是否启用趋势跟随模式
- mean_reversion_mode: 是否启用均值回归模式

返回格式：
{
  "optimized_parameters": {
    "position_size": 0.01,
    "stop_loss_atr_multiplier": 1.5,
    ...
  },
  "reasoning": "参数选择的原因",
  "risk_assessment": "风险评估",
  "confidence_score": 0.85
}
"""

    def _build_optimization_prompt(self, symbol_profile: Dict[str, Any], 
                                   historical_performance: Optional[Dict[str, Any]] = None) -> str:
        """构建优化提示词"""
        prompt = f"""请为以下交易品种优化交易策略参数：

## 品种基本信息
品种名称: {symbol_profile.get('symbol', 'UNKNOWN')}
分析日期: {symbol_profile.get('analyzed_at', 'N/A')}
历史数据天数: {symbol_profile.get('days_analyzed', 30)}

## 品种市场特征

### 波动性分析
{self._format_volatility_data(symbol_profile.get('volatility_metrics', {}))}

### 交易量分析
{self._format_volume_data(symbol_profile.get('volume_metrics', {}))}

### 价格行为分析
{self._format_price_data(symbol_profile.get('price_metrics', {}))}

### 点差分析
{self._format_spread_data(symbol_profile.get('spread_metrics', {}))}

### 交易时段分析
{self._format_session_data(symbol_profile.get('session_metrics', {}))}

### 相关性分析
{self._format_correlation_data(symbol_profile.get('correlation_metrics', {}))}

### 市场状态分析
{self._format_regime_data(symbol_profile.get('regime_metrics', {}))}

### 风险画像
{self._format_risk_data(symbol_profile.get('risk_profile', {}))}

### 最优交易周期
{self._format_timeframes_data(symbol_profile.get('optimal_timeframes', []))}

"""

        if historical_performance:
            prompt += f"\n## 历史表现数据\n{self._format_performance_data(historical_performance)}\n"

        prompt += """
请根据以上品种特征，生成最优的交易策略参数。考虑以下原则：
1. 高波动品种需要更宽的止损和更小的仓位
2. 高点差品种需要更高的止盈目标来覆盖成本
3. 趋势明显的品种适合趋势跟随策略
4. 震荡市场适合均值回归策略
5. 考虑不同交易时段的活跃度

返回严格的JSON格式结果。
"""
        return prompt

    def _parse_ai_response(self, content: str, symbol: str) -> Dict[str, Any]:
        """解析AI响应"""
        try:
            cleaned_content = content.strip()
            if "```json" in cleaned_content:
                cleaned_content = cleaned_content.split("```json")[1].split("```")[0]
            elif "```" in cleaned_content:
                cleaned_content = cleaned_content.split("```")[1].split("```")[0]
            
            result = json.loads(cleaned_content)
            
            if 'optimized_parameters' in result:
                params = result['optimized_parameters']
                params['symbol'] = symbol
                params['optimized_at'] = datetime.now().isoformat()
                params['reasoning'] = result.get('reasoning', '')
                params['risk_assessment'] = result.get('risk_assessment', '')
                params['confidence_score'] = result.get('confidence_score', 0.5)
                
                return params
            else:
                return self._generate_fallback_params_from_dict(result, symbol)
                
        except Exception as e:
            logger.error(f"Failed to parse AI response for {symbol}: {e}")
            return self._generate_fallback_params({'symbol': symbol})

    def _generate_fallback_params(self, symbol_profile: Dict[str, Any]) -> Dict[str, Any]:
        """生成备用参数"""
        symbol = symbol_profile.get('symbol', 'UNKNOWN')
        risk_profile = symbol_profile.get('risk_profile', {})
        volatility_metrics = symbol_profile.get('volatility_metrics', {}).get('H1', {})
        spread_metrics = symbol_profile.get('spread_metrics', {})
        regime_metrics = symbol_profile.get('regime_metrics', {})
        
        risk_level = risk_profile.get('risk_level', 'medium')
        volatility_percent = volatility_metrics.get('volatility_percent', 1.0)
        spread_ratio = spread_metrics.get('spread_to_atr_ratio', 0.05)
        trending_ratio = regime_metrics.get('trending_up_ratio', 0) + regime_metrics.get('trending_down_ratio', 0)
        
        if risk_level == 'high':
            base_risk = 0.5
            atr_multiplier_sl = 2.0
            atr_multiplier_tp = 3.0
        elif risk_level == 'low':
            base_risk = 2.0
            atr_multiplier_sl = 1.0
            atr_multiplier_tp = 2.0
        else:
            base_risk = 1.0
            atr_multiplier_sl = 1.5
            atr_multiplier_tp = 2.5
        
        if spread_ratio > 0.1:
            atr_multiplier_tp = max(atr_multiplier_tp, 4.0)
            base_risk *= 0.5
        
        position_size = max(0.01, round(base_risk / 100, 2))
        
        return {
            'symbol': symbol,
            'optimized_at': datetime.now().isoformat(),
            'optimized_parameters': {
                'position_size': position_size,
                'stop_loss_atr_multiplier': round(atr_multiplier_sl, 2),
                'take_profit_atr_multiplier': round(atr_multiplier_tp, 2),
                'risk_per_trade': round(base_risk, 2),
                'max_daily_trades': 10 if risk_level == 'low' else 5,
                'min_profit_target': round(atr_multiplier_tp * 0.5, 2),
                'trailing_stop_atr': round(atr_multiplier_sl * 0.8, 2),
                'break_even_atr': round(atr_multiplier_sl * 1.2, 2),
                'confluence_threshold': 3.0 if trending_ratio > 0.6 else 4.0,
                'position_multiplier': 1.0,
                'optimal_timeframe': 'H1' if trending_ratio > 0.5 else 'M15',
                'volatility_adjustment': round(volatility_percent / 100, 2),
                'session_filters': self._generate_session_filters(risk_level),
                'trend_following_mode': trending_ratio > 0.5,
                'mean_reversion_mode': trending_ratio <= 0.5
            },
            'reasoning': f'Fallback parameters based on risk level {risk_level}, volatility {volatility_percent}%, spread ratio {spread_ratio}',
            'risk_assessment': f'Generated using rule-based fallback due to AI unavailability',
            'confidence_score': 0.6
        }

    def _generate_fallback_params_from_dict(self, result: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """从字典生成备用参数"""
        params = result.get('optimized_parameters', result)
        params['symbol'] = symbol
        params['optimized_at'] = datetime.now().isoformat()
        params['reasoning'] = result.get('reasoning', 'Extracted from partial response')
        params['risk_assessment'] = result.get('risk_assessment', 'Unknown')
        params['confidence_score'] = result.get('confidence_score', 0.5)
        return params

    def _generate_session_filters(self, risk_level: str) -> Dict[str, bool]:
        """生成交易时段过滤器"""
        if risk_level == 'high':
            return {
                'asian_session': True,
                'london_session': True,
                'newyork_session': True,
                'overlap_session': True
            }
        else:
            return {
                'asian_session': True,
                'london_session': True,
                'newyork_session': True,
                'overlap_session': True
            }

    def _format_volatility_data(self, volatility_metrics: Dict[str, Any]) -> str:
        """格式化波动性数据"""
        if not volatility_metrics:
            return "无波动性数据"
        
        lines = []
        for tf, data in volatility_metrics.items():
            lines.append(f"- {tf}: 波动率 {data.get('volatility_percent', 0):.2f}%, ATR {data.get('avg_true_range', 0):.4f}")
        return "\n".join(lines)

    def _format_volume_data(self, volume_metrics: Dict[str, Any]) -> str:
        """格式化交易量数据"""
        if not volume_metrics:
            return "无交易量数据"
        
        lines = []
        for tf, data in volume_metrics.items():
            lines.append(f"- {tf}: 平均交易量 {data.get('avg_volume', 0):.0f}, 波动率 {data.get('volume_volatility', 0):.2f}%")
        return "\n".join(lines)

    def _format_price_data(self, price_metrics: Dict[str, Any]) -> str:
        """格式化价格数据"""
        if not price_metrics:
            return "无价格数据"
        
        return f"""趋势强度: {price_metrics.get('price_trend', 0):.4f}
偏度: {price_metrics.get('skewness', 0):.4f}
峰度: {price_metrics.get('kurtosis', 0):.4f}
动量因子: {price_metrics.get('momentum_factor', 0):.4f}
均值回归因子: {price_metrics.get('mean_reversion_factor', 0):.4f}"""

    def _format_spread_data(self, spread_metrics: Dict[str, Any]) -> str:
        """格式化点差数据"""
        if not spread_metrics:
            return "无点差数据"
        
        return f"""当前点差: {spread_metrics.get('current_spread', 0)} 点
点差百分比: {spread_metrics.get('spread_percent', 0):.4f}%
点差/ATR比: {spread_metrics.get('spread_to_atr_ratio', 0):.4f}"""

    def _format_session_data(self, session_metrics: Dict[str, Any]) -> str:
        """格式化交易时段数据"""
        if not session_metrics:
            return "无交易时段数据"
        
        active_hours = [k.replace('hour_', '') for k, v in session_metrics.items() 
                       if v.get('volume', 0) > 0]
        return f"活跃时段: {', '.join(active_hours) if active_hours else '无'}"

    def _format_correlation_data(self, correlation_metrics: Dict[str, float]) -> str:
        """格式化相关性数据"""
        if not correlation_metrics:
            return "无相关性数据"
        
        lines = []
        for symbol, corr in correlation_metrics.items():
            lines.append(f"- {symbol}: {corr:.3f}")
        return "\n".join(lines)

    def _format_regime_data(self, regime_metrics: Dict[str, Any]) -> str:
        """格式化市场状态数据"""
        if not regime_metrics:
            return "无市场状态数据"
        
        return f"""上升趋势比例: {regime_metrics.get('trending_up_ratio', 0):.2%}
下降趋势比例: {regime_metrics.get('trending_down_ratio', 0):.2%}
震荡比例: {regime_metrics.get('ranging_ratio', 0):.2%}
当前状态: {regime_metrics.get('current_regime', 'unknown')}"""

    def _format_risk_data(self, risk_profile: Dict[str, Any]) -> str:
        """格式化风险数据"""
        if not risk_profile:
            return "无风险数据"
        
        return f"""风险等级: {risk_profile.get('risk_level', 'unknown')}
波动性分数: {risk_profile.get('volatility_score', 0):.4f}
点差效率: {risk_profile.get('spread_efficiency', 0):.4f}
趋势适应性: {risk_profile.get('trend_suitability', 0):.4f}
综合分数: {risk_profile.get('overall_score', 0):.4f}"""

    def _format_timeframes_data(self, timeframes: list) -> str:
        """格式化周期数据"""
        if not timeframes:
            return "无周期数据"
        return f"最优周期: {', '.join(timeframes)}"

    def _format_performance_data(self, performance: Dict[str, Any]) -> str:
        """格式化表现数据"""
        if not performance:
            return "无表现数据"
        
        return f"""总交易次数: {performance.get('total_trades', 0)}
胜率: {performance.get('win_rate', 0):.2%}
平均盈利: {performance.get('avg_profit', 0):.2f}
平均亏损: {performance.get('avg_loss', 0):.2f}
最大回撤: {performance.get('max_drawdown', 0):.2f}
夏普比率: {performance.get('sharpe_ratio', 0):.2f}"""

    def _load_parameter_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载参数模板"""
        return {
            'high_volatility': {
                'position_size': 0.01,
                'stop_loss_atr_multiplier': 2.0,
                'take_profit_atr_multiplier': 3.0,
                'risk_per_trade': 0.5
            },
            'low_volatility': {
                'position_size': 0.02,
                'stop_loss_atr_multiplier': 1.0,
                'take_profit_atr_multiplier': 2.0,
                'risk_per_trade': 2.0
            },
            'trending': {
                'trend_following_mode': True,
                'mean_reversion_mode': False,
                'trailing_stop_atr': 1.5
            },
            'ranging': {
                'trend_following_mode': False,
                'mean_reversion_mode': True,
                'trailing_stop_atr': 1.0
            }
        }