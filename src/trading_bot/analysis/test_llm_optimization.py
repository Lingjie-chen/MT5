#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型参数优化系统 - 单元测试

测试所有核心组件的功能

作者: MT5 Trading Bot Team
创建时间: 2026-02-21
"""

import unittest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import tempfile
import os
import sys

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_parameter_optimizer import LLMParameterOptimizer
from bayesian_llm_optimizer import BayesianLLMOptimizer
from parameter_history_learner import ParameterHistoryLearner
from adaptive_parameter_tuner import AdaptiveParameterTuner
from enhanced_optimization import EnhancedOptimizationEngine
class MockObjectiveFunction:
    """模拟目标函数"""
    
    def __init__(self, noise_level=0.1):
        self.noise_level = noise_level
    
    def __call__(self, params):
        """计算性能指标"""
        # 简单的二次函数 + 噪声
        score = 0.0
        for name, value in params.items():
            score -= (value - 0.5) ** 2  # 0.5是最优值
        
        # 添加噪声
        noise = np.random.normal(0, self.noise_level)
        
        # 返回性能指标
        return {
            'return': max(-1.0, min(1.0, score + noise)),
            'sharpe': max(0.0, min(2.0, (score + 1.0) + noise)),
            'max_drawdown': max(0.0, min(0.5, (-score) * 0.5 + noise * 0.1))
        }
class TestLLMParameterOptimizer(unittest.TestCase):
    """测试LLM参数优化器"""
    
    def setUp(self):
        """设置测试环境"""
        self.param_bounds = {
            'param1': (0.0, 1.0),
            'param2': (0.0, 1.0),
            'param3': (0.0, 1.0)
        }
        self.optimizer = LLMParameterOptimizer(
            param_bounds=self.param_bounds,
            objective_metrics=['return', 'sharpe', 'max_drawdown'],
            model_type='qwen'
        )
        self.objective_func = MockObjectiveFunction()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.optimizer.n_params, 3)
        self.assertEqual(len(self.optimizer.param_names), 3)
        self.assertIsNotNone(self.optimizer.param_history)
    
    def test_parameter_normalization(self):
        """测试参数归一化"""
        params = {'param1': 0.0, 'param2': 0.5, 'param3': 1.0}
        normalized = self.optimizer._normalize_params(params)
        
        self.assertAlmostEqual(normalized[0], 0.0)
        self.assertAlmostEqual(normalized[1], 0.5)
        self.assertAlmostEqual(normalized[2], 1.0)
    
    def test_parameter_denormalization(self):
        """测试参数还原"""
        normalized = np.array([0.0, 0.5, 1.0])
        params = self.optimizer._denormalize_params(normalized)
        
        self.assertAlmostEqual(params['param1'], 0.0)
        self.assertAlmostEqual(params['param2'], 0.5)
        self.assertAlmostEqual(params['param3'], 1.0)
    
    def test_recommend_params(self):
        """测试参数推荐"""
        market_data = {
            'trend_strength': 0.7,
            'volatility': 0.3,
            'volume_ratio': 1.2,
            'sentiment': 0.5,
            'momentum': 0.6,
            'choppiness_index': 0.4
        }
        
        # 添加一些历史数据
        for _ in range(5):
            params = self.optimizer._get_random_params()
            performance = self.objective_func(params)
            self.optimizer.update_performance(params, performance, market_data)
        
        # 推荐参数
        recommended = self.optimizer.recommend_params(market_data, use_exploration=False)
        
        self.assertIn('param1', recommended)
        self.assertIn('param2', recommended)
        self.assertIn('param3', recommended)
        
        # 检查参数是否在边界内
        for name, value in recommended.items():
            min_val, max_val = self.param_bounds[name]
            self.assertGreaterEqual(value, min_val)
            self.assertLessEqual(value, max_val)
    
    def test_update_performance(self):
        """测试性能更新"""
        params = {'param1': 0.5, 'param2': 0.5, 'param3': 0.5}
        performance = {
            'return': 0.5,
            'sharpe': 1.0,
            'max_drawdown': 0.1
        }
        market_data = {
            'trend_strength': 0.5,
            'volatility': 0.3,
            'volume_ratio': 1.0,
            'sentiment': 0.5,
            'momentum': 0.5,
            'choppiness_index': 0.5
        }
        
        self.optimizer.update_performance(params, performance, market_data)
        
        self.assertEqual(len(self.optimizer.param_history), 1)
        self.assertEqual(len(self.optimizer.performance_history), 1)
        self.assertEqual(len(self.optimizer.market_state_history), 1)
    
    def test_export_import_history(self):
        """测试历史数据导出导入"""
        # 添加一些数据
        for _ in range(10):
            params = self.optimizer._get_random_params()
            performance = self.objective_func(params)
            market_data = {
                'trend_strength': 0.5,
                'volatility': 0.3,
                'volume_ratio': 1.0,
                'sentiment': 0.5,
                'momentum': 0.5,
                'choppiness_index': 0.5
            }
            self.optimizer.update_performance(params, performance, market_data)
        
        # 导出到临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name
        
        try:
            self.optimizer.export_history(temp_file)
            
            # 创建新优化器并导入
            new_optimizer = LLMParameterOptimizer(
                param_bounds=self.param_bounds,
                objective_metrics=['return', 'sharpe', 'max_drawdown']
            )
            new_optimizer.load_history(temp_file)
            
            # 验证数据
            self.assertEqual(len(new_optimizer.param_history), 10)
            self.assertEqual(len(new_optimizer.performance_history), 10)
        finally:
            os.unlink(temp_file)
class TestBayesianLLMOptimizer(unittest.TestCase):
    """测试贝叶斯优化器"""
    
    def setUp(self):
        """设置测试环境"""
        self.param_bounds = {
            'param1': (0.0, 1.0),
            'param2': (0.0, 1.0),
            'param3': (0.0, 1.0)
        }
        self.optimizer = BayesianLLMOptimizer(
            param_bounds=self.param_bounds,
            objective_metrics=['return', 'sharpe', 'max_drawdown'],
            n_initial_points=5,
            use_llm=False  # 测试时不使用LLM
        )
        self.objective_func = MockObjectiveFunction()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(len(self.optimizer.gp_models), 3)
        self.assertIsNotNone(self.optimizer.X_observed)
    
    def test_optimization(self):
        """测试优化"""
        best_params, best_performance = self.optimizer.optimize(
            objective_function=self.objective_func,
            n_iterations=20
        )
        
        self.assertIsNotNone(best_params)
        self.assertIsNotNone(best_performance)
        self.assertIn('param1', best_params)
        self.assertIn('param2', best_params)
        self.assertIn('param3', best_params)
    
    def test_param_explanations(self):
        """测试参数解释"""
        # 运行一些优化
        self.optimizer.optimize(
            objective_function=self.objective_func,
            n_iterations=30
        )
        
        explanations = self.optimizer.get_param_explanations()
        
        self.assertIn('param1', explanations)
        self.assertIn('param2', explanations)
        self.assertIn('param3', explanations)
        
        # 检查每个参数的解释
        for name in self.param_bounds:
            self.assertIn('importance', explanations[name])
            self.assertIn('range', explanations[name])
            self.assertIn('recommended', explanations[name])
            self.assertIn('adjustment_strategy', explanations[name])
class TestParameterHistoryLearner(unittest.TestCase):
    """测试参数历史学习器"""
    
    def setUp(self):
        """设置测试环境"""
        self.param_names = ['param1', 'param2', 'param3']
        self.learner = ParameterHistoryLearner(
            param_names=self.param_names,
            n_clusters=3
        )
        self.objective_func = MockObjectiveFunction()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(len(self.learner.market_feature_names), 6)
        self.assertEqual(self.learner.n_clusters, 3)
    
    def test_add_record(self):
        """测试添加记录"""
        params = {'param1': 0.5, 'param2': 0.5, 'param3': 0.5}
        performance = self.objective_func(params)
        market_state = {
            'trend_strength': 0.5,
            'volatility': 0.3,
            'volume_ratio': 1.0,
            'sentiment': 0.5,
            'momentum': 0.5,
            'choppiness_index': 0.5
        }
        
        self.learner.add_record(params, performance, market_state)
        
        self.assertEqual(len(self.learner.parameter_history), 1)
        self.assertEqual(len(self.learner.performance_history), 1)
        self.assertEqual(len(self.learner.market_state_history), 1)
    
    def test_learning(self):
        """测试学习"""
        # 添加足够的数据
        for _ in range(30):
            params = {name: np.random.uniform(0, 1) for name in self.param_names}
            performance = self.objective_func(params)
            market_state = {
                'trend_strength': np.random.uniform(0, 1),
                'volatility': np.random.uniform(0, 1),
                'volume_ratio': np.random.uniform(0.5, 1.5),
                'sentiment': np.random.uniform(-1, 1),
                'momentum': np.random.uniform(-1, 1),
                'choppiness_index': np.random.uniform(0, 100)
            }
            self.learner.add_record(params, performance, market_state)
        
        # 学习
        self.learner.learn()
        
        # 验证聚类
        self.assertIsNotNone(self.learner.cluster_model)
        self.assertIsNotNone(self.learner.cluster_labels)
        self.assertIsNotNone(self.learner.cluster_centers)
    
    def test_predict_best_params(self):
        """测试预测最优参数"""
        # 添加数据并学习
        for _ in range(30):
            params = {name: np.random.uniform(0, 1) for name in self.param_names}
            performance = self.objective_func(params)
            market_state = {
                'trend_strength': np.random.uniform(0, 1),
                'volatility': np.random.uniform(0, 1),
                'volume_ratio': np.random.uniform(0.5, 1.5),
                'sentiment': np.random.uniform(-1, 1),
                'momentum': np.random.uniform(-1, 1),
                'choppiness_index': np.random.uniform(0, 100)
            }
            self.learner.add_record(params, performance, market_state)
        
        self.learner.learn()
        
        # 预测
        market_state = {
            'trend_strength': 0.5,
            'volatility': 0.3,
            'volume_ratio': 1.0,
            'sentiment': 0.5,
            'momentum': 0.5,
            'choppiness_index': 50.0
        }
        
        candidates = self.learner.predict_best_params(market_state, top_k=3)
        
        self.assertGreater(len(candidates), 0)
        self.assertLessEqual(len(candidates), 3)
class TestAdaptiveParameterTuner(unittest.TestCase):
    """测试自适应参数调整器"""
    
    def setUp(self):
        """设置测试环境"""
        self.current_params = {
            'param1': 0.5,
            'param2': 0.5,
            'param3': 0.5
        }
        self.param_bounds = {
            'param1': (0.0, 1.0),
            'param2': (0.0, 1.0),
            'param3': (0.0, 1.0)
        }
        self.tuner = AdaptiveParameterTuner(
            current_params=self.current_params,
            param_bounds=self.param_bounds,
            adjustment_window=10,
            performance_threshold=0.02
        )
        self.objective_func = MockObjectiveFunction()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.tuner.current_params, self.current_params)
        self.assertEqual(len(self.tuner.performance_history), 0)
    
    def test_monitor_performance(self):
        """测试性能监控"""
        performance = self.objective_func(self.current_params)
        self.tuner.monitor_performance(performance)
        
        self.assertEqual(len(self.tuner.performance_history), 1)
    
    def test_adjust_parameters(self):
        """测试参数调整"""
        suggested_params = {
            'param1': 0.6,
            'param2': 0.6,
            'param3': 0.6
        }
        
        success, msg = self.tuner.adjust_parameters(suggested_params, force=True)
        
        self.assertTrue(success)
        self.assertAlmostEqual(self.tuner.current_params['param1'], 0.6)
    
    def test_rollback(self):
        """测试回滚"""
        # 创建几个版本
        for i in range(3):
            params = {
                'param1': 0.5 + i * 0.1,
                'param2': 0.5 + i * 0.1,
                'param3': 0.5 + i * 0.1
            }
            self.tuner.adjust_parameters(params, force=True)
        
        # 回滚1个版本
        success, msg = self.tuner.rollback(1)
        
        self.assertTrue(success)
        self.assertAlmostEqual(self.tuner.current_params['param1'], 0.6)
class TestEnhancedOptimizationEngine(unittest.TestCase):
    """测试增强优化引擎"""
    
    def setUp(self):
        """设置测试环境"""
        self.param_bounds = {
            'param1': (0.0, 1.0),
            'param2': (0.0, 1.0),
            'param3': (0.0, 1.0)
        }
        self.engine = EnhancedOptimizationEngine(
            param_bounds=self.param_bounds,
            optimization_mode='hybrid',
            objective_metrics=['return', 'sharpe', 'max_drawdown']
        )
        self.objective_func = MockObjectiveFunction()
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.engine.optimization_mode, 'hybrid')
        self.assertIsNotNone(self.engine.llm_optimizer)
    
    def test_set_current_params(self):
        """测试设置当前参数"""
        params = {'param1': 0.5, 'param2': 0.5, 'param3': 0.5}
        self.engine.set_current_params(params)
        
        self.assertIsNotNone(self.engine.adaptive_tuner)
        self.assertEqual(self.engine.adaptive_tuner.current_params, params)
    
    def test_optimize(self):
        """测试优化"""
        best_params, best_performance = self.engine.optimize(
            objective_function=self.objective_func,
            n_iterations=20
        )
        
        self.assertIsNotNone(best_params)
        self.assertIsNotNone(best_performance)
    
    def test_recommend_parameters(self):
        """测试参数推荐"""
        market_data = {
            'trend_strength': 0.5,
            'volatility': 0.3,
            'volume_ratio': 1.0,
            'sentiment': 0.5,
            'momentum': 0.5,
            'choppiness_index': 50.0
        }
        
        # 先运行一些优化以建立历史
        for _ in range(10):
            self.engine.optimize(
                objective_function=self.objective_func,
                n_iterations=5
            )
        
        recommendations = self.engine.recommend_parameters(market_data, top_k=3)
        
        self.assertGreater(len(recommendations), 0)
        self.assertLessEqual(len(recommendations), 3)
def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试
    suite.addTests(loader.loadTestsFromTestCase(TestLLMParameterOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestBayesianLLMOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestParameterHistoryLearner))
    suite.addTests(loader.loadTestsFromTestCase(TestAdaptiveParameterTuner))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedOptimizationEngine))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result
if __name__ == '__main__':
    print("=" * 60)
    print("大模型参数优化系统 - 单元测试")
    print("=" * 60)
    print()
    
    result = run_tests()
    
    print()
    print("=" * 60)
    if result.wasSuccessful():
        print("✓ 所有测试通过!")
    else:
        print("✗ 部分测试失败")
        print(f"  失败数: {len(result.failures)}")
        print(f"  错误数: {len(result.errors)}")
    print("=" * 60)
