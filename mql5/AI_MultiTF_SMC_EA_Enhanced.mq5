//+------------------------------------------------------------------+
//| AI_MultiTF_SMC_EA_Enhanced.mq5                                   |
//| Copyright 2024, AI Quant Trading                                 |
//| https://github.com/ai-quant-trading                              |
//| 增强版：集成高级技术分析和风险管理功能                            |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Quant Trading"
#property link      "https://github.com/ai-quant-trading"
#property version   "2.00"

//+------------------------------------------------------------------+
//| EA输入参数                                                       |
//+------------------------------------------------------------------+
input string InputSymbol = "GOLD";                // 交易品种（建议直接指定，避免使用空值）
input ENUM_TIMEFRAMES InputTimeframe = PERIOD_H1; // 交易周期

// 资金管理参数
input double RiskPerTrade = 1.0;                  // 每笔交易风险百分比 (0-10)
input double MaxDailyLoss = 2.0;                  // 每日最大亏损百分比 (0-5)
input double MaxTotalRisk = 3.0;                  // 总风险百分比 (0-15)
input int MaxPositions = 1;                       // 最大持仓数量
input int MaxConsecutiveLosses = 3;               // 最大连续亏损次数

// 服务器连接参数
input string ServerIP = "198.18.0.1";             // 服务器IP地址
input int ServerPort = 5002;                      // 服务器端口
input bool UseAutoDetectIP = false;               // 启用自动检测服务器IP（先关闭）
input bool EnableSSL = false;                     // 启用SSL/HTTPS（先关闭）

// EA设置参数
input int MagicNumber = 123456;                   // 魔术数字
input bool EnableLogging = true;                  // 启用日志记录

// 信号过滤参数
input int MinSignalStrength = 60;                 // 最小信号强度
input int SignalConfirmations = 1;                // 信号确认次数

// 性能优化参数
input int SignalCacheTime = 300;                  // 信号缓存时间(秒)
input int NetworkTimeout = 5000;                  // 网络超时时间(毫秒)

// 增强分析参数
input bool EnableAdvancedAnalysis = true;        // 启用高级分析
input bool EnableRiskManagement = true;         // 启用风险管理
input bool EnableMarketRegimeDetection = true;   // 启用市场状态检测
input bool EnableSupportResistance = true;       // 启用支撑阻力分析

//+------------------------------------------------------------------+
//| 全局变量                                                         |
//+------------------------------------------------------------------+
string TradingSymbol;                             // 实际使用的交易品种
ENUM_TIMEFRAMES TradingTimeframe;                 // 实际使用的交易周期
bool EA_Running = false;                          // EA运行状态
string PythonServerURL;                           // Python服务器URL（动态生成）
string CurrentServerIP;                           // 当前使用的服务器IP（可修改）
bool ServerConnected = false;                     // 服务器连接状态

// 账户管理变量
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
double CurrentEquity = 0.0;                       // 当前权益

// 信号处理变量
string LastSignal = "none";                       // 上一次信号
int SignalConfirmCount = 0;                       // 信号确认计数
int LastSignalTime = 0;                           // 上一次信号时间

// 持仓跟踪变量
int CurrentPositions = 0;                         // 当前持仓数量
double TotalRiskExposure = 0.0;                   // 总风险暴露

// 增强分析变量
string CurrentMarketRegime = "unknown";           // 当前市场状态
double MarketVolatility = 0.0;                    // 市场波动率
double RiskLevel = 0.0;                           // 风险等级
double SupportLevels[];                           // 支撑位数组
double ResistanceLevels[];                        // 阻力位数组

// 缓存设置
int CACHE_EXPIRY = 300;                           // 信号缓存时间(秒)

//+------------------------------------------------------------------+
//| 服务器IP工具函数                                                 |
//+------------------------------------------------------------------+

// 构建服务器URL
string BuildServerURL(string ip_address)
{
    string protocol = EnableSSL ? "https://" : "http://";
    string url = protocol + ip_address + ":" + IntegerToString(ServerPort);
    return url;
}

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
        case 150:   return "Prohibited by FIFO rules";
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
        case 4015:  return "Wrong jump";
        case 4016:  return "Not initialized array";
        case 4017:  return "DLL calls are not allowed";
        case 4018:  return "Cannot load library";
        case 4019:  return "Cannot call function";
        case 4020:  return "Expert function calls are not allowed";
        case 4021:  return "Not enough memory for temp string returned from function";
        case 4022:  return "System is busy";
        case 4023:  return "DLL-function call critical error";
        case 4024:  return "Internal error";
        case 4025:  return "Out of memory";
        case 4026:  return "Invalid pointer";
        case 4027:  return "Too many formatters in the format function";
        case 4028:  return "Invalid format parameters";
        case 4029:  return "Invalid datetime";
        case 4030:  return "Array is too long";
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
        case 4066:  return "Requested history data is in updating state";
        case 4067:  return "Internal trade error";
        case 4068:  return "Resource not found";
        case 4069:  return "Resource not supported";
        case 4070:  return "Duplicate resource";
        case 4071:  return "Cannot initialize custom indicator";
        case 4072:  return "Cannot load custom indicator";
        case 4073:  return "No history data";
        case 4074:  return "Not enough memory for history data";
        case 4075:  return "Not enough memory for indicator";
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
        case 4210:  return "Unknown symbol";
        case 4211:  return "Object is not found";
        case 4212:  return "Unknown object type";
        case 4213:  return "No object name";
        case 4214:  return "Object coordinates error";
        case 4215:  return "No specified subwindow";
        case 4216:  return "Some error in object function";
        case 5001:  return "Too many opened files";
        case 5002:  return "Wrong file name";
        case 5003:  return "Too long file name";
        case 5004:  return "Cannot open file";
        case 5005:  return "Text file buffer allocation error";
        case 5006:  return "Cannot delete file";
        case 5007:  return "Invalid file handle";
        case 5008:  return "Wrong file handle";
        case 5009:  return "File must be opened for writing";
        case 5010:  return "File must be opened for reading";
        case 5011:  return "File must be opened with FILE_BIN flag";
        case 5012:  return "More data";
        case 5013:  return "End of file";
        case 5014:  return "Some file error";
        case 5015:  return "Wrong file name";
        case 5016:  return "Too many opened files";
        case 5017:  return "No file name";
        case 5018:  return "Too long file name";
        case 5019:  return "Cannot delete file";
        case 5020:  return "Invalid file handle";
        case 5021:  return "File must be opened for writing";
        default:    return "Unknown error (" + IntegerToString(error_code) + ")";
    }
}

//+------------------------------------------------------------------+
//| 日志记录函数                                                     |
//+------------------------------------------------------------------+
void LogMessage(string message)
{
    if(EnableLogging)
    {
        Print("[AI_MultiTF_SMC_EA_Enhanced] ", TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS), " - ", message);
    }
}

//+------------------------------------------------------------------+
//| 获取K线数据函数                                                 |
//+------------------------------------------------------------------+
bool GetRatesData(MqlRates &rates[], int count = 100)
{
    int copied = CopyRates(TradingSymbol, TradingTimeframe, 0, count, rates);
    if(copied <= 0)
    {
        LogMessage("获取K线数据失败，错误: " + IntegerToString(GetLastError()));
        return false;
    }
    return true;
}

//+------------------------------------------------------------------+
//| 构建请求数据函数                                                 |
//+------------------------------------------------------------------+
string BuildRequestData(MqlRates &rates[])
{
    string json_data = "{\n";
    json_data += "  \"symbol\": \"" + TradingSymbol + "\",\n";
    json_data += "  \"timeframe\": \"" + EnumToString(TradingTimeframe) + "\",\n";
    json_data += "  \"rates\": [\n";
    
    for(int i = 0; i < ArraySize(rates); i++)
    {
        json_data += "    {\n";
        json_data += "      \"time\": " + IntegerToString(rates[i].time) + ",\n";
        json_data += "      \"open\": " + DoubleToString(rates[i].open, 5) + ",\n";
        json_data += "      \"high\": " + DoubleToString(rates[i].high, 5) + ",\n";
        json_data += "      \"low\": " + DoubleToString(rates[i].low, 5) + ",\n";
        json_data += "      \"close\": " + DoubleToString(rates[i].close, 5) + ",\n";
        json_data += "      \"tick_volume\": " + IntegerToString(rates[i].tick_volume) + "\n";
        json_data += "    }";
        
        if(i < ArraySize(rates) - 1)
            json_data += ",\n";
        else
            json_data += "\n";
    }
    
    json_data += "  ]\n";
    json_data += "}";
    
    return json_data;
}

//+------------------------------------------------------------------+
//| 发送HTTP请求函数                                                 |
//+------------------------------------------------------------------+
bool SendHTTPRequest(string url, string data, string &response, int timeout_ms = 5000)
{
    char post_data[];
    char result_data[];
    string headers = "Content-Type: application/json\r\n";
    
    // 转换为字节数组
    StringToCharArray(data, post_data, 0, StringLen(data));
    
    // 发送POST请求
    int res = WebRequest("POST", url, headers, timeout_ms, post_data, result_data, headers);
    
    if(res == -1)
    {
        int error_code = GetLastError();
        LogMessage("HTTP请求失败，错误: " + IntegerToString(error_code) + ", 描述: " + GetErrorDescription(error_code));
        return false;
    }
    
    response = CharArrayToString(result_data);
    return true;
}

//+------------------------------------------------------------------+
//| 解析信号响应函数                                                 |
//+------------------------------------------------------------------+
bool ParseSignalResponse(string response, string &signal, int &strength, string &analysis)
{
    // 简单的JSON解析（实际项目中应使用更健壮的解析方法）
    if(StringFind(response, "\"signal\": \"buy\"") != -1)
    {
        signal = "buy";
    }
    else if(StringFind(response, "\"signal\": \"sell\"") != -1)
    {
        signal = "sell";
    }
    else if(StringFind(response, "\"signal\": \"hold\"") != -1)
    {
        signal = "hold";
    }
    else
    {
        signal = "none";
    }
    
    // 解析信号强度
    int strength_start = StringFind(response, "\"strength\": ");
    if(strength_start != -1)
    {
        strength_start += 12; // 跳过 "\"strength\": "
        int strength_end = StringFind(response, ",", strength_start);
        if(strength_end == -1) strength_end = StringFind(response, "}", strength_start);
        
        if(strength_end != -1)
        {
            string strength_str = StringSubstr(response, strength_start, strength_end - strength_start);
            strength = (int)StringToInteger(strength_str);
        }
    }
    
    // 解析分析信息
    int analysis_start = StringFind(response, "\"analysis\": \"");
    if(analysis_start != -1)
    {
        analysis_start += 13; // 跳过 "\"analysis\": \""
        int analysis_end = StringFind(response, "\"", analysis_start);
        if(analysis_end != -1)
        {
            analysis = StringSubstr(response, analysis_start, analysis_end - analysis_start);
        }
    }
    
    return signal != "none";
}

//+------------------------------------------------------------------+
//| 获取交易信号函数                                                 |
//+------------------------------------------------------------------+
bool GetTradingSignal(string &signal, int &strength, string &analysis)
{
    MqlRates rates[];
    if(!GetRatesData(rates))
        return false;
    
    string request_data = BuildRequestData(rates);
    string response;
    
    if(!SendHTTPRequest(PythonServerURL + "/get_signal", request_data, response, NetworkTimeout))
        return false;
    
    return ParseSignalResponse(response, signal, strength, analysis);
}

//+------------------------------------------------------------------+
//| 获取详细分析函数                                                 |
//+------------------------------------------------------------------+
bool GetDetailedAnalysis(string &analysis_report)
{
    if(!EnableAdvancedAnalysis)
    {
        analysis_report = "高级分析已禁用";
        return false;
    }
    
    MqlRates rates[];
    if(!GetRatesData(rates))
        return false;
    
    string request_data = BuildRequestData(rates);
    string response;
    
    if(!SendHTTPRequest(PythonServerURL + "/analysis", request_data, response, NetworkTimeout))
        return false;
    
    analysis_report = response;
    return true;
}

//+------------------------------------------------------------------+
//| 风险管理检查函数                                                 |
//+------------------------------------------------------------------+
bool RiskManagementCheck()
{
    if(!EnableRiskManagement)
        return true;
    
    // 检查每日亏损限制
    if(DailyLoss >= MaxDailyLoss * AccountBalance / 100.0)
    {
        LogMessage("达到每日亏损限制，停止交易");
        return false;
    }
    
    // 检查总风险限制
    if(TotalRiskExposure >= MaxTotalRisk * AccountBalance / 100.0)
    {
        LogMessage("达到总风险限制，停止开仓");
        return false;
    }
    
    // 检查连续亏损次数
    if(ConsecutiveLosses >= MaxConsecutiveLosses)
    {
        LogMessage("达到最大连续亏损次数，暂停交易");
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| 计算仓位大小函数                                                 |
//+------------------------------------------------------------------+
double CalculatePositionSize()
{
    double risk_amount = AccountBalance * RiskPerTrade / 100.0;
    
    // 获取当前价格和止损距离
    double current_price = SymbolInfoDouble(TradingSymbol, SYMBOL_ASK);
    double stop_loss_distance = 0.0;
    
    // 这里应该根据具体的止损策略计算止损距离
    // 简化处理：使用固定点数止损
    double point = SymbolInfoDouble(TradingSymbol, SYMBOL_POINT);
    stop_loss_distance = 100 * point; // 100点止损
    
    if(stop_loss_distance <= 0)
        return 0.01; // 最小仓位
    
    double position_size = risk_amount / stop_loss_distance;
    
    // 限制仓位大小
    double min_lot = SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_MIN);
    double max_lot = SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_MAX);
    
    position_size = MathMax(position_size, min_lot);
    position_size = MathMin(position_size, max_lot);
    
    return NormalizeDouble(position_size, 2);
}

//+------------------------------------------------------------------+
//| 开仓函数                                                         |
//+------------------------------------------------------------------+
bool OpenPosition(string signal_type)
{
    if(!RiskManagementCheck())
        return false;
    
    if(CurrentPositions >= MaxPositions)
    {
        LogMessage("已达到最大持仓数量限制");
        return false;
    }
    
    double volume = CalculatePositionSize();
    if(volume <= 0)
    {
        LogMessage("计算仓位大小失败");
        return false;
    }
    
    MqlTradeRequest request = {};
    MqlTradeResult result = {};
    
    request.action = TRADE_ACTION_DEAL;
    request.symbol = TradingSymbol;
    request.volume = volume;
    request.magic = MagicNumber;
    request.comment = "AI_MultiTF_SMC_EA_Enhanced";
    
    if(signal_type == "buy")
    {
        request.type = ORDER_TYPE_BUY;
        request.price = SymbolInfoDouble(TradingSymbol, SYMBOL_ASK);
    }
    else if(signal_type == "sell")
    {
        request.type = ORDER_TYPE_SELL;
        request.price = SymbolInfoDouble(TradingSymbol, SYMBOL_BID);
    }
    else
    {
        LogMessage("无效的信号类型: " + signal_type);
        return false;
    }
    
    // 设置止损和止盈（简化处理）
    double stop_loss = 0.0;
    double take_profit = 0.0;
    
    // 这里应该根据具体的策略设置止损止盈
    // 简化处理：使用固定点数
    
    if(OrderSend(request, result))
    {
        LogMessage("成功开" + signal_type + "仓，订单号: " + IntegerToString(result.order));
        CurrentPositions++;
        return true;
    }
    else
    {
        LogMessage("开" + signal_type + "仓失败，错误: " + IntegerToString(GetLastError()));
        return false;
    }
}

//+------------------------------------------------------------------+
//| 平仓函数                                                         |
//+------------------------------------------------------------------+
bool CloseAllPositions()
{
    bool success = true;
    
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        ulong ticket = PositionGetTicket(i);
        if(PositionSelectByTicket(ticket))
        {
            if(PositionGetInteger(POSITION_MAGIC) == MagicNumber)
            {
                MqlTradeRequest request = {};
                MqlTradeResult result = {};
                
                request.action = TRADE_ACTION_DEAL;
                request.position = ticket;
                request.symbol = TradingSymbol;
                request.volume = PositionGetDouble(POSITION_VOLUME);
                request.magic = MagicNumber;
                
                if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY)
                {
                    request.type = ORDER_TYPE_SELL;
                    request.price = SymbolInfoDouble(TradingSymbol, SYMBOL_BID);
                }
                else
                {
                    request.type = ORDER_TYPE_BUY;
                    request.price = SymbolInfoDouble(TradingSymbol, SYMBOL_ASK);
                }
                
                if(!OrderSend(request, result))
                {
                    LogMessage("平仓失败，订单号: " + IntegerToString(ticket) + ", 错误: " + IntegerToString(GetLastError()));
                    success = false;
                }
                else
                {
                    LogMessage("成功平仓，订单号: " + IntegerToString(ticket));
                }
            }
        }
    }
    
    CurrentPositions = 0;
    return success;
}

//+------------------------------------------------------------------+
//| 更新账户统计函数                                                 |
//+------------------------------------------------------------------+
void UpdateAccountStats()
{
    AccountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    CurrentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    // 更新最大回撤
    if(CurrentEquity > InitialBalance)
    {
        InitialBalance = CurrentEquity;
        MaxDrawdown = 0.0;
    }
    else
    {
        double drawdown = (InitialBalance - CurrentEquity) / InitialBalance * 100.0;
        MaxDrawdown = MathMax(MaxDrawdown, drawdown);
    }
    
    // 更新每日亏损
    MqlDateTime current_time;
    TimeToStruct(TimeCurrent(), current_time);
    
    if(current_time.day != LastTradeDay.day || current_time.mon != LastTradeDay.mon || current_time.year != LastTradeDay.year)
    {
        DailyLoss = 0.0;
        LastTradeDay = current_time;
    }
}

//+------------------------------------------------------------------+
//| 初始化函数                                                       |
//+------------------------------------------------------------------+
int OnInit()
{
    LogMessage("EA初始化开始");
    
    // 设置交易品种和周期
    TradingSymbol = InputSymbol;
    TradingTimeframe = InputTimeframe;
    
    // 构建服务器URL
    if(UseAutoDetectIP)
    {
        // 这里可以实现自动检测IP的逻辑
        CurrentServerIP = ServerIP;
    }
    else
    {
        CurrentServerIP = ServerIP;
    }
    
    PythonServerURL = BuildServerURL(CurrentServerIP);
    
    // 初始化账户统计
    AccountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    InitialBalance = AccountBalance;
    CurrentEquity = AccountBalance;
    TimeToStruct(TimeCurrent(), LastTradeDay);
    
    // 测试服务器连接
    string test_response;
    if(SendHTTPRequest(PythonServerURL + "/health", "", test_response, 3000))
    {
        ServerConnected = true;
        LogMessage("服务器连接成功: " + PythonServerURL);
    }
    else
    {
        ServerConnected = false;
        LogMessage("服务器连接失败，请检查网络连接和服务器状态");
    }
    
    EA_Running = true;
    LogMessage("EA初始化完成");
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| 反初始化函数                                                     |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    LogMessage("EA停止运行，原因: " + IntegerToString(reason));
    
    // 关闭所有持仓
    if(CurrentPositions > 0)
    {
        LogMessage("正在关闭所有持仓...");
        CloseAllPositions();
    }
    
    EA_Running = false;
    LogMessage("EA已停止");
}

//+------------------------------------------------------------------+
//| 主循环函数                                                       |
//+------------------------------------------------------------------+
void OnTick()
{
    if(!EA_Running)
        return;
    
    // 更新账户统计
    UpdateAccountStats();
    
    // 检查是否是新K线
    static datetime last_bar_time = 0;
    datetime current_bar_time = iTime(TradingSymbol, TradingTimeframe, 0);
    
    if(current_bar_time == last_bar_time)
        return; // 同一根K线，不处理
    
    last_bar_time = current_bar_time;
    
    // 获取交易信号
    string current_signal;
    int current_strength;
    string current_analysis;
    
    if(!GetTradingSignal(current_signal, current_strength, current_analysis))
    {
        LogMessage("获取交易信号失败");
        return;
    }
    
    // 检查信号强度
    if(current_strength < MinSignalStrength)
    {
        LogMessage("信号强度不足: " + IntegerToString(current_strength) + " < " + IntegerToString(MinSignalStrength));
        return;
    }
    
    // 信号确认逻辑
    if(current_signal == LastSignal)
    {
        SignalConfirmCount++;
    }
    else
    {
        SignalConfirmCount = 1;
        LastSignal = current_signal;
    }
    
    if(SignalConfirmCount < SignalConfirmations)
    {
        LogMessage("信号确认中... (" + IntegerToString(SignalConfirmCount) + "/" + IntegerToString(SignalConfirmations) + ")");
        return;
    }
    
    // 执行交易逻辑
    if(current_signal == "buy" || current_signal == "sell")
    {
        if(CurrentPositions > 0)
        {
            // 如果有持仓，先平仓
            LogMessage("检测到新信号，正在平仓...");
            CloseAllPositions();
        }
        
        // 开新仓
        if(OpenPosition(current_signal))
        {
            LogMessage("成功执行" + current_signal + "信号");
            
            // 获取详细分析报告（如果启用）
            if(EnableAdvancedAnalysis)
            {
                string analysis_report;
                if(GetDetailedAnalysis(analysis_report))
                {
                    LogMessage("详细分析报告: " + analysis_report);
                }
            }
        }
    }
    else if(current_signal == "hold")
    {
        LogMessage("保持观望: " + current_analysis);
    }
    
    // 重置信号确认计数
    SignalConfirmCount = 0;
}
//+------------------------------------------------------------------+
        case 5022:  return "File must be opened for reading";
        case 5023:  return "File must be opened with FILE_BIN flag";
        case 5024:  return "More data";
        case 5025:  return "End of file";
        case 5026:  return "Some file error";
        case 5027:  return "Wrong file name";
        case 5028:  return "Too many opened files";
        case 5029:  return "No file name";
        case 5030:  return "Too long file name";
        case 5031:  return "Cannot delete file";
        case 5032:  return "Invalid file handle";
        case 5033:  return "File must be opened for writing";
        case 5034:  return "File must be opened for reading";
        case 5035:  return "File must be opened with FILE_BIN flag";
        case 5036:  return "More data";
        case 5037:  return "End of file";
        case 5038:  return "Some file error";
        case 5039:  return "Wrong file name";
        case 5040:  return "Too many opened files";
        case 5041:  return "No file name";
        case 5042:  return "Too long file name";
        case 5043:  return "Cannot delete file";
        case 5044:  return "Invalid file handle";
        case 5045:  return "File must be opened for writing";
        case 5046:  return "File must be opened for reading";
        case 5047:  return "File must be opened with FILE_BIN flag";
        case 5048:  return "More data";
        case 5049:  return "End of file";
        case 5050:  return "Some file error";
        case 5051:  return "Wrong file name";
        case 5052:  return "Too many opened files";
        case 5053:  return "No file name";
        case 5054:  return "Too long file name";
        case 5055:  return "Cannot delete file";
        case 5056:  return "Invalid file handle";
        case 5057:  return "File must be opened for writing";
        case 5058:  return "File must be opened for reading";
        case 5059:  return "File must be opened with FILE_BIN flag";
        case 5060:  return "More data";
        case 5061:  return "End of file";
        case 5062:  return "Some file error";
        case 5063:  return "Wrong file name";
        case 5064:  return "Too many opened files";
        case 5065:  return "No file name";
        case 5066:  return "Too long file name";
        case 5067:  return "Cannot delete file";
        case 5068:  return "Invalid file handle";
        case 5069:  return "File must be opened for writing";
        case 5070:  return "File must be opened for reading";
        case 5071:  return "File must be opened with FILE_BIN flag";
        case 5072:  return "More data";
        case 5073:  return "End of file";
        case 5074:  return "Some file error";
        case 5075:  return "Wrong file name";
        case 5076:  return "Too many opened files";
        case 5077:  return "No file name";
        case 5078:  return "Too long file name";
        case 5079:  return "Cannot delete file";
        case 5080:  return "Invalid file handle";
        case 5081:  return "File must be opened for writing";
        case 5082:  return "File must be opened for reading";
        case 5083:  return "File must be opened with FILE_BIN flag";
        case 5084:  return "More data";
        case 5085:  return "End of file";
        case 5086:  return "Some file error";
        case 5087:  return "Wrong file name";
        case 5088:  return "Too many opened files";
        case 5089:  return "No file name";
        case 5090:  return "Too long file name";
        case 5091:  return "Cannot delete file";
        case 5092:  return "Invalid file handle";
        case 5093:  return "File must be opened for writing";
        case 5094:  return "File must be opened for reading";
        case 5095:  return "File must be opened with FILE_BIN flag";
        case 5096:  return "More data";
        case 5097:  return "End of file";
        case 5098:  return "Some file error";
        case 5099:  return "Wrong file name";
        case 5100:  return "Too many opened files";
        case 5101:  return "No file name";
        case 5102:  return "Too long file name";
        case 5103:  return "Cannot delete file";
        case 5104:  return "Invalid file handle";
        case 5105:  return "File must be opened for writing";
        case 5106:  return "File must be opened for reading";
        case 5107:  return "File must be opened with FILE_BIN flag";
        case 5108:  return "More data";
        case 5109:  return "End of file";
        case 5110:  return "Some file error";
        case 5111:  return "Wrong file name";
        case 5112:  return "Too many opened files";
        case 5113:  return "No file name";
        case 5114:  return "Too long file name";
        case 5115:  return "Cannot delete file";
        case 5116:  return "Invalid file handle";
        case 5117:  return "File must be opened for writing";
        case 5118:  return "File must be opened for reading";
        case 5119:  return "File must be opened with FILE_BIN flag";
        case 5120:  return "More data";
        case 5121:  return "End of file";
        case 5122:  return "Some file error";
        case 5123:  return "Wrong file name";
        case 5124:  return "Too many opened files";
        case 5125:  return "No file name";
        case 5126:  return "Too long file name";
        case 5127:  return "Cannot delete file";
        case 5128:  return "Invalid file handle";
        case 5129:  return "File must be opened for writing";
        case 5130:  return "File must be opened for reading";
        case 5131:  return "File must be opened with FILE_BIN flag";
        case 5132:  return "More data";
        case 5133:  return "End of file";
        case 5134:  return "Some file error";
        case 5135:  return "Wrong file name";
        case 5136:  return "Too many opened files";
        case 5137:  return "No file name";
        case 5138:  return "Too long file name";
        case 5139:  return "Cannot delete file";
        case 5140:  return "Invalid file handle";
        case 5141:  return "File must be opened for writing";
        case 5142:  return "File must be opened for reading";
        case 5143:  return "File must be opened with FILE_BIN flag";
        case 5144:  return "More data";
        case 5145:  return "End of file";
        case 5146:  return "Some file error";
        case 5147:  return "Wrong file name";
        case 5148:  return "Too many opened files";
        case 5149:  return "No file name";
        case 5150:  return "Too long file name";
        case 5151:  return "Cannot delete file";
        case 5152:  return "Invalid file handle";
        case 5153:  return "File must be opened for writing";
        case 5154:  return "File must be opened for reading";
        case 5155:  return "File must be opened with FILE_BIN flag";
        case 5156:  return "More data";
        case 5157:  return "End of file";
        case 5158:  return "Some file error";
        case 5159:  return "Wrong file name";
        case 5160:  return "Too many opened files";
        case 5161:  return "No file name";
        case 5162:  return "Too long file name";
        case 5163:  return "Cannot delete file";
        case 5164:  return "Invalid file handle";
        case 5165:  return "File must be opened for writing";
        case 5166:  return "File must be opened for reading";
        case 5167:  return "File must be opened with FILE_BIN flag";
        case 5168:  return "More data";
        case 5169:  return "End of file";
        case 5170:  return "Some file error";
        case 5171:  return "Wrong file name";
        case 5172:  return "Too many opened files";
        case 5173:  return "No file name";
        case 5174:  return "Too long file name";
        case 5175:  return "Cannot delete file";
        case 5176:  return "Invalid file handle";
        case 5177:  return "File must be opened for writing";
        case 5178:  return "File must be opened for reading";
        case 5179:  return "File must be opened with FILE_BIN flag";
        case 5180:  return "More data";
        case 5181:  return "End of file";
        case 5182:  return "Some file error";
        case 5183:  return "Wrong file name";
        case 5184:  return "Too many opened files";
        case 5185:  return "No file name";
        case 5186:  return "Too long file name";
        case 5187:  return "Cannot delete file";
        case 5188:  return "Invalid file handle";
        case 5189:  return "File must be opened for writing";
        case 5190:  return "File must be opened for reading";
        case 5191:  return "File must be opened with FILE_BIN flag";
        case 5192:  return "More data";
        case 5193:  return "End of file";
        case 5194:  return "Some file error";
        case 5195:  return "Wrong file name";
        case 5196:  return "Too many opened files";
        case 5197:  return "No file name";
        case 5198:  return "Too long file name";
        case 5199:  return "Cannot delete file";
        case 5200:  return "Invalid file handle";
        case 5201:  return "File must be opened for writing";
        case 5202:  return "File must be opened for reading";
        case 5203:  return "File must be opened with FILE_BIN flag";
        case 5204:  return "More data";
        case 5205:  return "End of file";
        case 5206:  return "Some file error";
        case 5207:  return "Wrong file name";
        case 5208:  return "Too many opened files";
        case 5209:  return "No file name";
        case 5210:  return "Too long file name";
        case 5211:  return "Cannot delete file";
        case 5212:  return "Invalid file handle";
        case 5213:  return "File must be opened for writing";
        case 5214:  return "File must be opened for reading";
        case 5215:  return "File must be opened with FILE_BIN flag";
        case 5216:  return "More data";
        case 5217:  return "End of file";
        case 5218:  return "Some file error";
        case 5219:  return "Wrong file name";
        case 5220:  return "Too many opened files";
        case 5221:  return "No file name";
        case 5222:  return "Too long file name";
        case 5223:  return "Cannot delete file";
        case 5224:  return "Invalid file handle";
        case 5225:  return "File must be opened for writing";
        case 5226:  return "File must be opened for reading";
        case 5227:  return "File must be opened with FILE_BIN flag";
        case 5228:  return "More data";
        case 5229:  return "End of file";
        case 5230:  return "Some file error";
        case 5231:  return "Wrong file name";
        case 5232:  return "Too many opened files";
        case 5233:  return "No file name";
        case 5234:  return "Too long file name";
        case 5235:  return "Cannot delete file";
        case 5236:  return "Invalid file handle";
        case 5237:  return "File must be opened for writing";
        case 5238:  return "File must be opened for reading";
        case 5239:  return "File must be opened with FILE_BIN flag";
        case 5240:  return "More data";
        case 5241:  return "End of file";
        case 5242:  return "Some file error";
        case 5243:  return "Wrong file name";
        case 5244:  return "Too many opened files";
        case 5245:  return "No file name";
        case 5246:  return "Too long file name";
        case 5247:  return "Cannot delete file";
        case 5248:  return "Invalid file handle";
        case 5249:  return "File must be opened for writing";
        case 5250:  return "File must be opened for reading";
        case 5251:  return "File must be opened with FILE_BIN flag";
        case 5252:  return "More data";
        case 5253:  return "End of file";
        case 5254:  return "Some file error";
        case 5255:  return "Wrong file name";
        case 5256:  return "Too many opened files";
        case 5257:  return "No file name";
        case 5258:  return "Too long file name";
        case 5259:  return "Cannot delete file";
        case 5260:  return "Invalid file handle";
        case 5261:  return "File must be opened for writing";
        case 5262:  return "File must be opened for reading";
        case 5263:  return "File must be opened with FILE_BIN flag";
        case 5264:  return "More data";
        case 5265:  return "End of file";
        case 5266:  return "Some file error";
        case 5267:  return "Wrong file name";
        case 5268:  return "Too many opened files";
        case 5269:  return "No file name";
        case 5270:  return "Too long file name";
        case 5271:  return "Cannot delete file";
        case 5272:  return "Invalid file handle";
        case 5273:  return "File must be opened for writing";
        case 5274:  return "File must be opened for reading";
        case 5275:  return "File must be opened with FILE_BIN flag";
        case 5276:  return "More data";
        case 5277:  return "End of file";
        case 5278:  return "Some file error";
        case 5279:  return "Wrong file name";
        case 5280:  return "Too many opened files";
        case 5281:  return "No file name";
        case 5282:  return "Too long file name";
        case 5283:  return "Cannot delete file";
        case 5284:  return "Invalid file handle";
        case 5285:  return "File must be opened for writing";
        case 5286:  return "File must be opened for reading";
        case 5287:  return "File must be opened with FILE_BIN flag";
        case 5288:  return "More data";
        case 5289:  return "End of file";
        case 5290:  return "Some file error";