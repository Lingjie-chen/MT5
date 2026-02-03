import logging
import os
from typing import Optional, Dict, Any

from ai.deepseek_client import DeepSeekClient
from ai.qwen_client import QwenClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AIClientFactory:
    """
    AI客户端工厂类，用于创建和管理AI客户端实例
    基于ValueCell的模型工厂模式实现，支持多种模型配置
    """
    
    def __init__(self):
        """初始化AI客户端工厂"""
        self.siliconflow_api_key = os.getenv("SILICONFLOW_API_KEY", "your_siliconflow_api_key")
        self.clients = {}
        logger.info("AI客户端工厂初始化完成")
    
    def create_client(self, client_type: str, model: Optional[str] = None) -> Optional[Any]:
        """
        创建AI客户端实例
        
        Args:
            client_type (str): 客户端类型，支持 'deepseek' 或 'qwen'
            model (Optional[str]): 模型名称，不提供则使用默认值
            
        Returns:
            Optional[Any]: 创建的客户端实例，失败返回None
        """
        # 检查API密钥是否配置
        if not self.siliconflow_api_key or self.siliconflow_api_key == "your_siliconflow_api_key":
            logger.error("未配置SILICONFLOW_API_KEY环境变量")
            return None
        
        # 获取统一的SiliconFlow API URL
        siliconflow_api_url = os.getenv("SILICONFLOW_API_URL", "https://api.siliconflow.cn/v1")
        
        # 创建客户端实例
        try:
            if client_type == 'deepseek':
                # 使用DeepSeek客户端
                model_name = model or os.getenv("DEEPSEEK_MODEL", "deepseek-ai/DeepSeek-V3.1-Terminus")
                client = DeepSeekClient(
                    api_key=self.siliconflow_api_key,
                    base_url=siliconflow_api_url,
                    model=model_name
                )
                logger.info(f"创建DeepSeek客户端成功，模型: {model_name}, API: {siliconflow_api_url}")
                return client
            
            elif client_type == 'qwen':
                # 使用Qwen客户端
                model_name = model or os.getenv("QWEN_MODEL", "Qwen/Qwen3-VL-235B-A22B-Thinking")
                client = QwenClient(
                    api_key=self.siliconflow_api_key,
                    base_url=siliconflow_api_url,
                    model=model_name
                )
                logger.info(f"创建Qwen客户端成功，模型: {model_name}, API: {siliconflow_api_url}")
                return client
            
            else:
                logger.error(f"不支持的客户端类型: {client_type}")
                return None
        
        except Exception as e:
            logger.error(f"创建AI客户端失败: {e}")
            return None
    
    def get_client(self, client_type: str, model: Optional[str] = None) -> Optional[Any]:
        """
        获取或创建AI客户端实例（单例模式）
        
        Args:
            client_type (str): 客户端类型
            model (Optional[str]): 模型名称
            
        Returns:
            Optional[Any]: 客户端实例，失败返回None
        """
        # 创建客户端唯一标识
        client_key = f"{client_type}_{model}" if model else client_type
        
        # 如果客户端已存在，直接返回
        if client_key in self.clients:
            logger.info(f"使用已存在的客户端实例: {client_key}")
            return self.clients[client_key]
        
        # 否则创建新客户端
        client = self.create_client(client_type, model)
        if client:
            self.clients[client_key] = client
        
        return client
    
    def initialize_all_clients(self) -> Dict[str, Any]:
        """
        初始化所有支持的AI客户端
        基于ValueCell的模型工厂模式推荐实现
        
        Returns:
            Dict[str, Any]: 初始化的客户端字典，包含 'deepseek' 和 'qwen' 客户端
        """
        logger.info("开始初始化所有AI客户端")
        
        # 初始化DeepSeek客户端
        deepseek_client = self.get_client('deepseek')
        if not deepseek_client:
            logger.error("DeepSeek客户端初始化失败")
        
        # 初始化Qwen客户端
        qwen_client = self.get_client('qwen')
        if not qwen_client:
            logger.error("Qwen客户端初始化失败")
        
        # 保存到客户端字典
        clients = {
            'deepseek': deepseek_client,
            'qwen': qwen_client
        }
        
        logger.info("所有AI客户端初始化完成")
        return clients
    
    def close_clients(self):
        """
        关闭所有客户端连接
        """
        # 目前客户端无需显式关闭连接，预留接口
        logger.info("关闭所有AI客户端连接")
        self.clients.clear()


def initialize_ai_clients() -> Dict[str, Any]:
    """
    初始化AI客户端的工厂函数
    基于ValueCell的模型工厂模式实现，用于全局客户端初始化
    
    Returns:
        Dict[str, Any]: 初始化的客户端字典
    """
    factory = AIClientFactory()
    return factory.initialize_all_clients()


if __name__ == "__main__":
    """测试AI客户端工厂"""
    # 测试工厂模式
    factory = AIClientFactory()
    
    # 测试创建DeepSeek客户端
    deepseek_client = factory.create_client('deepseek')
    print(f"DeepSeek客户端创建: {'成功' if deepseek_client else '失败'}")
    
    # 测试创建Qwen客户端
    qwen_client = factory.create_client('qwen')
    print(f"Qwen客户端创建: {'成功' if qwen_client else '失败'}")
    
    # 测试单例模式
    deepseek_client2 = factory.get_client('deepseek')
    print(f"单例模式测试: {'成功' if deepseek_client is deepseek_client2 else '失败'}")
    
    # 测试初始化所有客户端
    all_clients = factory.initialize_all_clients()
    print(f"所有客户端初始化: {'成功' if all_clients else '失败'}")
    print(f"DeepSeek客户端: {'可用' if all_clients['deepseek'] else '不可用'}")
    print(f"Qwen客户端: {'可用' if all_clients['qwen'] else '不可用'}")
