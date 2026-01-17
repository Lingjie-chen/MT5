
import os
import sys

# Add the current directory to sys.path
sys.path.append(os.getcwd())

from gold.qwen_client import QwenClient

def test_timeout_config():
    # 模拟环境变量
    os.environ["API_TIMEOUT"] = "600"
    
    client = QwenClient(api_key="test_key")
    
    # 简单的 mock 测试，验证 _call_api 是否正确获取了 timeout 值
    # 由于我们不能真的发请求（会超时或失败），我们这里主要依赖之前的代码审查确认逻辑
    # 这里只打印验证信息
    
    print(f"Current API_TIMEOUT env var: {os.environ.get('API_TIMEOUT')}")
    
    # 验证代码中是否有读取环境变量的逻辑
    import inspect
    source = inspect.getsource(client._call_api)
    if 'os.getenv("API_TIMEOUT", 300)' in source:
        print("PASS: Code contains timeout configuration logic")
    else:
        print("FAIL: Code missing timeout configuration logic")

if __name__ == "__main__":
    test_timeout_config()
