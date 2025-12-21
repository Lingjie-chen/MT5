//+------------------------------------------------------------------+
//| Socket.mqh                                                      |
//| Copyright 2024, MetaQuotes Software Corp.                       |
//| https://www.mql5.com                                            |
//+------------------------------------------------------------------+
#property copyright "Copyright 2024, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict

//+------------------------------------------------------------------+
//| Socket库常量定义                                                 |
//+------------------------------------------------------------------+
#define SOCKET_INVALID_HANDLE   -1
#define SOCKET_ERROR            -1
#define AF_INET                 2
#define SOCK_STREAM             1
#define IPPROTO_TCP             6

//+------------------------------------------------------------------+
//| Socket函数实现                                                   |
//+------------------------------------------------------------------+

// 导入Windows Socket API
#import "ws2_32.dll"
int WSAStartup(short wVersionRequested, uchar &lpWSAData[]);
int WSACleanup(void);
int socket(int af, int type, int protocol);
int closesocket(int s);
int connect(int s, uchar &name[], int namelen);
int send(int s, uchar &buf[], int len, int flags);
int recv(int s, uchar &buf[], int len, int flags);
int select(int nfds, uchar &readfds[], uchar &writefds[], uchar &exceptfds[], uchar &timeout[]);
ushort htons(ushort hostshort);
uint inet_addr(string cp);
#import

//+------------------------------------------------------------------+
//| Socket结构定义                                                   |
//+------------------------------------------------------------------+
struct sockaddr_in
{
    short   sin_family;
    ushort  sin_port;
    uint    sin_addr;
    uchar   sin_zero[8];
};

//+------------------------------------------------------------------+
//| 全局变量                                                         |
//+------------------------------------------------------------------+
bool SocketLibraryInitialized = false;

//+------------------------------------------------------------------+
//| 初始化Socket库                                                   |
//+------------------------------------------------------------------+
bool InitializeSocketLibrary()
{
    if(SocketLibraryInitialized)
        return true;
    
    uchar wsaData[512];
    short version = 0x0202; // Winsock 2.2
    
    int result = WSAStartup(version, wsaData);
    if(result == 0)
    {
        SocketLibraryInitialized = true;
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| 清理Socket库                                                     |
//+------------------------------------------------------------------+
void CleanupSocketLibrary()
{
    if(SocketLibraryInitialized)
    {
        WSACleanup();
        SocketLibraryInitialized = false;
    }
}

//+------------------------------------------------------------------+
//| 创建Socket                                                       |
//+------------------------------------------------------------------+
int CustomSocketCreate(void)
{
    if(!InitializeSocketLibrary())
        return SOCKET_INVALID_HANDLE;
    
    int sock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if(sock == SOCKET_ERROR)
        return SOCKET_INVALID_HANDLE;
    
    return sock;
}

//+------------------------------------------------------------------+
//| 关闭Socket                                                       |
//+------------------------------------------------------------------+
bool CustomSocketClose(int socket)
{
    if(socket == SOCKET_INVALID_HANDLE)
        return false;
    
    int result = closesocket(socket);
    return (result != SOCKET_ERROR);
}

//+------------------------------------------------------------------+
//| 连接到服务器                                                     |
//+------------------------------------------------------------------+
bool CustomSocketConnect(int socket, string host, int port, int timeout_ms=5000)
{
    if(socket == SOCKET_INVALID_HANDLE)
        return false;
    
    // 解析主机地址
    uint addr = inet_addr(host);
    if(addr == 0xFFFFFFFF)
        return false;
    
    // 准备地址结构
    sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_port = htons((ushort)port);
    address.sin_addr = addr;
    ArrayInitialize(address.sin_zero, 0);
    
    // 转换为字节数组
    uchar addr_data[16];
    ArrayInitialize(addr_data, 0);
    
    // 复制地址结构到字节数组
    for(int i = 0; i < 2; i++)
        addr_data[i] = (uchar)((address.sin_family >> (i * 8)) & 0xFF);
    
    for(int i = 0; i < 2; i++)
        addr_data[2 + i] = (uchar)((address.sin_port >> (i * 8)) & 0xFF);
    
    for(int i = 0; i < 4; i++)
        addr_data[4 + i] = (uchar)((address.sin_addr >> (i * 8)) & 0xFF);
    
    // 连接
    int result = connect(socket, addr_data, 16);
    
    // 检查连接状态
    if(result == SOCKET_ERROR)
    {
        // 非阻塞模式下，连接可能正在进行中
        // 这里简化处理，直接返回连接结果
        return false;
    }
    
    return true;
}

//+------------------------------------------------------------------+
//| 发送数据                                                         |
//+------------------------------------------------------------------+
int CustomSocketSend(int socket, uchar &data[], int size)
{
    if(socket == SOCKET_INVALID_HANDLE || size <= 0)
        return SOCKET_ERROR;
    
    int sent = send(socket, data, size, 0);
    return sent;
}

//+------------------------------------------------------------------+
//| 接收数据                                                         |
//+------------------------------------------------------------------+
int CustomSocketRead(int socket, uchar &buffer[], int size, int timeout_ms=100)
{
    if(socket == SOCKET_INVALID_HANDLE || size <= 0)
        return SOCKET_ERROR;
    
    // 检查是否有数据可读
    if(!CustomSocketIsReadable(socket, timeout_ms))
        return 0;
    
    int received = recv(socket, buffer, size, 0);
    return received;
}

//+------------------------------------------------------------------+
//| 检查Socket是否可读                                               |
//+------------------------------------------------------------------+
bool CustomSocketIsReadable(int socket, int timeout_ms=100)
{
    if(socket == SOCKET_INVALID_HANDLE)
        return false;
    
    // 准备select参数
    uchar readfds[32];
    uchar writefds[32];
    uchar exceptfds[32];
    uchar timeout[8];
    
    ArrayInitialize(readfds, 0);
    ArrayInitialize(writefds, 0);
    ArrayInitialize(exceptfds, 0);
    ArrayInitialize(timeout, 0);
    
    // 设置超时时间
    timeout[0] = (uchar)((timeout_ms / 1000) & 0xFF);
    timeout[1] = (uchar)(((timeout_ms / 1000) >> 8) & 0xFF);
    timeout[2] = (uchar)(((timeout_ms % 1000) * 1000) & 0xFF);
    timeout[3] = (uchar)((((timeout_ms % 1000) * 1000) >> 8) & 0xFF);
    
    // 设置socket到readfds
    int fd_index = socket / 8;
    int fd_bit = socket % 8;
    if(fd_index < 32)
        readfds[fd_index] = (uchar)(readfds[fd_index] | (1 << fd_bit));
    
    int result = select(socket + 1, readfds, writefds, exceptfds, timeout);
    
    if(result > 0)
    {
        // 检查socket是否在readfds中
        if(fd_index < 32 && ((readfds[fd_index] & (1 << fd_bit)) != 0))
            return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| 检查Socket是否可写                                               |
//+------------------------------------------------------------------+
bool CustomSocketIsWritable(int socket, int timeout_ms=100)
{
    if(socket == SOCKET_INVALID_HANDLE)
        return false;
    
    // 准备select参数
    uchar readfds[32];
    uchar writefds[32];
    uchar exceptfds[32];
    uchar timeout[8];
    
    ArrayInitialize(readfds, 0);
    ArrayInitialize(writefds, 0);
    ArrayInitialize(exceptfds, 0);
    ArrayInitialize(timeout, 0);
    
    // 设置超时时间
    timeout[0] = (uchar)((timeout_ms / 1000) & 0xFF);
    timeout[1] = (uchar)(((timeout_ms / 1000) >> 8) & 0xFF);
    timeout[2] = (uchar)(((timeout_ms % 1000) * 1000) & 0xFF);
    timeout[3] = (uchar)((((timeout_ms % 1000) * 1000) >> 8) & 0xFF);
    
    // 设置socket到writefds
    int fd_index = socket / 8;
    int fd_bit = socket % 8;
    if(fd_index < 32)
        writefds[fd_index] = (uchar)(writefds[fd_index] | (1 << fd_bit));
    
    int result = select(socket + 1, readfds, writefds, exceptfds, timeout);
    
    if(result > 0)
    {
        // 检查socket是否在writefds中
        if(fd_index < 32 && ((writefds[fd_index] & (1 << fd_bit)) != 0))
            return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| 辅助函数                                                         |
//+------------------------------------------------------------------+

// 将字符串转换为IP地址
uint StringToIP(string ip_str)
{
    string parts[4];
    int count = StringSplit(ip_str, '.', parts);
    
    if(count != 4)
        return 0;
    
    uint ip = 0;
    for(int i = 0; i < 4; i++)
    {
        int part = (int)StringToInteger(parts[i]);
        if(part < 0 || part > 255)
            return 0;
        ip |= (part << (24 - i * 8));
    }
    
    return ip;
}

// 检查IP地址是否有效
bool IsValidIP(string ip_str)
{
    return (StringToIP(ip_str) != 0);
}

//+------------------------------------------------------------------+