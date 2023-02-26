import os
import logging
from pathlib import Path


def get_logger(
    logger_name: str = "mf_logger", filename: str = "movie_finder_logs.txt"
) -> logging.Logger:
    """
    Function for getting a logger object using a logger name from anywhere

    Args:
        logger_name (str, optional): Logger name to be used. Defaults to "mf_logger".
        filename (str, optional): Logger file name. Defaults to "movie_finder_logs.txt".

    Returns:
        logging.Logger: Logger object
    """
    logging_dir = Path(os.environ.get("MOVIE_FINDER_LOG", "."))

    log_formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
    )

    log_writer = logging.FileHandler(logging_dir / filename)
    log_writer.setFormatter(log_formatter)

    logger = logging.getLogger(logger_name)
    logger.addHandler(log_writer)

    return logger
