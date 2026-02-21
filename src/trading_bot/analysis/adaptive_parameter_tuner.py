#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时参数调整机制 - Adaptive Parameter Tuner

基于策略表现实时调整参数
支持参数漂移检测、自动修正和热更新

作者: MT5 Trading Bot Team
创建时间: 2026-02-21
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional, Any, Callable
from datetime import datetime, timedelta
from collections import deque
from scipy import stats
import json
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)
class AdaptiveParameterTuner:
    """
    自适应参数调整器
    
    核心功能:
    1. 基于策略表现实时调整参数
    2. 参数漂移检测和自动修正
    3. 参数热更新和回滚
    4. 性能监控和告警
    """
    
    def __init__(self,
                 current_params: Dict[str, float],
                 param_bounds: Dict[str, Tuple[float, float]],
                 adjustment_window: int = 10,
                 performance_threshold: float = 0.02,
                 drift_detection_window: int = 20):
        """
        初始化自适应参数调整器
        
        Args:
            current_params: 当前参数
            param_bounds: 参数边界
            adjustment_window: 参数调整窗口（交易次数）
            performance_threshold: 性能下降阈值
            drift_detection_window: 参数漂移检测窗口
        """
        self.current_params = current_params.copy()
        self.param_bounds = param_bounds
        self.param_names = list(param_bounds.keys())
        
        self.adjustment_window = adjustment_window
        self.performance_threshold = performance_threshold
        self.drift_detection_window = drift_detection_window
        
        # 性能监控
        self.performance_history = deque(maxlen=100)
        self.parameter_history = deque(maxlen=100)
        
        # 参数漂移检测
        self.drift_detected = False
        self.drift_start_time = None
        self.drift_magnitude = 0.0
        
        # 参数版本控制
        self.param_versions = []  # (timestamp, params, version)
        self.current_version = 0
        self.rollback_version = None
        
        # 调整统计
        self.adjustment_stats = {
            'total_adjustments': 0,
            'successful_adjustments': 0,
            'failed_adjustments': 0,
            'rollbacks': 0,
            'last_adjustment_time': None
        }
        
        # 告警状态
        self.alerts = []
        self.last_alert_time = None
        
        # 缓存
        self._performance_cache = deque(maxlen=adjustment_window)
        self._param_cache = deque(maxlen=drift_detection_window)
        
        logger.info("自适应参数调整器初始化完成")
    
    def monitor_performance(self, performance: Dict[str, float]):
        """
        监控性能
        
        Args:
            performance: 性能指标
        """
        # 存储性能
        self.performance_history.append({
            'timestamp': datetime.now(),
            'performance': performance,
            'params': self.current_params.copy()
        })
        
        # 更新缓存
        self._performance_cache.append(performance)
        
        # 检测性能下降
        self._detect_performance_decline()
        
        # 检测参数漂移
        self._detect_parameter_drift()
        
        # 生成告警
        self._check_alerts()
    
    def _detect_performance_decline(self):
        """检测性能下降"""
        if len(self._performance_cache) < self.adjustment_window:
            return
        
        # 计算平均性能
        recent_perf = list(self._performance_cache)
        avg_return = np.mean([p.get('return', 0) for p in recent_perf])
        
        # 比较基线性能
        if len(self.performance_history) > self.adjustment_window:
            baseline_perf = [
                p['performance'] for p in list(self.performance_history)
                [-2 * self.adjustment_window:-self.adjustment_window]
            ]
            baseline_return = np.mean([p.get('return', 0) for p in baseline_perf])
            
            # 检测下降
            decline = (baseline_return - avg_return) / (abs(baseline_return) + 1e-6)
            if decline > self.performance_threshold:
                logger.warning(f"检测到性能下降: {decline:.2%}")
                self._add_alert('performance_decline', 
                               f"性能下降 {decline:.2%}",
                               severity='warning')
    
    def _detect_parameter_drift(self):
        """检测参数漂移"""
        # 缓存当前参数
        self._param_cache.append(self.current_params.copy())
        
        if len(self._param_cache) < self.drift_detection_window:
            return
        
        # 计算参数变化
        params_matrix = np.array([
            [p[name] for name in self.param_names]
            for p in self._param_cache
        ])
        
        # 计算标准差作为漂移度量
        param_std = np.std(params_matrix, axis=0)
        avg_std = np.mean(param_std)
        
        # 计算相对于参数范围的漂移
        drifts = []
        for i, name in enumerate(self.param_names):
            min_val, max_val = self.param_bounds[name]
            if max_val > min_val:
                drift = param_std[i] / (max_val - min_val)
                drifts.append(drift)
        
        if drifts:
            avg_drift = np.mean(drifts)
            max_drift = np.max(drifts)
            
            # 检测漂移
            drift_threshold = 0.1  # 10%的参数范围
            if avg_drift > drift_threshold or max_drift > 2 * drift_threshold:
                self.drift_detected = True
                self.drift_magnitude = avg_drift
                
                if self.drift_start_time is None:
                    self.drift_start_time = datetime.now()
                
                logger.warning(f"检测到参数漂移: {avg_drift:.2%}, 最大漂移: {max_drift:.2%}")
                self._add_alert('parameter_drift',
                               f"参数漂移 {avg_drift:.2%}",
                               severity='warning')
            else:
                if self.drift_detected and avg_drift < drift_threshold / 2:
                    logger.info("参数漂移已修正")
                    self.drift_detected = False
                    self.drift_start_time = None
    
    def _check_alerts(self):
        """检查告警条件"""
        now = datetime.now()
        
        # 清理过期告警
        self.alerts = [
            alert for alert in self.alerts
            if now - alert['timestamp'] < timedelta(hours=1)
        ]
        
        # 如果有高严重度告警，且距离上次告警超过5分钟
        high_severity_alerts = [
            alert for alert in self.alerts
            if alert['severity'] == 'critical'
        ]
        
        if high_severity_alerts:
            if self.last_alert_time is None or \
               now - self.last_alert_time > timedelta(minutes=5):
                # 发送告警通知
                self._send_alert_notification(high_severity_alerts[-1])
                self.last_alert_time = now
    
    def _add_alert(self, alert_type: str, message: str, severity: str = 'info'):
        """添加告警"""
        alert = {
            'timestamp': datetime.now(),
            'type': alert_type,
            'message': message,
            'severity': severity
        }
        self.alerts.append(alert)
        
        logger.warning(f"告警: [{alert_type}] {message} (严重度: {severity})")
    
    def _send_alert_notification(self, alert: Dict[str, Any]):
        """发送告警通知"""
        # 这里可以集成Telegram或其他通知方式
        message = f"⚠️ {alert['severity'].upper()} Alert\n" \
                  f"Type: {alert['type']}\n" \
                  f"Message: {alert['message']}\n" \
                  f"Time: {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
        
        logger.warning(f"发送告警通知: {message}")
        
        # TODO: 集成Telegram通知
        # from utils.telegram_notifier import TelegramNotifier
        # telegram = TelegramNotifier()
        # telegram.send_message(message)
    
    def adjust_parameters(self,
                          suggested_params: Dict[str, float],
                          force: bool = False) -> Tuple[bool, str]:
        """
        调整参数
        
        Args:
            suggested_params: 建议的参数
            force: 是否强制调整
        
        Returns:
            (是否成功, 消息)
        """
        # 验证参数
        if not self._validate_params(suggested_params):
            msg = "参数验证失败"
            self.adjustment_stats['failed_adjustments'] += 1
            return False, msg
        
        # 计算调整幅度
        adjustment_magnitude = self._calculate_adjustment_magnitude(
            self.current_params,
            suggested_params
        )
        
        # 检查是否需要调整
        if not force and adjustment_magnitude < 0.01:
            msg = "调整幅度太小，跳过"
            return False, msg
        
        # 创建参数版本
        self._create_param_version(suggested_params)
        
        # 应用调整
        try:
            self.current_params = suggested_params.copy()
            self.parameter_history.append({
                'timestamp': datetime.now(),
                'params': self.current_params.copy(),
                'version': self.current_version
            })
            
            self.adjustment_stats['successful_adjustments'] += 1
            self.adjustment_stats['total_adjustments'] += 1
            self.adjustment_stats['last_adjustment_time'] = datetime.now()
            
            # 清除漂移检测
            self.drift_detected = False
            self.drift_start_time = None
            
            msg = f"参数调整成功，幅度: {adjustment_magnitude:.2%}"
            logger.info(msg)
            return True, msg
            
        except Exception as e:
            msg = f"参数调整失败: {e}"
            self.adjustment_stats['failed_adjustments'] += 1
            logger.error(msg)
            return False, msg
    
    def _validate_params(self, params: Dict[str, float]) -> bool:
        """验证参数有效性"""
        # 检查必需参数
        for name in self.param_names:
            if name not in params:
                return False
        
        # 检查参数范围
        for name, value in params.items():
            if name in self.param_bounds:
                min_val, max_val = self.param_bounds[name]
                if not (min_val <= value <= max_val):
                    return False
        
        return True
    
    def _calculate_adjustment_magnitude(self,
                                       current: Dict[str, float],
                                       suggested: Dict[str, float]) -> float:
        """计算调整幅度"""
        magnitudes = []
        
        for name in self.param_names:
            if name in current and name in suggested:
                min_val, max_val = self.param_bounds[name]
                range_size = max_val - min_val
                if range_size > 0:
                    magnitude = abs(suggested[name] - current[name]) / range_size
                    magnitudes.append(magnitude)
        
        return np.mean(magnitudes) if magnitudes else 0.0
    
    def _create_param_version(self, params: Dict[str, float]):
        """创建参数版本"""
        self.current_version += 1
        
        self.param_versions.append({
            'timestamp': datetime.now(),
            'params': params.copy(),
            'version': self.current_version
        })
        
        # 限制版本历史长度
        if len(self.param_versions) > 50:
            self.param_versions = self.param_versions[-50:]
    
    def rollback(self, n_versions: int = 1) -> Tuple[bool, str]:
        """
        回滚参数
        
        Args:
            n_versions: 回滚版本数
        
        Returns:
            (是否成功, 消息)
        """
        if len(self.param_versions) < n_versions + 1:
            msg = f"没有足够的版本历史（当前: {len(self.param_versions)}）"
            return False, msg
        
        # 计算目标版本
        target_version = self.current_version - n_versions
        
        # 找到目标版本
        target_record = None
        for record in reversed(self.param_versions):
            if record['version'] == target_version:
                target_record = record
                break
        
        if not target_record:
            msg = f"未找到版本 {target_version}"
            return False, msg
        
        # 回滚
        try:
            self.current_params = target_record['params'].copy()
            self.current_version = target_version
            self.rollback_version = target_version
            
            self.adjustment_stats['rollbacks'] += 1
            
            msg = f"回滚到版本 {target_version}"
            logger.info(msg)
            return True, msg
            
        except Exception as e:
            msg = f"回滚失败: {e}"
            logger.error(msg)
            return False, msg
    
    def auto_tune(self,
                  objective_function: Callable[[Dict[str, float]], Dict[str, float]],
                  n_iterations: int = 10) -> Dict[str, Any]:
        """
        自动调参
        
        Args:
            objective_function: 目标函数
            n_iterations: 迭代次数
        
        Returns:
            调优结果
        """
        logger.info(f"开始自动调参，迭代次数: {n_iterations}")
        
        results = []
        best_score = -np.inf
        best_params = None
        
        for i in range(n_iterations):
            # 生成候选参数
            candidate = self._generate_candidate_params()
            
            # 评估
            try:
                performance = objective_function(candidate)
                score = self._calculate_score(performance)
                
                results.append({
                    'iteration': i + 1,
                    'params': candidate,
                    'performance': performance,
                    'score': score
                })
                
                # 更新最优
                if score > best_score:
                    best_score = score
                    best_params = candidate.copy()
                
                logger.info(f"迭代 {i+1}/{n_iterations}: 得分={score:.4f}")
                
            except Exception as e:
                logger.error(f"迭代 {i+1} 失败: {e}")
        
        # 应用最优参数
        if best_params:
            success, msg = self.adjust_parameters(best_params, force=True)
            
            return {
                'success': success,
                'message': msg,
                'best_score': best_score,
                'best_params': best_params,
                'all_results': results
            }
        else:
            return {
                'success': False,
                'message': '未找到有效参数',
                'all_results': results
            }
    
    def _generate_candidate_params(self) -> Dict[str, float]:
        """生成候选参数"""
        # 基于当前参数添加扰动
        candidate = {}
        
        for name, value in self.current_params.items():
            min_val, max_val = self.param_bounds[name]
            range_size = max_val - min_val
            
            # 添加高斯噪声
            noise_scale = range_size * 0.1 * (1.0 + self.drift_magnitude)
            noise = np.random.normal(0, noise_scale)
            
            candidate[name] = np.clip(value + noise, min_val, max_val)
        
        return candidate
    
    def _calculate_score(self, performance: Dict[str, float]) -> float:
        """计算综合得分"""
        score = 0.0
        
        if 'return' in performance:
            score += performance['return'] * 0.3
        if 'sharpe' in performance:
            score += performance['sharpe'] * 0.4
        if 'max_drawdown' in performance:
            normalized_dd = max(0, min(1, performance['max_drawdown'] / 0.5))
            score += (1 - normalized_dd) * 0.3
        
        return score
    
    def get_status(self) -> Dict[str, Any]:
        """获取调整器状态"""
        # 计算最近性能
        recent_perfs = [
            p['performance'] for p in list(self.performance_history)[-10:]
        ] if self.performance_history else []
        
        avg_return = np.mean([p.get('return', 0) for p in recent_perfs]) if recent_perfs else 0.0
        
        return {
            'current_params': self.current_params,
            'current_version': self.current_version,
            'drift_detected': self.drift_detected,
            'drift_magnitude': self.drift_magnitude,
            'drift_start_time': self.drift_start_time.isoformat() if self.drift_start_time else None,
            'recent_avg_return': float(avg_return),
            'adjustment_stats': self.adjustment_stats,
            'active_alerts': len([a for a in self.alerts if a['severity'] in ['warning', 'critical']]),
            'total_records': len(self.performance_history)
        }
    
    def export_state(self, filepath: str):
        """
        导出状态到文件
        
        Args:
            filepath: 保存路径
        """
        state = {
            'current_params': self.current_params,
            'current_version': self.current_version,
            'param_versions': self.param_versions,
            'adjustment_stats': self.adjustment_stats,
            'drift_detected': self.drift_detected,
            'drift_magnitude': self.drift_magnitude,
            'drift_start_time': self.drift_start_time.isoformat() if self.drift_start_time else None
        }
        
        # 处理非序列化对象
        def default_serializer(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, (datetime, timedelta)):
                return obj.isoformat()
            return str(obj)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False, default=default_serializer)
        
        logger.info(f"状态已导出到: {filepath}")
    
    def load_state(self, filepath: str):
        """
        从文件加载状态
        
        Args:
            filepath: 文件路径
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.current_params = state.get('current_params', {})
            self.current_version = state.get('current_version', 0)
            self.param_versions = state.get('param_versions', [])
            self.adjustment_stats = state.get('adjustment_stats', {})
            self.drift_detected = state.get('drift_detected', False)
            self.drift_magnitude = state.get('drift_magnitude', 0.0)
            
            # 恢复漂移开始时间
            drift_start_str = state.get('drift_start_time')
            if drift_start_str:
                self.drift_start_time = datetime.fromisoformat(drift_start_str)
            
            logger.info("状态已加载")
            
        except Exception as e:
            logger.error(f"加载状态失败: {e}")
    
    def reset(self):
        """重置调整器"""
        self.performance_history.clear()
        self.parameter_history.clear()
        self.param_versions.clear()
        
        self.drift_detected = False
        self.drift_start_time = None
        self.drift_magnitude = 0.0
        
        self.current_version = 0
        self.rollback_version = None
        
        self.adjustment_stats = {
            'total_adjustments': 0,
            'successful_adjustments': 0,
            'failed_adjustments': 0,
            'rollbacks': 0,
            'last_adjustment_time': None
        }
        
        self.alerts.clear()
        self.last_alert_time = None
        
        self._performance_cache.clear()
        self._param_cache.clear()
        
        logger.info("调整器已重置")
