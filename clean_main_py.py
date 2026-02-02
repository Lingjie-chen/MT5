
import os

file_path = r"c:\Users\Administrator\Desktop\MT5\src\trading_bot\main.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the valid shutdown end
shutdown_idx = -1
for i, line in enumerate(lines):
    if "def shutdown(self):" in line:
        # Look for the first mt5.shutdown() inside this method
        for j in range(i, len(lines)):
            if "mt5.shutdown()" in lines[j] and "logger.info" not in lines[j]: # Simple heuristic
                shutdown_idx = j
                break
        break

if shutdown_idx == -1:
    print("Could not find 'mt5.shutdown()' in 'def shutdown'")
    exit(1)

print(f"Found shutdown at line {shutdown_idx + 1}")

# Find the start of MultiSymbolBot
class_idx = -1
for i in range(shutdown_idx, len(lines)):
    if "class MultiSymbolBot:" in line: # This loop variable 'line' is stale! Bug in my thought.
        pass

for i in range(shutdown_idx, len(lines)):
    if "class MultiSymbolBot:" in lines[i]:
        class_idx = i
        break

if class_idx == -1:
    print("Could not find 'class MultiSymbolBot:'")
    exit(1)

print(f"Found class MultiSymbolBot at line {class_idx + 1}")

# Check if there are lines to delete
if class_idx > shutdown_idx + 1:
    print(f"Deleting lines {shutdown_idx + 2} to {class_idx}")
    # Keep lines[:shutdown_idx+1] and lines[class_idx:]
    new_lines = lines[:shutdown_idx+1] + lines[class_idx:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Garbage removed.")
else:
    print("No garbage found.")
