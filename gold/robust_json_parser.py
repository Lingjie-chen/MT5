import json
import re
import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

def extract_json_from_text(text: str) -> Optional[str]:
    """
    从LLM响应文本中提取JSON字符串。
    支持：
    1. ```json ... ``` 代码块
    2. 纯JSON字符串
    3. 混合文本中的 {...} 或 [...] 结构
    """
    if not text:
        return None

    # 1. 尝试匹配markdown代码块
    json_block_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(json_block_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # 2. 尝试寻找最外层的 {} 或 []
    # 使用简单的栈平衡查找可能更准确，但正则对于常见情况够用
    # 查找第一个 { 和最后一个 }
    stack = 0
    start_index = -1
    end_index = -1
    
    # 寻找对象 {}
    for i, char in enumerate(text):
        if char == '{':
            if stack == 0:
                start_index = i
            stack += 1
        elif char == '}':
            stack -= 1
            if stack == 0:
                end_index = i
                # 找到第一个完整的顶级对象后，我们可以尝试解析它
                # 如果需要支持多个对象，逻辑需要调整，但通常LLM只返回一个主要JSON
                candidate = text[start_index : end_index + 1]
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    # 如果解析失败，可能是内部花括号不匹配或格式错误，继续寻找
                    continue
    
    # 如果没找到有效的 {} 对象，尝试寻找数组 []
    stack = 0
    start_index = -1
    end_index = -1
    for i, char in enumerate(text):
        if char == '[':
            if stack == 0:
                start_index = i
            stack += 1
        elif char == ']':
            stack -= 1
            if stack == 0:
                end_index = i
                candidate = text[start_index : end_index + 1]
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    continue

    # 3. 如果都失败了，返回原始文本（可能它就是纯JSON，或者是非标准格式）
    return text.strip()

def parse_llm_json(
    text: str, 
    required_keys: Optional[List[str]] = None, 
    defaults: Optional[Dict[str, Any]] = None
) -> Union[Dict[str, Any], List[Any]]:
    """
    解析LLM返回的JSON，包含提取、校验和默认值填充逻辑。
    
    Args:
        text: LLM返回的原始文本
        required_keys: 必须存在的顶层键名列表（仅对字典类型有效）
        defaults: 缺失字段的默认值字典（仅对字典类型有效）
        
    Returns:
        解析后的Python对象（Dict或List）
        
    Raises:
        ValueError: 如果解析失败或缺少必要字段且无默认值
    """
    if not text:
        raise ValueError("输入文本为空")

    # 1. 提取JSON字符串
    json_str = extract_json_from_text(text)
    if not json_str:
        raise ValueError("无法从文本中提取JSON内容")

    # 2. 解析JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        # 尝试一些常见的修复
        try:
            # 有时候LLM会使用单引号
            data = json.loads(json_str.replace("'", '"'))
        except json.JSONDecodeError:
             # 尝试修复末尾的逗号 (简单情况)
            try:
                fixed_str = re.sub(r',\s*}', '}', json_str)
                fixed_str = re.sub(r',\s*]', ']', fixed_str)
                data = json.loads(fixed_str)
            except json.JSONDecodeError:
                raise ValueError(f"JSON解析失败: {e}")

    # 3. 校验和填充（仅针对字典）
    if isinstance(data, dict):
        if defaults:
            for key, value in defaults.items():
                if key not in data:
                    data[key] = value
        
        if required_keys:
            missing_keys = [k for k in required_keys if k not in data]
            if missing_keys:
                raise ValueError(f"JSON缺少必要字段: {', '.join(missing_keys)}")
                
    return data

def safe_parse_or_default(
    text: str,
    required_keys: Optional[List[str]] = None,
    defaults: Optional[Dict[str, Any]] = None,
    fallback: Optional[Any] = None
) -> Any:
    """
    安全解析JSON，失败时返回fallback值。
    """
    try:
        return parse_llm_json(text, required_keys, defaults)
    except Exception as e:
        logger.warning(f"JSON解析失败，使用fallback: {e}")
        logger.debug(f"原始文本: {text[:200]}...")
        if fallback is not None:
            return fallback
        raise e
