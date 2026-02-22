import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class SymbolConfigCache:
    """
    品种参数存储和缓存系统
    用于存储和检索品种画像、优化参数和历史表现数据
    """

    def __init__(self, cache_dir: str = "cache/symbol_configs"):
        self.cache_dir = cache_dir
        self.cache_expiry_hours = 24
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """确保缓存目录存在"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Created cache directory: {self.cache_dir}")

    def _get_cache_file_path(self, symbol: str, cache_type: str) -> str:
        """获取缓存文件路径"""
        safe_symbol = symbol.replace("/", "_").replace("\\", "_")
        filename = f"{safe_symbol}_{cache_type}.json"
        return os.path.join(self.cache_dir, filename)

    def _is_cache_valid(self, file_path: str) -> bool:
        """检查缓存是否有效"""
        if not os.path.exists(file_path):
            return False
        
        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        expiry_time = datetime.now() - timedelta(hours=self.cache_expiry_hours)
        
        return file_time > expiry_time

    def save_symbol_profile(self, symbol: str, profile: Dict[str, Any]) -> bool:
        """
        保存品种画像到缓存
        
        Args:
            symbol: 交易品种
            profile: 品种画像数据
            
        Returns:
            是否保存成功
        """
        try:
            cache_file = self._get_cache_file_path(symbol, "profile")
            
            profile['cached_at'] = datetime.now().isoformat()
            profile['symbol'] = symbol
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved symbol profile for {symbol} to cache")
            return True
            
        except Exception as e:
            logger.error(f"Error saving symbol profile for {symbol}: {e}")
            return False

    def load_symbol_profile(self, symbol: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        从缓存加载品种画像
        
        Args:
            symbol: 交易品种
            force_refresh: 是否强制刷新
            
        Returns:
            品种画像数据，如果不存在或已过期则返回None
        """
        if force_refresh:
            return None
        
        try:
            cache_file = self._get_cache_file_path(symbol, "profile")
            
            if not self._is_cache_valid(cache_file):
                logger.debug(f"Cache for {symbol} is expired or not exists")
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            
            logger.info(f"Loaded symbol profile for {symbol} from cache")
            return profile
            
        except Exception as e:
            logger.error(f"Error loading symbol profile for {symbol}: {e}")
            return None

    def save_optimized_params(self, symbol: str, params: Dict[str, Any]) -> bool:
        """
        保存优化参数到缓存
        
        Args:
            symbol: 交易品种
            params: 优化参数数据
            
        Returns:
            是否保存成功
        """
        try:
            cache_file = self._get_cache_file_path(symbol, "optimized_params")
            
            params['cached_at'] = datetime.now().isoformat()
            params['symbol'] = symbol
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(params, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved optimized params for {symbol} to cache")
            return True
            
        except Exception as e:
            logger.error(f"Error saving optimized params for {symbol}: {e}")
            return False

    def load_optimized_params(self, symbol: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        从缓存加载优化参数
        
        Args:
            symbol: 交易品种
            force_refresh: 是否强制刷新
            
        Returns:
            优化参数数据，如果不存在或已过期则返回None
        """
        if force_refresh:
            return None
        
        try:
            cache_file = self._get_cache_file_path(symbol, "optimized_params")
            
            if not self._is_cache_valid(cache_file):
                logger.debug(f"Cache for {symbol} is expired or not exists")
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                params = json.load(f)
            
            logger.info(f"Loaded optimized params for {symbol} from cache")
            return params
            
        except Exception as e:
            logger.error(f"Error loading optimized params for {symbol}: {e}")
            return None

    def save_performance_stats(self, symbol: str, stats: Dict[str, Any]) -> bool:
        """
        保存历史表现统计到缓存
        
        Args:
            symbol: 交易品种
            stats: 历史表现数据
            
        Returns:
            是否保存成功
        """
        try:
            cache_file = self._get_cache_file_path(symbol, "performance")
            
            stats['cached_at'] = datetime.now().isoformat()
            stats['symbol'] = symbol
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(stats, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved performance stats for {symbol} to cache")
            return True
            
        except Exception as e:
            logger.error(f"Error saving performance stats for {symbol}: {e}")
            return False

    def load_performance_stats(self, symbol: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        从缓存加载历史表现统计
        
        Args:
            symbol: 交易品种
            force_refresh: 是否强制刷新
            
        Returns:
            历史表现数据，如果不存在或已过期则返回None
        """
        if force_refresh:
            return None
        
        try:
            cache_file = self._get_cache_file_path(symbol, "performance")
            
            if not self._is_cache_valid(cache_file):
                logger.debug(f"Cache for {symbol} is expired or not exists")
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
            
            logger.info(f"Loaded performance stats for {symbol} from cache")
            return stats
            
        except Exception as e:
            logger.error(f"Error loading performance stats for {symbol}: {e}")
            return None

    def get_all_cached_symbols(self) -> list:
        """
        获取所有已缓存的品种列表
        
        Returns:
            品种名称列表
        """
        try:
            symbols = set()
            
            for filename in os.listdir(self.cache_dir):
                if filename.endswith("_profile.json"):
                    symbol_part = filename.replace("_profile.json", "")
                    symbols.add(symbol_part.replace("_", "/"))
            
            return sorted(list(symbols))
            
        except Exception as e:
            logger.error(f"Error getting cached symbols: {e}")
            return []

    def clear_cache(self, symbol: Optional[str] = None, cache_type: Optional[str] = None):
        """
        清除缓存
        
        Args:
            symbol: 指定品种，None表示清除所有
            cache_type: 指定缓存类型，None表示清除所有类型
        """
        try:
            if symbol:
                if cache_type:
                    cache_file = self._get_cache_file_path(symbol, cache_type)
                    if os.path.exists(cache_file):
                        os.remove(cache_file)
                        logger.info(f"Cleared cache for {symbol} ({cache_type})")
                else:
                    for ct in ["profile", "optimized_params", "performance"]:
                        self.clear_cache(symbol, ct)
            else:
                for filename in os.listdir(self.cache_dir):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
                logger.info("Cleared all cache")
                
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def get_cache_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        获取缓存信息
        
        Args:
            symbol: 指定品种，None表示获取所有品种信息
            
        Returns:
            缓存信息字典
        """
        try:
            info = {
                'cache_dir': self.cache_dir,
                'cache_expiry_hours': self.cache_expiry_hours,
                'symbols': []
            }
            
            symbols_to_check = [symbol] if symbol else self.get_all_cached_symbols()
            
            for sym in symbols_to_check:
                symbol_info = {
                    'symbol': sym,
                    'profile': None,
                    'optimized_params': None,
                    'performance': None
                }
                
                for cache_type in ["profile", "optimized_params", "performance"]:
                    cache_file = self._get_cache_file_path(sym, cache_type)
                    if os.path.exists(cache_file):
                        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
                        is_valid = self._is_cache_valid(cache_file)
                        
                        symbol_info[cache_type] = {
                            'exists': True,
                            'valid': is_valid,
                            'cached_at': file_time.isoformat(),
                            'age_hours': (datetime.now() - file_time).total_seconds() / 3600
                        }
                
                info['symbols'].append(symbol_info)
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {}

    def export_config(self, output_file: str) -> bool:
        """
        导出所有配置到文件
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'symbols': {}
            }
            
            for symbol in self.get_all_cached_symbols():
                profile = self.load_symbol_profile(symbol)
                params = self.load_optimized_params(symbol)
                performance = self.load_performance_stats(symbol)
                
                if profile or params or performance:
                    export_data['symbols'][symbol] = {
                        'profile': profile,
                        'optimized_params': params,
                        'performance': performance
                    }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported all configs to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting config: {e}")
            return False

    def import_config(self, input_file: str, overwrite: bool = False) -> bool:
        """
        从文件导入配置
        
        Args:
            input_file: 输入文件路径
            overwrite: 是否覆盖现有配置
            
        Returns:
            是否导入成功
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            for symbol, symbol_data in import_data.get('symbols', {}).items():
                if not overwrite and self.load_symbol_profile(symbol):
                    logger.info(f"Skipping {symbol} (cache exists and overwrite=False)")
                    continue
                
                if 'profile' in symbol_data:
                    self.save_symbol_profile(symbol, symbol_data['profile'])
                
                if 'optimized_params' in symbol_data:
                    self.save_optimized_params(symbol, symbol_data['optimized_params'])
                
                if 'performance' in symbol_data:
                    self.save_performance_stats(symbol, symbol_data['performance'])
            
            logger.info(f"Imported configs from {input_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing config: {e}")
            return False

    def get_config_hash(self, symbol: str, cache_type: str) -> Optional[str]:
        """
        获取配置的哈希值，用于检测变更
        
        Args:
            symbol: 交易品种
            cache_type: 缓存类型
            
        Returns:
            哈希值，如果不存在则返回None
        """
        try:
            cache_file = self._get_cache_file_path(symbol, cache_type)
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            return file_hash
            
        except Exception as e:
            logger.error(f"Error calculating config hash for {symbol}: {e}")
            return None
