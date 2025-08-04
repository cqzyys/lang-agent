import logging
import os
import sys
import time
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

__root__ = Path(__file__).parent.parent.parent.resolve()
logger_initialized = {}
LOG_FORMAT = (
    "[%(asctime)s] %(levelname)s %(name)s %(filename)s [line:%(lineno)d]: %(message)s"
)


def get_logger(
    name=None, log_file=__root__ / "log/main.log", log_level=logging.DEBUG
) -> logging.Logger:
    logger = logging.getLogger(name)
    if name in logger_initialized:
        return logger
    formatter = logging.Formatter(LOG_FORMAT, datefmt="%Y/%m/%d %H:%M:%S")
    # console log
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setFormatter(formatter)
    logger.addHandler(sh)
    # file log
    if log_file is not None:
        os.makedirs(log_file.parent, exist_ok=True)
        tfh = TimedRotatingFileHandler(
            log_file,
            when="D",
            interval=1,
            backupCount=3,
            encoding="UTF-8",
            delay=False,
            utc=False,
            atTime=time,
        )
        tfh.setFormatter(formatter)
        logger.addHandler(tfh)
    logger.setLevel(log_level)
    logger_initialized[name] = True
    logger.propagate = False
    return logger
