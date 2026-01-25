import os
import sys
import time
import threading
import logging

class FileWatcher:
    def __init__(self, directories, interval=3):
        """
        Initialize the FileWatcher.
        
        :param directories: List of directories to watch.
        :param interval: Polling interval in seconds.
        """
        self.directories = directories
        self.interval = interval
        self.last_mtimes = {}
        self.running = True
        self.logger = logging.getLogger("FileWatcher")
        
        # Initial scan
        self.last_mtimes = self.scan_files()

    def scan_files(self):
        mtimes = {}
        for directory in self.directories:
            if not os.path.exists(directory):
                continue
            for root, _, files in os.walk(directory):
                # Watch python files, env files, and perhaps json configs
                for f in files:
                    if f.endswith(".py") or f.endswith(".env") or f.endswith(".json"):
                        path = os.path.join(root, f)
                        try:
                            mtime = os.stat(path).st_mtime
                            mtimes[path] = mtime
                        except OSError:
                            pass
        return mtimes

    def watch(self):
        self.logger.info(f"Started watching for file changes in: {self.directories}")
        
        while self.running:
            time.sleep(self.interval)
            try:
                new_mtimes = self.scan_files()
                if self.check_changes(new_mtimes):
                    self.logger.warning("File change detected! Restarting bot...")
                    # Allow logs to flush
                    time.sleep(1.0)
                    # Force exit. The watchdog script (bat/sh) should handle the restart.
                    os._exit(0)
            except Exception as e:
                self.logger.error(f"Watcher error: {e}")

    def check_changes(self, new_mtimes):
        # Check for modified or new files
        for path, mtime in new_mtimes.items():
            if path not in self.last_mtimes:
                self.logger.info(f"New file detected: {path}")
                return True
            if mtime > self.last_mtimes[path]:
                self.logger.info(f"File modified: {path}")
                return True
        
        # Check for deleted files
        if len(new_mtimes) != len(self.last_mtimes):
             self.logger.info("File deletion detected")
             return True
             
        return False

    def start(self):
        thread = threading.Thread(target=self.watch, daemon=True)
        thread.start()
