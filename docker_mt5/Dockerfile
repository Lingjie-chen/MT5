FROM debian:bookworm-slim

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install Wine and dependencies
# Enable 32-bit architecture for Wine compatibility
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        wine \
        wine32 \
        wine64 \
        libwine \
        libwine:i386 \
        fonts-wine \
        xvfb \
        x11vnc \
        fluxbox \
        wget \
        cabextract \
        gnupg \
        curl \
        unzip \
        xauth \
        ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 2. Setup Wine Environment
ENV WINEPREFIX=/root/.wine
ENV WINEARCH=win64
ENV DISPLAY=:1

# Initialize Wine (this creates the prefix)
RUN winecfg || true

# 3. Install Python 3.10 for Windows
# We use Python 3.10 because pre-built TA-Lib wheels are readily available
WORKDIR /tmp
RUN wget https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe -O python_installer.exe && \
    wine python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 && \
    rm python_installer.exe && \
    wineserver -w

# 4. Install TA-Lib (Windows Wheel)
# Download wheel for CP310 (Python 3.10) and win_amd64
RUN wget https://github.com/cgohlke/talib-build/releases/download/v0.4.26/TA_Lib-0.4.26-cp310-cp310-win_amd64.whl -O ta_lib.whl && \
    wine python -m pip install ta_lib.whl && \
    rm ta_lib.whl

# 5. Download MT5 Installer
RUN wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe -O mt5setup.exe

# 6. Copy Project Files
WORKDIR /app
COPY . .

# 7. Install Dependencies
# We filter out TA-Lib from requirements because we installed it manually
RUN wine python -m pip install --upgrade pip && \
    grep -v "ta-lib" requirements.txt > requirements_no_talib.txt && \
    wine python -m pip install -r requirements_no_talib.txt

# 8. Setup Entrypoint
COPY docker_mt5/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5900
ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "gold/start.py"]
