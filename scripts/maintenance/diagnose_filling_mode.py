import os
import MetaTrader5 as mt5

def diagnose(symbol_name="GOLD", account_index=1):
    if not mt5.initialize():
        print(f"MT5 Init Failed: {mt5.last_error()}")
        return 1

    acc = os.getenv(f"MT5_ACCOUNT_{account_index}")
    pwd = os.getenv(f"MT5_PASSWORD_{account_index}")
    srv = os.getenv(f"MT5_SERVER_{account_index}")
    if acc and pwd and srv:
        mt5.login(int(acc), password=pwd, server=srv)

    info = mt5.symbol_info(symbol_name)
    print(f"symbol_info={bool(info)} last_error={mt5.last_error()}")
    if info is None:
        mt5.shutdown()
        return 2

    mt5.symbol_select(symbol_name, True)
    print(f"symbol={symbol_name} filling_mode_flags={info.filling_mode} volume_min={info.volume_min} volume_step={info.volume_step}")

    tick = mt5.symbol_info_tick(symbol_name)
    if tick is None:
        print(f"tick None last_error={mt5.last_error()}")
        mt5.shutdown()
        return 3

    vol = float(info.volume_min if info.volume_min and info.volume_min > 0 else 0.01)
    modes = [
        ("IOC", mt5.ORDER_FILLING_IOC),
        ("FOK", mt5.ORDER_FILLING_FOK),
        ("RETURN", mt5.ORDER_FILLING_RETURN),
    ]

    for name, mode in modes:
        req = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol_name,
            "volume": vol,
            "type": mt5.ORDER_TYPE_BUY,
            "price": float(tick.ask),
            "deviation": 20,
            "magic": 999999,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mode,
        }
        res = mt5.order_check(req)
        if res is None:
            print(f"order_check {name}: None last_error={mt5.last_error()}")
        else:
            print(f"order_check {name}: retcode={res.retcode} comment={res.comment}")

    mt5.shutdown()
    return 0

if __name__ == "__main__":
    raise SystemExit(diagnose())
