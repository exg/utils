import math


def format_size(n: int) -> str:
    if n == 0:
        return "0"
    units = ("", "K", "M", "G", "T", "P", "E", "Z", "Y")
    exp = int(math.log(n, 1024))
    size = n / (1 << (10 * exp))
    return f"{size:.2f}{units[exp]}"
