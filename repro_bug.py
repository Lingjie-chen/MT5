
import sys
import os
import logging
from crypto.optimization import WOAm

# Mock objective function
def objective(params):
    return sum(params)

def run_test(steps_val, description):
    print(f"Testing with steps={steps_val} ({description})...")
    optimizer = WOAm(pop_size=10)
    bounds = [(0, 10), (0, 10), (0, 10)]
    
    try:
        best, score = optimizer.optimize(objective, bounds, steps=steps_val, epochs=1)
        print("Success!")
        return True
    except TypeError as e:
        print(f"Caught expected TypeError: {e}")
        return False
    except Exception as e:
        print(f"Caught unexpected exception: {e}")
        return False

if __name__ == "__main__":
    # 1. Test the bug
    print("--- Reproduction ---")
    bug_repro = run_test(15, "Integer value - Bug")
    
    # 2. Test the fix (List)
    print("\n--- Fix Verification (List) ---")
    fix_repro_list = run_test([1, 1, 1], "List of ints - Fix")

    # 3. Test the fix (None)
    print("\n--- Fix Verification (None) ---")
    fix_repro_none = run_test(None, "None - Fix")
    
    if not bug_repro and fix_repro_list and fix_repro_none:
        print("\nVERIFICATION SUCCESSFUL: Bug reproduced and fix works.")
    else:
        print("\nVERIFICATION FAILED.")
