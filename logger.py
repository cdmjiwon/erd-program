import logging
import os
from pathlib import Path
from datetime import datetime


class AppLogger:
    def __init__(self, log_file='erd_program.log'):
        self.log_dir = Path.home() / '.erd_program'
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_path = self.log_dir / log_file
        
        self.logger = logging.getLogger('ERDProgram')
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.handlers:
            file_handler = logging.FileHandler(
                self.log_path,
                encoding='utf-8',
                mode='a'
            )
            file_handler.setLevel(logging.DEBUG)
            
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def get_log_path(self):
        return str(self.log_path)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message, exc_info=False):
        self.logger.error(message, exc_info=exc_info)
    
    def exception(self, message):
        self.logger.exception(message)

