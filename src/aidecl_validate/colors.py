import sys

GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
RESET = "\033[0m"

_enabled = True


def disable():
    global _enabled
    _enabled = False


def colorize(text, color):
    if not _enabled or not sys.stdout.isatty():
        return text
    return f"{color}{text}{RESET}"
