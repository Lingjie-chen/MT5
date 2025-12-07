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
#include <stdlib.mqh>
#include <time.mqh>
#include <Json/Json.mqh> // 添加JSON解析库

//+------------------------------------------------------------------+
//| EA输入参数                                                       |
//+------------------------------------------------------------------+
input string SymbolName = "GOLD";                // 交易品种
input ENUM_TIMEFRAMES Timeframe = PERIOD_H1;      // 交易周期
input double RiskPerTrade = 1.0;                  // 每笔交易风险百分比
input double MaxDailyLoss = 2.0;                  // 每日最大亏损百分比
input string PythonServerURL = "http://localhost:5001"; // Python服务URL
input int MagicNumber = 123456;                   // 魔术数字
input bool EnableLogging = true;                  // 启用日志记录

//+------------------------------------------------------------------+
//| 全局变量                                                         |
//+------------------------------------------------------------------+
bool EA_Running = false;                          // EA运行状态
double AccountBalance = 0.0;                      // 账户余额
double DailyLoss = 0.0;                           // 当日亏损
datetime LastTradeDay = 0;                        // 最后交易日期
int SignalStrength = 0;                           // 信号强度

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
    
    // 测试Python服务器连接
    TestPythonServerConnection();
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| 去初始化函数                                                     |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    // 平仓所有头寸
    CloseAllPositions();
    
    // 取消所有挂单
    DeleteAllPendingOrders();
    
    if(EnableLogging)
        Print("AI_MultiTF_SMC_EA 已停止，原因: ", reason);
    
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
//| 测试Python服务器连接                                             |
//+------------------------------------------------------------------+
void TestPythonServerConnection()
{
    string testURL = PythonServerURL + "/health";
    string response = "";
    
    // 发送HTTP GET请求
    int error = WebRequest(
        "GET",
        testURL,
        "",
        NULL,
        5000,
        NULL,
        0,
        response
    );
    
    if(error == 0)
    {
        if(EnableLogging)
            Print("Python服务器连接成功！响应: ", response);
    } 
    else
    {
        if(EnableLogging)
            Print("Python服务器连接失败！错误: ", error, ", 描述: ", WebRequestLastError());
        
        // 尝试使用127.0.0.1
        testURL = StringReplace(PythonServerURL, "localhost", "127.0.0.1") + "/health";
        error = WebRequest(
            "GET",
            testURL,
            "",
            NULL,
            5000,
            NULL,
            0,
            response
        );
        
        if(error == 0)
        {
            if(EnableLogging)
                Print("Python服务器连接成功(使用127.0.0.1)！响应: ", response);
        }
        else
        {
            if(EnableLogging)
                Print("Python服务器连接失败(使用127.0.0.1)！错误: ", error, ", 描述: ", WebRequestLastError());
        }
    }
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
string GetAISignal(const MqlRates &rates[])
{
    // 构建JSON请求
    JsonObject request_obj;
    request_obj.Add("symbol", SymbolName);
    request_obj.Add("timeframe", EnumToString(Timeframe));
    
    // 添加最近20根K线数据
    JsonArray rates_array;
    for(int i = 0; i < MathMin(20, ArraySize(rates)); i++)
    {
        JsonObject rate_obj;
        rate_obj.Add("time", (long)rates[i].time);
        rate_obj.Add("open", rates[i].open);
        rate_obj.Add("high", rates[i].high);
        rate_obj.Add("low", rates[i].low);
        rate_obj.Add("close", rates[i].close);
        rate_obj.Add("volume", rates[i].tick_volume);
        rates_array.Add(rate_obj);
    }
    request_obj.Add("rates", rates_array);
    
    string request_data = request_obj.ToString();
    string response = "";
    
    // 发送HTTP请求
    int error = WebRequest(
        "POST",
        PythonServerURL + "/get_signal",
        "Content-Type: application/json\r\n",
        NULL,
        5000,  // 5秒超时
        request_data,
        0,
        response
    );
    
    if(error != 0)
    {
        if(EnableLogging)
            PrintFormat("Python服务请求失败: 错误=%d, 描述=%s", error, WebRequestLastError());
        return "none";
    }
    
    if(EnableLogging)
        Print("Python服务响应: ", response);
    
    // 解析响应
    JsonObject response_obj;
    if(!response_obj.Parse(response))
    {
        if(EnableLogging)
            Print("无法解析Python服务响应");
        return "none";
    }
    
    // 获取信号和信号强度
    string signal = "none";
    if(response_obj.HasKey("signal"))
        signal = response_obj["signal"].ToString();
    
    if(response_obj.HasKey("signal_strength"))
        SignalStrength = response_obj["signal_strength"].ToInteger();
    
    return signal;
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
        ExecuteOrder(ORDER_TYPE_BUY);
    }
    // 处理卖出信号
    else if(signal == "sell" && !has_short)
    {
        // 平仓多头头寸
        if(has_long)
            CloseAllLongPositions();
        
        // 执行卖出
        ExecuteOrder(ORDER_TYPE_SELL);
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
bool ExecuteOrder(ENUM_ORDER_TYPE order_type)
{
    // 检查EA是否运行
    if(!EA_Running)
        return false;
    
    // 计算仓位大小
    double lot_size = CalculateLotSize();
    if(lot_size <= 0)
    {
        if(EnableLogging)
            Print("仓位计算失败，无法执行订单");
        return false;
    }
    
    // 准备订单请求
    MqlTradeRequest request = {};
    MqlTradeResult result = {};
    
    // 设置订单参数
    request.action = TRADE_ACTION_DEAL;
    request.symbol = SymbolName;
    request.volume = lot_size;
    request.type = order_type;
    request.deviation = 3;  // 3点滑点
    request.magic = MagicNumber;
    request.comment = "AI_MultiTF_SMC_EA";
    request.type_filling = ORDER_FILLING_IOC;  // 立即或取消
    request.type_time = ORDER_TIME_GTC;       // 直至取消
    
    // 获取当前价格
    request.price = order_type == ORDER_TYPE_BUY ? SymbolInfoDouble(SymbolName, SYMBOL_ASK) : SymbolInfoDouble(SymbolName, SYMBOL_BID);
    
    // 计算ATR用于SL/TP
    double atr = iATR(SymbolName, Timeframe, 14, 0);
    if(atr > 0)
    {
        request.sl = order_type == ORDER_TYPE_BUY ? request.price - atr * 2 : request.price + atr * 2;
        request.tp = order_type == ORDER_TYPE_BUY ? request.price + atr * 3 : request.price - atr * 3;
    }
    
    // 发送订单
    if(!OrderSend(request, result))
    {
        if(EnableLogging)
            PrintFormat("OrderSend失败: 错误=%d, 结果=%d, 评论=%s", GetLastError(), result.retcode, result.comment);
        return false;
    }
    
    if(EnableLogging)
        PrintFormat("订单执行成功: 订单号=%d, 类型=%s, 手数=%.2f, 价格=%.5f", 
                   result.order, EnumToString(order_type), lot_size, request.price);
    
    return true;
}

//+------------------------------------------------------------------+
//| 计算仓位大小                                                     |
//+------------------------------------------------------------------+
double CalculateLotSize()
{
    // 计算每手的价值
    double tick_value = SymbolInfoDouble(SymbolName, SYMBOL_TRADE_TICK_VALUE);
    double tick_size = SymbolInfoDouble(SymbolName, SYMBOL_TRADE_TICK_SIZE);
    
    // 计算风险金额
    double risk_amount = AccountBalance * (RiskPerTrade / 100.0);
    
    // 计算ATR
    double atr = iATR(SymbolName, Timeframe, 14, 0);
    if(atr <= 0)
        atr = 0.01; // 默认ATR值
    
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
    lot_size = MathMax(min_lot, MathMin(max_lot, lot_size));
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
        if(PositionSelectByTicket(PositionGetTicket(i)))
        {
            if(PositionGetString(POSITION_SYMBOL) == SymbolName && PositionGetInteger(POSITION_MAGIC) == MagicNumber)
            {
                if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
                {
                    double volume = PositionGetDouble(POSITION_VOLUME);
                    if(ClosePosition(PositionGetTicket(i), volume))
                    {
                        if(EnableLogging)
                            Print("平仓成功，订单号: ", PositionGetTicket(i), ", 类型: 多头");
                    }
                    else
                    {
                        if(EnableLogging)
                            Print("平仓失败，订单号: ", PositionGetTicket(i), ", 错误代码: ", GetLastError());
                    }
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
        if(PositionSelectByTicket(PositionGetTicket(i)))
        {
            if(PositionGetString(POSITION_SYMBOL) == SymbolName && PositionGetInteger(POSITION_MAGIC) == MagicNumber)
            {
                if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL)
                {
                    double volume = PositionGetDouble(POSITION_VOLUME);
                    if(ClosePosition(PositionGetTicket(i), volume))
                    {
                        if(EnableLogging)
                            Print("平仓成功，订单号: ", PositionGetTicket(i), ", 类型: 空头");
                    }
                    else
                    {
                        if(EnableLogging)
                            Print("平仓失败，订单号: ", PositionGetTicket(i), ", 错误代码: ", GetLastError());
                    }
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
//| 平仓单个仓位                                                     |
//+------------------------------------------------------------------+
bool ClosePosition(int ticket, double volume)
{
    // 准备订单请求
    MqlTradeRequest request = {};
    MqlTradeResult result = {};
    
    // 设置平仓参数
    request.action = TRADE_ACTION_DEAL;
    request.position = ticket;
    request.volume = volume;
    request.symbol = PositionGetString(POSITION_SYMBOL);
    request.type = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? ORDER_TYPE_SELL : ORDER_TYPE_BUY;
    request.price = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY ? SymbolInfoDouble(request.symbol, SYMBOL_BID) : SymbolInfoDouble(request.symbol, SYMBOL_ASK);
    request.deviation = 3;
    request.magic = MagicNumber;
    request.comment = "Close Position";
    request.type_filling = ORDER_FILLING_IOC;
    request.type_time = ORDER_TIME_GTC;
    
    // 发送平仓订单
    if(!OrderSend(request, result))
    {
        return false;
    }
    
    return result.retcode == TRADE_RETCODE_DONE;
}

//+------------------------------------------------------------------+
//| 取消所有挂单                                                     |
//+------------------------------------------------------------------+
void DeleteAllPendingOrders()
{
    for(int i = OrdersTotal() - 1; i >= 0; i--)
    {
        if(OrderSelect(i, SELECT_BY_POS, MODE_ORDERS))
        {
            if(OrderGetString(ORDER_SYMBOL) == SymbolName && OrderGetInteger(ORDER_MAGIC) == MagicNumber)
            {
                if(OrderDelete(OrderGetInteger(ORDER_TICKET)))
                {
                    if(EnableLogging)
                        Print("取消挂单成功，订单号: ", OrderGetInteger(ORDER_TICKET));
                }
                else
                {
                    if(EnableLogging)
                        Print("取消挂单失败，订单号: ", OrderGetInteger(ORDER_TICKET), ", 错误代码: ", GetLastError());
                }
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
