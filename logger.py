from enum import StrEnum


class Logger:

    class LogLevel(StrEnum):
        INFO = "INFO"
        DEBUG = "DEBUG"
        WARNING = "WARNING"
        ERROR = "ERROR"

    @staticmethod
    def log(
        message: str,
        level: LogLevel = LogLevel.INFO,
    ) -> None:
        match level:
            case Logger.LogLevel.INFO:
                coloring = "\033[94m"
            case Logger.LogLevel.DEBUG:
                coloring = "\033[92m"
            case Logger.LogLevel.WARNING:
                coloring = "\033[93m"
            case Logger.LogLevel.ERROR:
                coloring = "\033[91m"
        print(f"[{coloring}{level}\033[0m] {message}")

    @staticmethod
    def info(message: str) -> None:
        Logger.log(message, Logger.LogLevel.INFO)

    @staticmethod
    def debug(message: str) -> None:
        Logger.log(message, Logger.LogLevel.DEBUG)

    @staticmethod
    def warning(message: str) -> None:
        Logger.log(message, Logger.LogLevel.WARNING)

    @staticmethod
    def error(message: str) -> None:
        Logger.log(message, Logger.LogLevel.ERROR)
