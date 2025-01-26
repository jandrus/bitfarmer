#!/usr/bin/env python3

from colorama import Fore, Style

PRIMARY_COLOR = Fore.BLUE + Style.BRIGHT
SECONDARY_COLOR = Fore.MAGENTA + Style.BRIGHT
INFO_COLOR = Fore.CYAN + Style.BRIGHT
SUCCESS_COLOR = Fore.GREEN + Style.BRIGHT
WARNING_COLOR = Fore.YELLOW + Style.BRIGHT
ERROR_COLOR = Fore.RED + Style.BRIGHT


def primary_color(s: str) -> str:
    """Return string colored with primary color"""
    return f"{PRIMARY_COLOR}{s}{Fore.RESET}{Style.RESET_ALL}"


def secondary_color(s: str) -> str:
    """Return string colored with secondary color"""
    return f"{SECONDARY_COLOR}{s}{Fore.RESET}{Style.RESET_ALL}"


def info_color(s: str) -> str:
    """Return string colored with info color"""
    return f"{INFO_COLOR}{s}{Fore.RESET}{Style.RESET_ALL}"


def success_color(s: str) -> str:
    """Return string colored with success color"""
    return f"{SUCCESS_COLOR}{s}{Fore.RESET}{Style.RESET_ALL}"


def warn_color(s: str) -> str:
    """Return string colored with warning color"""
    return f"{WARNING_COLOR}{s}{Fore.RESET}{Style.RESET_ALL}"


def err_color(s: str) -> str:
    """Return string colored with error color"""
    return f"{ERROR_COLOR}{s}{Fore.RESET}{Style.RESET_ALL}"


def print_primary(s: str):
    """Print string colored with primary color"""
    print(primary_color(s))


def print_secondary(s: str):
    """Print string colored with secondary color"""
    print(secondary_color(s))


def print_info(s: str):
    """Print string colored with info color"""
    print(info_color(s))


def print_success(s: str):
    """Print string colored with success color"""
    print(success_color(s))


def print_warn(s: str):
    """Print string colored with warning color"""
    print(warn_color(s))


def print_error(s: str):
    """Print string colored with error color"""
    print(err_color(s))


if __name__ == "__main__":
    print_primary("End the Fed -> Primary color")
    print_secondary("End the Fed -> Secondary color")
    print_info("End the Fed -> Info color")
    print_success("End the Fed -> Success color")
    print_warn("End the Fed -> Warning color")
    print_error("End the Fed -> Error color")
