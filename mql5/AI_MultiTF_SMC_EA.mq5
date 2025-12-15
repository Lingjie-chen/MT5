//+------------------------------------------------------------------+
//| AI_MultiTF_SMC_EA.mq5                                            |
//| Copyright 2024, AI Quant Trading                                 |
//| https://github.com/ai-quant-trading                              |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Quant Trading"
#property link      "https://github.com/ai-quant-trading"
#property version   "1.00"

//+------------------------------------------------------------------+
//| MT5 WebRequest URL白名单提示                                     |
//| 请在MetaEditor中添加以下URL到WebRequest白名单：                   |
//| http://localhost:5001                                            |
//| http://127.0.0.1:5001                                            |
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| EA输入参数                                                       |
//+------------------------------------------------------------------+
input string InputSymbol = "";                    // 交易品种（留空则使用当前图表品种）
input ENUM_TIMEFRAMES InputTimeframe = PERIOD_H1; // 交易周期

// 资金管理参数
input double RiskPerTrade = 1.0;                  // 每笔交易风险百分比 (0-10)
input double MaxDailyLoss = 2.0;                  // 每日最大亏损百分比 (0-5)
input double MaxTotalRisk = 3.0;                  // 总风险百分比 (0-15)
input int MaxPositions = 1;                       // 最大持仓数量
input int MaxConsecutiveLosses = 3;               // 最大连续亏损次数

// EA设置参数
input string PythonServerURL = "http://localhost:5001"; // Python服务URL
input int MagicNumber = 123456;                   // 魔术数字
input bool EnableLogging = true;                  // 启用日志记录

// 信号过滤参数
input int MinSignalStrength = 70;                 // 最小信号强度
input int SignalConfirmations = 1;                // 信号确认次数

// 性能优化参数
input int SignalCacheTime = 300;                  // 信号缓存时间(秒)
input int NetworkTimeout = 5000;                  // 网络超时时间(毫秒)

//+------------------------------------------------------------------+
//| 全局变量                                                         |
//+------------------------------------------------------------------+
string TradingSymbol;                             // 实际使用的交易品种
ENUM_TIMEFRAMES TradingTimeframe;                 // 实际使用的交易周期
bool EA_Running = false;                          // EA运行状态
double AccountBalance = 0.0;                      // 账户余额
double DailyLoss = 0.0;                           // 当日亏损
MqlDateTime LastTradeDay;                         // 最后交易日期
int SignalStrength = 0;                           // 信号强度

// 性能跟踪变量
int ConsecutiveLosses = 0;                        // 连续亏损次数
int TotalTrades = 0;                              // 总交易次数
int WinningTrades = 0;                            // 盈利交易次数
int LosingTrades = 0;                             // 亏损交易次数

double TotalProfit = 0.0;                         // 总盈利
double MaxDrawdown = 0.0;                         // 最大回撤

double InitialBalance = 0.0;                      // 初始账户余额

// 信号处理变量
string LastSignal = "none";                       // 上一次信号
int SignalConfirmCount = 0;                       // 信号确认计数
int LastSignalTime = 0;                           // 上一次信号时间

// 持仓跟踪变量
int CurrentPositions = 0;                         // 当前持仓数量
double TotalRiskExposure = 0.0;                   // 总风险暴露

double CurrentEquity = 0.0;                       // 当前权益

// 缓存设置
int CACHE_EXPIRY = 300;                           // 信号缓存时间(秒)

//+------------------------------------------------------------------+
//| 错误代码转字符串                                                  |
//+------------------------------------------------------------------+
string GetErrorDescription(int error_code)
{
    switch(error_code)
    {
        case 0:     return "No error";
        case 1:     return "No error returned, but result is unknown";
        case 2:     return "Common error";
        case 3:     return "Invalid trade parameters";
        case 4:     return "Trade server is busy";
        case 5:     return "Old version of the client terminal";
        case 6:     return "No connection with trade server";
        case 7:     return "Not enough rights";
        case 8:     return "Too frequent requests";
        case 9:     return "Malfunctional trade operation";
        case 64:    return "Account disabled";
        case 65:    return "Invalid account";
        case 128:   return "Trade timeout";
        case 129:   return "Invalid price";
        case 130:   return "Invalid stops";
        case 131:   return "Invalid trade volume";
        case 132:   return "Market is closed";
        case 133:   return "Trade is disabled";
        case 134:   return "Not enough money";
        case 135:   return "Price changed";
        case 136:   return "Off quotes";
        case 137:   return "Broker is busy";
        case 138:   return "Requote";
        case 139:   return "Order is locked";
        case 140:   return "Long positions only allowed";
        case 141:   return "Too many requests";
        case 145:   return "Modification denied because order is too close to market";
        case 146:   return "Trade context is busy";
        case 147:   return "Expirations are denied by broker";
        case 148:   return "Too many open and pending orders";
        case 149:   return "Hedging is prohibited";
        case 150:   return "Prohibit closing by opposite";
        case 4000:  return "No error";
        case 4001:  return "Wrong function pointer";
        case 4002:  return "Array index is out of range";
        case 4003:  return "No memory for function call stack";
        case 4004:  return "Recursive stack overflow";
        case 4005:  return "Not enough stack for parameter";
        case 4006:  return "No memory for parameter string";
        case 4007:  return "No memory for temp string";
        case 4008:  return "Not initialized string";
        case 4009:  return "Not initialized string in array";
        case 4010:  return "No memory for array string";
        case 4011:  return "Too long string";
        case 4012:  return "Remainder from zero divide";
        case 4013:  return "Zero divide";
        case 4014:  return "Unknown command";
        case 4015:  return "Wrong jump (never generated error)";
        case 4016:  return "Not initialized array";
        case 4017:  return "DLL calls are not allowed";
        case 4018:  return "Cannot load library";
        case 4019:  return "Cannot call function";
        case 4020:  return "Expert function calls are not allowed";
        case 4021:  return "Not enough memory for temp string returned from function";
        case 4022:  return "System is busy (never generated error)";
        case 4050:  return "Invalid function parameters count";
        case 4051:  return "Invalid function parameter value";
        case 4052:  return "String function internal error";
        case 4053:  return "Some array error";
        case 4054:  return "Incorrect series array using";
        case 4055:  return "Custom indicator error";
        case 4056:  return "Arrays are incompatible";
        case 4057:  return "Global variables processing error";
        case 4058:  return "Global variable not found";
        case 4059:  return "Function is not allowed in testing mode";
        case 4060:  return "Function is not confirmed";
        case 4061:  return "Send mail error";
        case 4062:  return "String parameter expected";
        case 4063:  return "Integer parameter expected";
        case 4064:  return "Double parameter expected";
        case 4065:  return "Array as parameter expected";
        case 4066:  return "Requested history data is in update state";
        case 4067:  return "Some error in trade operation";
        case 4099:  return "End of file";
        case 4100:  return "Some file error";
        case 4101:  return "Wrong file name";
        case 4102:  return "Too many opened files";
        case 4103:  return "Cannot open file";
        case 4104:  return "Incompatible access to a file";
        case 4105:  return "No order selected";
        case 4106:  return "Unknown symbol";
        case 4107:  return "Invalid price parameter";
        case 4108:  return "Invalid ticket";
        case 4109:  return "Trade is not allowed";
        case 4110:  return "Longs are not allowed";
        case 4111:  return "Shorts are not allowed";
        case 4200:  return "Object already exists";
        case 4201:  return "Unknown object property";
        case 4202:  return "Object does not exist";
        case 4203:  return "Unknown object type";
        case 4204:  return "No object name";
        case 4205:  return "Object coordinates error";
        case 4206:  return "No specified subwindow";
        case 4207:  return "Some error in object function";
        case 4250:  return "Unknown chart property";
        case 4251:  return "Chart not found";
        case 4252:  return "Chart subwindow not found";
        case 4253:  return "Chart indicator not found";
        case 4254:  return "Symbol select error";
        case 5001:  return "Invalid URL";
        case 5002:  return "Failed to connect";
        case 5003:  return "Timeout";
        case 5004:  return "HTTP request failed";
        case 5005:  return "Failed to read HTTP response";
        default:    return "Unknown error (" + IntegerToString(error_code) + ")";
    }
}

//+------------------------------------------------------------------+
//| WebRequest错误转字符串                                           |
//+------------------------------------------------------------------+
string GetWebRequestErrorDescription(int error_code)
{
    switch(error_code)
    {
        case 4001:  return "Invalid URL";
        case 4002:  return "Failed to connect";
        case 4003:  return "Timeout";
        case 4004:  return "HTTP request failed";
        case 4005:  return "Failed to read HTTP response";
        case 4010:  return "Not allowed (URL not in the list of allowed URLs)";
        case 4011:  return "Not allowed (URL is in the list of blocked URLs)";
        default:    return "Unknown WebRequest error (" + IntegerToString(error_code) + ")";
    }
}

//+------------------------------------------------------------------+
//| 初始化函数                                                       |
//+------------------------------------------------------------------+
int OnInit()
{
    // 设置实际使用的交易品种和周期
    TradingSymbol = (InputSymbol == "") ? Symbol() : InputSymbol;
    TradingTimeframe = InputTimeframe;
    
    // 参数验证
    if(RiskPerTrade <= 0 || RiskPerTrade > 10)
    {
        PrintFormat("警告: 每笔交易风险参数应在0-10%%之间，当前值: %.2f%%", RiskPerTrade);
        return(INIT_FAILED);
    }
    
    if(MaxDailyLoss <= 0 || MaxDailyLoss > 5)
    {
        PrintFormat("警告: 每日最大亏损参数应在0-5%%之间，当前值: %.2f%%", MaxDailyLoss);
        return(INIT_FAILED);
    }
    
    if(MaxTotalRisk <= 0 || MaxTotalRisk > 15)
    {
        PrintFormat("警告: 总风险参数应在0-15%%之间，当前值: %.2f%%", MaxTotalRisk);
        return(INIT_FAILED);
    }
    
    if(MaxPositions <= 0)
    {
        Print("错误: 最大持仓数量必须大于0");
        return(INIT_FAILED);
    }
    
    // 检查交易品种是否存在
    if(!SymbolSelect(TradingSymbol, true))
    {
        PrintFormat("错误: 交易品种 %s 不存在或无法访问", TradingSymbol);
        return(INIT_FAILED);
    }
    
    // 初始化全局变量
    InitialBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    AccountBalance = InitialBalance;
    CurrentEquity = InitialBalance;
    CACHE_EXPIRY = SignalCacheTime;
    
    // 设置最后交易日期
    MqlDateTime current_time;
    TimeToStruct(TimeCurrent(), current_time);
    LastTradeDay = current_time;
    
    // 初始化日志
    if(EnableLogging)
    {
        PrintFormat("AI_MultiTF_SMC_EA v%s 初始化成功");
        PrintFormat("交易品种: %s", TradingSymbol);
        PrintFormat("交易周期: %s", EnumToString(TradingTimeframe));
        PrintFormat("每笔交易风险: %.2f%%", RiskPerTrade);
        PrintFormat("每日最大亏损: %.2f%%", MaxDailyLoss);
        PrintFormat("总风险百分比: %.2f%%", MaxTotalRisk);
        PrintFormat("最大持仓数量: %d", MaxPositions);
        PrintFormat("最小信号强度: %d", MinSignalStrength);
        PrintFormat("信号确认次数: %d", SignalConfirmations);
        PrintFormat("Python服务URL: %s", PythonServerURL);
        PrintFormat("魔术数字: %d", MagicNumber);
        PrintFormat("信号缓存时间: %d秒", SignalCacheTime);
        PrintFormat("网络超时时间: %d毫秒", NetworkTimeout);
    }
    
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
    
    // 更新当前权益
    CurrentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    
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
    long trade_mode = SymbolInfoInteger(TradingSymbol, SYMBOL_TRADE_MODE);
    if(trade_mode == SYMBOL_TRADE_MODE_DISABLED)
    {
        if(EnableLogging)
            PrintFormat("交易品种 %s 不可交易", TradingSymbol);
        return;
    }
    
    // 检查连续亏损次数
    if(ConsecutiveLosses >= MaxConsecutiveLosses)
    {
        if(EnableLogging)
            PrintFormat("已达到最大连续亏损次数(%d)，停止交易", MaxConsecutiveLosses);
        CloseAllPositions();
        EA_Running = false;
        return;
    }
    
    // 检查当前持仓数量
    CurrentPositions = PositionsTotal();
    if(CurrentPositions >= MaxPositions)
    {
        if(EnableLogging)
            PrintFormat("已达到最大持仓数量(%d)，暂不执行新订单", MaxPositions);
        return;
    }
    
    // 检查总风险暴露
    double current_drawdown = (InitialBalance - CurrentEquity) / InitialBalance * 100;
    if(current_drawdown >= MaxTotalRisk)
    {
        if(EnableLogging)
            PrintFormat("总风险暴露(%.2f%%)已达到上限(%.2f%%)，停止交易", current_drawdown, MaxTotalRisk);
        CloseAllPositions();
        EA_Running = false;
        return;
    }
    
    // 获取当前市场数据
    MqlRates rates[];
    int count = CopyRates(TradingSymbol, TradingTimeframe, 0, 100, rates);
    if(count <= 0)
    {
        int error_code = GetLastError();
        if(EnableLogging)
            PrintFormat("无法获取市场数据，错误代码: %d，错误描述: %s", error_code, GetErrorDescription(error_code));
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
    
    // 更新最大回撤
    UpdateMaxDrawdown();
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
    int error = 0;
    
    // 发送HTTP GET请求
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
        response = CharArrayToString(response_data);
        if(EnableLogging)
            Print("Python服务器连接成功！响应: ", response);
    } 
    else
    {
        if(EnableLogging)
            Print("Python服务器连接失败！错误: ", error, ", 描述: ", GetWebRequestErrorDescription(error));
        
        // 尝试使用127.0.0.1 - 修正StringReplace的用法
        string newURL = PythonServerURL;
        StringReplace(newURL, "localhost", "127.0.0.1");
        testURL = newURL + "/health";
        
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
            response = CharArrayToString(response_data);
            if(EnableLogging)
                Print("Python服务器连接成功(使用127.0.0.1)！响应: ", response);
        }
        else
        {
            if(EnableLogging)
                Print("Python服务器连接失败(使用127.0.0.1)！错误: ", error, ", 描述: ", GetWebRequestErrorDescription(error));
        }
    }
}

//+------------------------------------------------------------------+
//| 检查每日亏损                                                     |
//+------------------------------------------------------------------+
void CheckDailyLoss()
{
    MqlDateTime current_time;
    TimeToStruct(TimeCurrent(), current_time);
    
    // 新的一天，重置每日亏损和连续亏损次数
    if(current_time.day != LastTradeDay.day)
    {
        DailyLoss = 0.0;
        ConsecutiveLosses = 0;
        LastTradeDay = current_time;
        if(EnableLogging)
            Print("新的交易日，重置每日亏损和连续亏损计数");
        return;
    }
    
    // 计算当前账户余额和权益
    double current_balance = AccountInfoDouble(ACCOUNT_BALANCE);
    CurrentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    // 计算当前亏损
    double daily_drawdown = (InitialBalance - CurrentEquity) / InitialBalance * 100;
    
    // 检查是否超过每日最大亏损
    if(daily_drawdown >= MaxDailyLoss)
    {
        if(EnableLogging)
            PrintFormat("达到每日最大亏损限制(%.2f%%)，EA将停止交易", daily_drawdown);
        
        // 平仓所有头寸
        CloseAllPositions();
        
        // 停止EA
        EA_Running = false;
    }
    
    // 更新账户余额
    if(current_balance > AccountBalance)
    {
        AccountBalance = current_balance;
        ConsecutiveLosses = 0; // 重置连续亏损计数
    }
}

//+------------------------------------------------------------------+
//| 更新最大回撤                                                     |
//+------------------------------------------------------------------+
void UpdateMaxDrawdown()
{
    // 计算当前权益
    CurrentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    // 计算当前回撤
    double current_drawdown = (InitialBalance - CurrentEquity) / InitialBalance * 100;
    
    // 更新最大回撤
    if(current_drawdown > MaxDrawdown)
    {
        MaxDrawdown = current_drawdown;
        if(EnableLogging)
            PrintFormat("更新最大回撤: %.2f%%", MaxDrawdown);
    }
    
    // 更新总盈利
    double current_profit = CurrentEquity - InitialBalance;
    if(current_profit != TotalProfit)
    {
        TotalProfit = current_profit;
        if(EnableLogging)
            PrintFormat("更新总盈利: %.2f", TotalProfit);
    }
}

//+------------------------------------------------------------------+
//| 调用Python服务获取交易信号                                       |
//+------------------------------------------------------------------+
string GetAISignal(const MqlRates &rates[])
{
    // 初始化JSON构建
    string request_data = "{\"symbol\":\"" + TradingSymbol + "\",\"timeframe\":\"" + EnumToString(TradingTimeframe) + "\",\"rates\":[";
    
    // 添加最近20根K线数据
    int max_bars = MathMin(20, ArraySize(rates));
    
    for(int i = 0; i < max_bars; i++)
    {
        // 只添加有效时间的K线
        if(rates[i].time > 0)
        {
            request_data += "{\"time\":" + IntegerToString(rates[i].time) + ",";
            request_data += "\"open\":" + DoubleToString(rates[i].open, 5) + ",";
            request_data += "\"high\":" + DoubleToString(rates[i].high, 5) + ",";
            request_data += "\"low\":" + DoubleToString(rates[i].low, 5) + ",";
            request_data += "\"close\":" + DoubleToString(rates[i].close, 5) + ",";
            request_data += "\"tick_volume\":" + IntegerToString(rates[i].tick_volume) + "}";
            
            if(i < max_bars - 1 && (i + 1) < ArraySize(rates) && rates[i + 1].time > 0)
                request_data += ",";
        }
    }
    
    request_data += "]}";
    
    // 验证JSON格式
    if(EnableLogging)
    {
        Print("构建的JSON长度: ", StringLen(request_data));
        Print("JSON开头: ", StringSubstr(request_data, 0, 300));
        Print("JSON结尾: ", StringSubstr(request_data, StringLen(request_data)-100, 100));
    }
    
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
            PrintFormat("WebRequest失败: 错误代码=%d, 错误描述=%s", error, GetWebRequestErrorDescription(error));
        
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
    result = CharArrayToString(response_data);
    if(result == "")
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
    string pattern = "\"" + key + "\":\"";
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
    string pattern = "\"" + key + "\":";
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
            result = (int)StringToInteger(value_str);
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
    
    // 检查信号强度
    if(SignalStrength < MinSignalStrength)
    {
        if(EnableLogging)
            PrintFormat("信号强度(%d)低于最小值(%d)，忽略信号", SignalStrength, MinSignalStrength);
        return;
    }
    
    // 信号确认逻辑
    if(signal == LastSignal)
    {
        SignalConfirmCount++;
        if(EnableLogging)
            PrintFormat("信号确认计数: %d/%d", SignalConfirmCount, SignalConfirmations);
    }
    else
    {
        SignalConfirmCount = 1;
        LastSignal = signal;
        LastSignalTime = (int)TimeCurrent();
    }
    
    // 等待信号确认
    if(SignalConfirmCount < SignalConfirmations)
    {
        return;
    }
    
    // 重置信号确认计数
    SignalConfirmCount = 0;
    
    // 检查当前持仓
    bool has_long = false;
    bool has_short = false;
    
    // 获取所有持仓
    int positions_total = PositionsTotal();
    
    for(int i = positions_total - 1; i >= 0; i--)
    {
        if(PositionGetSymbol(i) == TradingSymbol)
        {
            ulong ticket = PositionGetTicket(i);
            if(PositionGetInteger(POSITION_MAGIC) == MagicNumber)
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
        if(ExecuteOrder(ORDER_TYPE_BUY))
        {
            TotalTrades++;
            if(EnableLogging)
                PrintFormat("执行买入信号，总交易次数: %d", TotalTrades);
        }
    }
    // 处理卖出信号
    else if(signal == "sell" && !has_short)
    {
        // 平仓多头头寸
        if(has_long)
            CloseAllLongPositions();
        
        // 执行卖出
        if(ExecuteOrder(ORDER_TYPE_SELL))
        {
            TotalTrades++;
            if(EnableLogging)
                PrintFormat("执行卖出信号，总交易次数: %d", TotalTrades);
        }
    }
    // 处理平仓信号
    else if(signal == "close_all")
    {
        CloseAllPositions();
        if(EnableLogging)
            Print("执行全平信号");
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
    request.symbol = TradingSymbol;
    request.volume = lot_size;
    request.type = order_type;
    request.deviation = 3;  // 3点滑点
    request.magic = MagicNumber;
    request.comment = "AI_MultiTF_SMC_EA";
    request.type_filling = ORDER_FILLING_IOC;  // 立即或取消
    request.type_time = ORDER_TIME_GTC;       // 直至取消
    
    // 获取当前价格
    double bid_price = SymbolInfoDouble(TradingSymbol, SYMBOL_BID);
    double ask_price = SymbolInfoDouble(TradingSymbol, SYMBOL_ASK);
    
    if(bid_price == 0.0 || ask_price == 0.0)
    {
        if(EnableLogging)
            Print("无法获取有效的价格数据");
        return false;
    }
    
    request.price = order_type == ORDER_TYPE_BUY ? ask_price : bid_price;
    
    // 计算ATR用于SL/TP
    int atr_handle = iATR(TradingSymbol, TradingTimeframe, 14);
    double atr[1];
    if(CopyBuffer(atr_handle, 0, 0, 1, atr) > 0 && atr[0] > 0)
    {
        if(order_type == ORDER_TYPE_BUY)
        {
            request.sl = request.price - atr[0] * 2;
            request.tp = request.price + atr[0] * 3;
        }
        else
        {
            request.sl = request.price + atr[0] * 2;
            request.tp = request.price - atr[0] * 3;
        }
        
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
    else
    {
        request.sl = 0.0;
        request.tp = 0.0;
    }
    
    // 发送订单
    if(!OrderSend(request, result))
    {
        int error_code = GetLastError();
        if(EnableLogging)
            PrintFormat("OrderSend失败: 错误代码=%d, 错误描述=%s, 结果=%d, 评论=%s", 
                      error_code, GetErrorDescription(error_code), result.retcode, result.comment);
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
    // 获取交易品种信息
    double tick_value = SymbolInfoDouble(TradingSymbol, SYMBOL_TRADE_TICK_VALUE);
    double tick_size = SymbolInfoDouble(TradingSymbol, SYMBOL_TRADE_TICK_SIZE);
    
    if(tick_size == 0.0)
    {
        if(EnableLogging)
            Print("无法获取有效的tick size");
        return 0.0;
    }
    
    // 计算风险金额
    double risk_amount = AccountBalance * (RiskPerTrade / 100.0);
    
    // 计算ATR
    int atr_handle = iATR(TradingSymbol, TradingTimeframe, 14);
    double atr[1];
    if(CopyBuffer(atr_handle, 0, 0, 1, atr) > 0 && atr[0] > 0)
    {
        // 计算止损点数
        double stop_loss_points = atr[0] / tick_size;
        
        // 计算每手风险
        double risk_per_lot = stop_loss_points * tick_value;
        
        if(risk_per_lot <= 0.0)
        {
            if(EnableLogging)
                Print("风险计算错误: risk_per_lot <= 0");
            return 0.0;
        }
        
        // 计算仓位大小
        double lot_size = risk_amount / risk_per_lot;
        
        // 获取最小和最大仓位
        double min_lot = SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_MIN);
        double max_lot = SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_MAX);
        double lot_step = SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_STEP);
        
        // 调整仓位大小
        lot_size = MathMax(min_lot, MathMin(max_lot, lot_size));
        lot_size = lot_step * MathRound(lot_size / lot_step);
        
        return lot_size;
    }
    
    if(EnableLogging)
        Print("无法计算ATR，使用默认仓位");
    return SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_MIN);
}

//+------------------------------------------------------------------+
//| 平仓所有多头头寸                                                 |
//+------------------------------------------------------------------+
void CloseAllLongPositions()
{
    // 获取所有持仓
    int positions_total = PositionsTotal();
    
    for(int i = positions_total - 1; i >= 0; i--)
    {
        if(PositionGetSymbol(i) == TradingSymbol)
        {
            ulong ticket = PositionGetTicket(i);
            if(PositionGetInteger(POSITION_MAGIC) == MagicNumber && PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
            {
                double volume = PositionGetDouble(POSITION_VOLUME);
                if(ClosePosition(ticket, volume))
                {
                    if(EnableLogging)
                        Print("平仓成功，订单号: ", ticket, ", 类型: 多头");
                }
                else
                {
                    int error_code = GetLastError();
                    if(EnableLogging)
                        Print("平仓失败，订单号: ", ticket, ", 错误代码: ", error_code, " - ", GetErrorDescription(error_code));
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
    int positions_total = PositionsTotal();
    
    for(int i = positions_total - 1; i >= 0; i--)
    {
        if(PositionGetSymbol(i) == TradingSymbol)
        {
            ulong ticket = PositionGetTicket(i);
            if(PositionGetInteger(POSITION_MAGIC) == MagicNumber && PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL)
            {
                double volume = PositionGetDouble(POSITION_VOLUME);
                if(ClosePosition(ticket, volume))
                {
                    if(EnableLogging)
                        Print("平仓成功，订单号: ", ticket, ", 类型: 空头");
                }
                else
                {
                    int error_code = GetLastError();
                    if(EnableLogging)
                        Print("平仓失败，订单号: ", ticket, ", 错误代码: ", error_code, " - ", GetErrorDescription(error_code));
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
bool ClosePosition(ulong ticket, double volume)
{
    // 检查仓位是否存在
    if(!PositionSelectByTicket(ticket))
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
            PrintFormat("平仓订单发送失败: 错误代码=%d, 错误描述=%s", error_code, GetErrorDescription(error_code));
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
    int orders_total = OrdersTotal();
    
    if(orders_total <= 0)
    {
        if(EnableLogging)
            Print("没有找到挂单");
        return;
    }
    
    for(int i = orders_total - 1; i >= 0; i--)
    {
        ulong order_ticket = OrderGetTicket(i);
        string order_symbol = OrderGetString(ORDER_SYMBOL);
        long order_magic = OrderGetInteger(ORDER_MAGIC);
        ENUM_ORDER_TYPE order_type = (ENUM_ORDER_TYPE)OrderGetInteger(ORDER_TYPE);
        
        // 检查订单是否属于当前EA
        if(order_symbol == TradingSymbol && order_magic == MagicNumber)
        {
            // 检查订单类型是否为挂单
            if(order_type == ORDER_TYPE_BUY_LIMIT || order_type == ORDER_TYPE_SELL_LIMIT ||
               order_type == ORDER_TYPE_BUY_STOP || order_type == ORDER_TYPE_SELL_STOP ||
               order_type == ORDER_TYPE_BUY_STOP_LIMIT || order_type == ORDER_TYPE_SELL_STOP_LIMIT)
            {
                MqlTradeRequest request = {};
                MqlTradeResult result = {};
                
                request.action = TRADE_ACTION_REMOVE;
                request.order = order_ticket;
                request.magic = MagicNumber;
                
                if(OrderSend(request, result))
                {
                    if(EnableLogging)
                        PrintFormat("取消挂单成功，订单号: %d, 类型: %s", order_ticket, EnumToString(order_type));
                }
                else
                {
                    int error_code = GetLastError();
                    if(EnableLogging)
                        PrintFormat("取消挂单失败，订单号: %d, 错误代码: %d, 错误描述: %s", 
                                  order_ticket, error_code, GetErrorDescription(error_code));
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
void OnTradeTransaction(const MqlTradeTransaction& trans,
                        const MqlTradeRequest& request,
                        const MqlTradeResult& result)
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