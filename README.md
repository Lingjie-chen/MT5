# MT5 AI Trading Strategy Integration

## Project Overview

This project integrates MetaTrader 5 (MT5) with a Python-based AI trading strategy server. It consists of two main components:

1. **MQL5 Expert Advisor** (`mq5/AI_MultiTF_SMC_EA_WebRequest.mq5`) - Runs in the MT5 terminal and sends market data to the Python server
2. **Python Flask Server** (`enhanced_server_ml.py`) - Processes market data, generates AI trading signals, and sends them back to the EA

## Architecture

```
┌───────────────────┐      ┌───────────────────┐
│  MetaTrader 5     │      │  Python Flask     │
│  Terminal         │      │  Server           │
│  ┌─────────────┐  │      │  ┌─────────────┐  │
│  │  AI_MultiTF  │  │      │  │  Enhanced   │  │
│  │  SMC_EA      │──┼──────┼──│  Server_ML  │  │
│  │  WebRequest  │  │ HTTP │  │             │  │
│  └─────────────┘  │      │  └─────────────┘  │
│                   │      │  ┌─────────────┐  │
│                   │      │  │  Data       │  │
│                   │      │  │  Processor  │  │
│                   │      │  └─────────────┘  │
│                   │      │  ┌─────────────┐  │
│                   │      │  │  AI/ML      │  │
│                   │      │  │  Model      │  │
│                   │      │  └─────────────┘  │
└───────────────────┘      └───────────────────┘
```

## Installation and Deployment

### Windows Installation (Recommended for Production)

#### 1. Install MetaTrader 5
- Download MT5 from your broker's website or from [MetaQuotes](https://www.metatrader5.com/)
- Install and run MT5

#### 2. Install Python
- Download Python 3.8+ from [python.org](https://www.python.org/)
- Install with pip and add to PATH

#### 3. Clone the Repository
```bash
git clone <repository-url>
cd quant_trading_strategy
```

#### 4. Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 5. Start the Flask Server
```bash
python enhanced_server_ml.py
```

#### 6. Install the MQL5 EA
- Open the `mq5/` directory
- Copy `AI_MultiTF_SMC_EA_WebRequest.mq5` and `Include/fixed_json_functions.mqh` to your MT5 Experts directory
- Open MT5, go to Tools > MetaEditor
- Compile the EA
- Attach the EA to a chart in MT5

### macOS Installation

MetaTrader 5 Python library has limited support on macOS. Here are several options:

#### Option 1: Native Python with Mock Data
```bash
# Install Python dependencies (MT5 will be skipped automatically)
pip install -r requirements.txt

# Start the server (will use mock data)
python enhanced_server_ml.py
```

#### Option 2: Wine + Windows Python
```bash
# Install Wine
brew install --cask wine-stable

# Install Windows Python via Wine
wine msiexec /i https://www.python.org/ftp/python/3.9.0/python-3.9.0-amd64.msi

# Install MT5 library via Wine
wine pip install MetaTrader5
```

#### Option 3: Virtual Machine
1. Install Parallels Desktop, VMware Fusion, or UTM
2. Create a Windows 10/11 virtual machine
3. Follow the Windows installation instructions above

#### Option 4: Docker Container
```bash
# Create Dockerfile
cat > Dockerfile << EOF
FROM python:3.9-windowsservercore
RUN pip install MetaTrader5 flask pandas numpy scikit-learn
COPY . /app
WORKDIR /app
CMD ["python", "enhanced_server_ml.py"]
EOF

# Build and run
docker build -t mt5-python .
docker run -p 5002:5002 mt5-python
```

## API Endpoints

### POST /get_signal
**Description**: Get AI trading signals

**Request Body**:
```json
{
  "symbol": "EURUSD",
  "timeframe": "H1",
  "count": 100,
  "rates": [
    {
      "time": 1630000000,
      "open": 1.1800,
      "high": 1.1850,
      "low": 1.1780,
      "close": 1.1820,
      "tick_volume": 1000
    }
  ]
}
```

**Response**:
```json
{
  "signal": "buy",
  "strength": 85,
  "analysis": "Bullish trend confirmed with strong momentum",
  "timestamp": "2023-10-01T12:00:00Z"
}
```

### GET /health
**Description**: Check server health status

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2023-10-01T12:00:00Z",
  "uptime": 3600
}
```

### POST /analysis
**Description**: Get detailed market analysis

**Response**:
```json
{
  "symbol": "EURUSD",
  "timeframe": "H1",
  "trend": "bullish",
  "indicators": {
    "rsi": 65,
    "ema_fast": 1.1820,
    "ema_slow": 1.1790
  },
  "support": [1.1750, 1.1700],
  "resistance": [1.1850, 1.1900]
}
```

### POST /train_model
**Description**: Trigger model retraining

**Response**:
```json
{
  "status": "training_started",
  "timestamp": "2023-10-01T12:00:00Z"
}
```

## Configuration

### EA Configuration
Edit the EA settings in MT5:
- `WebRequestHost` - Python server IP address (default: 127.0.0.1)
- `WebRequestPort` - Python server port (default: 5002)
- `SignalCacheTimeout` - Cache duration for signals (default: 30 seconds)

### Server Configuration
Edit `enhanced_server_ml.py`:
- `host` - Server binding address (default: 0.0.0.0)
- `port` - Server port (default: 5002)
- `debug` - Debug mode (default: False)

## Data Processing

The Python server processes market data through several steps:

1. **Data Validation**: Checks for invalid prices, timestamps, and data integrity
2. **Feature Generation**: Calculates technical indicators (RSI, EMA, ATR)
3. **AI Model Inference**: Uses scikit-learn models to generate signals
4. **Signal Validation**: Ensures signals are within valid ranges
5. **Response Generation**: Formats results into JSON

## Security Considerations

1. **Data Validation**: All incoming requests are validated to prevent malicious input
2. **Rate Limiting**: Prevents excessive requests from overwhelming the server
3. **JSON Sanitization**: Removes special characters and control sequences
4. **Response Validation**: Verifies all signals before sending to the EA

## Troubleshooting

### Common Issues

1. **MT5 Library Not Found**
   - On Windows: Ensure MetaTrader 5 is installed correctly
   - On macOS: Use mock data mode or virtual machine

2. **Connection Refused**
   - Check if the Python server is running
   - Verify IP address and port settings
   - Ensure firewall allows connections

3. **Invalid JSON Response**
   - Check if the server is running correctly
   - Review server logs for errors
   - Verify EA settings

4. **Slow Response Times**
   - Reduce the number of candles in requests
   - Optimize the AI model
   - Use a faster computer or VM

5. **Port Already in Use**
   - Identify the conflicting process: `lsof -i :5002`
   - Stop the process: `kill <PID>`
   - Or change the server port in `enhanced_server_ml.py`

### Logging

- Server logs are written to `server.log`
- EA logs can be viewed in MT5's Journal tab
- Debug logs can be enabled by setting `debug=True` in the server

## Development

### Adding New Indicators

1. Edit `python/data_processor.py` and add new calculation methods
2. Update the `generate_features` method to include new indicators
3. Retrain the AI model if necessary

### Customizing AI Models

1. Edit `enhanced_server_ml.py` and modify the `train_model` method
2. Experiment with different scikit-learn algorithms
3. Adjust hyperparameters for better performance

## Production Deployment

For production use, consider:

1. Using a dedicated Windows server or VM
2. Setting up proper logging and monitoring
3. Implementing HTTPS for secure communication
4. Adding authentication and authorization
5. Using a production-grade WSGI server like Gunicorn or uWSGI

## License

This project is licensed under the MIT License.

## Support

For support or questions, please contact the development team or refer to the project documentation.
