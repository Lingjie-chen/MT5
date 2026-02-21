import os
import re

content = open('src/trading_bot/6个文件', 'r').read()

pattern = r'\*\*文件\*\*: `([^`]+)`\n\n```python\n(.*?)```'
matches = re.finditer(pattern, content, re.DOTALL)

os.makedirs('src/trading_bot/analysis', exist_ok=True)

for match in matches:
    filename = match.group(1)
    code = match.group(2)
    filepath = os.path.join('src/trading_bot/analysis', filename)
    with open(filepath, 'w') as f:
        f.write(code.strip() + '\n')
    print('Created:', filepath)
