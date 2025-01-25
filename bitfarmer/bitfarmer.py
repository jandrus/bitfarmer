#!/usr/bin/env python3

import os
import select
import sys
import time
from datetime import datetime

from requests import exceptions
from colorama import Fore
from yaspin import yaspin

import bitfarmer.config as config
import bitfarmer.log as log
import bitfarmer.ntp as ntp
from bitfarmer.elphapex import ElphapexDG1
from bitfarmer.volcminer import VolcminerD1

# TODO:
#  + edit config GUIDED
#  + volcminer -> fans not full when stopped
#  + colors -> file
#  + fault tolerant - error handling
#  + encrypt config - at end
#  + pool api - at end
#  + make package


WAIT_TIME = 60
BANNER = """   ___  _ __  ____
  / _ )(_) /_/ __/__ _______ _  ___ ____
 / _  / / __/ _// _ `/ __/  ' \/ -_) __/
/____/_/\__/_/  \_,_/_/ /_/_/_/\__/_/
"""
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
        action_prompt += (
            f"{Fore.RED}'{action['key']}'{Fore.YELLOW} -> {action['expl']}, "
        )
    action_prompt = action_prompt[:-2]
    action_prompt += Fore.RESET
    print(action_prompt)
    print(prompt, end="", flush=True)
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
            conf = config.manually_edit_conf(conf)
        case "s":
            _ = stop_miners(conf, False, all_miners=True)
        case "r":
            _ = start_miners(conf, False, all_miners=True)
        case "x":
            print("Goodbye")
            sys.exit(0)
        case _:
            raise ValueError("Invalid action")
    return conf


def get_miners(conf: dict) -> list:
    """Get list of miner objects from config"""
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
    return miners


def get_ts(conf: dict) -> int:
    """Get timestamp"""
    try:
        return ntp.get_ts(conf["ntp"]["primary"])
    except:
        log.log_msg(f"NTP server {conf['ntp']['primary']} failed", "WARNING")
    return ntp.get_ts(conf["ntp"]["secondary"])


def is_tod_active(ts: int, conf: dict) -> bool:
    """Returns true if time of day is currently active"""
    dt = datetime.fromtimestamp(ts)
    hour = dt.hour
    weekday = dt.strftime("%A")
    date = dt.strftime("%m/%d/%Y")
    # print(f"TIMESTAMP\n\tHOUR: {hour}, DAY: {weekday}, DATE: {date}")
    return (
        weekday in conf["tod_schedule"]["days"]
        and hour in conf["tod_schedule"]["hours"]
        and date not in conf["tod_schedule"]["exceptions"]
    )


def stop_miners(conf: dict, for_tod: bool, all_miners: bool = False) -> bool:
    """stop miners"""
    miners = get_miners(conf)
    if for_tod:
        print("Stopping miners for time of day metering")
        log.log_msg("Stopping miners for time of day metering", "INFO")
    if all_miners:
        print("Stopping ALL miners")
        log.log_msg("Stopping ALL miners", "INFO")
    for miner in miners:
        if all_miners or miner.tod and for_tod:
            print(f"Stopping {miner.ip}")
            _ = miner.stop_mining()
            log.log_msg(f"{miner.ip} stopped mining", "INFO")
            miner.reboot()
            log.log_msg(f"{miner.ip} rebooted", "INFO")
    with yaspin(
        text="Miners have been stopped, waiting 2 minutess for reboot",
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
        print("Starting miners for time of day metering")
        log.log_msg("Starting miners for time of day metering", "INFO")
    if all_miners:
        print("Starting ALL miners")
        log.log_msg("Starting ALL miners", "INFO")
    for miner in miners:
        if all_miners or for_tod and miner.tod:
            print(f"Starting {miner.ip}")
            _ = miner.start_mining()
            log.log_msg(f"{miner.ip} started mining", "INFO")
    with yaspin(
        text="Miners have been started, waiting 2 minutes for configuration to reload",
        color="blue",
        timer=True,
    ) as sp:
        time.sleep(120)
        sp.ok()
    return False


def main():
    try:
        miners_have_been_stopped = False
        clear_screen()
        print(BANNER)
        conf = config.get_conf()
        while True:
            clear_screen()
            ts = get_ts(conf)
            print(Fore.GREEN + BANNER)
            print(time.ctime(ts) + Fore.RESET)
            if is_tod_active(ts, conf) and not miners_have_been_stopped:
                miners_have_been_stopped = stop_miners(conf, True)
            if not is_tod_active(ts, conf) and miners_have_been_stopped:
                miners_have_been_stopped = start_miners(conf, True)
            miners = get_miners(conf)
            for miner in miners:
                try:
                    stats = miner.get_miner_status()
                    if conf["view"] == "small":
                        stats.print_small()
                    else:
                        stats.pprint()
                    log.log_stats(str(stats))
                except Exception as e:
                    print(f"Error for {miner.ip} -> {e}")
                    log.log_msg(f"Error for {miner.ip} -> {e}", "ERROR")
            user_input = get_input("Action: ", WAIT_TIME)
            if user_input is not None:
                conf = perform_action(user_input, conf)
    except exceptions.Timeout as e:
        msg = f"Timeout error: {str(e)}"
        print(f"ERROR: {msg}")
        log.log_msg(msg, "ERROR")
    except Exception as e:
        log.log_msg(f"Unknown error: {str(e)}", "CRITICAL")
        sys.exit(1)
    except KeyboardInterrupt:
        log.log_msg("program exit by user", "INFO")
        print(f"{Fore.GREEN}Goodbye{Fore.RESET}")


if __name__ == "__main__":
    main()
