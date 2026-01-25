//+------------------------------------------------------------------+
//| 修复后的JSON生成函数                                             |
//+------------------------------------------------------------------+
string GenerateRateEntry(MqlRates &rate)
{
    // 手动构建单个rate条目，避免StringFormat的复杂性
    string entry = "{";
    entry += "\"time\":" + IntegerToString(rate.time) + ",";
    entry += "\"open\":" + DoubleToString(rate.open, _Digits) + ",";
    entry += "\"high\":" + DoubleToString(rate.high, _Digits) + ",";
    entry += "\"low\":" + DoubleToString(rate.low, _Digits) + ",";
    entry += "\"close\":" + DoubleToString(rate.close, _Digits) + ",";
    entry += "\"tick_volume\":" + IntegerToString(rate.tick_volume);
    entry += "}";
    return entry;
}

//+------------------------------------------------------------------+
//| 生成完整的JSON请求                                               |
//+------------------------------------------------------------------+
string GenerateJSONRequest(string symbol, string timeframe, int count, MqlRates &rates[])
{
    // 构建rates数组
    string rates_array = "[";
    for(int i = 0; i < count; i++)
    {
        if(i > 0) rates_array += ",";
        rates_array += GenerateRateEntry(rates[i]);
    }
    rates_array += "]";
    
    // 构建完整JSON
    string json = "{";
    json += "\"symbol\":\"" + symbol + "\",";
    json += "\"timeframe\":\"" + timeframe + "\",";
    json += "\"count\":" + IntegerToString(count) + ",";
    json += "\"rates\":" + rates_array;
    json += "}";
    
    return json;
}