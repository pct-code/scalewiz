"""This module is for validation commands to be used with entry widgets."""


def can_be_float(s: str) -> bool:
    try:
        if float(s):
            return True
    except ValueError:
        return False


def can_be_pos_float(s: str) -> bool:
    try:
        return float(s) > 0
    except ValueError:
        return False


def can_be_pos_int(s: str) -> bool:
    try:
        return int(s) > 0
    except ValueError:
        return False
