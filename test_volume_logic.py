
def normalize_volume(lot, step, v_min, v_max):
    print(f"Input: {lot} | Step: {step} | Min: {v_min} | Max: {v_max}")
    
    if step > 0:
        steps = round(lot / step)
        lot = steps * step
        print(f"  After Step: {lot}")
    
    if v_min > 0:
        lot = max(v_min, lot)
        print(f"  After Min: {lot}")
        
    if v_max > 0:
        lot = min(v_max, lot)
        print(f"  After Max: {lot}")
        
    lot = round(lot, 2)
    print(f"  Final: {lot}")
    return lot

print("--- Test Case 1: Standard Gold ---")
normalize_volume(0.123, 0.01, 0.01, 100)

print("\n--- Test Case 2: Micro Lot ---")
normalize_volume(0.005, 0.01, 0.01, 100)

print("\n--- Test Case 3: Large Step ---")
normalize_volume(0.15, 0.1, 0.1, 100)

print("\n--- Test Case 4: Max Limit ---")
normalize_volume(150, 0.01, 0.01, 100)

print("\n--- Test Case 5: Floating Point Drift ---")
normalize_volume(0.30000000000000004, 0.01, 0.01, 100)
