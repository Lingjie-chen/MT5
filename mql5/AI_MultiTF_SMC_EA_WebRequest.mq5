//+------------------------------------------------------------------+
//| AI_MultiTF_SMC_EA_WebRequest.mq5                                 |
//| Copyright 2024, AI Quant Trading                                |
//| https://github.com/ai-quant-trading                             |
//| WebRequest版本：基于HTTP通信的MQL5-Python集成（稳定版）           |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, AI Quant Trading"
#property link      "https://github.com/ai-quant-trading"
#property version   "3.1"
#property description "AI多时间框架SMC交易系统 - WebRequest通信版"
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
#include <fixed_json_functions.mqh>

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

// WebRequest连接相关结构
struct SWebRequestConnection
{
    string host;
    int port;
    datetime last_request_time;
    
    SWebRequestConnection() : host("127.0.0.1"), port(5002), last_request_time(0) {}
};

// 全局WebRequest连接对象
SWebRequestConnection WebRequestConn;

//+------------------------------------------------------------------+
//| WebRequest通信函数                                               |
//+------------------------------------------------------------------+
bool WebRequestSend(string request, string &response, int timeout_ms = 45000)
{
    // 检查是否在短时间内重复请求
    if(TimeCurrent() - WebRequestConn.last_request_time < 1)
        return false;
    
    WebRequestConn.last_request_time = TimeCurrent();
    
    // 构建URL
    string url = "http://" + WebRequestConn.host + ":" + IntegerToString(WebRequestConn.port) + "/get_signal";
    
    // 设置请求头
    string headers = "Content-Type: application/json\r\n";
    
    // 发送WebRequest
    char data[], result[];
    int len = StringToCharArray(request, data);
    
    // 移除字符串末尾的空字符（\0），避免发送额外数据导致JSON解析错误
    if(len > 0)
        ArrayResize(data, len - 1);
        
    string result_headers;
    
    int res = WebRequest("POST", url, headers, timeout_ms, data, result, result_headers);
    
    if(res == 200) // HTTP 200 OK
    {
        response = CharArrayToString(result);
        LogMessage("WebRequest成功，响应: " + response);
        return true;
    }
    else
    {
        LogMessage("WebRequest失败，错误码: " + IntegerToString(res));
        LogMessage("请求URL: " + url);
        LogMessage("请求数据: " + request);
        if(StringLen(result_headers) > 0)
            LogMessage("响应头: " + result_headers);
        if(ArraySize(result) > 0)
        {
            string result_str = CharArrayToString(result);
            if(StringLen(result_str) > 0)
                LogMessage("响应内容: " + result_str);
        }
        return false;
    }
}

//+------------------------------------------------------------------+
//| 数据验证和安全性函数                                             |
//+------------------------------------------------------------------+
bool ValidateSymbol(string symbol)
{
    // 验证交易品种格式
    if(StringLen(symbol) == 0 || StringLen(symbol) > 20)
        return false;
    
    // 检查是否包含非法字符
    string invalid_chars = "!@#$%^&*()+=[]{}|;:'\",<>/?`~\\";
    for(int i = 0; i < StringLen(invalid_chars); i++)
    {
        if(StringFind(symbol, StringSubstr(invalid_chars, i, 1)) != -1)
            return false;
    }
    
    return true;
}

bool ValidateTimeframe(ENUM_TIMEFRAMES timeframe)
{
    // 验证时间周期是否有效
    ENUM_TIMEFRAMES valid_timeframes[] = {PERIOD_M1, PERIOD_M5, PERIOD_M15, PERIOD_M30, 
                                         PERIOD_H1, PERIOD_H4, PERIOD_D1, PERIOD_W1, PERIOD_MN1};
    
    for(int i = 0; i < ArraySize(valid_timeframes); i++)
    {
        if(timeframe == valid_timeframes[i])
            return true;
    }
    
    return false;
}

bool ValidateRatesData(MqlRates &rates[], int count)
{
    // 验证K线数据完整性
    if(ArraySize(rates) != count || count < 10 || count > 1000)
        return false;
    
    for(int i = 0; i < ArraySize(rates); i++)
    {
        // 验证价格逻辑
        if(rates[i].low > rates[i].high || rates[i].low > rates[i].open || 
           rates[i].low > rates[i].close || rates[i].high < rates[i].open || 
           rates[i].high < rates[i].close)
            return false;
        
        // 验证价格范围
        if(rates[i].open <= 0 || rates[i].high <= 0 || rates[i].low <= 0 || rates[i].close <= 0)
            return false;
        
        // 验证成交量
        if(rates[i].tick_volume < 0)
            return false;
        
        // 验证时间戳
        if(rates[i].time <= 0 || rates[i].time > TimeCurrent() + 86400) // 不能超过当前时间+1天
            return false;
    }
    
    return true;
}

string SanitizeJSONString(string json_input)
{
    // 清理JSON字符串中的特殊字符
    string result = json_input;
    
    // 转义双引号
    StringReplace(result, "\"", "\\\"");
    
    // 转义反斜杠
    StringReplace(result, "\\", "\\\\");
    
    // 转义换行符
    StringReplace(result, "\n", "\\n");
    
    // 转义制表符
    StringReplace(result, "\t", "\\t");
    
    // 移除控制字符
    for(int i = 0; i < StringLen(result); i++)
    {
        ushort ch = StringGetCharacter(result, i);
        if(ch < 32 && ch != 9 && ch != 10 && ch != 13) // 保留制表符、换行符、回车符
        {
            StringSetCharacter(result, i, ' ');
        }
    }
    
    return result;
}

bool ValidateSignalResult(string signal, int strength, string analysis)
{
    // 验证信号结果的有效性
    
    // 验证信号类型 (不区分大小写)
    string upper_signal = signal;
    StringToUpper(upper_signal);
    
    string valid_signals[] = {"BUY", "SELL", "HOLD", "NONE"};
    bool signal_valid = false;
    for(int i = 0; i < ArraySize(valid_signals); i++)
    {
        if(upper_signal == valid_signals[i])
        {
            signal_valid = true;
            break;
        }
    }
    
    if(!signal_valid)
        return false;
    
    // 验证信号强度
    if(strength < 0 || strength > 100)
        return false;
    
    // 验证分析文本长度
    if(StringLen(analysis) > 1000)
        return false;
    
    return true;
}

bool ValidateJSONResponse(string response)
{
    // 验证JSON响应格式
    if(StringLen(response) == 0)
        return false;
    
    // 检查基本JSON结构
    if(StringFind(response, "{") == -1 || StringFind(response, "}") == -1)
        return false;
    
    // 检查是否包含必需字段
    if(StringFind(response, "\"signal\"") == -1)
        return false;
    
    // 检查响应长度限制（防止过大响应）
    if(StringLen(response) > 10000)
        return false;
    
    return true;
}

bool GetSignalFromWebRequest(string &signal, int &strength, string &analysis)
{
    // 验证交易品种
    if(!ValidateSymbol(TradingSymbol))
    {
        LogMessage("无效的交易品种: " + TradingSymbol);
        return false;
    }
    
    // 验证时间周期
    if(!ValidateTimeframe(TradingTimeframe))
    {
        LogMessage("无效的时间周期: " + EnumToString(TradingTimeframe));
        return false;
    }
    
    // 准备请求数据
    MqlRates rates[];
    int data_count = 100;
    if(!GetRatesData(rates, data_count))
    {
        LogMessage("获取K线数据失败");
        return false;
    }
    
    // 获取实际的rates数组大小
    int actual_rates_count = ArraySize(rates);
    LogMessage("实际获取的rates数组大小: " + IntegerToString(actual_rates_count));
    
    // 验证K线数据
    if(!ValidateRatesData(rates, actual_rates_count))
    {
        LogMessage("K线数据验证失败");
        return false;
    }
    
    // 构建请求JSON - 完全重写JSON生成逻辑，确保格式正确
    string request = "";
    
    // 直接使用交易品种名称，不进行过度转义
    string sanitized_symbol = TradingSymbol;
    
    // 转换时间周期为Python服务器期望的格式
    string timeframe_str = "H1"; // 默认H1
    if(TradingTimeframe == PERIOD_M1) timeframe_str = "M1";
    else if(TradingTimeframe == PERIOD_M5) timeframe_str = "M5";
    else if(TradingTimeframe == PERIOD_M15) timeframe_str = "M15";
    else if(TradingTimeframe == PERIOD_M30) timeframe_str = "M30";
    else if(TradingTimeframe == PERIOD_H1) timeframe_str = "H1";
    else if(TradingTimeframe == PERIOD_H4) timeframe_str = "H4";
    else if(TradingTimeframe == PERIOD_D1) timeframe_str = "D1";
    else if(TradingTimeframe == PERIOD_W1) timeframe_str = "W1";
    else if(TradingTimeframe == PERIOD_MN1) timeframe_str = "MN1";
    
    // 使用修复后的JSON生成函数，避免StringFormat的复杂性
    int rates_count = actual_rates_count;
    
    // 构建完整的JSON请求，使用新的JSON生成函数
    request = GenerateJSONRequest(sanitized_symbol, timeframe_str, rates_count, rates);
    
    // 验证JSON格式
    if(StringLen(request) < 10 || StringFind(request, "{") == -1 || StringFind(request, "}") == -1)
    {
        LogMessage("JSON格式验证失败");
        return false;
    }
    
    // 添加调试日志，记录实际生成的JSON数据（前200个字符）
    string debug_json = request;
    if(StringLen(debug_json) > 200)
        debug_json = StringSubstr(debug_json, 0, 200) + "...";
    LogMessage("生成的JSON请求: " + debug_json);
    
    // 清理JSON字符串，移除首尾空白字符和其他控制字符
    string cleaned_json = request;
    
    // 移除开头的控制字符
    while(StringLen(cleaned_json) > 0 && (cleaned_json[0] < 32 || cleaned_json[0] == 127))
        cleaned_json = StringSubstr(cleaned_json, 1);
    
    // 移除结尾的控制字符
    while(StringLen(cleaned_json) > 0 && (cleaned_json[StringLen(cleaned_json)-1] < 32 || cleaned_json[StringLen(cleaned_json)-1] == 127))
        cleaned_json = StringSubstr(cleaned_json, 0, StringLen(cleaned_json)-1);
    
    // 验证JSON格式完整性
    int first_brace = StringFind(cleaned_json, "{");
    int last_brace = StringFind(cleaned_json, "}", StringLen(cleaned_json) - 1);
    if(first_brace != 0 || last_brace != StringLen(cleaned_json) - 1)
    {
        // 如果JSON格式不完整，则尝试修复
        if(first_brace > 0)
            cleaned_json = StringSubstr(cleaned_json, first_brace);
        if(last_brace >= 0 && last_brace < StringLen(cleaned_json) - 1)
            cleaned_json = StringSubstr(cleaned_json, 0, last_brace + 1);
    }
    
    // 发送请求并获取响应
    string response;
    if(!WebRequestSend(cleaned_json, response))
    {
        LogMessage("WebRequest通信失败");
        return false;
    }
    
    // 验证响应
    if(!ValidateJSONResponse(response))
    {
        LogMessage("服务器响应格式无效");
        return false;
    }
    
    // 使用更安全的JSON解析方法
    bool success = ParseJSONResponse(response, signal, strength, analysis);
    
    if(!success)
    {
        LogMessage("JSON响应解析失败: " + response);
        return false;
    }
    
    // 验证解析结果
    if(!ValidateSignalResult(signal, strength, analysis))
    {
        LogMessage("信号结果验证失败");
        return false;
    }
    
    return true;
}

bool ParseJSONResponse(string response, string &signal, int &strength, string &analysis)
{
    // 重置输出参数
    signal = "none";
    strength = 0;
    analysis = "";
    
    // 查找信号字段
    int signal_start = StringFind(response, "\"signal\":\"");
    if(signal_start == -1) return false;
    
    signal_start += 9; // 跳过 "signal":"
    int signal_end = StringFind(response, "\"", signal_start);
    if(signal_end == -1) return false;
    
    signal = StringSubstr(response, signal_start, signal_end - signal_start);
    
    // 查找强度字段
    int strength_start = StringFind(response, "\"strength\":");
    if(strength_start == -1) return false;
    
    strength_start += 10; // 跳过 "strength":
    int strength_end = StringFind(response, ",", strength_start);
    if(strength_end == -1) strength_end = StringFind(response, "}", strength_start);
    if(strength_end == -1) return false;
    
    string strength_str = StringSubstr(response, strength_start, strength_end - strength_start);
    strength = (int)StringToInteger(strength_str);
    
    // 查找分析字段
    int analysis_start = StringFind(response, "\"analysis\":\"");
    if(analysis_start != -1)
    {
        analysis_start += 11; // 跳过 "analysis":"
        int analysis_end = StringFind(response, "\"", analysis_start);
        if(analysis_end != -1)
            analysis = StringSubstr(response, analysis_start, analysis_end - analysis_start);
    }
    
    // 验证解析结果
    if(signal == "" || strength < 0 || strength > 100)
        return false;
    
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
    };
    
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
//| PEM 引擎类                                                       |
//+------------------------------------------------------------------+
class CPEMEngine
{
private:
    string m_symbol;
    ENUM_TIMEFRAMES m_timeframe;
    int m_ma_fast_handle;
    int m_ma_slow_handle;
    int m_adx_handle;
    
    // PEM Coefficients
    double m_coeffs[7];
    
    // Trend Filter Params
    int m_ma_fast_period;
    int m_ma_slow_period;
    double m_adx_threshold;

public:
    CPEMEngine(string symbol, ENUM_TIMEFRAMES tf, int fast_ma, int slow_ma, double adx_thresh) :
        m_symbol(symbol), m_timeframe(tf), 
        m_ma_fast_period(fast_ma), m_ma_slow_period(slow_ma), m_adx_threshold(adx_thresh)
    {
        // Initialize coefficients
        m_coeffs[0] = 0.2752466;
        m_coeffs[1] = 0.01058082;
        m_coeffs[2] = 0.55162082;
        m_coeffs[3] = 0.03687016;
        m_coeffs[4] = 0.27721318;
        m_coeffs[5] = 0.1483476;
        m_coeffs[6] = 0.0008025;
        
        // Initialize indicators
        m_ma_fast_handle = iMA(m_symbol, m_timeframe, m_ma_fast_period, 0, MODE_SMA, PRICE_CLOSE);
        m_ma_slow_handle = iMA(m_symbol, m_timeframe, m_ma_slow_period, 0, MODE_SMA, PRICE_CLOSE);
        m_adx_handle = iADX(m_symbol, m_timeframe, 14);
    }
    
    ~CPEMEngine()
    {
        if(m_ma_fast_handle != INVALID_HANDLE) IndicatorRelease(m_ma_fast_handle);
        if(m_ma_slow_handle != INVALID_HANDLE) IndicatorRelease(m_ma_slow_handle);
        if(m_adx_handle != INVALID_HANDLE) IndicatorRelease(m_adx_handle);
    }
    
    void Update(string &signal, int &strength, string &analysis)
    {
        signal = "none";
        strength = 0;
        analysis = "";
        
        // 1. Calculate Prediction
        double price_t1 = iClose(m_symbol, m_timeframe, 1);
        double price_t2 = iClose(m_symbol, m_timeframe, 2);
        
        if (price_t1 == 0 || price_t2 == 0) return;
        
        double predicted_price = GetPrediction(price_t1, price_t2);
        double current_price = SymbolInfoDouble(m_symbol, SYMBOL_ASK);
        
        bool raw_buy = predicted_price > current_price;
        bool raw_sell = predicted_price < current_price;
        
        // 2. Trend Filter
        double ma_fast_val = GetIndicatorValue(m_ma_fast_handle, 0);
        double ma_slow_val = GetIndicatorValue(m_ma_slow_handle, 0);
        double adx_val = GetIndicatorValue(m_adx_handle, 0); // ADX main line
        
        bool is_strong_trend = adx_val >= m_adx_threshold;
        bool is_uptrend = ma_fast_val > ma_slow_val;
        bool is_downtrend = ma_fast_val < ma_slow_val;
        
        // 3. Final Signal
        if (raw_buy && is_strong_trend && is_uptrend)
        {
            signal = "BUY";
            strength = 75; // Trend following + Prediction
            analysis = StringFormat("PEM: Predicted %.5f > Current %.5f | Trend UP (ADX: %.1f)", 
                predicted_price, current_price, adx_val);
        }
        else if (raw_sell && is_strong_trend && is_downtrend)
        {
            signal = "SELL";
            strength = 75;
            analysis = StringFormat("PEM: Predicted %.5f < Current %.5f | Trend DOWN (ADX: %.1f)", 
                predicted_price, current_price, adx_val);
        }
    }
    
private:
    double GetPrediction(double t1, double t2)
    {
        return m_coeffs[0] * t1 +
               m_coeffs[1] * MathPow(t1, 2) +
               m_coeffs[2] * t2 +
               m_coeffs[3] * MathPow(t2, 2) +
               m_coeffs[4] * (t1 - t2) +
               m_coeffs[5] * MathSin(t1) +
               m_coeffs[6];
    }
    
    double GetIndicatorValue(int handle, int buffer_num, int index=0)
    {
        double buffer[];
        if(CopyBuffer(handle, buffer_num, index, 1, buffer) > 0)
            return buffer[0];
        return 0.0;
    }
};

//+------------------------------------------------------------------+
//| SMC 引擎类                                                       |
//+------------------------------------------------------------------+
class CSMCEngine
{
private:
    string m_symbol;
    ENUM_TIMEFRAMES m_tf; // Current TF
    
    // Sentiment Settings
    ENUM_TIMEFRAMES m_tf_htf;
    ENUM_TIMEFRAMES m_tf_ltf1;
    ENUM_TIMEFRAMES m_tf_ltf2;
    int m_ma_period;
    
    // Indicators
    int m_handle_htf;
    int m_handle_ltf1;
    int m_handle_ltf2;
    
    // Strategy Flags
    bool m_use_sentiment;
    bool m_allow_bos;
    bool m_allow_ob;
    bool m_allow_fvg;
    
    // State
    int m_current_sentiment; // 1:Bull, -1:Bear, 2:RiskOn, -2:RiskOff, 0:Neutral
    string m_sentiment_text;
    string m_active_strategy;
    datetime m_last_update;

public:
    CSMCEngine(string symbol, ENUM_TIMEFRAMES tf, 
               ENUM_TIMEFRAMES htf, ENUM_TIMEFRAMES ltf1, ENUM_TIMEFRAMES ltf2,
               int ma_period, bool use_sent, bool allow_bos, bool allow_ob, bool allow_fvg) :
        m_symbol(symbol), m_tf(tf), 
        m_tf_htf(htf), m_tf_ltf1(ltf1), m_tf_ltf2(ltf2),
        m_ma_period(ma_period), m_use_sentiment(use_sent),
        m_allow_bos(allow_bos), m_allow_ob(allow_ob), m_allow_fvg(allow_fvg)
    {
        m_handle_htf = iMA(m_symbol, m_tf_htf, m_ma_period, 0, MODE_EMA, PRICE_CLOSE);
        m_handle_ltf1 = iMA(m_symbol, m_tf_ltf1, m_ma_period, 0, MODE_EMA, PRICE_CLOSE);
        m_handle_ltf2 = iMA(m_symbol, m_tf_ltf2, m_ma_period, 0, MODE_EMA, PRICE_CLOSE);
        
        m_last_update = 0;
        m_current_sentiment = 0;
        m_sentiment_text = "Neutral";
        m_active_strategy = "OB";
    }
    
    ~CSMCEngine()
    {
        IndicatorRelease(m_handle_htf);
        IndicatorRelease(m_handle_ltf1);
        IndicatorRelease(m_handle_ltf2);
    }
    
    void Update(string &signal, int &strength, string &analysis)
    {
        signal = "none";
        strength = 0;
        analysis = "";
        
        // 1. Calculate Sentiment
        CalculateSentiment();
        
        // 2. Select Strategy
        SelectStrategy();
        
        // 3. Execute Strategy
        bool signal_found = false;
        
        // Priority based on active strategy
        if (m_active_strategy == "BOS" && m_allow_bos) {
            signal_found = DetectBOS(signal, strength, analysis);
        } else if (m_active_strategy == "FVG" && m_allow_fvg) {
            signal_found = DetectFVG(signal, strength, analysis);
        } else if (m_active_strategy == "OB" && m_allow_ob) {
            signal_found = DetectOB(signal, strength, analysis);
        }
        
        // If primary strategy yields nothing, try others with lower priority/strength
        if (!signal_found) {
            if (m_allow_fvg && DetectFVG(signal, strength, analysis)) {
                strength = 60; // Lower strength for secondary
                analysis = "Secondary FVG: " + analysis;
            } else if (m_allow_ob && DetectOB(signal, strength, analysis)) {
                strength = 60;
                analysis = "Secondary OB: " + analysis;
            }
        }
    }

private:
    void CalculateSentiment()
    {
        if (TimeCurrent() - m_last_update < 60) return;
        m_last_update = TimeCurrent();
        
        double ma_htf = GetMA(m_handle_htf);
        double price_htf = iClose(m_symbol, m_tf_htf, 0);
        
        // Bias
        int bias = 0;
        if (price_htf > ma_htf) bias = 1;
        else if (price_htf < ma_htf) bias = -1;
        
        // Structure (Simplified for performance: Check Higher Highs/Lower Lows on LTF1)
        bool bullish_structure = IsBullishStructure(m_tf_ltf1);
        bool bearish_structure = IsBearishStructure(m_tf_ltf1);
        
        // Breakout
        bool breakout = HasBreakout(m_tf_ltf1, bias);
        
        // Logic from SMC_Sent.mq5
        m_current_sentiment = 0;
        m_sentiment_text = "Neutral";
        
        if (bias == 1 && bullish_structure) { m_current_sentiment = 1; m_sentiment_text = "Bullish"; }
        else if (bias == -1 && bearish_structure) { m_current_sentiment = -1; m_sentiment_text = "Bearish"; }
        
        if (bias == 1 && breakout) { m_current_sentiment = 2; m_sentiment_text = "Risk-On"; }
        else if (bias == -1 && breakout) { m_current_sentiment = -2; m_sentiment_text = "Risk-Off"; }
    }
    
    void SelectStrategy()
    {
        if (!m_use_sentiment) {
            m_active_strategy = "ALL";
            return;
        }
        
        switch(m_current_sentiment) {
            case 1: case -1: m_active_strategy = "BOS"; break;
            case 2: case -2: m_active_strategy = "FVG"; break;
            default: m_active_strategy = "OB"; break;
        }
    }
    
    bool DetectOB(string &signal, int &strength, string &analysis)
    {
        // Check recent candles for OB pattern
        for(int i = 2; i < 10; i++) {
            // Bullish OB: Bear followed by Strong Bull
            if(iClose(m_symbol, m_tf, i) > iOpen(m_symbol, m_tf, i) && 
               iClose(m_symbol, m_tf, i+1) < iOpen(m_symbol, m_tf, i+1)) {
                
                double body_bull = MathAbs(iClose(m_symbol, m_tf, i) - iOpen(m_symbol, m_tf, i));
                double body_bear = MathAbs(iClose(m_symbol, m_tf, i+1) - iOpen(m_symbol, m_tf, i+1));
                
                if(body_bull > body_bear * 1.2) { // 1.2x engulfing
                    double ob_high = iHigh(m_symbol, m_tf, i+1);
                    double ob_low = iLow(m_symbol, m_tf, i+1);
                    double current = SymbolInfoDouble(m_symbol, SYMBOL_ASK);
                    
                    // Retest
                    if(current <= ob_high && current >= ob_low) {
                        signal = "BUY";
                        strength = 75;
                        analysis = "SMC OB: Bullish Retest (" + m_sentiment_text + ")";
                        return true;
                    }
                }
            }
            // Bearish OB
            if(iClose(m_symbol, m_tf, i) < iOpen(m_symbol, m_tf, i) && 
               iClose(m_symbol, m_tf, i+1) > iOpen(m_symbol, m_tf, i+1)) {
                
                double body_bear = MathAbs(iClose(m_symbol, m_tf, i) - iOpen(m_symbol, m_tf, i));
                double body_bull = MathAbs(iClose(m_symbol, m_tf, i+1) - iOpen(m_symbol, m_tf, i+1));
                
                if(body_bear > body_bull * 1.2) {
                    double ob_high = iHigh(m_symbol, m_tf, i+1);
                    double ob_low = iLow(m_symbol, m_tf, i+1);
                    double current = SymbolInfoDouble(m_symbol, SYMBOL_BID);
                    
                    if(current >= ob_low && current <= ob_high) {
                        signal = "SELL";
                        strength = 75;
                        analysis = "SMC OB: Bearish Retest (" + m_sentiment_text + ")";
                        return true;
                    }
                }
            }
        }
        return false;
    }
    
    bool DetectFVG(string &signal, int &strength, string &analysis)
    {
        // Check recent candles for FVG
        for(int i = 1; i < 5; i++) {
            // Bullish FVG: Low[i] > High[i+2]
            double low_i = iLow(m_symbol, m_tf, i);
            double high_i2 = iHigh(m_symbol, m_tf, i+2);
            
            if (low_i > high_i2) {
                double current = SymbolInfoDouble(m_symbol, SYMBOL_ASK);
                // Retest
                if (current <= low_i && current >= high_i2) {
                    signal = "BUY";
                    strength = 85;
                    analysis = "SMC FVG: Bullish Retest (" + m_sentiment_text + ")";
                    return true;
                }
            }
            
            // Bearish FVG: High[i] < Low[i+2]
            double high_i = iHigh(m_symbol, m_tf, i);
            double low_i2 = iLow(m_symbol, m_tf, i+2);
            
            if (high_i < low_i2) {
                double current = SymbolInfoDouble(m_symbol, SYMBOL_BID);
                if (current >= high_i && current <= low_i2) {
                    signal = "SELL";
                    strength = 85;
                    analysis = "SMC FVG: Bearish Retest (" + m_sentiment_text + ")";
                    return true;
                }
            }
        }
        return false;
    }
    
    bool DetectBOS(string &signal, int &strength, string &analysis)
    {
        // Simple 5-bar Fractal BOS
        int high_idx = iHighest(m_symbol, m_tf, MODE_HIGH, 20, 1);
        int low_idx = iLowest(m_symbol, m_tf, MODE_LOW, 20, 1);
        
        if (high_idx < 0 || low_idx < 0) return false;
        
        double swing_high = iHigh(m_symbol, m_tf, high_idx);
        double swing_low = iLow(m_symbol, m_tf, low_idx);
        double current = iClose(m_symbol, m_tf, 0);
        
        if (current > swing_high) {
            signal = "BUY";
            strength = 80;
            analysis = "SMC BOS: Breakout Up (" + m_sentiment_text + ")";
            return true;
        }
        
        if (current < swing_low) {
            signal = "SELL";
            strength = 80;
            analysis = "SMC BOS: Breakout Down (" + m_sentiment_text + ")";
            return true;
        }
        
        return false;
    }

    // Helpers
    double GetMA(int handle) {
        double buf[1];
        if(CopyBuffer(handle, 0, 0, 1, buf) > 0) return buf[0];
        return 0;
    }
    
    bool IsBullishStructure(ENUM_TIMEFRAMES tf) {
        // Higher Highs & Higher Lows logic simplified
        double h1 = iHigh(m_symbol, tf, iHighest(m_symbol, tf, MODE_HIGH, 10, 1));
        double h2 = iHigh(m_symbol, tf, iHighest(m_symbol, tf, MODE_HIGH, 10, 11));
        double l1 = iLow(m_symbol, tf, iLowest(m_symbol, tf, MODE_LOW, 10, 1));
        double l2 = iLow(m_symbol, tf, iLowest(m_symbol, tf, MODE_LOW, 10, 11));
        return (h1 > h2 && l1 > l2);
    }
    
    bool IsBearishStructure(ENUM_TIMEFRAMES tf) {
        double h1 = iHigh(m_symbol, tf, iHighest(m_symbol, tf, MODE_HIGH, 10, 1));
        double h2 = iHigh(m_symbol, tf, iHighest(m_symbol, tf, MODE_HIGH, 10, 11));
        double l1 = iLow(m_symbol, tf, iLowest(m_symbol, tf, MODE_LOW, 10, 1));
        double l2 = iLow(m_symbol, tf, iLowest(m_symbol, tf, MODE_LOW, 10, 11));
        return (h1 < h2 && l1 < l2);
    }
    
    bool HasBreakout(ENUM_TIMEFRAMES tf, int bias) {
        double current = iClose(m_symbol, tf, 0);
        if (bias == 1) {
            double h = iHigh(m_symbol, tf, iHighest(m_symbol, tf, MODE_HIGH, 10, 1));
            return current > h;
        } else if (bias == -1) {
            double l = iLow(m_symbol, tf, iLowest(m_symbol, tf, MODE_LOW, 10, 1));
            return current < l;
        }
        return false;
    }
};

//+------------------------------------------------------------------+
//| MTF 引擎类                                                       |
//+------------------------------------------------------------------+
class CMTFEngine
{
private:
    string m_symbol;
    ENUM_TIMEFRAMES m_htf1;
    ENUM_TIMEFRAMES m_htf2;
    int m_swing_length;
    
    double m_demand_zones[]; // [top, bottom, top, bottom...]
    double m_supply_zones[];
    int m_demand_count;
    int m_supply_count;
    
    int m_atr_handle;
    datetime m_last_zone_update;
    
public:
    CMTFEngine(string symbol, ENUM_TIMEFRAMES htf1, ENUM_TIMEFRAMES htf2, int swing_len) : 
        m_symbol(symbol), m_htf1(htf1), m_htf2(htf2), m_swing_length(swing_len)
    {
        m_demand_count = 0;
        m_supply_count = 0;
        ArrayResize(m_demand_zones, 200); // Max 100 zones
        ArrayResize(m_supply_zones, 200);
        m_atr_handle = iATR(m_symbol, Period(), 14);
        m_last_zone_update = 0;
    }
    
    ~CMTFEngine()
    {
        if(m_atr_handle != INVALID_HANDLE) IndicatorRelease(m_atr_handle);
    }
    
    void Update(string &signal, int &strength, string &analysis)
    {
        signal = "none";
        strength = 0;
        analysis = "";
        
        // 1. MTF Alignment
        // HTF1 & HTF2 必须同向 (上一根已完成K线)
        int dir_htf1 = GetCandleDirection(m_htf1, 1);
        int dir_htf2 = GetCandleDirection(m_htf2, 1);
        
        // 当前周期K线也最好同向，或者是刚开始
        int dir_curr = GetCandleDirection(Period(), 0);
        
        int confirmed_dir = 0;
        if (dir_htf1 == dir_htf2 && dir_htf1 != 0) {
            // 如果当前K线反向，则暂时观望，除非它很弱
            if (dir_curr == 0 || dir_curr == dir_htf1) {
                confirmed_dir = dir_htf1;
            }
        }
        
        if (confirmed_dir == 0) return;
        
        // 2. Zone Check (Supply/Demand)
        UpdateZones();
        double current_price = SymbolInfoDouble(m_symbol, SYMBOL_BID);
        bool in_demand = IsInZone(current_price, true);
        bool in_supply = IsInZone(current_price, false);
        
        // 3. Signal Generation
        if (confirmed_dir > 0) { // Bullish
            if (in_supply) {
                // 多头趋势但撞上供给区 -> 风险
                return;
            }
            
            signal = "BUY";
            strength = 70;
            string zone_info = "";
            
            if (in_demand) {
                strength = 85; // 在需求区获得支撑 -> 强信号
                zone_info = " (In Demand Zone)";
            }
            
            analysis = StringFormat("MTF: Bullish Alignment [%s=%s, %s=%s]%s", 
                EnumToString(m_htf1), "UP", EnumToString(m_htf2), "UP", zone_info);
                
        } else { // Bearish
            if (in_demand) {
                // 空头趋势但撞上需求区 -> 风险
                return;
            }
            
            signal = "SELL";
            strength = 70;
            string zone_info = "";
            
            if (in_supply) {
                strength = 85; // 在供给区受阻 -> 强信号
                zone_info = " (In Supply Zone)";
            }
            
            analysis = StringFormat("MTF: Bearish Alignment [%s=%s, %s=%s]%s", 
                EnumToString(m_htf1), "DOWN", EnumToString(m_htf2), "DOWN", zone_info);
        }
    }
    
private:
    int GetCandleDirection(ENUM_TIMEFRAMES tf, int index)
    {
        double open = iOpen(m_symbol, tf, index);
        double close = iClose(m_symbol, tf, index);
        if (close > open) return 1;
        if (close < open) return -1;
        return 0;
    }
    
    void UpdateZones()
    {
        // 仅在新K线时更新，或每隔一段时间更新
        datetime current_bar_time = iTime(m_symbol, Period(), 0);
        if (current_bar_time == m_last_zone_update) return;
        m_last_zone_update = current_bar_time;
        
        // 获取ATR用于计算区域宽度
        double atr_values[1];
        if(CopyBuffer(m_atr_handle, 0, 0, 1, atr_values) != 1) return;
        double atr = atr_values[0];
        double box_width = atr * 1.0; // 默认 Box_Width = 1.0
        
        m_demand_count = 0;
        m_supply_count = 0;
        
        int bars = MathMin(500, Bars(m_symbol, Period())); // 扫描最近500根
        int swing_len = m_swing_length;
        
        // 简化的 Swing 检测
        for(int i = swing_len; i < bars - swing_len; i++)
        {
            // Swing Low (Demand)
            bool is_swing_low = true;
            double low_i = iLow(m_symbol, Period(), i);
            
            for(int j = 1; j <= swing_len; j++) {
                if(low_i >= iLow(m_symbol, Period(), i - j) || low_i >= iLow(m_symbol, Period(), i + j)) {
                    is_swing_low = false; break;
                }
            }
            
            if(is_swing_low && m_demand_count < 50) {
                // 添加 Demand Zone
                double bottom = low_i;
                double top = bottom + box_width;
                // 检查重叠 (简单跳过)
                m_demand_zones[m_demand_count * 2] = top;
                m_demand_zones[m_demand_count * 2 + 1] = bottom;
                m_demand_count++;
            }
            
            // Swing High (Supply)
            bool is_swing_high = true;
            double high_i = iHigh(m_symbol, Period(), i);
            
            for(int j = 1; j <= swing_len; j++) {
                if(high_i <= iHigh(m_symbol, Period(), i - j) || high_i <= iHigh(m_symbol, Period(), i + j)) {
                    is_swing_high = false; break;
                }
            }
            
            if(is_swing_high && m_supply_count < 50) {
                // 添加 Supply Zone
                double top = high_i;
                double bottom = top - box_width;
                m_supply_zones[m_supply_count * 2] = top;
                m_supply_zones[m_supply_count * 2 + 1] = bottom;
                m_supply_count++;
            }
        }
    }
    
    bool IsInZone(double price, bool check_demand)
    {
        double tolerance = 50 * Point(); // Zone_Tolerance_Points
        
        if (check_demand) {
            for(int i = 0; i < m_demand_count; i++) {
                double top = m_demand_zones[i * 2];
                double bottom = m_demand_zones[i * 2 + 1];
                if (price >= (bottom - tolerance) && price <= (top + tolerance)) return true;
            }
        } else {
            for(int i = 0; i < m_supply_count; i++) {
                double top = m_supply_zones[i * 2];
                double bottom = m_supply_zones[i * 2 + 1];
                if (price >= (bottom - tolerance) && price <= (top + tolerance)) return true;
            }
        }
        return false;
    }
};

//+------------------------------------------------------------------+
//| CRT 引擎类                                                       |
//+------------------------------------------------------------------+
class CCRTEngine
{
private:
    string m_symbol;
    ENUM_TIMEFRAMES m_range_tf;
    ENUM_TIMEFRAMES m_confirm_tf;
    
    // CRT 状态变量
    datetime m_prev_range_time;
    double   m_range_high;
    double   m_range_low;
    bool     m_is_positive_direction; // true=多头(上一根收盘>开盘), false=空头
    bool     m_range_broken;
    double   m_breakout_point;
    bool     m_signal_generated;
    datetime m_breakout_time;
    datetime m_last_confirm_time;
    
    // 图形对象名称前缀
    string   m_obj_prefix;

public:
    CCRTEngine(string symbol, ENUM_TIMEFRAMES range_tf, ENUM_TIMEFRAMES confirm_tf) : 
        m_symbol(symbol), m_range_tf(range_tf), m_confirm_tf(confirm_tf)
    {
        m_prev_range_time = 0;
        m_range_high = 0.0;
        m_range_low = 0.0;
        m_is_positive_direction = false;
        m_range_broken = false;
        m_breakout_point = 0.0;
        m_signal_generated = false;
        m_breakout_time = 0;
        m_last_confirm_time = 0;
        m_obj_prefix = "CRT_";
    }
    
    ~CCRTEngine()
    {
        // 清理图形对象
        ObjectsDeleteAll(ChartID(), m_obj_prefix);
    }
    
    // 主更新函数，返回信号
    // signal: "BUY", "SELL", "NONE"
    // strength: 0-100
    // analysis: 分析描述
    void Update(string &signal, int &strength, string &analysis)
    {
        signal = "none";
        strength = 0;
        analysis = "";
        
        datetime current_range_time = iTime(m_symbol, m_range_tf, 0);
        double current_bid = SymbolInfoDouble(m_symbol, SYMBOL_BID);
        
        // 1. 检测新区间形成
        if (current_range_time != m_prev_range_time) {
            ProcessNewRange(current_range_time);
        }
        
        // 如果区间未定义则返回
        if (m_range_high == 0.0 || m_range_low == 0.0) return;
        
        // 2. 检测区间突破 (操纵阶段)
        CheckBreakout(current_bid);
        
        // 3. 处理交易信号
        if (m_range_broken && !m_signal_generated) {
            if (CheckSignal(current_bid, signal, strength, analysis)) {
                m_signal_generated = true; // 标记该区间已产生信号，避免重复
                
                // 绘制信号图形
                DrawSignalGraphics(signal == "BUY");
            }
        }
    }
    
private:
    void ProcessNewRange(datetime new_range_time)
    {
        m_prev_range_time = new_range_time;
        
        // 获取前一区间蜡烛数据 (Range TF 的上一根K线)
        double prev_high = iHigh(m_symbol, m_range_tf, 1);
        double prev_low = iLow(m_symbol, m_range_tf, 1);
        double prev_open = iOpen(m_symbol, m_range_tf, 1);
        double prev_close = iClose(m_symbol, m_range_tf, 1);
        
        m_range_high = prev_high;
        m_range_low = prev_low;
        m_is_positive_direction = (prev_close > prev_open);
        
        // 重置状态
        m_range_broken = false;
        // 初始突破点：如果是多头方向，关注下方突破；如果是空头方向，关注上方突破
        m_breakout_point = m_is_positive_direction ? m_range_low : m_range_high;
        m_signal_generated = false;
        m_breakout_time = 0;
        m_last_confirm_time = 0;
        
        // 绘制区间
        DrawRange();
    }
    
    void CheckBreakout(double current_price)
    {
        // 优化：不仅检查当前价格，还检查最近K线的极值，以防漏掉快速插针（Wick）
        // 这使得策略在 RunOnNewBarOnly=true 时也能正常工作
        double low0 = iLow(m_symbol, m_confirm_tf, 0);
        double high0 = iHigh(m_symbol, m_confirm_tf, 0);
        double low1 = iLow(m_symbol, m_confirm_tf, 1);
        double high1 = iHigh(m_symbol, m_confirm_tf, 1);
        
        if (low0 == 0 || high0 == 0 || low1 == 0 || high1 == 0) return;

        // 获取检测范围内的极值
        double check_low = MathMin(low0, low1);
        double check_high = MathMax(high0, high1);
        
        // 使用更极端的低点/高点来判断是否突破
        if (m_is_positive_direction && check_low <= m_range_low) {
            // 多头区间，价格跌破最低价 -> 潜在操纵
            if (!m_range_broken) {
                m_range_broken = true;
                m_breakout_time = TimeCurrent();
            }
            // 更新最低点 (最大操纵深度)
            m_breakout_point = MathMin(m_breakout_point, check_low);
            
        } else if (!m_is_positive_direction && check_high >= m_range_high) {
            // 空头区间，价格突破最高价 -> 潜在操纵
            if (!m_range_broken) {
                m_range_broken = true;
                m_breakout_time = TimeCurrent();
            }
            // 更新最高点 (最大操纵深度)
            m_breakout_point = MathMax(m_breakout_point, check_high);
        }
    }
    
    bool CheckSignal(double current_price, string &signal, int &strength, string &analysis)
    {
        // 1. 检查反转确认 (价格是否回到区间内)
        if (!CheckReversalConfirmation()) return false;
        
        // 2. 检查操纵深度
        if (!CheckManipulationDepth()) return false;
        
        // 3. 生成信号
        if (m_is_positive_direction && current_price > m_range_low) {
            // 多头区间 + 跌破后回升 -> 买入
            signal = "BUY";
            strength = 80; // CRT 信号通常较强
            analysis = StringFormat("CRT: 多头区间操纵确认. 区间范围 [%.5f - %.5f], 操纵低点 %.5f", 
                                  m_range_low, m_range_high, m_breakout_point);
            return true;
        } else if (!m_is_positive_direction && current_price < m_range_high) {
            // 空头区间 + 突破后回落 -> 卖出
            signal = "SELL";
            strength = 80;
            analysis = StringFormat("CRT: 空头区间操纵确认. 区间范围 [%.5f - %.5f], 操纵高点 %.5f", 
                                  m_range_low, m_range_high, m_breakout_point);
            return true;
        }
        
        return false;
    }
    
    bool CheckReversalConfirmation()
    {
        if (CRTConfirmBars == 0) return true;
        
        datetime current_confirm_time = iTime(m_symbol, m_confirm_tf, 0);
        
        // 只在确认K线收盘时检查(或者每根新确认K线检查一次)
        // 这里逻辑简化：检查过去 N 根确认K线的收盘价
        
        // 我们需要确保至少有一根K线收盘在区间内
        // 注意：原版逻辑是"等待N根K线收盘在区间内"。
        
        // 简单的实现：检查最近 CRTConfirmBars 根K线是否都满足条件
        // 但原版是"累计计数"，这里我们简化为：只要最近一根K线收盘回到区间，且这是新的确认周期
        
        if (current_confirm_time == m_last_confirm_time) return false; // 当前K线已检查过
        
        // 检查最近 CRTConfirmBars 根已完成的K线 (从索引1开始)
        int confirm_count = 0;
        for (int i = 1; i <= CRTConfirmBars; i++) {
            double close = iClose(m_symbol, m_confirm_tf, i);
            if (m_is_positive_direction && close > m_range_low) {
                confirm_count++;
            } else if (!m_is_positive_direction && close < m_range_high) {
                confirm_count++;
            }
        }
        
        if (confirm_count >= CRTConfirmBars) {
            m_last_confirm_time = current_confirm_time;
            return true;
        }
        
        return false;
    }
    
    bool CheckManipulationDepth()
    {
        if (!CRTUseManipulationFilter) return true;
        
        double range_size = m_range_high - m_range_low;
        if (range_size == 0) return false;
        
        double manipulation_depth = m_is_positive_direction ? (m_range_low - m_breakout_point) : (m_breakout_point - m_range_high);
        double manipulation_percent = (manipulation_depth / range_size) * 100.0;
        
        return (manipulation_percent >= CRTMinManipulationPercent);
    }
    
    // --- 图形绘制辅助函数 ---
    void DrawRange()
    {
        // 绘制区间矩形
        string name = m_obj_prefix + "Range_" + TimeToString(m_prev_range_time);
        datetime start_time = iTime(m_symbol, m_range_tf, 1);
        datetime end_time = m_prev_range_time;
        
        color rect_color = m_is_positive_direction ? clrLightGreen : clrLightPink;
        
        if (ObjectFind(ChartID(), name) < 0) {
            ObjectCreate(ChartID(), name, OBJ_RECTANGLE, 0, start_time, m_range_high, end_time, m_range_low);
            ObjectSetInteger(ChartID(), name, OBJPROP_COLOR, rect_color);
            ObjectSetInteger(ChartID(), name, OBJPROP_FILL, true);
            ObjectSetInteger(ChartID(), name, OBJPROP_BACK, true);
        }
    }
    
    void DrawSignalGraphics(bool is_buy)
    {
        string suffix = TimeToString(TimeCurrent());
        
        // 绘制操纵矩形
        string manip_name = m_obj_prefix + "Manip_" + suffix;
        double range_edge = is_buy ? m_range_low : m_range_high;
        
        ObjectCreate(ChartID(), manip_name, OBJ_RECTANGLE, 0, m_prev_range_time, range_edge, TimeCurrent(), m_breakout_point);
        ObjectSetInteger(ChartID(), manip_name, OBJPROP_COLOR, clrOrange);
        ObjectSetInteger(ChartID(), manip_name, OBJPROP_STYLE, STYLE_DOT);
        
        // 绘制箭头
        string arrow_name = m_obj_prefix + "Arrow_" + suffix;
        ObjectCreate(ChartID(), arrow_name, OBJ_ARROW, 0, TimeCurrent(), m_breakout_point);
        ObjectSetInteger(ChartID(), arrow_name, OBJPROP_ARROWCODE, is_buy ? 233 : 234);
        ObjectSetInteger(ChartID(), arrow_name, OBJPROP_COLOR, is_buy ? clrBlue : clrRed);
        ObjectSetInteger(ChartID(), arrow_name, OBJPROP_WIDTH, 2);
    }
};

//+------------------------------------------------------------------+
//| EA输入参数                                                       |
//+------------------------------------------------------------------+
input group "=== 基本设置 ==="
input string InputSymbol = "";                    // 交易品种（空值使用当前图表）
input ENUM_TIMEFRAMES InputTimeframe = PERIOD_CURRENT; // 交易周期
input string ServerIP = "127.0.0.1";              // AI服务器IP地址
input int ServerPort = 5002;                      // AI服务器端口

input group "=== Telegram通知设置 ==="
input bool    InpEnableTelegram    = true;                         // 启用Telegram通知
input string  InpTelegramToken     = "8253887074:AAE_o7hfEb6iJCZ2MdVIezOC_E0OnTCvCzY"; // Telegram Bot Token
input string  InpTelegramChatID    = "5254086791";                           // Telegram Chat ID

input group "=== 资金管理 ==="
input double RiskPerTrade = 10.0;                  // 每笔交易风险百分比 (0.1-5)
input double MaxDailyLoss = 15.0;                  // 每日最大亏损百分比 (0.5-10)
input double MaxTotalRisk = 30.0;                  // 总风险百分比 (1-15)
input int MaxPositions = 10;                       // 最大持仓数量 (1-10)
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

input group "=== 性能优化 ==="
input bool RunOnNewBarOnly = true;                // 仅在新K线开启时运行
input bool EnableLocalFilter = false;             // 启用本地预过滤(减少API调用)
input int LocalRSIThreshold = 30;                 // 本地过滤RSI阈值 (30表示 <30 或 >70 触发)

input group "=== CRT 策略设置 ==="
input bool            EnableCRT = true;                          // 启用CRT策略
input ENUM_TIMEFRAMES CRTRangeTimeframe = PERIOD_H4;             // CRT区间时间框
input bool            CRTUseManipulationFilter = true;           // 使用操纵深度过滤
input double          CRTMinManipulationPercent = 5.0;           // 最小操纵百分比
input int             CRTConfirmBars = 1;                        // 反转确认K线数
input double          CRTDistributionProjection = 50.0;          // 分布投影百分比

input group "=== MTF 策略设置 ==="
input bool            EnableMTF = true;                          // 启用MTF策略
input ENUM_TIMEFRAMES MTF_HTF1 = PERIOD_H1;                      // 高级时间框1
input ENUM_TIMEFRAMES MTF_HTF2 = PERIOD_H4;                      // 高级时间框2
input int             MTF_SwingLength = 20;                      // 供需区Swing长度

input group "=== PEM 策略设置 ==="
input bool            EnablePEM = true;                          // 启用PEM策略
input int             PEM_MA_Fast = 108;                         // 快速均线周期
input int             PEM_MA_Slow = 60;                          // 慢速均线周期
input double          PEM_ADX_Threshold = 20.0;                  // ADX 阈值

input group "=== SMC 策略设置 ==="
input bool            EnableSMC = true;                          // 启用SMC策略
input ENUM_TIMEFRAMES SMC_HTF = PERIOD_H4;                       // 情绪分析HTF
input ENUM_TIMEFRAMES SMC_LTF1 = PERIOD_H1;                      // 情绪分析LTF1
input ENUM_TIMEFRAMES SMC_LTF2 = PERIOD_M30;                     // 情绪分析LTF2
input int             SMC_MA_Period = 200;                       // 情绪MA周期
input bool            SMC_UseSentiment = true;                   // 使用情绪过滤
input bool            SMC_AllowBOS = true;                       // 允许BOS策略
input bool            SMC_AllowOB = true;                        // 允许OB策略
input bool            SMC_AllowFVG = true;                       // 允许FVG策略

//+------------------------------------------------------------------+
//| 全局变量                                                         |
//+------------------------------------------------------------------+
string TradingSymbol;                             // 实际使用的交易品种
ENUM_TIMEFRAMES TradingTimeframe;                 // 实际使用的交易周期
bool EA_Running = false;                          // EA运行状态
datetime LastBarTime = 0;                         // 上一次K线时间

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
CCRTEngine*      CRTEngine      = NULL;           // CRT引擎
CMTFEngine*      MTFEngine      = NULL;           // MTF引擎
CPEMEngine*      PEMEngine      = NULL;           // PEM引擎
CSMCEngine*      SMCEngine      = NULL;           // SMC引擎
CMyOrderTracker* OrderTracker   = NULL;           // 订单跟踪器
CTrade*          Trade          = NULL;           // 交易对象

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
        case 64:    return "账户被禁用";
        case 65:    return "无效的账户";
        case 128:   return "交易超时";
        case 129:   return "无效的价格";
        case 130:   return "无效的止损";
        case 131:   return "无效的交易量";
        case 132:   return "市场已关闭";
        case 133:   return "交易被禁用";
        case 134:   return "资金不足";
        case 135:   return "价格已变化";
        case 136:   return "没有报价";
        case 137:   return "经纪人繁忙";
        case 138:   return "重新报价";
        case 139:   return "订单被经纪人锁定";
        case 140:   return "只允许买入";
        case 141:   return "交易请求过多";
        case 145:   return "交易被经纪人修改";
        case 146:   return "交易上下文繁忙";
        case 147:   return "过期交易品种";
        case 148:   return "交易品种过多";
        case 149:   return "挂单过多";
        case 150:   return "交易模式被禁止";
        case 151:   return "挂单被禁止";
        case 152:   return "交易量过小";
        case 153:   return "交易量过大";
        case 154:   return "交易量步长错误";
        case 155:   return "交易量过多";
        case 156:   return "交易被禁止";
        case 157:   return "交易模式被禁止";
        case 158:   return "挂单被禁止";
        case 159:   return "交易量过小";
        case 160:   return "交易量过大";
        case 161:   return "交易量步长错误";
        case 162:   return "交易量过多";
        case 4000:  return "没有错误";
        case 4001:  return "错误";
        case 4002:  return "无效的参数";
        case 4003:  return "服务器错误";
        case 4004:  return "错误的值";
        case 4005:  return "错误的版本";
        case 4006:  return "网络错误";
        case 4007:  return "未知的用户";
        case 4008:  return "用户超时";
        case 4009:  return "用户被禁止";
        case 4010:  return "内部错误";
        case 4011:  return "数据错误";
        case 4012:  return "请求过多";
        case 4013:  return "无效的请求";
        case 4014:  return "无效的方法";
        case 4015:  return "拒绝访问";
        case 4016:  return "无效的来源";
        case 4752:  return "EA交易被禁止 (请在工具栏开启'算法交易')";
        case 4756:  return "交易请求发送失败";
        default:    return "未知错误 (" + IntegerToString(error_code) + ")";
    }
}

//+------------------------------------------------------------------+
//| 发送Telegram消息                                                  |
//+------------------------------------------------------------------+
void SendTelegramMessage(string message)
{
    if(!InpEnableTelegram)
        return;
        
    string url = "https://api.telegram.org/bot" + InpTelegramToken + "/sendMessage";
    
    // 转义消息中的特殊字符
    string escaped_message = message;
    StringReplace(escaped_message, "\"", "\\\"");
    StringReplace(escaped_message, "\n", "\\n");
    StringReplace(escaped_message, "\t", "\\t");
    
    // 构建JSON payload
    string payload = "{\"chat_id\": \"" + InpTelegramChatID + "\", \"text\": \"" + escaped_message + "\"}";
    
    char data[];
    int len = StringToCharArray(payload, data);
    if(len > 0)
        ArrayResize(data, len - 1);
        
    string headers = "Content-Type: application/json\r\n";
    char result[];
    string result_headers;
    
    // 发送请求
    int res = WebRequest("POST", url, headers, 3000, data, result, result_headers);
    
    if(res != 200)
    {
        // 避免无限递归日志
        Print("Telegram发送失败, 错误码: ", res);
    }
}

bool GetRatesData(MqlRates &rates[], int count)
{
    ArraySetAsSeries(rates, true);
    int copied = CopyRates(_Symbol, _Period, 0, count, rates);
    
    // 记录实际复制的数据条数
    LogMessage("请求数据条数: " + IntegerToString(count) + ", 实际复制条数: " + IntegerToString(copied));
    
    // 如果复制的数据少于请求的数据，检查是否至少复制了最小需要的数据量
    if(copied < 10) // 最小需要10条数据
    {
        LogMessage("获取的K线数据不足，最少需要10条");
        return false;
    }
    
    // 如果复制的数据少于请求的数据，调整count参数以匹配实际数据
    if(copied < count)
    {
        LogMessage("调整请求的数据条数从 " + IntegerToString(count) + " 到 " + IntegerToString(copied));
        // 注意：这里我们不需要做任何事情，因为我们将使用实际的数组大小
    }
    
    return (copied >= 10); // 至少要有10条数据
}


//+------------------------------------------------------------------+
//| 检查交易时间是否允许                                              |
//+------------------------------------------------------------------+
bool IsTradingAllowed()
{
    if(!EnableTradingHours)
        return true;
    
    MqlDateTime time;
    TimeToStruct(TimeCurrent(), time);
    
    // 检查周末
    if(SkipWeekend && (time.day_of_week == 0 || time.day_of_week == 6))
        return false;
    
    // 检查交易时间
    if(time.hour < TradingStartHour || time.hour > TradingEndHour)
        return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| 检查风险管理是否允许                                              |
//+------------------------------------------------------------------+
bool IsRiskManagementAllowed()
{
    if(!EnableRiskManagement)
        return true;
    
    // 检查每日亏损限制
    double daily_pnl = OrderTracker.GetTotalProfitToday();
    if(daily_pnl < 0 && MathAbs(daily_pnl) > AccountBalance * MaxDailyLoss / 100.0)
    {
        LogMessage("达到每日亏损限制，停止交易");
        return false;
    }
    
    // 检查总风险限制
    double total_pnl = OrderTracker.GetTotalProfit();
    if(total_pnl < 0 && MathAbs(total_pnl) > AccountBalance * MaxTotalRisk / 100.0)
    {
        LogMessage("达到总风险限制，停止交易");
        return false;
    }
    
    // 检查连续亏损
    if(ConsecutiveLosses >= MaxConsecutiveLosses)
    {
        LogMessage("达到最大连续亏损次数，停止交易");
        return false;
    }
    
    // 检查最大持仓数量
    if(OrderTracker.GetTotalPositions() >= MaxPositions)
        return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| 处理AI信号                                                       |
//+------------------------------------------------------------------+
void ProcessSignal(string signal, int strength, string analysis)
{
    // 检查信号强度
    if(strength < MinSignalStrength)
    {
        LogMessage("信号强度不足: " + signal + " (强度: " + IntegerToString(strength) + ")");
        return;
    }
    
    // 信号确认逻辑
    if(signal == LastSignal && TimeCurrent() - LastSignalTime < SignalCacheTime)
    {
        SignalConfirmCount++;
    }
    else
    {
        SignalConfirmCount = 1;
        LastSignal = signal;
        LastSignalTime = TimeCurrent();
    }
    
    // 需要足够的确认次数
    if(SignalConfirmCount < SignalConfirmations)
    {
        LogMessage("信号确认中: " + signal + " (确认: " + IntegerToString(SignalConfirmCount) + "/" + 
                  IntegerToString(SignalConfirmations) + ")");
        return;
    }
    
    // 更新信号缓存
    SignalCache.signal = signal;
    SignalCache.strength = strength;
    SignalCache.analysis = analysis;
    SignalCache.timestamp = TimeCurrent();
    SignalCache.is_valid = true;
    
    LogMessage("AI信号确认: " + signal + " (强度: " + IntegerToString(strength) + ", 分析: " + analysis + ")");
    
    // 执行交易
    ExecuteTrade(signal, strength);
}

//+------------------------------------------------------------------+
//| 使用本地分析                                                     |
//+------------------------------------------------------------------+
void UseLocalAnalysis()
{
    string signal = "none";
    int strength = 0;
    string analysis = "";

    // 1. 尝试使用 CRT 策略
    if (EnableCRT && CRTEngine != NULL)
    {
        CRTEngine.Update(signal, strength, analysis);
        if (signal != "none")
        {
            ProcessSignal(signal, strength, analysis);
            return; // CRT 产生信号则直接返回
        }
    }

    // 2. 尝试使用 MTF 策略
    if (EnableMTF && MTFEngine != NULL)
    {
        MTFEngine.Update(signal, strength, analysis);
        if (signal != "none")
        {
            ProcessSignal(signal, strength, analysis);
            return; // MTF 产生信号则直接返回
        }
    }

    // 3. 尝试使用 PEM 策略
    if (EnablePEM && PEMEngine != NULL)
    {
        PEMEngine.Update(signal, strength, analysis);
        if (signal != "none")
        {
            ProcessSignal(signal, strength, analysis);
            return; // PEM 产生信号则直接返回
        }
    }

    // 4. 尝试使用 SMC 策略
    if (EnableSMC && SMCEngine != NULL)
    {
        SMCEngine.Update(signal, strength, analysis);
        if (signal != "none")
        {
            ProcessSignal(signal, strength, analysis);
            return; // SMC 产生信号则直接返回
        }
    }

    if(!EnableAdvancedAnalysis)
        return;
    
    // 获取市场状态
    string market_regime = MarketAnalyzer.GetMarketRegime();
    double rsi = MarketAnalyzer.GetRSI();
    double atr = MarketAnalyzer.GetATR();
    
    signal = "none";
    strength = 50;
    
    // 简单的本地分析逻辑
    if(rsi > 70 && market_regime == "overbought")
    {
        signal = "sell";
        strength = 65;
    }
    else if(rsi < 30 && market_regime == "oversold")
    {
        signal = "buy";
        strength = 65;
    }
    
    if(signal != "none")
    {
        ProcessSignal(signal, strength, "本地分析 - RSI: " + DoubleToString(rsi, 1) + ", 市场状态: " + market_regime);
    }
}

//+------------------------------------------------------------------+
//| 执行交易                                                         |
//+------------------------------------------------------------------+
void ExecuteTrade(string signal, int strength)
{
    // 获取当前价格
    double bid = SymbolInfoDouble(TradingSymbol, SYMBOL_BID);
    double ask = SymbolInfoDouble(TradingSymbol, SYMBOL_ASK);
    double spread = ask - bid;
    
    // 计算交易量
    double lot_size = CalculateLotSize();
    
    // 计算止损和止盈
    double atr = MarketAnalyzer.GetATR();
    double sl_distance = atr * ATRMultiplier;
    double tp_distance = sl_distance * RiskRewardRatio;
    
    double sl_price = 0.0;
    double tp_price = 0.0;
    
    if(signal == "buy")
    {
        sl_price = bid - sl_distance;
        tp_price = bid + tp_distance;
        
        if(Trade.Buy(lot_size, TradingSymbol, 0, sl_price, tp_price))
        {
            LogMessage("买入订单执行成功");
            ConsecutiveLosses = 0;
            ConsecutiveWins++;
        }
        else
        {
            LogMessage("买入订单执行失败: " + GetErrorDescription(GetLastError()));
        }
    }
    else if(signal == "sell")
    {
        sl_price = ask + sl_distance;
        tp_price = ask - tp_distance;
        
        if(Trade.Sell(lot_size, TradingSymbol, 0, sl_price, tp_price))
        {
            LogMessage("卖出订单执行成功");
            ConsecutiveLosses = 0;
            ConsecutiveWins++;
        }
        else
        {
            LogMessage("卖出订单执行失败: " + GetErrorDescription(GetLastError()));
        }
    }
    
    // 更新性能统计
    TotalTrades++;
    SignalConfirmCount = 0;
    LastSignal = signal;
    LastSignalTime = TimeCurrent();
}

//+------------------------------------------------------------------+
//| 计算交易量                                                       |
//+------------------------------------------------------------------+
double CalculateLotSize()
{
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double risk_amount = balance * RiskPerTrade / 100.0;
    
    double atr = MarketAnalyzer.GetATR();
    double sl_distance = atr * ATRMultiplier;
    
    double tick_value = SymbolInfoDouble(TradingSymbol, SYMBOL_TRADE_TICK_VALUE);
    double tick_size = SymbolInfoDouble(TradingSymbol, SYMBOL_TRADE_TICK_SIZE);
    
    if(tick_value == 0 || tick_size == 0)
        return 0.01;
    
    double risk_per_tick = risk_amount / (sl_distance / tick_size);
    double lot_size = risk_per_tick / tick_value;
    
    // 标准化交易量
    double min_lot = SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_MIN);
    double max_lot = SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_MAX);
    double lot_step = SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_STEP);
    
    lot_size = MathMax(lot_size, min_lot);
    lot_size = MathMin(lot_size, max_lot);
    lot_size = MathRound(lot_size / lot_step) * lot_step;
    
    return lot_size;
}

//+------------------------------------------------------------------+
//| 风险管理检查                                                     |
//+------------------------------------------------------------------+
bool RiskManagementCheck()
{
    if(!EnableRiskManagement)
        return true;
    
    // 检查每日亏损限制
    double daily_loss_limit = AccountInfoDouble(ACCOUNT_BALANCE) * MaxDailyLoss / 100.0;
    if(DailyLoss >= daily_loss_limit)
    {
        LogMessage("达到每日亏损限制，停止交易");
        return false;
    }
    
    // 检查总风险限制
    double total_risk_limit = AccountInfoDouble(ACCOUNT_BALANCE) * MaxTotalRisk / 100.0;
    if(TotalTrades > 0 && TotalProfit < -total_risk_limit)
    {
        LogMessage("达到总风险限制，停止交易");
        return false;
    }
    
    // 检查连续亏损
    if(ConsecutiveLosses >= MaxConsecutiveLosses)
    {
        LogMessage("达到最大连续亏损次数，停止交易");
        return false;
    }
    
    // 检查持仓数量
    if(OrderTracker.GetTotalPositions() >= MaxPositions)
    {
        LogMessage("达到最大持仓数量，停止开新仓");
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| 交易时间检查                                                     |
//+------------------------------------------------------------------+
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
//| 初始化函数                                                       |
//+------------------------------------------------------------------+
int OnInit()
{
    // 设置交易品种和时间周期
    TradingSymbol = (InputSymbol == "") ? _Symbol : InputSymbol;
    TradingTimeframe = (InputTimeframe == PERIOD_CURRENT) ? _Period : InputTimeframe;
    
    // 更新服务器连接配置
    WebRequestConn.host = ServerIP;
    WebRequestConn.port = ServerPort;
    
    // 初始化账户信息
    AccountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    CurrentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    PeakEquity = CurrentEquity;
    
    // 初始化交易对象
    Trade = new CTrade();
    Trade.SetExpertMagicNumber(MagicNumber);
    Trade.SetDeviationInPoints(10);
    
    // 初始化市场分析器
    MarketAnalyzer = new CMarketAnalyzer(TradingSymbol, TradingTimeframe);
    
    // 初始化CRT引擎
    if (EnableCRT)
    {
        CRTEngine = new CCRTEngine(TradingSymbol, CRTRangeTimeframe, TradingTimeframe);
        LogMessage("CRT引擎已初始化 - 区间: " + EnumToString(CRTRangeTimeframe) + ", 确认: " + EnumToString(TradingTimeframe));
    }
    
    // 初始化MTF引擎
    if (EnableMTF)
    {
        MTFEngine = new CMTFEngine(TradingSymbol, MTF_HTF1, MTF_HTF2, MTF_SwingLength);
        LogMessage("MTF引擎已初始化 - HTF1: " + EnumToString(MTF_HTF1) + ", HTF2: " + EnumToString(MTF_HTF2));
    }
    
    // 初始化PEM引擎
    if (EnablePEM)
    {
        PEMEngine = new CPEMEngine(TradingSymbol, TradingTimeframe, PEM_MA_Fast, PEM_MA_Slow, PEM_ADX_Threshold);
        LogMessage("PEM引擎已初始化 - FastMA: " + IntegerToString(PEM_MA_Fast) + ", SlowMA: " + IntegerToString(PEM_MA_Slow));
    }
    
    // 初始化SMC引擎
    if (EnableSMC)
    {
        SMCEngine = new CSMCEngine(TradingSymbol, TradingTimeframe, SMC_HTF, SMC_LTF1, SMC_LTF2, SMC_MA_Period, SMC_UseSentiment, SMC_AllowBOS, SMC_AllowOB, SMC_AllowFVG);
        LogMessage("SMC引擎已初始化 - Sentiment: " + (SMC_UseSentiment ? "ON" : "OFF"));
    }
    
    // 初始化订单跟踪器
    OrderTracker = new CMyOrderTracker();
    
    // 设置最后交易日期
    TimeToStruct(TimeCurrent(), LastTradeDay);
    
    EA_Running = true;
    LogMessage("AI多时间框架SMC交易系统WebRequest版已启动");
    LogMessage("交易品种: " + TradingSymbol + ", 时间周期: " + EnumToString(TradingTimeframe));
    LogMessage("AI服务器地址: " + WebRequestConn.host + ":" + IntegerToString(WebRequestConn.port));
    
    SendTelegramMessage("🚀 EA Started\nSymbol: " + TradingSymbol + "\nTimeframe: " + EnumToString(TradingTimeframe) + "\nServer: " + WebRequestConn.host);
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| 反初始化函数                                                     |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    EA_Running = false;
    
    // 清理资源
    if(MarketAnalyzer != NULL)
    {
        delete MarketAnalyzer;
        MarketAnalyzer = NULL;
    }
    
    if(CRTEngine != NULL)
    {
        delete CRTEngine;
        CRTEngine = NULL;
    }
    
    if(MTFEngine != NULL)
    {
        delete MTFEngine;
        MTFEngine = NULL;
    }
    
    if(PEMEngine != NULL)
    {
        delete PEMEngine;
        PEMEngine = NULL;
    }
    
    if(SMCEngine != NULL)
    {
        delete SMCEngine;
        SMCEngine = NULL;
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
    
    LogMessage("AI多时间框架SMC交易系统已停止");
    SendTelegramMessage("🛑 EA Stopped\nSymbol: " + TradingSymbol);
}

//+------------------------------------------------------------------+
//| 检查是否是新K线                                                  |
//+------------------------------------------------------------------+
bool IsNewBar()
{
    datetime current_time = iTime(_Symbol, _Period, 0);
    if(LastBarTime != current_time)
    {
        LastBarTime = current_time;
        return true;
    }
    return false;
}

//+------------------------------------------------------------------+
//| 本地分析预过滤                                                   |
//+------------------------------------------------------------------+
bool IsLocalSetupValid()
{
    if(MarketAnalyzer == NULL) 
        return true;
    
    // 如果已有持仓，则不需要频繁调用AI（除非需要AI来管理平仓，但目前逻辑是SL/TP管理）
    // 如果您希望AI管理平仓，可以注释掉下面这段
    if(OrderTracker.GetTotalPositions() >= MaxPositions)
        return false;
        
    // 1. RSI 过滤
    double rsi = MarketAnalyzer.GetRSI();
    
    // 检查RSI极端区域 (例如 <30 或 >70)
    // 只有在市场处于极端状态时，才认为"值得"调用AI进行深入分析
    if(rsi < LocalRSIThreshold || rsi > (100 - LocalRSIThreshold))
    {
        LogMessage("本地分析触发: RSI=" + DoubleToString(rsi, 2) + " (进入潜在反转区)");
        return true;
    }
    
    // 2. 波动率过滤 (可选)
    double volatility = MarketAnalyzer.GetVolatility();
    if(volatility > 0.5) // 只有当市场有一定波动时才交易
    {
        // 如果RSI没有触发，但波动率很高，也许值得一看？
        // 这里我们保持保守，主要依赖RSI
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| 主循环函数                                                       |
//+------------------------------------------------------------------+
void OnTick()
{
    if(!EA_Running)
        return;
    
    // 更新账户信息
    UpdateAccountInfo();
    
    // 更新订单信息
    OrderTracker.UpdateOrders(MagicNumber);
    
    // 检查交易条件
    if(!IsTradingTime() || !RiskManagementCheck())
        return;
        
    // === 性能优化：新K线检查 ===
    if(RunOnNewBarOnly && !IsNewBar())
        return;
        
    // === 性能优化：本地预过滤 ===
    // 在调用昂贵的API之前，先用本地指标判断是否"值得"分析
    if(EnableLocalFilter && !IsLocalSetupValid())
        return;
    
    // 尝试获取AI信号
    string signal;
    int strength;
    string analysis;
    if(!GetSignalFromWebRequest(signal, strength, analysis))
    {
        // AI信号获取失败，使用本地分析
        UseLocalAnalysis();
    }
    else
    {
        // 处理获取到的AI信号
        ProcessAISignal(signal, strength, analysis);
    }
}

//+------------------------------------------------------------------+
//| 处理AI信号                                                       |
//+------------------------------------------------------------------+
void ProcessAISignal(string signal, int strength, string analysis)
{
    // 转换为大写以统一处理
    string upper_signal = signal;
    StringToUpper(upper_signal);

    // 检查信号强度是否满足要求
    if(strength < MinSignalStrength)
    {
        LogMessage("信号强度不足: " + upper_signal + " (强度: " + IntegerToString(strength) + ")");
        return;
    }
    
    // 更新信号缓存
    SignalCache.signal = upper_signal;
    SignalCache.strength = strength;
    SignalCache.analysis = analysis;
    SignalCache.timestamp = TimeCurrent();
    SignalCache.is_valid = true;
    
    LogMessage("AI信号处理: " + upper_signal + " (强度: " + IntegerToString(strength) + ")");
    
    // 发送Telegram通知
    string tg_msg = "🤖 AI Signal Update\n" +
                    "Symbol: " + TradingSymbol + "\n" +
                    "Timeframe: " + EnumToString(TradingTimeframe) + "\n" +
                    "Direction: " + upper_signal + "\n" +
                    "Strength: " + IntegerToString(strength) + "\n" +
                    "Analysis: " + analysis;
    SendTelegramMessage(tg_msg);
    
    // 根据信号执行交易逻辑
    if(upper_signal == "BUY")
    {
        ExecuteBuySignal(strength);
    }
    else if(upper_signal == "SELL")
    {
        ExecuteSellSignal(strength);
    }
    else if(upper_signal == "HOLD")
    {
        LogMessage("AI建议持仓观望");
    }
}

//+------------------------------------------------------------------+
//| 执行买入信号                                                     |
//+------------------------------------------------------------------+
void ExecuteBuySignal(int strength)
{
    if(Trade == NULL)
        return;
        
    // 计算交易量
    double volume = CalculateVolume();
    if(volume <= 0)
        return;
        
    // 计算止损和止盈
    double sl = CalculateStopLoss(true);
    double tp = CalculateTakeProfit(true, sl);
    
    // 执行买入
    if(Trade.Buy(volume, TradingSymbol, 0, sl, tp, "AI Buy Signal (Strength: " + IntegerToString(strength) + ")"))
    {
        LogMessage("执行买入信号，强度: " + IntegerToString(strength));
        SendTelegramMessage("✅ Buy Order Executed\nSymbol: " + TradingSymbol + "\nVolume: " + DoubleToString(volume, 2) + "\nSignal Strength: " + IntegerToString(strength));
    }
    else
    {
        string error_msg = GetErrorDescription(GetLastError());
        LogMessage("买入执行失败: " + error_msg);
        SendTelegramMessage("❌ Buy Failed\nSymbol: " + TradingSymbol + "\nReason: " + error_msg);
    }
}

//+------------------------------------------------------------------+
//| 执行卖出信号                                                     |
//+------------------------------------------------------------------+
void ExecuteSellSignal(int strength)
{
    if(Trade == NULL)
        return;
        
    // 计算交易量
    double volume = CalculateVolume();
    if(volume <= 0)
        return;
        
    // 计算止损和止盈
    double sl = CalculateStopLoss(false);
    double tp = CalculateTakeProfit(false, sl);
    
    // 执行卖出
    if(Trade.Sell(volume, TradingSymbol, 0, sl, tp, "AI Sell Signal (Strength: " + IntegerToString(strength) + ")"))
    {
        LogMessage("执行卖出信号，强度: " + IntegerToString(strength));
        SendTelegramMessage("✅ Sell Order Executed\nSymbol: " + TradingSymbol + "\nVolume: " + DoubleToString(volume, 2) + "\nSignal Strength: " + IntegerToString(strength));
    }
    else
    {
        string error_msg = GetErrorDescription(GetLastError());
        LogMessage("卖出执行失败: " + error_msg);
        SendTelegramMessage("❌ Sell Failed\nSymbol: " + TradingSymbol + "\nReason: " + error_msg);
    }
}

//+------------------------------------------------------------------+
//| 计算交易量                                                       |
//+------------------------------------------------------------------+
double CalculateVolume()
{
    // 基于风险百分比计算交易量
    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
    double risk_amount = balance * RiskPerTrade / 100.0;
    
    // 获取当前价格和点值
    double price = SymbolInfoDouble(TradingSymbol, SYMBOL_ASK);
    double point = SymbolInfoDouble(TradingSymbol, SYMBOL_POINT);
    double tick_value = SymbolInfoDouble(TradingSymbol, SYMBOL_TRADE_TICK_VALUE);
    
    if(point <= 0 || tick_value <= 0)
        return 0.0;
        
    // 计算止损距离（基于ATR）
    double atr = MarketAnalyzer.GetATR();
    double stop_distance = atr * ATRMultiplier;
    
    // 计算交易量
    double volume = risk_amount / (stop_distance / point * tick_value);
    
    // 标准化交易量
    double min_volume = SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_MIN);
    double max_volume = SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_MAX);
    double step_volume = SymbolInfoDouble(TradingSymbol, SYMBOL_VOLUME_STEP);
    
    volume = MathMax(volume, min_volume);
    volume = MathMin(volume, max_volume);
    volume = MathRound(volume / step_volume) * step_volume;
    
    return volume;
}

//+------------------------------------------------------------------+
//| 计算止损                                                         |
//+------------------------------------------------------------------+
double CalculateStopLoss(bool is_buy)
{
    if(!EnableDynamicStopLoss)
        return 0.0;
        
    double current_price = is_buy ? SymbolInfoDouble(TradingSymbol, SYMBOL_BID) : SymbolInfoDouble(TradingSymbol, SYMBOL_ASK);
    double atr = MarketAnalyzer.GetATR();
    
    if(is_buy)
        return current_price - atr * ATRMultiplier;
    else
        return current_price + atr * ATRMultiplier;
}

//+------------------------------------------------------------------+
//| 计算止盈                                                         |
//+------------------------------------------------------------------+
double CalculateTakeProfit(bool is_buy, double stop_loss)
{
    if(stop_loss == 0.0)
        return 0.0;
        
    double current_price = is_buy ? SymbolInfoDouble(TradingSymbol, SYMBOL_BID) : SymbolInfoDouble(TradingSymbol, SYMBOL_ASK);
    
    if(is_buy)
        return current_price + (current_price - stop_loss) * RiskRewardRatio;
    else
        return current_price - (stop_loss - current_price) * RiskRewardRatio;
}

//+------------------------------------------------------------------+
//| 定时器函数（可选）                                               |
//+------------------------------------------------------------------+
void OnTimer()
{
    // 可以用于定期任务，如性能统计、日志清理等
}

//+------------------------------------------------------------------+
//| 更新账户信息                                                     |
//+------------------------------------------------------------------+
void UpdateAccountInfo()
{
    // 更新权益
    CurrentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    
    // 更新峰值权益和最大回撤
    if(CurrentEquity > PeakEquity)
        PeakEquity = CurrentEquity;
    
    MaxDrawdown = MathMax(MaxDrawdown, (PeakEquity - CurrentEquity) / PeakEquity * 100.0);
    
    // 检查是否是新的一天
    MqlDateTime current_time;
    TimeToStruct(TimeCurrent(), current_time);
    
    if(current_time.day != LastTradeDay.day || 
       current_time.mon != LastTradeDay.mon || 
       current_time.year != LastTradeDay.year)
    {
        // 新的一天，重置每日统计
        DailyLoss = 0.0;
        DailyProfit = 0.0;
        LastTradeDay = current_time;
        
        LogMessage("新交易日开始");
    }
}