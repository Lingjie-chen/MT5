//+------------------------------------------------------------------+
//| AI_MultiTF_SMC_EA.mq5                                            |
//| Copyright 2024, AI Quant Trading                                 |
//| https://github.com/ai-quant-trading                              |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Quant Trading"
#property link      "https://github.com/ai-quant-trading"
#property version   "1.00"
#property strict
#property expert
#property indicator_separate_window
#property indicator_buffers 0
#property indicator_plots 0

//+------------------------------------------------------------------+
//| MT5 WebRequest URL白名单提示                                     |
//| 请在MetaEditor中添加以下URL到WebRequest白名单：                   |
//| http://localhost:5001                                            |
//| http://127.0.0.1:5001                                            |
//+------------------------------------------------------------------+

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
    // 参数验证
    if(RiskPerTrade <= 0 || RiskPerTrade > 10)
    {
        Print("警告: 每笔交易风险参数应在0-10%之间，当前值: ", RiskPerTrade, "%");
        return(INIT_FAILED);
    }
    
    if(MaxDailyLoss <= 0 || MaxDailyLoss > 5)
    {
        Print("警告: 每日最大亏损参数应在0-5%之间，当前值: ", MaxDailyLoss, "%");
        return(INIT_FAILED);
    }
    
    // 检查交易品种是否存在
    if(!SymbolInfoInteger(SymbolName, SYMBOL_SELECT))
    {
        Print("错误: 交易品种 ", SymbolName, " 不存在或无法访问");
        return(INIT_FAILED);
    }
    
    // 设置EA名称
    ExpertSetString(EXPERT_NAME, "AI_MultiTF_SMC_EA");
    
    // 初始化日志
    if(EnableLogging)
    {
        PrintFormat("AI_MultiTF_SMC_EA v%s 初始化成功", #property_version);
        PrintFormat("交易品种: %s", SymbolName);
        PrintFormat("交易周期: %s", EnumToString(Timeframe));
        PrintFormat("每笔交易风险: %.2f%%", RiskPerTrade);
        PrintFormat("每日最大亏损: %.2f%%", MaxDailyLoss);
        PrintFormat("Python服务URL: %s", PythonServerURL);
        PrintFormat("魔术数字: %d", MagicNumber);
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
    
    // 检查账户是否可用
    if(AccountInfoInteger(ACCOUNT_TRADE_ALLOWED) != 1)
    {
        if(EnableLogging)
            Print("交易功能不可用");
        return;
    }
    
    // 检查交易品种是否可用
    if(!SymbolInfoInteger(SymbolName, SYMBOL_TRADE))
    {
        if(EnableLogging)
            Print("交易品种 ", SymbolName, " 不可交易");
        return;
    }
    
    // 获取当前市场数据
    MqlRates rates[];
    int count = CopyRates(SymbolName, Timeframe, 0, 100, rates);
    if(count <= 0)
    {
        int error_code = GetLastError();
        if(EnableLogging)
            PrintFormat("无法获取市场数据，错误代码: %d，错误描述: %s", error_code, ErrorDescription(error_code));
        return;
    }
    
    // 检查数据完整性
    if(ArraySize(rates) < 20)
    {
        if(EnableLogging)
            Print("市场数据不足，需要至少20根K线");
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
    string response_headers = "";
    uchar request_data[];
    uchar response_data[];
    string response = "";
    
    // 发送HTTP GET请求
    int error = WebRequest(
        "GET",
        testURL,
        "",
        5000,
        request_data,
        response_data,
        response_headers
    );
    
    if(error == 0)
    {
        CharArrayToString(response_data, 0, WHOLE_ARRAY, response);
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
            5000,
            request_data,
            response_data,
            response_headers
        );
        
        if(error == 0)
        {
            CharArrayToString(response_data, 0, WHOLE_ARRAY, response);
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
    // 构建JSON请求字符串
    string request_data = "{\"symbol\":\"" + SymbolName + "\",\"timeframe\":\"" + EnumToString(Timeframe) + "\",\"rates\":[";
    
    // 添加最近20根K线数据
    for(int i = 0; i < MathMin(20, ArraySize(rates)); i++)
    {
        request_data += "{\"time\":" + IntegerToString(rates[i].time) + ",";
        request_data += "\"open\":" + DoubleToString(rates[i].open, 5) + ",";
        request_data += "\"high\":" + DoubleToString(rates[i].high, 5) + ",";
        request_data += "\"low\":" + DoubleToString(rates[i].low, 5) + ",";
        request_data += "\"close\":" + DoubleToString(rates[i].close, 5) + ",";
        request_data += "\"volume\":" + IntegerToString(rates[i].tick_volume) + "}";
        
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
    
    // 解析响应获取信号
    string signal = ParseJSON(response, "signal");
    SignalStrength = ParseJSONInt(response, "signal_strength");
    
    return signal;
}

//+------------------------------------------------------------------+
//| 发送HTTP请求                                                     |
//+------------------------------------------------------------------+
string SendHTTPRequest(string url, string data)
{
    string result = "";
    string headers = "Content-Type: application/json\r\n";
    uchar request_data[];
    uchar response_data[];
    string response_headers = "";
    
    // 检查URL格式
    if(StringFind(url, "http://") != 0 && StringFind(url, "https://") != 0)
    {
        if(EnableLogging)
            Print("WebRequest: URL格式无效，必须以http://或https://开头");
        return "";
    }
    
    // 将字符串转换为uchar数组
    if(StringToCharArray(data, request_data) <= 0)
    {
        if(EnableLogging)
            Print("WebRequest: 请求数据转换失败");
        return "";
    }
    
    // 发送WebRequest
    int error = WebRequest(
        "POST",
        url,
        headers,
        5000,
        request_data,
        response_data,
        response_headers
    );
    
    if(error != 0)
    {
        if(EnableLogging)
            PrintFormat("WebRequest失败: 错误代码=%d, 错误描述=%s", error, WebRequestLastError());
        
        // 错误处理：根据不同错误类型进行不同处理
        switch(error)
        {
            case 400:
                Print("WebRequest: 请求参数错误");
                break;
            case 401:
                Print("WebRequest: 未授权访问");
                break;
            case 403:
                Print("WebRequest: 禁止访问");
                break;
            case 404:
                Print("WebRequest: 请求的资源不存在");
                break;
            case 500:
                Print("WebRequest: 服务器内部错误");
                break;
            default:
                Print("WebRequest: 网络请求失败");
                break;
        }
        
        return "";
    }
    
    // 检查响应数据
    if(ArraySize(response_data) <= 0)
    {
        if(EnableLogging)
            Print("WebRequest: 未收到响应数据");
        return "";
    }
    
    // 将uchar数组转换为字符串
    if(CharArrayToString(response_data, 0, WHOLE_ARRAY, result) <= 0)
    {
        if(EnableLogging)
            Print("WebRequest: 响应数据转换失败");
        return "";
    }
    
    return result;
}

//+------------------------------------------------------------------+
//| 解析JSON字符串，获取字符串值                                     |
//+------------------------------------------------------------------+
string ParseJSON(string json, string key)
{
    string result = "none";
    
    // 构建搜索模式
    string pattern = "\"" + key + ":\"";
    int start_pos = StringFind(json, pattern, 0);
    
    if(start_pos != -1)
    {
        int value_start = start_pos + StringLen(pattern);
        int value_end = StringFind(json, "\"", value_start);
        
        if(value_end != -1)
        {
            result = StringSubstr(json, value_start, value_end - value_start);
        }
    }
    
    return result;
}

//+------------------------------------------------------------------+
//| 解析JSON字符串，获取整数值                                       |
//+------------------------------------------------------------------+
int ParseJSONInt(string json, string key)
{
    int result = 0;
    
    // 构建搜索模式
    string pattern = "\"" + key + ":";
    int start_pos = StringFind(json, pattern, 0);
    
    if(start_pos != -1)
    {
        int value_start = start_pos + StringLen(pattern);
        int value_end = StringFind(json, ",", value_start);
        if(value_end == -1)
            value_end = StringFind(json, "}", value_start);
        
        if(value_end != -1)
        {
            string value_str = StringSubstr(json, value_start, value_end - value_start);
            result = (int)StrToDouble(value_str);
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
    bool has_long = false;
    bool has_short = false;
    
    // 获取所有持仓
    ulong position_tickets[];
    int count = PositionsGetTicketList(position_tickets);
    
    for(int i = 0; i < count; i++)
    {
        if(PositionSelect(position_tickets[i]))
        {
            if(PositionGetString(POSITION_SYMBOL) == SymbolName && PositionGetInteger(POSITION_MAGIC) == MagicNumber)
            {
                if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
                    has_long = true;
                else if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL)
                    has_short = true;
            }
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
    {
        if(EnableLogging)
            Print("EA未运行，无法执行订单");
        return false;
    }
    
    // 检查订单类型是否有效
    if(order_type != ORDER_TYPE_BUY && order_type != ORDER_TYPE_SELL)
    {
        if(EnableLogging)
            Print("无效的订单类型: ", EnumToString(order_type));
        return false;
    }
    
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
    double bid_price = SymbolInfoDouble(SymbolName, SYMBOL_BID);
    double ask_price = SymbolInfoDouble(SymbolName, SYMBOL_ASK);
    
    if(bid_price == 0.0 || ask_price == 0.0)
    {
        if(EnableLogging)
            Print("无法获取有效的价格数据");
        return false;
    }
    
    request.price = order_type == ORDER_TYPE_BUY ? ask_price : bid_price;
    
    // 计算ATR用于SL/TP
    double atr = iATR(SymbolName, Timeframe, 14);
    if(atr > 0)
    {
        request.sl = order_type == ORDER_TYPE_BUY ? request.price - atr * 2 : request.price + atr * 2;
        request.tp = order_type == ORDER_TYPE_BUY ? request.price + atr * 3 : request.price - atr * 3;
        
        // 检查SL/TP是否有效
        if(order_type == ORDER_TYPE_BUY)
        {
            if(request.sl >= request.price || request.tp <= request.price)
            {
                if(EnableLogging)
                    Print("无效的SL/TP设置");
                // 使用默认SL/TP
                request.sl = 0.0;
                request.tp = 0.0;
            }
        }
        else
        {
            if(request.sl <= request.price || request.tp >= request.price)
            {
                if(EnableLogging)
                    Print("无效的SL/TP设置");
                // 使用默认SL/TP
                request.sl = 0.0;
                request.tp = 0.0;
            }
        }
    }
    
    // 发送订单
    if(!OrderSend(request, result))
    {
        int error_code = GetLastError();
        if(EnableLogging)
            PrintFormat("OrderSend失败: 错误代码=%d, 错误描述=%s, 结果=%d, 评论=%s", 
                      error_code, ErrorDescription(error_code), result.retcode, result.comment);
        return false;
    }
    
    // 检查订单执行结果
    if(result.retcode != TRADE_RETCODE_DONE && result.retcode != TRADE_RETCODE_PLACED)
    {
        if(EnableLogging)
            PrintFormat("订单执行失败: 结果代码=%d, 评论=%s", result.retcode, result.comment);
        return false;
    }
    
    if(EnableLogging)
        PrintFormat("订单执行成功: 订单号=%d, 类型=%s, 手数=%.2f, 价格=%.5f, SL=%.5f, TP=%.5f", 
                   result.order, EnumToString(order_type), lot_size, request.price, request.sl, request.tp);
    
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
    double atr = iATR(SymbolName, Timeframe, 14);
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
    // 获取所有持仓
    ulong position_tickets[];
    int count = PositionsGetTicketList(position_tickets);
    
    for(int i = count - 1; i >= 0; i--)
    {
        if(PositionSelect(position_tickets[i]))
        {
            if(PositionGetString(POSITION_SYMBOL) == SymbolName && PositionGetInteger(POSITION_MAGIC) == MagicNumber)
            {
                if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
                {
                    double volume = PositionGetDouble(POSITION_VOLUME);
                    if(ClosePosition((int)position_tickets[i], volume))
                    {
                        if(EnableLogging)
                            Print("平仓成功，订单号: ", (string)position_tickets[i], ", 类型: 多头");
                    }
                    else
                    {
                        if(EnableLogging)
                            Print("平仓失败，订单号: ", (string)position_tickets[i], ", 错误代码: ", GetLastError());
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
    // 获取所有持仓
    ulong position_tickets[];
    int count = PositionsGetTicketList(position_tickets);
    
    for(int i = count - 1; i >= 0; i--)
    {
        if(PositionSelect(position_tickets[i]))
        {
            if(PositionGetString(POSITION_SYMBOL) == SymbolName && PositionGetInteger(POSITION_MAGIC) == MagicNumber)
            {
                if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL)
                {
                    double volume = PositionGetDouble(POSITION_VOLUME);
                    if(ClosePosition((int)position_tickets[i], volume))
                    {
                        if(EnableLogging)
                            Print("平仓成功，订单号: ", (string)position_tickets[i], ", 类型: 空头");
                    }
                    else
                    {
                        if(EnableLogging)
                            Print("平仓失败，订单号: ", (string)position_tickets[i], ", 错误代码: ", GetLastError());
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
    // 检查仓位是否存在
    if(!PositionSelect(ticket))
    {
        if(EnableLogging)
            PrintFormat("无法找到仓位 #%d", ticket);
        return false;
    }
    
    // 验证仓位参数
    if(volume <= 0)
    {
        if(EnableLogging)
            Print("无效的平仓手数");
        return false;
    }
    
    // 获取仓位信息
    string position_symbol = PositionGetString(POSITION_SYMBOL);
    ENUM_POSITION_TYPE position_type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
    double position_volume = PositionGetDouble(POSITION_VOLUME);
    
    // 检查请求的手数是否超过可用手数
    if(volume > position_volume)
    {
        if(EnableLogging)
            PrintFormat("请求的平仓手数(%.2f)超过可用手数(%.2f)", volume, position_volume);
        volume = position_volume;  // 调整为可用手数
    }
    
    // 准备订单请求
    MqlTradeRequest request = {};
    MqlTradeResult result = {};
    
    // 设置平仓参数
    request.action = TRADE_ACTION_DEAL;
    request.position = ticket;
    request.volume = volume;
    request.symbol = position_symbol;
    request.type = position_type == POSITION_TYPE_BUY ? ORDER_TYPE_SELL : ORDER_TYPE_BUY;
    request.deviation = 3;
    request.magic = MagicNumber;
    request.comment = "AI_MultiTF_SMC_EA - Close Position";
    request.type_filling = ORDER_FILLING_IOC;
    request.type_time = ORDER_TIME_GTC;
    
    // 获取当前价格
    double bid_price = SymbolInfoDouble(position_symbol, SYMBOL_BID);
    double ask_price = SymbolInfoDouble(position_symbol, SYMBOL_ASK);
    
    if(bid_price == 0.0 || ask_price == 0.0)
    {
        if(EnableLogging)
            Print("无法获取有效的平仓价格");
        return false;
    }
    
    request.price = position_type == POSITION_TYPE_BUY ? bid_price : ask_price;
    
    // 发送平仓订单
    if(!OrderSend(request, result))
    {
        int error_code = GetLastError();
        if(EnableLogging)
            PrintFormat("平仓订单发送失败: 错误代码=%d, 错误描述=%s", error_code, ErrorDescription(error_code));
        return false;
    }
    
    // 检查平仓结果
    if(result.retcode != TRADE_RETCODE_DONE && result.retcode != TRADE_RETCODE_PLACED)
    {
        if(EnableLogging)
            PrintFormat("平仓执行失败: 结果代码=%d, 评论=%s", result.retcode, result.comment);
        return false;
    }
    
    if(EnableLogging)
        PrintFormat("平仓成功: 订单号=%d, 类型=%s, 手数=%.2f", 
                   result.order, EnumToString(position_type), volume);
    
    return true;
}

//+------------------------------------------------------------------+
//| 取消所有挂单                                                     |
//+------------------------------------------------------------------+
void DeleteAllPendingOrders()
{
    // 获取所有订单
    ulong order_tickets[];
    int count = OrdersGetTicketList(order_tickets);
    
    if(count <= 0)
    {
        if(EnableLogging)
            Print("没有找到挂单");
        return;
    }
    
    for(int i = count - 1; i >= 0; i--)
    {
        if(OrderSelect(order_tickets[i], SELECT_BY_TICKET))
        {
            // 检查订单是否属于当前EA
            if(OrderGetString(ORDER_SYMBOL) == SymbolName && OrderGetInteger(ORDER_MAGIC) == MagicNumber)
            {
                // 检查订单类型是否为挂单
                ENUM_ORDER_TYPE order_type = (ENUM_ORDER_TYPE)OrderGetInteger(ORDER_TYPE);
                if(order_type == ORDER_TYPE_BUY_LIMIT || order_type == ORDER_TYPE_SELL_LIMIT ||
                   order_type == ORDER_TYPE_BUY_STOP || order_type == ORDER_TYPE_SELL_STOP ||
                   order_type == ORDER_TYPE_BUY_STOP_LIMIT || order_type == ORDER_TYPE_SELL_STOP_LIMIT)
                {
                    if(OrderDelete(order_tickets[i]))
                    {
                        if(EnableLogging)
                            PrintFormat("取消挂单成功，订单号: %d, 类型: %s", order_tickets[i], EnumToString(order_type));
                    }
                    else
                    {
                        int error_code = GetLastError();
                        if(EnableLogging)
                            PrintFormat("取消挂单失败，订单号: %d, 错误代码: %d, 错误描述: %s", 
                                      order_tickets[i], error_code, ErrorDescription(error_code));
                    }
                }
            }
        }
        else
        {
            int error_code = GetLastError();
            if(EnableLogging)
                PrintFormat("无法选择订单 #%d, 错误代码: %d, 错误描述: %s", 
                          order_tickets[i], error_code, ErrorDescription(error_code));
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
