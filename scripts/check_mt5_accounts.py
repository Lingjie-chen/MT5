import sys
import os
import MetaTrader5 as mt5
from dotenv import load_dotenv

# Adjust path to find src if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Load .env explicitly
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

def check_account_connection(account_id_env, password_env, server_env, label):
    account = os.getenv(account_id_env)
    password = os.getenv(password_env)
    server = os.getenv(server_env)
    
    if not account or not password or not server:
        print(f"❌ {label}: Configuration missing in .env")
        return False
        
    try:
        account = int(account)
    except ValueError:
        print(f"❌ {label}: Account ID {account} is not a valid integer")
        return False

    print(f"\nAttempting to connect to {label}...")
    print(f"  Account: {account}")
    print(f"  Server:  {server}")
    
    # Initialize MT5 (if not already)
    if not mt5.initialize():
        print(f"  Critical Error: MT5 Initialize Failed: {mt5.last_error()}")
        return False
        
    # Login
    authorized = mt5.login(account, password=password, server=server)
    
    if authorized:
        info = mt5.account_info()
        if info:
            print(f"✅ {label}: Login Successful!")
            print(f"  Balance: {info.balance} {info.currency}")
            print(f"  Equity:  {info.equity}")
            print(f"  Name:    {info.name}")
            print(f"  Server:  {info.server}")
        else:
             print(f"⚠️ {label}: Login successful but failed to retrieve account info.")
    else:
        err = mt5.last_error()
        print(f"❌ {label}: Login Failed. Error Code: {err}")
        # Common error codes:
        # -2: Common error
        # 10004: Trade server is busy
        # 10027: Enable 'Automated trading'
        
    return authorized

def main():
    print("=== MT5 Multi-Account Connection Check ===")
    
    # Check Account 1
    check_account_connection("MT5_ACCOUNT_1", "MT5_PASSWORD_1", "MT5_SERVER_1", "Account 1 (Ava-Real)")
    
    # Check Account 2
    check_account_connection("MT5_ACCOUNT_2", "MT5_PASSWORD_2", "MT5_SERVER_2", "Account 2 (Exness)")
    
    # Check Account 3
    check_account_connection("MT5_ACCOUNT_3", "MT5_PASSWORD_3", "MT5_SERVER_3", "Account 3 (Ava-Demo)")
    
    print("\n=== Check Complete ===")
    mt5.shutdown()

if __name__ == "__main__":
    main()
