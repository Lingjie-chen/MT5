
import os

file_path = r"c:\Users\Administrator\Desktop\MT5\src\trading_bot\main.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the start line
start_idx = -1
for i, line in enumerate(lines):
    if "if df is not None:" in line:
        start_idx = i + 1
        break

if start_idx == -1:
    print("Could not find 'if df is not None:'")
    exit(1)

# Find the end line (before except)
# We look for "except Exception as e:" around line 3934
end_idx = -1
for i in range(len(lines) - 1, start_idx, -1):
    if "except Exception as e:" in lines[i] and "Error in main loop" in lines[i+1]:
        end_idx = i
        break

if end_idx == -1:
    # Try finding strictly by content if line number shifted
    for i in range(len(lines) - 1, start_idx, -1):
        if "except Exception as e:" in lines[i]:
            # Check context
            if i+1 < len(lines) and "logger.error" in lines[i+1] and "Error in main loop" in lines[i+1]:
                end_idx = i
                break

if end_idx == -1:
    print("Could not find matching 'except Exception as e:' block")
    # For debugging, print lines around expected end
    # print(lines[-50:])
    exit(1)

print(f"Block range: {start_idx+1} to {end_idx}")

# Insert try:
indentation = " " * 24
lines.insert(start_idx, indentation + "try:\n")

# Indent the block
# The block is now from start_idx + 1 to end_idx + 1 (because we inserted one line)
block_start = start_idx + 1
block_end = end_idx + 1

for i in range(block_start, block_end):
    if lines[i].strip(): # Only indent non-empty lines
        lines[i] = "    " + lines[i]

# Adjust except block indentation
# The except block starts at block_end
# It should be at 24 spaces (same as try)
# Currently it's likely at 20 spaces (based on previous analysis)
# We need to make sure it matches 'try' (24 spaces)

# Check except line indentation
except_line = lines[block_end]
current_indent = len(except_line) - len(except_line.lstrip())
print(f"Current except indentation: {current_indent}")

# We want 24 spaces
desired_indent = 24
if current_indent != desired_indent:
    lines[block_end] = " " * desired_indent + except_line.lstrip()
    
    # Also fix indentation for the except block content (3 lines usually)
    # logger.error
    # time.sleep
    # continue
    
    i = block_end + 1
    while i < len(lines) and (len(lines[i]) - len(lines[i].lstrip())) > current_indent:
        # Increase indentation relative to new except
        # Assuming original was consistent relative to except
        # We just add (desired - current) spaces
        if lines[i].strip():
            lines[i] = " " * (desired_indent + 4) + lines[i].lstrip()
        i += 1

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Indentation fixed.")
