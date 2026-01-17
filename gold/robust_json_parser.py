
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

def repair_json_string(json_str: str) -> str:
    """
    尝试修复损坏的JSON字符串
    """
    # 1. 替换非法的控制字符 (Unescaped newlines/tabs)
    # 将未转义的换行符替换为 \n，制表符替换为 \t
    # 注意：这可能会误伤，但对于LLM输出来说通常是安全的假设
    new_str = ""
    i = 0
    length = len(json_str)
    in_string = False
    
    while i < length:
        char = json_str[i]
        
        if char == '"':
            # 检查是否转义
            if i > 0 and json_str[i-1] == '\\':
                # 是转义的引号，不做状态切换 (除非是 \\")
                pass 
            else:
                in_string = not in_string
        
        if in_string:
            if char == '\n':
                new_str += '\\n'
            elif char == '\t':
                new_str += '\\t'
            elif char == '\r':
                new_str += '' # 忽略
            else:
                new_str += char
        else:
            new_str += char
        i += 1
    
    # 2. 尝试闭合截断的JSON
    # 简单的堆栈法闭合括号
    stack = []
    quote_open = False
    
    # 重新扫描一遍处理后的字符串以确定闭合状态
    # 这里我们简化处理，直接基于最后的字符状态来修补
    
    # 更简单的方法：如果解析失败且是 Unterminated string，直接补引号
    # 但我们这里是预处理，所以只能做通用的括号平衡
    
    # 重新计算括号平衡
    final_str = new_str
    
    # 检查引号是否闭合
    quote_count = 0
    escape = False
    for char in final_str:
        if char == '\\':
            escape = not escape
        elif char == '"' and not escape:
            quote_count += 1
            escape = False
        else:
            escape = False
            
    if quote_count % 2 != 0:
        final_str += '"'
        
    # 检查括号平衡
    stack = []
    for char in final_str:
        if char == '{':
            stack.append('}')
        elif char == '[':
            stack.append(']')
        elif char == '}' or char == ']':
            if stack and stack[-1] == char:
                stack.pop()
    
    # 补全剩余的括号
    while stack:
        final_str += stack.pop()
        
    return final_str

def parse_llm_json(
    text: str, 
    required_keys: Optional[List[str]] = None, 
    defaults: Optional[Dict[str, Any]] = None
) -> Union[Dict[str, Any], List[Any]]:
    """
    解析LLM返回的JSON，包含提取、校验和默认值填充逻辑。
    """
    if not text:
        raise ValueError("输入文本为空")

    # 1. 提取JSON字符串
    json_str = extract_json_from_text(text)
    if not json_str:
        # 如果提取失败，尝试使用原始文本
        json_str = text.strip()

    # 2. 解析JSON
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        # 尝试修复
        try:
            # 2.1 基础修复：替换单引号，修复末尾逗号
            fixed_str = json_str.replace("'", '"')
            fixed_str = re.sub(r',\s*}', '}', fixed_str)
            fixed_str = re.sub(r',\s*]', ']', fixed_str)
            data = json.loads(fixed_str)
        except json.JSONDecodeError:
            # 2.2 进阶修复：处理未转义字符和截断
            try:
                repaired_str = repair_json_string(json_str)
                data = json.loads(repaired_str)
                logger.info("JSON通过高级修复逻辑成功解析")
            except json.JSONDecodeError as e:
                # 2.3 终极尝试：如果是 Unterminated string，尝试直接补齐引号和括号
                # 有时候 repair_json_string 可能没覆盖到所有情况
                try:
                    # 针对常见的 "Unterminated string" 错误
                    if "Unterminated string" in str(e):
                         # 暴力补齐
                         last_ditch_str = json_str + '"}]}' # 假设是典型的 [{"... truncated
                         # 或者
                         # last_ditch_str = json_str + '"}' 
                         # 这很难猜，但我们可以尝试几种常见的结束符
                         pass
                    
                    raise ValueError(f"JSON解析失败: {e}")
                except:
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
        # logger.debug(f"原始文本: {text[:200]}...")
        if fallback is not None:
            return fallback
        raise e
