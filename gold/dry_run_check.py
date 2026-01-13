def infer_trade_type_from_qwen(action, entry_conditions, bid, ask):
    action = (action or "").lower().strip()
    entry_conditions = entry_conditions or {}
    entry_price = entry_conditions.get("limit_price", entry_conditions.get("entry_price", 0.0)) or 0.0
    if entry_price and action in {"buy", "add_buy"}:
        return "limit_buy" if entry_price < ask else "stop_buy"
    if entry_price and action in {"sell", "add_sell"}:
        return "limit_sell" if entry_price > bid else "stop_sell"
    return action


def run():
    bid = 1.1659
    ask = 1.1661

    eurusd = {
        "action": "sell",
        "entry_conditions": {"limit_price": 1.1663},
        "exit_conditions": {"sl_price": 1.1675, "tp_price": 1.1635},
        "position_size": 0.15,
    }
    assert infer_trade_type_from_qwen(eurusd["action"], eurusd["entry_conditions"], bid, ask) == "limit_sell"

    eurusd2 = {
        "action": "sell",
        "entry_conditions": {"limit_price": 1.1650},
    }
    assert infer_trade_type_from_qwen(eurusd2["action"], eurusd2["entry_conditions"], bid, ask) == "stop_sell"

    buy1 = {"action": "buy", "entry_conditions": {"limit_price": 1.1655}}
    assert infer_trade_type_from_qwen(buy1["action"], buy1["entry_conditions"], bid, ask) == "limit_buy"

    buy2 = {"action": "buy", "entry_conditions": {"limit_price": 1.1665}}
    assert infer_trade_type_from_qwen(buy2["action"], buy2["entry_conditions"], bid, ask) == "stop_buy"

    print("dry_run_check: OK")


if __name__ == "__main__":
    run()

