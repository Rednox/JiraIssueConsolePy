import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger with a simple, consistent formatter.

    Call this early in CLI entrypoints or in tests if you need predictable logging.
    """
    numeric = getattr(logging, level.upper(), logging.INFO)
    handler = logging.StreamHandler()
    fmt = "%(asctime)s %(levelname)s %(name)s - %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    root = logging.getLogger()
    root.setLevel(numeric)
    if not root.handlers:
        root.addHandler(handler)
