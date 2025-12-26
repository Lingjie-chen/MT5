import os
import time
import sys
import paramiko
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- 配置 ---
# 请修改为您的阿里云服务器信息
HOST = 'YOUR_ALIYUN_IP'
PORT = 22
USERNAME = 'Administrator'
PASSWORD = 'YOUR_PASSWORD'
REMOTE_PATH = 'C:/QuantProject' # 远程目标路径

class SyncHandler(FileSystemEventHandler):
    def __init__(self, sftp):
        self.sftp = sftp

    def on_modified(self, event):
        if event.is_directory:
            return
        self.upload_file(event.src_path)

    def on_created(self, event):
        if event.is_directory:
            return
        self.upload_file(event.src_path)
        
    def upload_file(self, local_path):
        # 排除 .git 和 __pycache__
        if '.git' in local_path or '__pycache__' in local_path:
            return
            
        try:
            # 计算相对路径
            rel_path = os.path.relpath(local_path, os.getcwd())
            remote_file_path = os.path.join(REMOTE_PATH, rel_path).replace('\\', '/')
            
            # 确保远程目录存在 (简单处理，假设父目录已存在或不报错)
            # 实际生产中可能需要递归创建远程目录
            
            print(f"检测到变更: {rel_path} -> 上传中...")
            self.sftp.put(local_path, remote_file_path)
            print(f"上传成功: {remote_file_path}")
        except Exception as e:
            print(f"上传失败: {e}")

def main():
    print(f"正在连接到服务器 {HOST}...")
    try:
        transport = paramiko.Transport((HOST, PORT))
        transport.connect(username=USERNAME, password=PASSWORD)
        sftp = paramiko.SFTPClient.from_transport(transport)
        print("连接成功！开始监听文件变更...")
        
        event_handler = SyncHandler(sftp)
        observer = Observer()
        observer.schedule(event_handler, path='.', recursive=True)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        sftp.close()
        transport.close()
    except Exception as e:
        print(f"连接或运行时错误: {e}")
        print("请确保服务器已安装 OpenSSH Server 并允许 22 端口连接。")

if __name__ == "__main__":
    # 检查依赖
    try:
        import paramiko
        import watchdog
    except ImportError:
        print("请先安装依赖: pip install paramiko watchdog")
        sys.exit(1)
        
    main()
