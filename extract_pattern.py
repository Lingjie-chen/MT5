import re
with open('/Users/lenovo/Downloads/大模型交易模式识别系统_项目实施报告.md', 'r') as f:
    content = f.read()
match = re.search(r'import json\n(.*?)\nwith open', content, re.DOTALL)
if match:
    # Not embedded code... Ah wait, the Python source files were NOT embedded inside the MD! 
    # Let's check the MD content for "```python" blocks
    pass
