import logging
import os

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[31;1m'  # Bold Red
    }
    
    # Reset color
    RESET = '\033[0m'
    
    PREFIX_WIDTH = 9
    
    # Format: "{level}: {date} - {message}"
    FORMAT = '%(levelname)s %(asctime)s - %(message)s'
    
    def __init__(self, *args, **kwargs):
        # Date format: YYYY-MM-DD HH:MM:SS
        super().__init__(self.FORMAT, datefmt='%Y-%m-%d %H:%M:%S', *args, **kwargs)
    
    def format(self, record):
        plain_level = record.levelname
        
        plain_prefix = plain_level + ":"
        padded_plain_prefix = f"{plain_prefix:<{self.PREFIX_WIDTH}}"
        
        # Get color for the level
        level_color = self.COLORS.get(plain_level, '')
        
        if level_color:
            # Replace level with color
            colored_prefix = padded_plain_prefix.replace(plain_level, f"{level_color}{plain_level}{self.RESET}", 1)
        else:
            colored_prefix = padded_plain_prefix
        
        # Overwrite record.levelname
        record.levelname = colored_prefix

        formatted = super().format(record)
        
        # Windows: CRLF for multi-line
        if os.name == 'nt':
            formatted = formatted.replace('\n', '\r\n')
        
        return formatted

def setup_logging(level=logging.INFO, log_file=None):
    """Konfiguruje globalne logowanie z kolorami."""
    # Delete existing handlers if exist
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Root logger
    root = logging.getLogger()
    root.setLevel(level)  # default INFO; change to DEBUG for verbose
    
    # Console handler (colored)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter())
    root.addHandler(console_handler)
    
    # File log handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        root.addHandler(file_handler)
    
    root.propagate = False
    
    return root
