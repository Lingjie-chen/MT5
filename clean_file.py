import sys
import os

path = r"src\trading_bot\ai\qwen_client.py"
abs_path = os.path.abspath(path)
print(f"Processing: {abs_path}")

try:
    with open(abs_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace Chinese punctuation
    replacements = {
        '，': ',',
        '：': ':',
        '（': '(',
        '）': ')',
        '“': '"',
        '”': '"',
        '‘': "'",
        '’': "'",
        '。': '.',
        '！': '!',
        '？': '?',
        '；': ';',
        '…': '...',
        '、': ',',
        '—': '-'
    }
    
    new_content = content
    for old, new in replacements.items():
        new_content = new_content.replace(old, new)

    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("Successfully cleaned file.")
except Exception as e:
    print(f"Error: {e}")
