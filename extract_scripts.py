import re

with open('/Users/lenovo/Downloads/大模型多因子模型构建系统_实施报告.md', 'r') as f:
    content = f.read()

# The first Python block is factor_discovery.py
match1 = re.search(r'```python\n(.*?)```', content, re.DOTALL)
if match1:
    with open('src/trading_bot/analysis/factor_discovery.py', 'w') as f:
        f.write(match1.group(1))
    print("Extracted factor_discovery.py")

# The test script starts at line 1236, as a string variable `test_script = """..."""`
match2 = re.search(r'test_script = """\n(.*?)\n"""', content, re.DOTALL)
if match2:
    with open('src/trading_bot/analysis/test_factor_discovery.py', 'w') as f:
        f.write(match2.group(1))
    print("Extracted test_factor_discovery.py")
