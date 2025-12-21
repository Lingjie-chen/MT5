//+------------------------------------------------------------------+
//| AI_MultiTF_SMC_EA_Socket_Enhanced.mq5                           |
//| Copyright 2024, AI Quant Trading                                |
//| https://github.com/ai-quant-trading                             |
//| Socket版本：基于底层Socket通信的MQL5-Python集成（修复版）         |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Quant Trading"
#property link      "https://github.com/ai-quant-trading"
#property version   "3.1"
#property description "AI多时间框架SMC交易系统 - Socket通信增强版"
#property description "集成AI信号分析、高级风险管理和市场状态检测"

//+------------------------------------------------------------------+
//| 包含文件                                                         |
//+------------------------------------------------------------------+
#include <Trade/Trade.mqh>
#include <Trade/AccountInfo.mqh>
#include <Trade/PositionInfo.mqh>
#include <Trade/SymbolInfo.mqh>
#include <Indicators/Indicator.mqh>
#include <Indicators/Trend.mqh>
#include <Indicators/Oscilators.mqh>
#include <Arrays/ArrayObj.mqh>
#include <Socket.mqh>  // MQL5 Socket库

//+------------------------------------------------------------------+
//| 结构定义                                                         |
//+------------------------------------------------------------------+
struct SSignalCache
{
    string signal;
    int strength;
    string analysis;
    datetime timestamp;
    bool is_valid;
    
    SSignalCache() : signal("none"), strength(0), analysis(""), timestamp(0), is_valid(false) {}
};

// Socket连接相关结构
struct SSocketConnection
{
    int socket;
    string host;
    int port;
    bool connected;
    datetime last_connect_time;
    
    SSocketConnection() : socket(-1), host("172.20.10.7"), port(9090), connected(false), last_connect_time(0) {}
};

// 全局Socket连接对象
SSocketConnection SocketConn;

//+------------------------------------------------------------------+
//| Socket通信函数                                                   |
//+------------------------------------------------------------------+
bool SocketConnect()
{
    // 如果已经连接，直接返回成功
    if(SocketConn.connected && SocketConn.socket != -1)
        return true;
    
    // 检查是否在短时间内重复连接
    if(TimeCurrent() - SocketConn.last_connect_time < 5)
        return false;
    
    SocketConn.last_connect_time = TimeCurrent();
    
    // 创建Socket
    SocketConn.socket = CustomSocketCreate();
    if(SocketConn.socket == SOCKET_INVALID_HANDLE)
    {
        LogMessage("Socket创建失败");
        return false;
    }
    
    // MQL5的Socket函数没有SetNonBlocking，我们使用默认设置
    // 连接到服务器
    if(!CustomSocketConnect(SocketConn.socket, SocketConn.host, SocketConn.port, 5000))
    {
        LogMessage("Socket连接失败: " + SocketConn.host + ":" + IntegerToString(SocketConn.port));
        CustomSocketClose(SocketConn.socket);
        SocketConn.socket = -1;
        return false;
    }
    
    SocketConn.connected = true;
    LogMessage("Socket连接成功: " + SocketConn.host + ":" + IntegerToString(SocketConn.port));
    return true;
}

void SocketDisconnect()
{
    if(SocketConn.socket != -1)
    {
        CustomSocketClose(SocketConn.socket);
        SocketConn.socket = -1;
    }
    SocketConn.connected = false;
    LogMessage("Socket连接已断开");
}

bool SocketSendRequest(string request, string &response, int timeout_ms = 5000)
{
    if(!SocketConn.connected || SocketConn.socket == -1)
    {
        if(!SocketConnect())
            return false;
    }
    
    // 发送请求（使用长度前缀格式）
    string message = IntegerToString(StringLen(request)) + ":" + request;
    uchar data[];
    StringToCharArray(message, data);
    
    int sent = CustomSocketSend(SocketConn.socket, data, ArraySize(data));
    if(sent <= 0)
    {
        LogMessage("Socket发送失败");
        SocketDisconnect();
        return false;
    }
    
    // 接收响应
    uint start_time = GetTickCount();  // GetTickCount()返回uint
    string buffer = "";
    
    uint timeout = (uint)timeout_ms;  // 将timeout_ms转换为uint
    
    while((uint)GetTickCount() - start_time < timeout)  // 确保都是uint类型
    {
        uchar recv_buffer[4096];
        int received = CustomSocketRead(SocketConn.socket, recv_buffer, ArraySize(recv_buffer), 100);
        
        if(received > 0)
        {
            buffer += CharArrayToString(recv_buffer, 0, received);
            
            // 检查是否收到完整响应
            int colon_pos = StringFind(buffer, ":");
            if(colon_pos != -1)
            {
                string length_str = StringSubstr(buffer, 0, colon_pos);
                long message_length_long = StringToInteger(length_str);  // 先转换为long
                int message_length = (int)message_length_long;  // 再转换为int
                
                if(StringLen(buffer) >= colon_pos + 1 + message_length)
                {
                    response = StringSubstr(buffer, colon_pos + 1, message_length);
                    return true;
                }
            }
        }
        else if(received == 0)
        {
            // 没有数据，继续等待
            Sleep(10);
        }
        else
        {
            // 接收错误
            LogMessage("Socket接收错误");
            SocketDisconnect();
            return false;
        }
    }
    
    LogMessage("Socket接收超时");
    SocketDisconnect();
    return false;
}

bool GetSignalFromSocket(string &signal, int &strength, string &analysis)
{
    // 准备请求数据
    MqlRates rates[];
    if(!GetRatesData(rates, 100))
    {
        LogMessage("获取K线数据失败");
        return false;
    }
    
    // 构建请求JSON
    string request = "{\"action\":\"get_signal\",\"symbol\":\"" + TradingSymbol + "\",\"timeframe\":\"" + 
                    EnumToString(TradingTimeframe) + "\",\"rates\":[";
    
    for(int i = 0; i < ArraySize(rates); i++)
    {
        if(i > 0) request += ",";
        request += "{\"time\":" + IntegerToString(rates[i].time) + ",\"open\":" + DoubleToString(rates[i].open, 5) + 
                  ",\"high\":" + DoubleToString(rates[i].high, 5) + ",\"low\":" + DoubleToString(rates[i].low, 5) + 
                  ",\"close\":" + DoubleToString(rates[i].close, 5) + ",\"tick_volume\":" + IntegerToString(rates[i].tick_volume) + "}";
    }
    request += "]}";
    
    // 发送请求并获取响应
    string response;
    if(!SocketSendRequest(request, response))
    {
        LogMessage("Socket通信失败");
        return false;
    }
    
    // 解析响应
    int signal_start = StringFind(response, "\"signal\":\"");
    int strength_start = StringFind(response, "\"strength\":");
    int analysis_start = StringFind(response, "\"analysis\":\"");
    
    if(signal_start == -1 || strength_start == -1 || analysis_start == -1)
    {
        LogMessage("响应格式错误: " + response);
        return false;
    }
    
    // 提取信号
    signal_start += 9; // 跳过 "signal":"
    int signal_end = StringFind(response, "\"", signal_start);
    if(signal_end != -1)
        signal = StringSubstr(response, signal_start, signal_end - signal_start);
    
    // 提取强度
    strength_start += 10; // 跳过 "strength":
    int strength_end = StringFind(response, ",", strength_start);
    if(strength_end == -1) strength_end = StringFind(response, "}", strength_start);
    if(strength_end != -1)
    {
        string strength_str = StringSubstr(response, strength_start, strength_end - strength_start);
        long strength_long = StringToInteger(strength_str);
        strength = (int)strength_long;
    }
    
    // 提取分析
    analysis_start += 11; // 跳过 "analysis":"
    int analysis_end = StringFind(response, "\"", analysis_start);
    if(analysis_end != -1)
        analysis = StringSubstr(response, analysis_start, analysis_end - analysis_start);
    
    return true;
}

//+------------------------------------------------------------------+
//| 我的订单信息类（自定义，避免与内置COrderInfo冲突）                |
//+------------------------------------------------------------------+
class CMyOrderInfo : public CObject
{
public:
    ulong ticket;
    datetime open_time;
    double open_price;
    double sl;
    double tp;
    double profit;
    string type;
    
    CMyOrderInfo() : ticket(0), open_time(0), open_price(0.0), sl(0.0), tp(0.0), profit(0.0), type("") {}
    
    // 必须重写Compare方法
    int Compare(const CObject *node, const int mode=0) const override
    {
        const CMyOrderInfo* other = node;
        if(other == NULL) return 1;
        
        if(this.ticket < other.ticket) return -1;
        if(this.ticket > other.ticket) return 1;
        return 0;
    }
};

//+------------------------------------------------------------------+
//| 订单跟踪器类                                                     |
//+------------------------------------------------------------------+
class CMyOrderTracker
{
private:
    CArrayObj m_orders;
    datetime m_last_update;
    
public:
    CMyOrderTracker() : m_last_update(0) 
    {
        // 启用CArrayObj的FreeMode以自动删除对象
        m_orders.FreeMode(true);
    }
    
    ~CMyOrderTracker()
    {
        m_orders.Clear();
    }
    
    void UpdateOrders(int magic)
    {
        datetime now = TimeCurrent();
        if(now - m_last_update < 1) // 每秒最多更新一次
            return;
            
        m_orders.Clear();
        
        // 获取当前持仓
        for(int i = 0; i < PositionsTotal(); i++)
        {
            ulong ticket = PositionGetTicket(i);
            if(PositionSelectByTicket(ticket))
            {
                if(PositionGetInteger(POSITION_MAGIC) == magic)
                {
                    CMyOrderInfo* order = new CMyOrderInfo();
                    order.ticket = ticket;
                    order.open_time = (datetime)PositionGetInteger(POSITION_TIME);
                    order.open_price = PositionGetDouble(POSITION_PRICE_OPEN);
                    order.sl = PositionGetDouble(POSITION_SL);
                    order.tp = PositionGetDouble(POSITION_TP);
                    order.profit = PositionGetDouble(POSITION_PROFIT);
                    order.type = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? "BUY" : "SELL";
                    
                    m_orders.Add(order);
                }
            }
        }
        
        m_last_update = now;
    }
    
    int GetTotalPositions()
    {
        return m_orders.Total();
    }
    
    double GetTotalProfit()
    {
        double total = 0.0;
        for(int i = 0; i < m_orders.Total(); i++)
        {
            CObject* obj = m_orders.At(i);
            if(obj != NULL)
            {
                CMyOrderInfo* order = obj;
                total += order.profit;
            }
        }
        return total;
    }
    
    double GetTotalProfitToday()
    {
        double total = 0.0;
        MqlDateTime today;
        TimeToStruct(TimeCurrent(), today);
        
        for(int i = 0; i < m_orders.Total(); i++)
        {
            CObject* obj = m_orders.At(i);
            if(obj != NULL)
            {
                CMyOrderInfo* order = obj;
                MqlDateTime order_time;
                TimeToStruct(order.open_time, order_time);
                
                if(order_time.day == today.day && 
                   order_time.mon == today.mon && 
                   order_time.year == today.year)
                {
                    total += order.profit;
                }
            }
        }
        return total;
    }
    
    void CloseAllPositions(string symbol, int magic)
    {
        CTrade trade;
        trade.SetExpertMagicNumber(magic);
        
        for(int i = PositionsTotal() - 1; i >= 0; i--)
        {
            ulong ticket = PositionGetTicket(i);
            if(PositionSelectByTicket(ticket))
            {
                if(PositionGetString(POSITION_SYMBOL) == symbol && 
                   PositionGetInteger(POSITION_MAGIC) == magic)
                {
                    if(!trade.PositionClose(ticket))
                    {
                        PrintFormat("平仓失败，订单号: %d, 错误: %d", ticket, GetLastError());
                    }
                }
            }
        }
        
        m_orders.Clear();
    }
};

//+------------------------------------------------------------------+
//| 市场分析器类                                                     |
//+------------------------------------------------------------------+
class CMarketAnalyzer
{
private:
    string m_symbol;
    ENUM_TIMEFRAMES m_timeframe;
    int m_atr_handle;
    int m_rsi_handle;
    
public:
    CMarketAnalyzer(string symbol, ENUM_TIMEFRAMES timeframe) : 
        m_symbol(symbol), m_timeframe(timeframe), m_atr_handle(INVALID_HANDLE), m_rsi_handle(INVALID_HANDLE)
    {
        // 创建指标句柄
        m_atr_handle = iATR(m_symbol, m_timeframe, 14);
        m_rsi_handle = iRSI(m_symbol, m_timeframe, 14, PRICE_CLOSE);
    }
    
    ~CMarketAnalyzer()
    {
        if(m_atr_handle != INVALID_HANDLE)
            IndicatorRelease(m_atr_handle);
        if(m_rsi_handle != INVALID_HANDLE)
            IndicatorRelease(m_rsi_handle);
    }
    
    double GetATR(int shift = 0)
    {
        if(m_atr_handle == INVALID_HANDLE)
            return 0.0;
            
        double buffer[1];
        if(CopyBuffer(m_atr_handle, 0, shift, 1, buffer) < 1)
            return 0.0;
            
        return buffer[0];
    }
    
    double GetRSI(int shift = 0)
    {
        if(m_rsi_handle == INVALID_HANDLE)
            return 50.0;
            
        double buffer[1];
        if(CopyBuffer(m_rsi_handle, 0, shift, 1, buffer) < 1)
            return 50.0;
            
        return buffer[0];
    }
    
    double GetVolatility(int period = 20)
    {
        double sum = 0.0;
        double prices[];
        ArraySetAsSeries(prices, true);
        
        if(CopyClose(m_symbol, m_timeframe, 0, period, prices) < period)
            return 0.0;
            
        double mean = 0.0;
        for(int i = 0; i < period; i++)
            mean += prices[i];
        mean /= period;
        
        for(int i = 0; i < period; i++)
            sum += MathPow(prices[i] - mean, 2);
            
        return MathSqrt(sum / period) / mean * 100.0;
    }
    
    string GetMarketRegime()
    {
        double atr = GetATR();
        double rsi = GetRSI();
        double volatility = GetVolatility();
        
        if(volatility > 2.0)
            return "high_volatility";
        else if(volatility < 0.5)
            return "low_volatility";
        else if(rsi > 70)
            return "overbought";
        else if(rsi < 30)
            return "oversold";
        else
            return "normal";
    }
};

//+------------------------------------------------------------------+
//| EA输入参数                                                       |
//+------------------------------------------------------------------+
input group "=== 基本设置 ==="
input string InputSymbol = "";                    // 交易品种（空值使用当前图表）
input ENUM_TIMEFRAMES InputTimeframe = PERIOD_CURRENT; // 交易周期

input group "=== 资金管理 ==="
input double RiskPerTrade = 1.0;                  // 每笔交易风险百分比 (0.1-5)
input double MaxDailyLoss = 2.0;                  // 每日最大亏损百分比 (0.5-10)
input double MaxTotalRisk = 3.0;                  // 总风险百分比 (1-15)
input int MaxPositions = 1;                       // 最大持仓数量 (1-10)
input int MaxConsecutiveLosses = 3;               // 最大连续亏损次数 (1-10)

input group "=== EA设置 ==="
input int MagicNumber = 20241201;                 // 魔术数字
input bool EnableLogging = true;                  // 启用日志记录
input bool EnableAlerts = true;                   // 启用警报

input group "=== 信号过滤 ==="
input int MinSignalStrength = 65;                 // 最小信号强度 (50-100)
input int SignalConfirmations = 2;                // 信号确认次数 (1-5)
input int SignalCacheTime = 300;                  // 信号缓存时间(秒)

input group "=== 高级分析 ==="
input bool EnableAdvancedAnalysis = true;         // 启用高级分析
input bool EnableRiskManagement = true;           // 启用风险管理
input bool EnableMarketRegimeDetection = true;    // 启用市场状态检测
input bool EnableDynamicStopLoss = true;          // 启用动态止损
input double ATRMultiplier = 2.0;                 // ATR止损乘数 (1-3)
input double RiskRewardRatio = 2.0;               // 风险回报比 (1-3)

input group "=== 交易时间 ==="
input bool EnableTradingHours = false;            // 启用交易时间限制
input int TradingStartHour = 0;                   // 交易开始时间(小时)
input int TradingEndHour = 23;                    // 交易结束时间(小时)
input bool SkipWeekend = true;                    // 跳过周末

//+------------------------------------------------------------------+
//| 全局变量                                                         |
//+------------------------------------------------------------------+
string TradingSymbol;                             // 实际使用的交易品种
ENUM_TIMEFRAMES TradingTimeframe;                 // 实际使用的交易周期
bool EA_Running = false;                          // EA运行状态

// 账户管理变量
double AccountBalance = 0.0;                      // 账户余额
double DailyLoss = 0.0;                           // 当日亏损
double DailyProfit = 0.0;                         // 当日盈利
MqlDateTime LastTradeDay;                         // 最后交易日期
int SignalStrength = 0;                           // 信号强度

// 性能跟踪变量
int ConsecutiveLosses = 0;                        // 连续亏损次数
int ConsecutiveWins = 0;                          // 连续盈利次数
int TotalTrades = 0;                              // 总交易次数
int WinningTrades = 0;                            // 盈利交易次数
int LosingTrades = 0;                             // 亏损交易次数
double TotalProfit = 0.0;                         // 总盈利
double MaxDrawdown = 0.0;                         // 最大回撤
double PeakEquity = 0.0;                          // 峰值权益
double CurrentEquity = 0.0;                       // 当前权益

// 信号处理变量
SSignalCache SignalCache;                         // 信号缓存
int SignalConfirmCount = 0;                       // 信号确认计数
string LastSignal = "none";                       // 上一次信号
datetime LastSignalTime = 0;                      // 上一次信号时间

// 市场分析变量
CMarketAnalyzer* MarketAnalyzer = NULL;           // 市场分析器
CMyOrderTracker* OrderTracker = NULL;             // 订单跟踪器
CTrade* Trade = NULL;                             // 交易对象

//+------------------------------------------------------------------+
//| 日志和工具函数                                                   |
//+------------------------------------------------------------------+
void LogMessage(string message)
{
    if(EnableLogging)
    {
        string timestamp = TimeToString(TimeCurrent(), TIME_DATE|TIME_SECONDS);
        Print("[AI_EA] ", timestamp, " - ", message);
    }
    
    if(EnableAlerts && StringFind(message, "错误") != -1)
    {
        Alert(message);
    }
}

string GetErrorDescription(int error_code)
{
    switch(error_code)
    {
        case 0:     return "成功";
        case 1:     return "没有错误，但结果未知";
        case 2:     return "通用错误";
        case 3:     return "无效的交易参数";
        case 4:     return "交易服务器繁忙";
        case 5:     return "客户端终端版本过旧";
        case 6:     return "与交易服务器无连接";
        case 7:     return "权限不足";
        case 8:     return "请求过于频繁";
        case 9:     return "交易操作功能异常";
        case 64:    return "账户被禁用";
        case 65:    return "无效账户";
        case 128:   return "交易超时";
        case 129:   return "无效价格";
        case 130:   return "无效止损";
        case 131:   return "无效交易量";
        case 132:   return "市场已关闭";
        case 133:   return "交易被禁用";
        case 134:   return "资金不足";
        case 135:   return "价格已变化";
        case 136:   return "没有报价";
        case 137:   return "经纪商繁忙";
        case 138:   return "重新报价";
        case 139:   return "订单被锁定";
        case 140:   return "只允许多头持仓";
        case 141:   return "请求过多";
        case 145:   return "订单离市场太近，修改被拒绝";
        case 146:   return "交易上下文繁忙";
        case 147:   return "经纪商拒绝设置到期时间";
        case 148:   return "挂单和持仓订单过多";
        case 149:   return "对冲被禁止";
        case 150:   return "违反FIFO规则";
        default:    return "未知错误 (" + IntegerToString(error_code) + ")";
    }
}

//+------------------------------------------------------------------+
//| 数据获取函数                                                     |
//+------------------------------------------------------------------+
bool GetRatesData(MqlRates &rates[], int count = 100)
{
    ResetLastError();
    
    int copied = CopyRates(TradingSymbol, TradingTimeframe, 0, count, rates);
    if(copied <= 0)
    {
        int error = GetLastError();
        LogMessage("获取K线数据失败，错误: " + IntegerToString(error) + " - " + GetErrorDescription(error));
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| 信号处理函数                                                     |
//+------------------------------------------------------------------+
bool GetCachedSignal(string &signal, int &strength, string &analysis)
{
    if(SignalCache.is_valid && 
       (TimeCurrent() - SignalCache.timestamp) < SignalCacheTime)
    {
        signal = SignalCache.signal;
        strength = SignalCache.strength;
        analysis = SignalCache.analysis;
        return true;
    }
    return false;
}

void UpdateSignalCache(string signal, int strength, string analysis)
{
    SignalCache.signal = signal;
    SignalCache.strength = strength;
    SignalCache.analysis = analysis;
    SignalCache.timestamp = TimeCurrent();
    SignalCache.is_valid = true;
}

bool GetTradingSignal(string &signal, int &strength, string &analysis)
{
    // 首先尝试从缓存获取
    if(GetCachedSignal(signal, strength, analysis))
    {
        LogMessage("使用缓存信号: " + signal + " (强度: " + IntegerToString(strength) + ")");
        return true;
    }
    
    // 通过Socket连接AI服务器获取实际信号
    if(GetSignalFromSocket(signal, strength, analysis))
    {
        // 更新缓存
        UpdateSignalCache(signal, strength, analysis);
        
        LogMessage("从AI服务器获取信号: " + signal + " (强度: " + IntegerToString(strength) + ")");
        LogMessage("分析结果: " + analysis);
        return true;
    }
    
    // 如果Socket连接失败，使用备用信号生成逻辑
    LogMessage("Socket连接失败，使用备用信号生成");
    
    // 基于技术指标的备用信号生成
    if(MarketAnalyzer != NULL)
    {
        string market_regime = MarketAnalyzer.GetMarketRegime();
        double atr_value = MarketAnalyzer.GetATR(0);
        double rsi_value = MarketAnalyzer.GetRSI(0);
        
        if(market_regime == "high_volatility")
        {
            signal = "hold";
            strength = 60;
            analysis = "备用信号 - 高波动市场，保持观望";
        }
        else if(market_regime == "low_volatility")
        {
            signal = "hold";
            strength = 60;
            analysis = "备用信号 - 低波动市场，保持观望";
        }
        else if(market_regime == "overbought" && rsi_value > 70)
        {
            signal = "sell";
            strength = 75;
            analysis = "备用信号 - 超买状态，RSI=" + DoubleToString(rsi_value, 2);
        }
        else if(market_regime == "oversold" && rsi_value < 30)
        {
            signal = "buy";
            strength = 75;
            analysis = "备用信号 - 超卖状态，RSI=" + DoubleToString(rsi_value, 2);
        }
        else
        {
            // 使用简单的移动平均交叉策略
            double ma_fast = iMA(TradingSymbol, TradingTimeframe, 10, 0, MODE_SMA, PRICE_CLOSE);
            double ma_slow = iMA(TradingSymbol, TradingTimeframe, 25, 0, MODE_SMA, PRICE_CLOSE);
            
            if(ma_fast > ma_slow)
            {
                signal = "buy";
                strength = 65;
                analysis = "备用信号 - MA10 > MA20，看涨";
            }
            else if(ma_fast < ma_slow)
            {
                signal = "sell";
                strength = 65;
                analysis = "备用信号 - MA10 < MA20，看跌";
            }
            else
            {
                signal = "hold";
                strength = 50;
                analysis = "备用信号 - 均线交叉不明显";
            }
        }
    }
    else
    {
        // 如果市场分析器不可用，使用简单的随机信号
        int random_signal = MathRand() % 100;
        
        if(random_signal < 40)
        {
            signal = "buy";
            strength = 70 + MathRand() % 30;
        }
        else if(random_signal < 80)
        {
            signal = "sell";
            strength = 70 + MathRand() % 30;
        }
        else
        {
            signal = "hold";
            strength = 50;
        }
        
        analysis = "备用信号 - 随机生成";
    }
    
    // 更新缓存
    UpdateSignalCache(signal, strength, analysis);
    
    LogMessage("生成备用信号: " + signal + " (强度: " + IntegerToString(strength) + ")");
    return true;
}

bool GetDetailedAnalysis(string &analysis_report)
{
    if(!EnableAdvancedAnalysis)
    {
        analysis_report = "高级分析已禁用";
        return false;
    }
    
    // 生成模拟分析报告
    analysis_report = "=== 市场分析报告 ===\n";
    analysis_report += "时间: " + TimeToString(TimeCurrent()) + "\n";
    analysis_report += "品种: " + TradingSymbol + "\n";
    analysis_report += "周期: " + EnumToString(TradingTimeframe) + "\n";
    
    if(MarketAnalyzer != NULL)
    {
        analysis_report += "ATR: " + DoubleToString(MarketAnalyzer.GetATR(), _Digits) + "\n";
        analysis_report += "RSI: " + DoubleToString(MarketAnalyzer.GetRSI(), 2) + "\n";
        analysis_report += "波动率: " + DoubleToString(MarketAnalyzer.GetVolatility(), 2) + "%\n";
        analysis_report += "市场状态: " + MarketAnalyzer.GetMarketRegime() + "\n";
    }
    
    analysis_report += "账户余额: " + DoubleToString(AccountBalance, 2) + "\n";
    analysis_report += "当前权益: " + DoubleToString(CurrentEquity, 2) + "\n";
    analysis_report += "最大回撤: " + DoubleToString(MaxDrawdown, 2) + "%\n";
    analysis_report += "===================";
    
    return true;
}

//+------------------------------------------------------------------+
//| 风险管理函数                                                     |
//+------------------------------------------------------------------+
bool RiskManagementCheck()
{
    if(!EnableRiskManagement)
        return true;
    
    // 更新账户信息
    AccountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    CurrentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    // 检查每日亏损限制
    double max_daily_loss_amount = AccountBalance * MaxDailyLoss / 100.0;
    if(DailyLoss >= max_daily_loss_amount)
    {
        LogMessage(StringFormat("达到每日亏损限制: %.2f >= %.2f", DailyLoss, max_daily_loss_amount));
        return false;
    }
    
    // 检查总风险限制
    double max_total_risk_amount = AccountBalance * MaxTotalRisk / 100.0;
    double current_risk = CalculateCurrentRisk();
    if(current_risk >= max_total_risk_amount)
    {
        LogMessage(StringFormat("达到总风险限制: %.2f >= %.2f", current_risk, max_total_risk_amount));
        return false;
    }
    
    // 检查连续亏损次数
    if(ConsecutiveLosses >= MaxConsecutiveLosses)
    {
        LogMessage(StringFormat("达到最大连续亏损次数: %d >= %d", ConsecutiveLosses, MaxConsecutiveLosses));
        return false;
    }
    
    // 检查保证金水平
    double margin_level = AccountInfoDouble(ACCOUNT_MARGIN_LEVEL);
    if(margin_level > 0 && margin_level < 100.0)
    {
        LogMessage(StringFormat("保证金水平过低: %.2f%%", margin_level));
        return false;
    }
    
    // 检查最大回撤
    if(MaxDrawdown > 20.0) // 20%最大回撤限制
    {
        LogMessage(StringFormat("达到最大回撤限制: %.2f%%", MaxDrawdown));
        return false;
    }
    
    // 检查交易时间
    if(!IsTradingTime())
    {
        LogMessage("非交易时间");
        return false;
    }
    
    return true;
}

double CalculateCurrentRisk()
{
    double total_risk = 0.0;
    
    for(int i = 0; i < PositionsTotal(); i++)
    {
        ulong ticket = PositionGetTicket(i);
        if(PositionSelectByTicket(ticket))
        {
            if(PositionGetString(POSITION_SYMBOL) == TradingSymbol &&
               PositionGetInteger(POSITION_MAGIC) == MagicNumber)
            {
                double volume = PositionGetDouble(POSITION_VOLUME);
                double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
                double sl = PositionGetDouble(POSITION_SL);
                
                if(sl > 0)
                {
                    double risk_per_lot = MathAbs(open_price - sl);
                    total_risk += risk_per_lot * volume;
                }
            }
        }
    }
    
    return total_risk;
}

bool IsTradingTime()
{
    if(!EnableTradingHours)
        return true;
    
    MqlDateTime current_time;
    TimeToStruct(TimeCurrent(), current_time);
    
    // 检查周末
    if(SkipWeekend && (current_time.day_of_week == 0 || current_time.day_of_week == 6))
        return false;
    
    // 检查交易时间
    if(current_time.hour < TradingStartHour || current_time.hour >= TradingEndHour)
        return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| 仓位管理函数                                                     |
//+------------------------------------------------------------------+
double CalculatePositionSize(string signal_type)
{
    double risk_amount = AccountBalance * RiskPerTrade / 100.0;
    
    // 获取当前价格
    double current_price = 0.0;
    double stop_loss_distance = 0.0;
    
    if(signal_type == "buy")
    {
        current_price = SymbolInfoDouble(TradingSymbol, SYMBOL_ASK);
    }
    else if(signal_type == "sell")
    {
        current_price = SymbolInfoDouble(TradingSymbol, SYMBOL_BID);
    }
    else
    {
        return 0.0;
    }
    
    // 计算止损距离
    if(EnableDynamicStopLoss && MarketAnalyzer != NULL)
    {
        double atr = MarketAnalyzer.GetATR();
        stop_loss_distance = atr * ATRMultiplier;
    }
    else
    {
        // 固定点数止损
        double point = SymbolInfoDouble(TradingSymbol, SYMBOL_POINT);
        stop_loss_distance = 100 * point;
    }
    
    if(stop_loss_distance <= 0)
    {
        LogMessage("无效的止损距离");
        return SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_MIN);
    }
    
    // 计算仓位大小
    double position_size = risk_amount / stop_loss_distance;
    
    // 限制仓位大小
    double min_lot = SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_MIN);
    double max_lot = SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_MAX);
    double lot_step = SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_STEP);
    
    position_size = MathMax(position_size, min_lot);
    position_size = MathMin(position_size, max_lot);
    
    // 对齐到步长
    position_size = MathRound(position_size / lot_step) * lot_step;
    
    // 检查保证金是否足够
    double margin_required = position_size * SymbolInfoDouble(TradingSymbol, SYMBOL_MARGIN_INITIAL);
    double free_margin = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
    
    if(margin_required > free_margin * 0.7) // 不超过70%的可用保证金
    {
        position_size = (free_margin * 0.7) / SymbolInfoDouble(TradingSymbol, SYMBOL_MARGIN_INITIAL);
        position_size = MathRound(position_size / lot_step) * lot_step;
        position_size = MathMax(position_size, min_lot);
        
        LogMessage("保证金不足，调整仓位大小");
    }
    
    LogMessage(StringFormat("计算仓位大小: %.2f (风险: %.2f, 止损距离: %.5f)", 
        position_size, risk_amount, stop_loss_distance));
    
    return NormalizeDouble(position_size, 2);
}

bool CalculateStopLossTakeProfit(string signal_type, double entry_price, 
                                 double &stop_loss, double &take_profit)
{
    double point = SymbolInfoDouble(TradingSymbol, SYMBOL_POINT);
    
    if(EnableDynamicStopLoss && MarketAnalyzer != NULL)
    {
        double atr = MarketAnalyzer.GetATR();
        double sl_distance = atr * ATRMultiplier;
        double tp_distance = sl_distance * RiskRewardRatio;
        
        if(signal_type == "buy")
        {
            stop_loss = entry_price - sl_distance;
            take_profit = entry_price + tp_distance;
        }
        else // sell
        {
            stop_loss = entry_price + sl_distance;
            take_profit = entry_price - tp_distance;
        }
    }
    else
    {
        // 固定点数
        double sl_points = 100;
        double tp_points = sl_points * RiskRewardRatio;
        
        if(signal_type == "buy")
        {
            stop_loss = entry_price - sl_points * point;
            take_profit = entry_price + tp_points * point;
        }
        else // sell
        {
            stop_loss = entry_price + sl_points * point;
            take_profit = entry_price - tp_points * point;
        }
    }
    
    // 验证止损止盈价格
    double stop_level = SymbolInfoInteger(TradingSymbol, SYMBOL_TRADE_STOPS_LEVEL) * point;
    
    if(signal_type == "buy")
    {
        if(stop_loss >= entry_price - stop_level)
        {
            stop_loss = entry_price - stop_level;
            LogMessage("调整止损到最小距离");
        }
        
        if(take_profit > 0 && take_profit <= entry_price + stop_level)
        {
            take_profit = entry_price + stop_level * 2;
        }
    }
    else // sell
    {
        if(stop_loss <= entry_price + stop_level)
        {
            stop_loss = entry_price + stop_level;
            LogMessage("调整止损到最小距离");
        }
        
        if(take_profit > 0 && take_profit >= entry_price - stop_level)
        {
            take_profit = entry_price - stop_level * 2;
        }
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| 交易执行函数                                                     |
//+------------------------------------------------------------------+
bool OpenPosition(string signal_type)
{
    if(!RiskManagementCheck())
    {
        LogMessage("风险管理检查未通过");
        return false;
    }
    
    if(OrderTracker.GetTotalPositions() >= MaxPositions)
    {
        LogMessage("已达到最大持仓数量限制");
        return false;
    }
    
    double volume = CalculatePositionSize(signal_type);
    if(volume <= 0)
    {
        LogMessage("计算仓位大小失败");
        return false;
    }
    
    // 获取入场价格
    double entry_price = 0;
    ENUM_ORDER_TYPE order_type;
    
    if(signal_type == "buy")
    {
        order_type = ORDER_TYPE_BUY;
        entry_price = SymbolInfoDouble(TradingSymbol, SYMBOL_ASK);
    }
    else // sell
    {
        order_type = ORDER_TYPE_SELL;
        entry_price = SymbolInfoDouble(TradingSymbol, SYMBOL_BID);
    }
    
    // 计算止损止盈
    double stop_loss = 0;
    double take_profit = 0;
    
    if(!CalculateStopLossTakeProfit(signal_type, entry_price, stop_loss, take_profit))
    {
        LogMessage("计算止损止盈失败");
        return false;
    }
    
    // 设置交易参数
    Trade.SetExpertMagicNumber(MagicNumber);
    Trade.SetDeviationInPoints(10);
    Trade.SetTypeFilling(ORDER_FILLING_FOK);
    
    // 执行交易
    if(order_type == ORDER_TYPE_BUY)
    {
        if(!Trade.Buy(volume, TradingSymbol, entry_price, stop_loss, take_profit, 
                     "AI_MultiTF_SMC_EA_Socket"))
        {
            LogMessage("买入失败，错误: " + IntegerToString(GetLastError()) + 
                      " - " + GetErrorDescription(GetLastError()));
            return false;
        }
    }
    else
    {
        if(!Trade.Sell(volume, TradingSymbol, entry_price, stop_loss, take_profit, 
                      "AI_MultiTF_SMC_EA_Socket"))
        {
            LogMessage("卖出失败，错误: " + IntegerToString(GetLastError()) + 
                      " - " + GetErrorDescription(GetLastError()));
            return false;
        }
    }
    
    LogMessage(StringFormat("成功开%s仓，价格: %.5f，止损: %.5f，止盈: %.5f，仓位: %.2f",
        signal_type, entry_price, stop_loss, take_profit, volume));
    
    // 更新订单跟踪
    OrderTracker.UpdateOrders(MagicNumber);
    
    return true;
}

bool CloseAllPositions()
{
    LogMessage("开始平仓所有持仓");
    
    bool success = true;
    int closed_count = 0;
    
    for(int i = PositionsTotal() - 1; i >= 0; i--)
    {
        ulong ticket = PositionGetTicket(i);
        if(PositionSelectByTicket(ticket))
        {
            if(PositionGetString(POSITION_SYMBOL) == TradingSymbol &&
               PositionGetInteger(POSITION_MAGIC) == MagicNumber)
            {
                Trade.SetExpertMagicNumber(MagicNumber);
                
                if(!Trade.PositionClose(ticket))
                {
                    LogMessage("平仓失败，订单号: " + IntegerToString(ticket) + 
                              "，错误: " + IntegerToString(GetLastError()));
                    success = false;
                }
                else
                {
                    closed_count++;
                    LogMessage("成功平仓，订单号: " + IntegerToString(ticket));
                }
            }
        }
    }
    
    LogMessage("平仓完成，共平仓 " + IntegerToString(closed_count) + " 个持仓");
    
    // 更新订单跟踪
    OrderTracker.UpdateOrders(MagicNumber);
    
    return success;
}

//+------------------------------------------------------------------+
//| 账户统计函数                                                     |
//+------------------------------------------------------------------+
void UpdateAccountStats()
{
    static datetime last_update = 0;
    datetime now = TimeCurrent();
    
    if(now - last_update < 1) // 每秒最多更新一次
        return;
    
    AccountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    CurrentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    // 更新峰值权益
    if(CurrentEquity > PeakEquity)
    {
        PeakEquity = CurrentEquity;
    }
    
    // 更新最大回撤
    if(PeakEquity > 0)
    {
        double drawdown = (PeakEquity - CurrentEquity) / PeakEquity * 100.0;
        if(drawdown > MaxDrawdown)
        {
            MaxDrawdown = drawdown;
        }
    }
    
    // 更新每日盈亏
    MqlDateTime current_time;
    TimeToStruct(now, current_time);
    
    if(current_time.day != LastTradeDay.day || 
       current_time.mon != LastTradeDay.mon || 
       current_time.year != LastTradeDay.year)
    {
        DailyLoss = 0.0;
        DailyProfit = 0.0;
        LastTradeDay = current_time;
        
        LogMessage("新交易日开始");
    }
    
    // 更新每日盈亏
    double today_profit = OrderTracker.GetTotalProfitToday();
    if(today_profit < 0)
    {
        DailyLoss = -today_profit;
    }
    else
    {
        DailyProfit = today_profit;
    }
    
    last_update = now;
}

void PrintStats()
{
    static datetime last_print = 0;
    datetime now = TimeCurrent();
    
    if(now - last_print < 60) // 每分钟打印一次
        return;
    
    string stats = "\n=== 账户统计 ===\n";
    stats += "账户余额: " + DoubleToString(AccountBalance, 2) + "\n";
    stats += "当前权益: " + DoubleToString(CurrentEquity, 2) + "\n";
    stats += "浮动盈亏: " + DoubleToString(CurrentEquity - AccountBalance, 2) + "\n";
    stats += "最大回撤: " + DoubleToString(MaxDrawdown, 2) + "%\n";
    stats += "当日盈利: " + DoubleToString(DailyProfit, 2) + "\n";
    stats += "当日亏损: " + DoubleToString(DailyLoss, 2) + "\n";
    stats += "连续亏损: " + IntegerToString(ConsecutiveLosses) + "\n";
    stats += "当前持仓: " + IntegerToString(OrderTracker.GetTotalPositions()) + "\n";
    stats += "=================";
    
    LogMessage(stats);
    
    last_print = now;
}

//+------------------------------------------------------------------+
//| 初始化函数                                                       |
//+------------------------------------------------------------------+
int OnInit()
{
    LogMessage("EA初始化开始");
    
    // 设置交易品种和周期
    TradingSymbol = (InputSymbol == "") ? Symbol() : InputSymbol;
    TradingTimeframe = (InputTimeframe == PERIOD_CURRENT) ? Period() : InputTimeframe;
    
    LogMessage("交易品种: " + TradingSymbol + "，周期: " + EnumToString(TradingTimeframe));
    
    // 验证交易品种
    if(!SymbolSelect(TradingSymbol, true))
    {
        LogMessage("无法选择交易品种: " + TradingSymbol);
        return INIT_FAILED;
    }
    
    // 初始化交易对象
    Trade = new CTrade();
    if(Trade == NULL)
    {
        LogMessage("创建交易对象失败");
        return INIT_FAILED;
    }
    
    // 初始化订单跟踪器
    OrderTracker = new CMyOrderTracker();
    if(OrderTracker == NULL)
    {
        LogMessage("创建订单跟踪器失败");
        delete Trade;
        return INIT_FAILED;
    }
    
    // 初始化市场分析器
    MarketAnalyzer = new CMarketAnalyzer(TradingSymbol, TradingTimeframe);
    if(MarketAnalyzer == NULL)
    {
        LogMessage("创建市场分析器失败");
        delete OrderTracker;
        delete Trade;
        return INIT_FAILED;
    }
    
    // 初始化账户统计
    AccountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    CurrentEquity = AccountBalance;
    PeakEquity = AccountBalance;
    TimeToStruct(TimeCurrent(), LastTradeDay);
    
    // 更新订单信息
    OrderTracker.UpdateOrders(MagicNumber);
    
    EA_Running = true;
    
    LogMessage("EA初始化完成");
    LogMessage("Magic Number: " + IntegerToString(MagicNumber));
    LogMessage("风险设置: " + DoubleToString(RiskPerTrade, 1) + "%/笔");
    LogMessage("最大持仓: " + IntegerToString(MaxPositions));
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| 反初始化函数                                                     |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    LogMessage("EA停止运行，原因: " + IntegerToString(reason));
    
    EA_Running = false;
    
    // 关闭所有持仓（根据设置）
    if(OrderTracker.GetTotalPositions() > 0)
    {
        LogMessage("正在关闭所有持仓...");
        CloseAllPositions();
    }
    
    // 清理对象
    if(MarketAnalyzer != NULL)
    {
        delete MarketAnalyzer;
        MarketAnalyzer = NULL;
    }
    
    if(OrderTracker != NULL)
    {
        delete OrderTracker;
        OrderTracker = NULL;
    }
    
    if(Trade != NULL)
    {
        delete Trade;
        Trade = NULL;
    }
    
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
    
    // 打印统计信息
    PrintStats();
    
    // 检查是否是新K线
    static datetime last_bar_time = 0;
    datetime current_bar_time = iTime(TradingSymbol, TradingTimeframe, 0);
    
    if(current_bar_time == last_bar_time && SignalCache.is_valid)
        return; // 同一根K线且缓存有效，不处理
    
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
        LogMessage("信号强度不足: " + IntegerToString(current_strength) + 
                  " < " + IntegerToString(MinSignalStrength));
        return;
    }
    
    // 信号确认逻辑
    if(current_signal == LastSignal && current_signal != "hold" && current_signal != "none")
    {
        SignalConfirmCount++;
    }
    else
    {
        SignalConfirmCount = 1;
        LastSignal = current_signal;
        LastSignalTime = TimeCurrent();
    }
    
    if(SignalConfirmCount < SignalConfirmations)
    {
        LogMessage("信号确认中... (" + IntegerToString(SignalConfirmCount) + 
                  "/" + IntegerToString(SignalConfirmations) + ")");
        return;
    }
    
    // 执行交易逻辑
    if(current_signal == "buy" || current_signal == "sell")
    {
        LogMessage("收到交易信号: " + current_signal + 
                  " (强度: " + IntegerToString(current_strength) + "%)");
        
        // 如果有持仓，先平仓（根据策略决定）
        if(OrderTracker.GetTotalPositions() > 0)
        {
            // 检查是否需要对冲或加仓
            // 简化处理：直接平仓开新仓
            LogMessage("检测到新信号，正在平仓...");
            CloseAllPositions();
            
            // 等待平仓完成
            Sleep(100);
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
                    LogMessage("详细分析报告:\n" + analysis_report);
                }
            }
        }
        else
        {
            LogMessage("执行" + current_signal + "信号失败");
        }
    }
    else if(current_signal == "hold" || current_signal == "none")
    {
        if(EnableLogging)
        {
            LogMessage("保持观望: " + current_analysis);
        }
        
        // 检查是否需要根据市场状态调整持仓
        if(EnableMarketRegimeDetection && MarketAnalyzer != NULL)
        {
            string regime = MarketAnalyzer.GetMarketRegime();
            if(regime == "high_volatility" && OrderTracker.GetTotalPositions() > 0)
            {
                LogMessage("高波动性市场，考虑减少风险暴露");
                // 可以考虑减仓或调整止损
            }
        }
    }
    
    // 重置信号确认计数
    SignalConfirmCount = 0;
    
    // 更新订单状态
    OrderTracker.UpdateOrders(MagicNumber);
}
//+------------------------------------------------------------------+