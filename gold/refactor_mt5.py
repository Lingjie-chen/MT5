
import re

file_path = '/Users/lenovo/tmp/quant_trading_strategy/gold/start.py'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_line = 0
end_line = 0

for i, line in enumerate(lines):
    if 'class SymbolTrader:' in line:
        start_line = i
    if 'class MultiSymbolBot:' in line:
        end_line = i
        break

if end_line == 0:
    end_line = len(lines)

print(f"Refactoring SymbolTrader from line {start_line} to {end_line}")

# Regex to replace mt5.func(...) or mt5.CONST
# We want to replace 'mt5.' with 'self.mt5.' but only if it's not already 'self.mt5.'
# and not in the __init__ arguments default values (which are evaluated at definition time)

# Actually, arguments defaults like `timeframe=mt5.TIMEFRAME_M15` are evaluated at module level.
# So we should NOT replace those in method signatures.

new_lines = lines[:start_line+1] # Keep class definition
class_body = lines[start_line+1:end_line]

for i, line in enumerate(class_body):
    # Skip def lines to avoid messing up default args
    if line.strip().startswith('def '):
        new_lines.append(line)
        continue
        
    # Replace mt5. with self.mt5.
    # Be careful not to replace 'import mt5' or 'from mt5' (though those are at top)
    # Also handle multiple occurrences
    
    # Simple replace
    new_line = line.replace('mt5.', 'self.mt5.')
    new_lines.append(new_line)

new_lines.extend(lines[end_line:])

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Done.")
