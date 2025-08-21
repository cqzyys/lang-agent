import logging
from typing import Dict
import os
import sys
import time
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

import colorlog

__root__ = Path(__file__).parent.parent.parent.resolve()
logger_initialized: Dict[str, bool] = {}

def get_logger(
    name=None, log_file=__root__ / "log/main.log", log_level=logging.DEBUG
) -> logging.Logger:
    logger = logging.getLogger(name)
    if name in logger_initialized:
        return logger
    if not logger.handlers:
        # console log
        std_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'white',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        std_handler = colorlog.StreamHandler(stream=sys.stdout)
        std_handler.setFormatter(std_formatter)
        logger.addHandler(std_handler)
        # file log
        if log_file is not None:
            os.makedirs(log_file.parent, exist_ok=True)
            file_handle = TimedRotatingFileHandler(
                log_file,
                when="D",
                interval=1,
                backupCount=3,
                encoding="UTF-8",
                delay=False,
                utc=False,
                atTime=time,
            )
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y/%m/%d %H:%M:%S"
            )
            file_handle.setFormatter(file_formatter)
            logger.addHandler(file_handle)
        logger.setLevel(log_level)
        logger_initialized[name] = True
        logger.propagate = False
    return logger
