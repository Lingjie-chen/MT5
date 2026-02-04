import sys
import os

path = r"src\trading_bot\ai\qwen_client.py"
abs_path = os.path.abspath(path)
print(f"Processing: {abs_path}")

try:
    with open(abs_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace """ with '''
    # But wait, we should be careful not to replace things that are already correct?
    # No, we just want to eliminate """ completely.
    new_content = content.replace('"""', "'''")

    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("Successfully replaced quotes.")
except Exception as e:
    print(f"Error: {e}")
