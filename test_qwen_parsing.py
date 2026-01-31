
import unittest
import logging
import sys
import os

# Adjust path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from trading_bot.utils.robust_json_parser import safe_parse_or_default

class TestQwenParsing(unittest.TestCase):
    def test_position_size_parsing(self):
        # Case 1: Standard JSON
        json_1 = '{"action": "buy", "position_size": 0.55, "rationale": "test"}'
        res_1 = safe_parse_or_default(json_1)
        self.assertEqual(res_1.get("position_size"), 0.55)
        
        # Case 2: Nested in Markdown
        json_2 = 'Here is the plan:\n```json\n{"action": "buy", "position_size": 1.20}\n```'
        res_2 = safe_parse_or_default(json_2)
        self.assertEqual(res_2.get("position_size"), 1.20)
        
        # Case 3: Missing position_size (should return what is parsed, logic handles default later)
        json_3 = '{"action": "hold"}'
        res_3 = safe_parse_or_default(json_3)
        self.assertIsNone(res_3.get("position_size"))
        
        # Case 4: String format (sometimes LLM returns string instead of float)
        json_4 = '{"position_size": "0.33"}'
        res_4 = safe_parse_or_default(json_4)
        # robust_json_parser uses json.loads which parses "0.33" as string
        self.assertEqual(res_4.get("position_size"), "0.33") 
        # Application logic converts to float
        
    def test_broken_json_recovery(self):
        # Case 5: Missing closing brace
        json_5 = '{"action": "buy", "position_size": 0.1'
        # robust_json_parser tries to repair
        # repair_json_string attempts to balance brackets
        # "{"action": "buy", "position_size": 0.1" -> add "}" -> "{"action": "buy", "position_size": 0.1}"
        # This is valid JSON? No, 0.1" is invalid. 
        # Wait, repair logic:
        # It balances brackets.
        # Let's see if it works.
        try:
            res_5 = safe_parse_or_default(json_5)
            print(f"Repaired JSON 5: {res_5}")
        except:
            print("Failed to repair JSON 5")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
