import logging
import re
import sys

class APIKeyRedactingFilter(logging.Filter):
    def __init__(self, patterns=None):
        super().__init__()
        # Matches typical patterns for API keys (e.g., Bearer <key>, api-key: <key>)
        self.patterns = patterns or [
            re.compile(r'(api[_-]?key\s*[:=]\s*)([\'"]?)([a-zA-Z0-9_\-]+)\2', re.IGNORECASE),
            re.compile(r'(bearer\s+)([a-zA-Z0-9_\-\.]+)', re.IGNORECASE)
        ]

    def filter(self, record):
        if isinstance(record.msg, str):
            for pattern in self.patterns:
                record.msg = pattern.sub(r'\1\2***REDACTED***\2', record.msg)
        return True

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    handler.addFilter(APIKeyRedactingFilter())
    logger.addHandler(handler)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
