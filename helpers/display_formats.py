
def cprint(text, color_str=None, end="\n"):
    """
    this function works like 'print' but with color
    """
    color_reset_code = '\033[0m'
    text_colors = {
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m'
    }
    color_code = text_colors.get(color_str, "")
    print(color_code + text + color_reset_code, end=end)
