import logging
import os

RESET = "\033[0m"
COLORS = {
    "ENTRY-THREAD": "\033[94m",
    "EXIT-THREAD": "\033[91m",
    "LIGHT-THREAD": "\033[93m",
    "MAIN-THREAD": "\033[97m",
}


class ColorFormatter(logging.Formatter):
    def format(self, record):
        source_name = getattr(record, "source_name", record.name)
        color = COLORS.get(source_name, "")
        message = super().format(record)
        return f"{color}{message}{RESET}"


def setup_file_logger(name, log_file):
    # Ensure logs folder exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


console_logger = logging.getLogger("CONSOLE")
console_logger.setLevel(logging.INFO)
console_logger.propagate = False

if not console_logger.handlers:
    console_handler = logging.StreamHandler()
    console_formatter = ColorFormatter(
        "%(asctime)s [%(source_name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    console_logger.addHandler(console_handler)

# Put log files in a single 'logs' directory at the root of raspberry_pi
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")

entry_logger = setup_file_logger("ENTRY-THREAD", os.path.join(LOGS_DIR, "entry.log"))
exit_logger = setup_file_logger("EXIT-THREAD", os.path.join(LOGS_DIR, "exit.log"))
light_logger = setup_file_logger("LIGHT-THREAD", os.path.join(LOGS_DIR, "light.log"))
main_logger = setup_file_logger("MAIN-THREAD", os.path.join(LOGS_DIR, "main.log"))


def log_both(logger, message, level="info"):
    file_log_method = getattr(logger, level, logger.info)
    console_log_method = getattr(console_logger, level, console_logger.info)

    file_log_method(message)
    console_log_method(message, extra={"source_name": logger.name})
