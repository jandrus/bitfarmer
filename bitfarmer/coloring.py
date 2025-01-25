#!/usr/bin/env python3

from colorama import Fore

PRIMARY_COLOR = Fore.BLUE
SECONDARY_COLOR = Fore.MAGENTA
ACCENT_COLOR = Fore.CYAN


def pri_color(s: str) -> str:
    """Return string colored with primary color"""
    return f"{PRIMARY_COLOR}{s}{PRIMARY_COLOR}"


def sec_color(s: str) -> str:
    """Return string colored with secondary color"""
    return f"{SECONDARY_COLOR}{s}{PRIMARY_COLOR}"


def acc_color(s: str) -> str:
    """Return string colored with accent color"""
    return f"{ACCENT_COLOR}{s}{PRIMARY_COLOR}"


# def print_pri(s: str):
#     """Print string colored with primary color"""
