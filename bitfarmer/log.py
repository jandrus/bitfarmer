#!/usr/bin/env python3

import os
import time

import bitfarmer.coloring as coloring
import bitfarmer.config as config

LOG_FILE = "bitfarmer.log"
MINER_LOG = "minerstats.csv"


def log_msg(msg: str, level: str, quiet: bool = False):
    """log information and errors"""
    with open(f"{config.DATA_DIR}{LOG_FILE}", "a", encoding="ascii") as f:
        f.write(f"{time.ctime()} - {level} - {msg}\n")
    if not quiet:
        match level:
            case "SUCCESS":
                coloring.print_success(msg)
            case "CRITICAL":
                coloring.print_error("Critical: " + msg)
            case "ERROR":
                coloring.print_error("Error: " + msg)
            case "WARNING":
                coloring.print_warn("Warning: " + msg)
            case "INFO":
                coloring.print_info(msg)
            case _:
                print(msg)


def log_stats(msg: str):
    """log miner stats"""
    if not os.path.isfile(f"{config.DATA_DIR}{MINER_LOG}"):
        with open(f"{config.DATA_DIR}{MINER_LOG}", "a", encoding="ascii") as f:
            f.write(
                "TS        , IP           , TYPE         , HOSTNAME , UPTIME      ,    HR NOW,    HR AVG,    HR 0,    HR 1,    HR 2,    HR 3, FAN 0, FAN 1, FAN 2, FAN 3, TMP 0, TMP 1, TMP 2, TMP 3, POOL                            , POOL USER\n"
            )
            f.write(f"{int(time.time())}, {msg}\n")
    else:
        with open(f"{config.DATA_DIR}{MINER_LOG}", "a", encoding="ascii") as f:
            f.write(f"{int(time.time())}, {msg}\n")
