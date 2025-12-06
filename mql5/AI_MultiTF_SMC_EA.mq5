//+------------------------------------------------------------------+
//| AI_MultiTF_SMC_EA.mq5                                            |
//| Copyright 2024, AI Quant Trading                                 |
//| https://github.com/ai-quant-trading                              |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Quant Trading"
#property link      "https://github.com/ai-quant-trading"
#property version   "1.00"
#property strict

// 包含必要的头文件
#include <MT4Orders.mqh>
#include <stdlib.mqh>
#include <time.mqh>
#include <WinInet.mqh>

//+------------------------------------------------------------------+
//| EA输入参数                                                       |
//+------------------------------------------------------------------+
input string SymbolName = "GOLD";                // 交易品种
input ENUM_TIMEFRAMES Timeframe = PERIOD_H1;      // 交易周期
input double RiskPerTrade = 1.0;                  // 每笔交易风险百分比
input double MaxDailyLoss = 2.0;                  // 每日最大亏损百分比
input string PythonServerURL = "http://localhost:5000"; // Python服务URL
input int MagicNumber = 123456;                   // 魔术数字
input bool EnableLogging = true;                  // 启用日志记录

//+------------------------------------------------------------------+
//| 全局变量                                                         |
//+------------------------------------------------------------------+
bool EA_Running = false;                          // EA运行状态
double AccountBalance = 0.0;                      // 账户余额
double DailyLoss = 0.0;                           // 当日亏损
datetime LastTradeDay = 0;                        // 最后交易日期

//+------------------------------------------------------------------+
//| 初始化函数                                                       |
//+------------------------------------------------------------------+
int OnInit()
{
    // 设置EA名称
    IndicatorSetString(INDICATOR_SHORTNAME, "AI_MultiTF_SMC_EA");
    
    // 初始化日志
    if(EnableLogging)
    {
        Print("AI_MultiTF_SMC_EA 初始化成功");
        Print("交易品种: ", SymbolName);
        Print("交易周期: ", EnumToString(Timeframe));
        Print("每笔交易风险: ", RiskPerTrade, "%");
        Print("每日最大亏损: ", MaxDailyLoss, "%");
        Print("Python服务URL: ", PythonServerURL);
    }
    
    // 获取初始账户余额
    AccountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    
    // 设置最后交易日期
    LastTradeDay = TimeDay(TimeCurrent());
    
    // 设置EA运行状态
    EA_Running = true;
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| 去初始化函数                                                     |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    // 关闭日志
    if(EnableLogging)
    {
        Print("AI_MultiTF_SMC_EA 去初始化成功，原因: ", reason);
    }
    
    // 设置EA运行状态
    EA_Running = false;
}

//+------------------------------------------------------------------+
//| 主函数                                                           |
//+------------------------------------------------------------------+
void OnTick()
{
    // 检查EA是否运行
    if(!EA_Running)
        return;
    
    // 检查每日亏损
    CheckDailyLoss();
    
    // 获取当前市场数据
    MqlRates rates[];
    int count = CopyRates(SymbolName, Timeframe, 0, 100, rates);
    if(count <= 0)
    {
        if(EnableLogging)
            Print("无法获取市场数据，错误代码: ", GetLastError());
        return;
    }
    
    // 调用Python服务获取交易信号
    string signal = GetAISignal(rates);
    
    // 处理交易信号
    ProcessSignal(signal);
}

//+------------------------------------------------------------------+
//| 检查每日亏损                                                     |
//+------------------------------------------------------------------+
void CheckDailyLoss()
{
    datetime current_time = TimeCurrent();
    int current_day = TimeDay(current_time);
    
    // 新的一天，重置每日亏损
    if(current_day != LastTradeDay)
    {
        DailyLoss = 0.0;
        LastTradeDay = current_day;
        if(EnableLogging)
            Print("新的交易日，重置每日亏损");
        return;
    }
    
    // 计算当前亏损
    double current_balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double drawdown = (AccountBalance - current_balance) / AccountBalance * 100;
    
    // 检查是否超过每日最大亏损
    if(drawdown >= MaxDailyLoss)
    {
        if(EnableLogging)
            Print("达到每日最大亏损限制，EA将停止交易");
        
        // 平仓所有头寸
        CloseAllPositions();
        
        // 停止EA
        EA_Running = false;
    }
}

//+------------------------------------------------------------------+
//| 调用Python服务获取交易信号                                       |
//+------------------------------------------------------------------+
string GetAISignal(MqlRates rates[])
{
    // 构建请求数据
    string request_data = "{\"symbol\":\"" + SymbolName + "\",";
    request_data += "\"timeframe\":\"" + EnumToString(Timeframe) + "\",";
    request_data += "\"rates\":[";
    
    // 添加最近20根K线数据
    for(int i = 0; i < MathMin(20, ArraySize(rates)); i++)
    {
        request_data += "{\"time\":\"" + TimeToString(rates[i].time, TIME_DATE|TIME_MINUTES) + "\",";
        request_data += "\"open\":" + DoubleToString(rates[i].open, 5) + ",";
        request_data += "\"high\":" + DoubleToString(rates[i].high, 5) + ",";
        request_data += "\"low\":" + DoubleToString(rates[i].low, 5) + ",";
        request_data += "\"close\":" + DoubleToString(rates[i].close, 5) + ",";
        request_data += "\"tick_volume\":" + IntegerToString(rates[i].tick_volume) + "}";
        
        if(i < MathMin(20, ArraySize(rates)) - 1)
            request_data += ",";
    }
    
    request_data += "]}";
    
    // 发送HTTP请求
    string response = SendHTTPRequest(PythonServerURL + "/get_signal", request_data);
    
    if(response == "")
    {
        if(EnableLogging)
            Print("Python服务请求失败");
        return "none";
    }
    
    if(EnableLogging)
        Print("Python服务响应: ", response);
    
    // 解析响应
    string signal = ParseJSON(response, "signal");
    
    return signal;
}

//+------------------------------------------------------------------+
//| 发送HTTP请求                                                     |
//+------------------------------------------------------------------+
string SendHTTPRequest(string url, string data)
{
    string result = "";
    
    // 打开连接
    int hSession = InternetOpenA("MQL5 HTTP Client", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
    if(hSession == INVALID_HANDLE)
        return result;
    
    int hConnect = InternetConnectA(hSession, "localhost", 5000, "", "", INTERNET_SERVICE_HTTP, 0, 0);
    if(hConnect == INVALID_HANDLE)
    {
        InternetCloseHandle(hSession);
        return result;
    }
    
    // 创建HTTP请求
    string headers = "Content-Type: application/json\r\n";
    DWORD dwFlags = INTERNET_FLAG_RELOAD | INTERNET_FLAG_NO_CACHE_WRITE;
    int hRequest = HttpOpenRequestA(hConnect, "POST", "/get_signal", NULL, NULL, NULL, dwFlags, 0);
    if(hRequest == INVALID_HANDLE)
    {
        InternetCloseHandle(hConnect);
        InternetCloseHandle(hSession);
        return result;
    }
    
    // 发送请求
    if(HttpSendRequestA(hRequest, headers, StringLen(headers), data, StringLen(data)))
    {
        // 读取响应
        char buffer[1024];
        DWORD bytesRead;
        while(InternetReadFile(hRequest, buffer, sizeof(buffer), &bytesRead) && bytesRead > 0)
        {
            result += CharArrayToString(buffer, 0, bytesRead);
        }
    }
    
    // 关闭连接
    InternetCloseHandle(hRequest);
    InternetCloseHandle(hConnect);
    InternetCloseHandle(hSession);
    
    return result;
}

//+------------------------------------------------------------------+
//| 解析JSON数据                                                     |
//+------------------------------------------------------------------+
string ParseJSON(string json, string key)
{
    string pattern = "\"" + key + "\":\"([^\"]*)\"";
    string result = "";
    
    int start_pos = StringFind(json, pattern, 0);
    if(start_pos != -1)
    {
        int value_start = start_pos + StringLen(key) + 3;
        int value_end = StringFind(json, "\"", value_start);
        if(value_end != -1)
        {
            result = StringSubstr(json, value_start, value_end - value_start);
        }
    }
    
    return result;
}

//+------------------------------------------------------------------+
//| 处理交易信号                                                     |
//+------------------------------------------------------------------+
void ProcessSignal(string signal)
{
    if(signal == "none" || !EA_Running)
        return;
    
    // 检查当前持仓
    int position_count = PositionsTotal();
    bool has_long = false;
    bool has_short = false;
    
    for(int i = 0; i < position_count; i++)
    {
        if(PositionGetSymbol(i) == SymbolName && PositionGetInteger(POSITION_MAGIC) == MagicNumber)
        {
            if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
                has_long = true;
            else if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL)
                has_short = true;
        }
    }
    
    // 处理买入信号
    if(signal == "buy" && !has_long)
    {
        // 平仓空头头寸
        if(has_short)
            CloseAllShortPositions();
        
        // 执行买入
        ExecuteOrder(OP_BUY);
    }
    // 处理卖出信号
    else if(signal == "sell" && !has_short)
    {
        // 平仓多头头寸
        if(has_long)
            CloseAllLongPositions();
        
        // 执行卖出
        ExecuteOrder(OP_SELL);
    }
    // 处理平仓信号
    else if(signal == "close_all")
    {
        CloseAllPositions();
    }
}

//+------------------------------------------------------------------+
//| 执行订单                                                         |
//+------------------------------------------------------------------+
void ExecuteOrder(ENUM_ORDER_TYPE order_type)
{
    // 检查EA是否运行
    if(!EA_Running)
        return;
    
    // 获取当前价格
    double ask = SymbolInfoDouble(SymbolName, SYMBOL_ASK);
    double bid = SymbolInfoDouble(SymbolName, SYMBOL_BID);
    
    // 计算ATR
    double atr = iATR(SymbolName, Timeframe, 14, 0);
    if(atr <= 0)
    {
        if(EnableLogging)
            Print("ATR计算失败，无法执行订单");
        return;
    }
    
    // 计算止损和止盈
    double stop_loss = 0.0;
    double take_profit = 0.0;
    
    if(order_type == OP_BUY)
    {
        stop_loss = ask - atr * 1.5;
        take_profit = ask + atr * 2.5;
    }
    else if(order_type == OP_SELL)
    {
        stop_loss = bid + atr * 1.5;
        take_profit = bid - atr * 2.5;
    }
    
    // 计算仓位大小
    double lot_size = CalculateLotSize(atr, order_type);
    if(lot_size <= 0)
    {
        if(EnableLogging)
            Print("仓位计算失败，无法执行订单");
        return;
    }
    
    // 执行订单
    int ticket = 0;
    if(order_type == OP_BUY)
    {
        ticket = OrderSend(SymbolName, OP_BUY, lot_size, ask, 3, stop_loss, take_profit, "AI_MultiTF_SMC_EA Buy", MagicNumber, 0, clrGreen);
    }
    else if(order_type == OP_SELL)
    {
        ticket = OrderSend(SymbolName, OP_SELL, lot_size, bid, 3, stop_loss, take_profit, "AI_MultiTF_SMC_EA Sell", MagicNumber, 0, clrRed);
    }
    
    // 检查订单执行结果
    if(ticket > 0)
    {
        if(EnableLogging)
            Print("订单执行成功，订单号: ", ticket, ", 类型: ", EnumToString(order_type), ", 手数: ", lot_size);
    }
    else
    {
        if(EnableLogging)
            Print("订单执行失败，错误代码: ", GetLastError());
    }
}

//+------------------------------------------------------------------+
//| 计算仓位大小                                                     |
//+------------------------------------------------------------------+
double CalculateLotSize(double atr, ENUM_ORDER_TYPE order_type)
{
    // 计算每手的价值
    double tick_value = SymbolInfoDouble(SymbolName, SYMBOL_TRADE_TICK_VALUE);
    double tick_size = SymbolInfoDouble(SymbolName, SYMBOL_TRADE_TICK_SIZE);
    
    // 计算风险金额
    double risk_amount = AccountBalance * (RiskPerTrade / 100.0);
    
    // 计算止损点数
    double stop_loss_points = atr / tick_size;
    
    // 计算每手风险
    double risk_per_lot = stop_loss_points * tick_value;
    
    // 计算仓位大小
    double lot_size = risk_amount / risk_per_lot;
    
    // 获取最小和最大仓位
    double min_lot = SymbolInfoDouble(SymbolName, SYMBOL_VOLUME_MIN);
    double max_lot = SymbolInfoDouble(SymbolName, SYMBOL_VOLUME_MAX);
    double lot_step = SymbolInfoDouble(SymbolName, SYMBOL_VOLUME_STEP);
    
    // 调整仓位大小
    lot_size = MathMax(min_lot, MathMin(max_lot, NormalizeDouble(lot_size, 2)));
    lot_size = lot_step * MathRound(lot_size / lot_step);
    
    return lot_size;
}

//+------------------------------------------------------------------+
//| 平仓所有多头头寸                                                 |
//+------------------------------------------------------------------+
void CloseAllLongPositions()
{
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        if(PositionGetSymbol(i) == SymbolName && PositionGetInteger(POSITION_MAGIC) == MagicNumber)
        {
            if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
            {
                double bid = SymbolInfoDouble(SymbolName, SYMBOL_BID);
                int ticket = PositionGetInteger(POSITION_TICKET);
                double volume = PositionGetDouble(POSITION_VOLUME);
                
                if(OrderClose(ticket, volume, bid, 3, clrRed))
                {
                    if(EnableLogging)
                        Print("平仓成功，订单号: ", ticket, ", 类型: 多头");
                }
                else
                {
                    if(EnableLogging)
                        Print("平仓失败，订单号: ", ticket, ", 错误代码: ", GetLastError());
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| 平仓所有空头头寸                                                 |
//+------------------------------------------------------------------+
void CloseAllShortPositions()
{
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        if(PositionGetSymbol(i) == SymbolName && PositionGetInteger(POSITION_MAGIC) == MagicNumber)
        {
            if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL)
            {
                double ask = SymbolInfoDouble(SymbolName, SYMBOL_ASK);
                int ticket = PositionGetInteger(POSITION_TICKET);
                double volume = PositionGetDouble(POSITION_VOLUME);
                
                if(OrderClose(ticket, volume, ask, 3, clrGreen))
                {
                    if(EnableLogging)
                        Print("平仓成功，订单号: ", ticket, ", 类型: 空头");
                }
                else
                {
                    if(EnableLogging)
                        Print("平仓失败，订单号: ", ticket, ", 错误代码: ", GetLastError());
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| 平仓所有头寸                                                     |
//+------------------------------------------------------------------+
void CloseAllPositions()
{
    CloseAllLongPositions();
    CloseAllShortPositions();
}

//+------------------------------------------------------------------+
//| 取消所有挂单                                                     |
//+------------------------------------------------------------------+
void DeleteAllPendingOrders()
{
    for(int i = OrdersTotal() - 1; i >= 0; i--)
    {
        if(OrderGetSymbol(i) == SymbolName && OrderGetInteger(ORDER_MAGIC) == MagicNumber)
        {
            int ticket = OrderGetInteger(ORDER_TICKET);
            if(OrderDelete(ticket))
            {
                if(EnableLogging)
                    Print("取消挂单成功，订单号: ", ticket);
            }
            else
            {
                if(EnableLogging)
                    Print("取消挂单失败，订单号: ", ticket, ", 错误代码: ", GetLastError());
            }
        }
    }
}

//+------------------------------------------------------------------+
//| 定时器函数                                                       |
//+------------------------------------------------------------------+
void OnTimer()
{
    // 可以在这里添加定时任务，例如定期更新模型或检查服务器连接
}

//+------------------------------------------------------------------+
//| 订单变化事件                                                     |
//+------------------------------------------------------------------+
void OnTrade()
{
    // 可以在这里处理订单变化事件
    if(EnableLogging)
        Print("检测到订单变化");
}

//+------------------------------------------------------------------+
//| 账户变化事件                                                     |
//+------------------------------------------------------------------+
void OnAccount()
{
    // 可以在这里处理账户变化事件
    if(EnableLogging)
        Print("检测到账户变化");
}
//+------------------------------------------------------------------+
//| EA结束函数                                                       |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    // 平仓所有头寸
    CloseAllPositions();
    
    // 取消所有挂单
    DeleteAllPendingOrders();
    
    if(EnableLogging)
        Print("AI_MultiTF_SMC_EA 已停止，原因: ", reason);
}
