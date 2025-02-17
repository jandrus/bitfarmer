#!/usr/bin/env python3

import json
import os
import select
import sys
import time
from datetime import datetime
from typing import Optional

from yaspin import yaspin

import bitfarmer.coloring as coloring
import bitfarmer.config as config
import bitfarmer.log as log
import bitfarmer.ntp as ntp
import bitfarmer.weather as weather
from bitfarmer.elphapex import ElphapexDG1
from bitfarmer.volcminer import VolcminerD1
from bitfarmer.weather import Weather

# TODO:
#   - get weather
#       + handle errors
#       + run hourly
#   - log weather
#   - log levels -> enum
#   - Miner types -> enum
#   - Temp Control

WAIT_TIME = 60
BANNER = """   ___  _ __  ____
  / _ )(_) /_/ __/__ _______ _  ___ ____
 / _  / / __/ _// _ `/ __/  ' \\/ -_) __/
/____/_/\\__/_/  \\_,_/_/ /_/_/_/\\__/_/"""
ACTIONS = [
    {"key": "a", "expl": "add miner"},
    {"key": "e", "expl": "edit config"},
    {"key": "s", "expl": "stop mining"},
    {"key": "r", "expl": "resume mining/apply config"},
    {"key": "x", "expl": "exit"},
]


def clear_screen():
    """Clear terminal"""
    os.system("cls" if os.name == "nt" else "clear")


def get_input(prompt: str, timeout: int) -> str | None:
    """Get user input with timeout"""
    action_prompt = ""
    for action in ACTIONS:
        action_prompt += coloring.secondary_color(
            "'" + action["key"] + "'"
        ) + coloring.primary_color(f" -> {action['expl']}, ")
    print(action_prompt)
    print(coloring.primary_color(prompt), end="", flush=True)
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if rlist:
        return sys.stdin.readline().strip().lower()
    return None


def perform_action(action: str, conf: dict) -> dict:
    """Perform actions by user"""
    match action:
        case "a":
            conf = config.add_miner(conf)
            conf = config.reload_config(conf)
        case "e":
            conf = config.edit_conf(conf)
            conf = config.reload_config(conf)
        case "s":
            _ = stop_miners(conf, False, all_miners=True)
        case "r":
            _ = start_miners(conf, False, all_miners=True)
        case "x":
            coloring.print_success("Goodbye")
            sys.exit(0)
        case _:
            coloring.print_warn("Invalid action")
            time.sleep(3)
    return conf


def get_miners(conf: dict) -> list:
    """Get list of miner objects from config"""
    log.log_msg("Gathering miners", "INFO", quiet=True)
    miners = []
    for miner_conf in conf["miners"]:
        match miner_conf["type"]:
            case "DG1+/DGHome":
                miners.append(ElphapexDG1(miner_conf))
            case "VolcMiner D1":
                miners.append(VolcminerD1(miner_conf))
            case _:
                raise ValueError(
                    f"Invalid miner type in config: {miner_conf['type']} - {miner_conf['ip']}"
                )
    log.log_msg("Gathering miners", "SUCCESS", quiet=True)
    return miners


def get_ts(conf: dict) -> int:
    """Get timestamp"""
    log.log_msg("Gathering time", "INFO", quiet=True)
    try:
        return ntp.get_ts(conf["ntp"]["primary"])
    except:
        log.log_msg(f"NTP server {conf['ntp']['primary']} failed", "WARNING")
    try:
        return ntp.get_ts(conf["ntp"]["secondary"])
    except:
        log.log_msg(f"NTP server {conf['ntp']['secondary']} failed", "WARNING")
    return int(time.time())


def is_tod_active(ts: int, conf: dict) -> bool:
    """Returns true if time of day is currently active"""
    dt = datetime.fromtimestamp(ts)
    hour = dt.hour
    weekday = dt.strftime("%A")
    date = dt.strftime("%m/%d/%Y")
    return (
        weekday in conf["tod_schedule"]["days"]
        and hour in conf["tod_schedule"]["hours"]
        and date not in conf["tod_schedule"]["exceptions"]
    )


def stop_miners(conf: dict, for_tod: bool, all_miners: bool = False) -> bool:
    """stop miners"""
    miners = get_miners(conf)
    if for_tod:
        log.log_msg("Stopping miners for time of day metering", "INFO")
    if all_miners:
        log.log_msg("Stopping ALL miners", "INFO")
    for miner in miners:
        try:
            if all_miners or miner.tod and for_tod:
                coloring.print_warn(f"Stopping {miner.ip}")
                _ = miner.stop_mining()
                log.log_msg(f"{miner.ip} stopped mining", "INFO")
                miner.reboot()
                log.log_msg(f"{miner.ip} rebooted", "INFO")
        except Exception as e:
            log.log_msg(f"Error stopping {miner.ip}", "ERROR", exc=e)
    with yaspin(
        text=coloring.info_color(
            "Miners have been stopped, waiting 2 minutess for reboot"
        ),
        color="blue",
        timer=True,
    ) as sp:
        time.sleep(120)
        sp.ok()
    return True


def start_miners(conf: dict, for_tod: bool, all_miners: bool = False) -> bool:
    """start miners"""
    miners = get_miners(conf)
    if for_tod:
        log.log_msg("Starting miners for time of day metering", "INFO")
    if all_miners:
        log.log_msg("Starting ALL miners", "INFO")
    for miner in miners:
        try:
            if all_miners or for_tod and miner.tod:
                coloring.print_info(f"Starting {miner.ip}")
                _ = miner.start_mining()
                log.log_msg(f"{miner.ip} started mining", "INFO")
        except Exception as e:
            log.log_msg(f"Error starting {miner.ip}", "ERROR", exc=e)
    with yaspin(
        text=coloring.info_color(
            "Miners have been started, waiting 2 minutes for configuration to reload"
        ),
        color="blue",
        timer=True,
    ) as sp:
        time.sleep(120)
        sp.ok()
    return False


def show_weather(conf: dict, wtr: str, ts: int) -> str:
    """Show weather on hourly basis"""
    if ts % 3600 // 60 == 0 or wtr == "":
        wtr = get_weather(conf)
        log.log_weather(wtr)
    return wtr


def get_weather(conf: dict) -> str:
    """Get weather and log errors"""
    try:
        log.log_msg("Gathering weather", "INFO", quiet=True)
        wtr = weather.get_weather(conf)
        return str(wtr)
    except:
        log.log_msg(
            f"Unable to gather weather for {conf['weather']['area']}", "WARNING"
        )
        return ""


def main():
    try:
        log.log_msg("Startup", "INFO", quiet=True)
        miners_have_been_stopped = False
        log.log_msg("Gathering configuration", "INFO", quiet=True)
        conf = config.get_conf()
        miners = get_miners(conf)
        # wtr_str = get_weather(conf)
        while True:
            clear_screen()
            ts = get_ts(conf)
            coloring.print_primary(BANNER)
            coloring.print_info(time.ctime(ts))
            # wtr_str = show_weather(conf, wtr_str, ts)
            # if wtr_str:
            #     print(wtr_str)
            if is_tod_active(ts, conf) and not miners_have_been_stopped:
                try:
                    miners_have_been_stopped = stop_miners(conf, True)
                except Exception as e:
                    log.log_msg("Error stopping miners", "ERROR", exc=e)
                    time.sleep(5)
            if not is_tod_active(ts, conf) and miners_have_been_stopped:
                try:
                    miners_have_been_stopped = start_miners(conf, True)
                except Exception as e:
                    log.log_msg("Error starting miners", "ERROR", exc=e)
                    time.sleep(5)
            for miner in miners:
                if not config.ping(miner.ip):
                    log.log_msg(f"{miner.ip} not pingable", "ERROR")
                    continue
                try:
                    stats = miner.get_miner_status()
                    if conf["view"] == "small":
                        stats.print_small(conf["icons"])
                    else:
                        stats.pprint(conf["icons"])
                    log.log_stats(str(stats))
                except Exception as e:
                    log.log_msg(
                        f"Error gathering data for {miner.ip}", "ERROR", exc=e)
                    time.sleep(5)
            user_input = get_input("Action: ", WAIT_TIME)
            if user_input is not None:
                conf = perform_action(user_input, conf)
                miners = get_miners(conf)
    except json.JSONDecodeError as e:
        log.log_msg("Config error", "CRITICAL", exc=e)
        sys.exit(1)
    except KeyboardInterrupt:
        log.log_msg("program exit by user", "INFO", quiet=True)
        coloring.print_success("Goodbye")
    except Exception as e:
        log.log_msg("Unknown error", "CRITICAL", exc=e)
        sys.exit(1)


if __name__ == "__main__":
    main()
