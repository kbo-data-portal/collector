import os
import logging
import time


def get_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        log_path = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler(
            os.path.join(log_path, f"{time.strftime('%Y-%m-%d_%H')}.log")
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )

        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)

    return logger
