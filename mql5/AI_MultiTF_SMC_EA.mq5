//+------------------------------------------------------------------+
//| AI_MultiTF_SMC_EA.mq5                                            |
//| Copyright 2024, AI Quant Trading                                 |
//| https://github.com/ai-quant-trading                              |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Quant Trading"
#property link      "https://github.com/ai-quant-trading"
#property version   "1.00"

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

// 服务器连接参数
input string ServerIP = "198.18.0.1";          // 服务器IP地址（重要！）
input int ServerPort = 5001;                      // 服务器端口
input bool UseAutoDetectIP = True;               // 启用自动检测服务器IP
input bool EnableSSL = True;                    // 启用SSL/HTTPS（如果服务器支持）

// EA设置参数
input int MagicNumber = 123456;                   // 魔术数字
input bool EnableLogging = true;                  // 启用日志记录

// 信号过滤参数
input int MinSignalStrength = 60;                 // 最小信号强度
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
string PythonServerURL;                           // Python服务器URL（动态生成）

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

// 缓存设置
int CACHE_EXPIRY = 300;                           // 信号缓存时间(秒)

//+------------------------------------------------------------------+
//| 服务器IP工具函数                                                 |
//+------------------------------------------------------------------+

// 获取本地可能的IP地址列表
string GetLocalIPAddresses()
{
    string ipList = "";
    
    // 尝试可能的局域网IP段
    string ipPrefixes[] = {
        "192.168.1.",    // 最常见的家庭网络
        "192.168.0.",    // 第二常见的家庭网络
        "10.0.0.",       // 公司网络
        "172.16.0.",     // 大型网络
        "169.254.",      // 自动配置IP
        "127.0.0.1"      // 本地回环
    };
    
    for(int i = 0; i < ArraySize(ipPrefixes); i++)
    {
        ipList += ipPrefixes[i] + "XXX"; // 占位符，实际使用时需要测试
        if(i < ArraySize(ipPrefixes) - 1)
            ipList += ", ";
    }
    
    return ipList;
}

// 构建服务器URL
string BuildServerURL()
{
    string protocol = EnableSSL ? "https://" : "http://";
    string url = protocol + ServerIP + ":" + IntegerToString(ServerPort);
    
    if(EnableLogging)
        PrintFormat("服务器URL构建为: %s", url);
    
    return url;
}

//+------------------------------------------------------------------+
//| 错误代码转字符串                                                  |
//+------------------------------------------------------------------+
string GetErrorDescription(int error_code)
{
    // 错误代码映射表
    string errors[][2] = {
        {"0", "No error"},
        {"1", "No error returned, but result is unknown"},
        {"2", "Common error"},
        {"3", "Invalid trade parameters"},
        {"4", "Trade server is busy"},
        {"5", "Old version of the client terminal"},
        {"6", "No connection with trade server"},
        {"7", "Not enough rights"},
        {"8", "Too frequent requests"},
        {"9", "Malfunctional trade operation"},
        {"64", "Account disabled"},
        {"65", "Invalid account"},
        {"128", "Trade timeout"},
        {"129", "Invalid price"},
        {"130", "Invalid stops"},
        {"131", "Invalid trade volume"},
        {"132", "Market is closed"},
        {"133", "Trade is disabled"},
        {"134", "Not enough money"},
        {"135", "Price changed"},
        {"136", "Off quotes"},
        {"137", "Broker is busy"},
        {"138", "Requote"},
        {"139", "Order is locked"},
        {"140", "Long positions only allowed"},
        {"141", "Too many requests"},
        {"145", "Modification denied because order is too close to market"},
        {"146", "Trade context is busy"},
        {"147", "Expirations are denied by broker"},
        {"148", "Too many open and pending orders"},
        {"149", "Hedging is prohibited"},
        {"150", "Prohibit closing by opposite"},
        {"4000", "No error"},
        {"4001", "Wrong function pointer"},
        {"4002", "Array index is out of range"},
        {"4003", "No memory for function call stack"},
        {"4004", "Recursive stack overflow"},
        {"4005", "Not enough stack for parameter"},
        {"4006", "No memory for parameter string"},
        {"4007", "No memory for temp string"},
        {"4008", "Not initialized string"},
        {"4009", "Not initialized string in array"},
        {"4010", "No memory for array string"},
        {"4011", "Too long string"},
        {"4012", "Remainder from zero divide"},
        {"4013", "Zero divide"},
        {"4014", "Unknown command"},
        {"4015", "Wrong jump (never generated error)"},
        {"4016", "Not initialized array"},
        {"4017", "DLL calls are not allowed"},
        {"4018", "Cannot load library"},
        {"4019", "Cannot call function"},
        {"4020", "Expert function calls are not allowed"},
        {"4021", "Not enough memory for temp string returned from function"},
        {"4022", "System is busy (never generated error)"},
        {"4050", "Invalid function parameters count"},
        {"4051", "Invalid function parameter value"},
        {"4052", "String function internal error"},
        {"4053", "Some array error"},
        {"4054", "Incorrect series array using"},
        {"4055", "Custom indicator error"},
        {"4056", "Arrays are incompatible"},
        {"4057", "Global variables processing error"},
        {"4058", "Global variable not found"},
        {"4059", "Function is not allowed in testing mode"},
        {"4060", "Function is not confirmed"},
        {"4061", "Send mail error"},
        {"4062", "String parameter expected"},
        {"4063", "Integer parameter expected"},
        {"4064", "Double parameter expected"},
        {"4065", "Array as parameter expected"},
        {"4066", "Requested history data is in update state"},
        {"4067", "Some error in trade operation"},
        {"4099", "End of file"},
        {"4100", "Some file error"},
        {"4101", "Wrong file name"},
        {"4102", "Too many opened files"},
        {"4103", "Cannot open file"},
        {"4104", "Incompatible access to a file"},
        {"4105", "No order selected"},
        {"4106", "Unknown symbol"},
        {"4107", "Invalid price parameter"},
        {"4108", "Invalid ticket"},
        {"4109", "Trade is not allowed"},
        {"4110", "Longs are not allowed"},
        {"4111", "Shorts are not allowed"},
        {"4200", "Object already exists"},
        {"4201", "Unknown object property"},
        {"4202", "Object does not exist"},
        {"4203", "Unknown object type"},
        {"4204", "No object name"},
        {"4205", "Object coordinates error"},
        {"4206", "No specified subwindow"},
        {"4207", "Some error in object function"},
        {"4250", "Unknown chart property"},
        {"4251", "Chart not found"},
        {"4252", "Chart subwindow not found"},
        {"4253", "Chart indicator not found"},
        {"4254", "Symbol select error"},
        {"5001", "Invalid URL"},
        {"5002", "Failed to connect"},
        {"5003", "Timeout"},
        {"5004", "HTTP request failed"},
        {"5005", "Failed to read HTTP response"},
        {"4010", "URL not in the list of allowed URLs"},
        {"4011", "URL is in the list of blocked URLs"}
    };
    
    for(int i = 0; i < ArraySize(errors); i++)
    {
        if(StringToInteger(errors[i][0]) == error_code)
            return errors[i][1];
    }
    
    return "Unknown error (" + IntegerToString(error_code) + ")";
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
    // 构建服务器URL
    PythonServerURL = BuildServerURL();
    
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
        PrintFormat("AI_MultiTF_SMC_EA v%s 初始化成功", _Version);
        PrintFormat("交易品种: %s", TradingSymbol);
        PrintFormat("交易周期: %s", EnumToString(TradingTimeframe));
        PrintFormat("服务器URL: %s", PythonServerURL);
        PrintFormat("服务器IP: %s:%d", ServerIP, ServerPort);
        PrintFormat("每笔交易风险: %.2f%%", RiskPerTrade);
        PrintFormat("每日最大亏损: %.2f%%", MaxDailyLoss);
        PrintFormat("总风险百分比: %.2f%%", MaxTotalRisk);
        PrintFormat("最大持仓数量: %d", MaxPositions);
        PrintFormat("最小信号强度: %d", MinSignalStrength);
        PrintFormat("信号确认次数: %d", SignalConfirmations);
        PrintFormat("魔术数字: %d", MagicNumber);
        PrintFormat("信号缓存时间: %d秒", SignalCacheTime);
        PrintFormat("网络超时时间: %d毫秒", NetworkTimeout);
        
        Print("===== 重要提示 =====");
        Print("1. 请确保Python服务器正在运行");
        PrintFormat("2. 服务器地址: http://%s:%d", ServerIP, ServerPort);
        Print("3. 在MT5的选项中，将此URL添加到WebRequest白名单:");
        PrintFormat("   - http://%s:%d", ServerIP, ServerPort);
        PrintFormat("   - http://localhost:%d", ServerPort);
        PrintFormat("   - http://127.0.0.1:%d", ServerPort);
        Print("===================");
    }
    
    // 设置EA运行状态
    EA_Running = true;
    
    // 测试Python服务器连接
    if(!TestPythonServerConnection())
    {
        Print("错误: 无法连接到Python服务器，请检查:");
        Print("1. 服务器IP是否正确: " + ServerIP);
        Print("2. 服务器端口是否正确: " + IntegerToString(ServerPort));
        Print("3. Python服务器是否已启动");
        Print("4. 防火墙是否允许端口 " + IntegerToString(ServerPort));
        Print("5. URL是否已添加到MT5的WebRequest白名单");
        Print("");
        Print("可能的服务器IP地址:");
        Print(GetLocalIPAddresses());
        
        return(INIT_FAILED);
    }
    
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
    {
        Print("AI_MultiTF_SMC_EA 已停止，原因: ", reason);
        PrintFormat("总交易次数: %d", TotalTrades);
        PrintFormat("盈利交易: %d", WinningTrades);
        PrintFormat("亏损交易: %d", LosingTrades);
        PrintFormat("总盈利: %.2f", TotalProfit);
        PrintFormat("最大回撤: %.2f%%", MaxDrawdown);
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
bool TestPythonServerConnection()
{
    string testURL = PythonServerURL + "/health";
    string response_headers = "";
    uchar request_data[];
    uchar response_data[];
    string response = "";
    int error = 0;
    
    if(EnableLogging)
        PrintFormat("测试服务器连接: %s", testURL);
    
    // 发送HTTP GET请求
    error = WebRequest(
        "GET",
        testURL,
        "",
        NetworkTimeout,
        request_data,
        response_data,
        response_headers
    );
    
    if(error == 0)
    {
        response = CharArrayToString(response_data);
        if(EnableLogging)
            Print("Python服务器连接成功！响应: ", response);
        return true;
    } 
    else
    {
        string error_desc = GetWebRequestErrorDescription(error);
        
        if(EnableLogging)
        {
            PrintFormat("Python服务器连接失败！");
            PrintFormat("错误代码: %d", error);
            PrintFormat("错误描述: %s", error_desc);
            PrintFormat("尝试的URL: %s", testURL);
        }
        
        // 尝试备用方案：使用127.0.0.1
        if(StringFind(ServerIP, "localhost") >= 0)
        {
            string altServerIP = "127.0.0.1";
            string altURL = (EnableSSL ? "https://" : "http://") + altServerIP + ":" + IntegerToString(ServerPort) + "/health";
            
            if(EnableLogging)
                PrintFormat("尝试备用地址: %s", altURL);
            
            error = WebRequest(
                "GET",
                altURL,
                "",
                NetworkTimeout,
                request_data,
                response_data,
                response_headers
            );
            
            if(error == 0)
            {
                if(EnableLogging)
                    Print("使用127.0.0.1连接成功！");
                
                // 更新ServerIP
                ServerIP = altServerIP;
                PythonServerURL = BuildServerURL();
                return true;
            }
        }
        
        return false;
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
    
    // 计算当前权益
    CurrentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    // 计算当前亏损
    double daily_drawdown = (InitialBalance - CurrentEquity) / InitialBalance * 100;
    
    // 更新每日亏损
    if(daily_drawdown > DailyLoss)
        DailyLoss = daily_drawdown;
    
    // 检查是否超过每日最大亏损
    if(DailyLoss >= MaxDailyLoss)
    {
        if(EnableLogging)
            PrintFormat("达到每日最大亏损限制(%.2f%%)，EA将停止交易", DailyLoss);
        
        // 平仓所有头寸
        CloseAllPositions();
        
        // 停止EA
        EA_Running = false;
    }
    
    // 更新账户余额
    double current_balance = AccountInfoDouble(ACCOUNT_BALANCE);
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
        
        // 更新交易统计
        if(current_profit > 0 && LosingTrades > 0)
            WinningTrades++;
        else if(current_profit < 0 && WinningTrades > 0)
            LosingTrades++;
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
            request_data += "\"open\":" + DoubleToString(rates[i].open, _Digits) + ",";
            request_data += "\"high\":" + DoubleToString(rates[i].high, _Digits) + ",";
            request_data += "\"low\":" + DoubleToString(rates[i].low, _Digits) + ",";
            request_data += "\"close\":" + DoubleToString(rates[i].close, _Digits) + ",";
            request_data += "\"tick_volume\":" + IntegerToString(rates[i].tick_volume) + "}";
            
            if(i < max_bars - 1 && (i + 1) < ArraySize(rates) && rates[i + 1].time > 0)
                request_data += ",";
        }
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
    
    // 解析响应获取信号
    string signal = ParseJSON(response, "signal");
    SignalStrength = ParseJSONInt(response, "signal_strength");
    
    if(EnableLogging)
    {
        PrintFormat("收到AI信号: %s (强度: %d)", signal, SignalStrength);
        PrintFormat("完整响应: %s", StringSubstr(response, 0, 500));
    }
    
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
        NetworkTimeout,
        request_data,
        response_data,
        response_headers
    );
    
    if(error != 0)
    {
        if(EnableLogging)
        {
            PrintFormat("WebRequest失败:");
            PrintFormat("错误代码: %d", error);
            PrintFormat("错误描述: %s", GetWebRequestErrorDescription(error));
            PrintFormat("请求URL: %s", url);
            PrintFormat("数据长度: %d", ArraySize(request_data));
            
            if(error == 4010 || error == 4011)
            {
                Print("===== 解决方案 =====");
                Print("1. 打开MetaEditor");
                Print("2. 点击工具 -> 选项 -> 专家选项卡");
                Print("3. 在'允许WebRequest列出的URL'中添加:");
                PrintFormat("   %s", url);
                Print("4. 重启MT5");
                Print("==================");
            }
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
    request.comment = "AI_MultiTF_SMC_EA v" + _Version;
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
        double atr_value = atr[0];
        double sl_distance = atr_value * 2.0;
        double tp_distance = atr_value * 3.0;
        
        if(order_type == ORDER_TYPE_BUY)
        {
            request.sl = NormalizeDouble(request.price - sl_distance, _Digits);
            request.tp = NormalizeDouble(request.price + tp_distance, _Digits);
        }
        else
        {
            request.sl = NormalizeDouble(request.price + sl_distance, _Digits);
            request.tp = NormalizeDouble(request.price - tp_distance, _Digits);
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
    double contract_size = SymbolInfoDouble(TradingSymbol, SYMBOL_TRADE_CONTRACT_SIZE);
    
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
        double stop_loss_points = atr[0] / _Point;
        
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
        
        if(EnableLogging)
            PrintFormat("仓位计算: 风险金额=%.2f, 止损点数=%.2f, 每手风险=%.2f, 最终手数=%.2f", 
                      risk_amount, stop_loss_points, risk_per_lot, lot_size);
        
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