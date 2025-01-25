#!/usr/bin/env python3

import json
import os
import subprocess
from datetime import datetime

import questionary as quest
from colorama import Fore
from platformdirs import user_data_dir, user_config_dir

from bitfarmer.miner import MinerStatus

AVAIL_MINERS = ["DG1+/DGHome", "VolcMiner D1"]
CONF_FILE = "conf.json"
ENC_CONF_FILE = "conf.gpg"
APP_NAME = "bitfarmer"
AUTHOR = "jimboslice"
DATA_DIR = user_data_dir(APP_NAME, AUTHOR) + "/"
CONF_DIR = user_config_dir(APP_NAME, AUTHOR) + "/"
ENCRYPT = False


def reload_config(conf: dict) -> dict:
    """write config and return new config"""
    write_config(conf)
    return read_conf()


def write_config(conf: dict):
    """write config file"""
    with open(f"{CONF_DIR}{CONF_FILE}", "w") as f:
        json.dump(conf, f, indent=4)


def read_conf() -> dict:
    """read config file"""
    conf = {}
    with open(f"{CONF_DIR}{CONF_FILE}", "r") as f:
        conf = json.load(f)
    return conf


def get_conf() -> dict:
    """Get config if exists or initialize if it does not"""
    if os.path.isfile(f"{CONF_DIR}{CONF_FILE}"):
        return read_conf()
    return init_config()


def init_config() -> dict:
    """Initialize config"""
    os.makedirs(CONF_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"{Fore.GREEN}Creating initial configuration{Fore.RESET}")
    conf = {}
    tod = confirm("\nSetup time of day schedule?")
    if tod:
        conf = setup_time_of_day(conf)
    conf = choose_view(conf)
    conf = select_editor(conf)
    conf = set_ntp(conf)
    conf = add_pool(conf)
    while True:
        add_more = confirm("\nAdd more pools?")
        if not add_more:
            break
        conf = add_pool(conf)
    conf = add_miner(conf)
    while True:
        add_more = confirm("\nAdd more miners?")
        if not add_more:
            break
        conf = add_miner(conf)
    print(json.dumps(conf, indent=2))
    write_config(conf)
    edit = confirm("\nManually make edits to config?")
    if edit:
        conf = manually_edit_conf(conf)
    return conf


def manually_edit_conf(conf: dict) -> dict:
    """Open conf file in selected editor"""
    subprocess.run([conf["editor"], f"{CONF_DIR}{CONF_FILE}"])
    return read_conf()


def set_ntp(conf: dict) -> dict:
    """Set ntp servers"""
    print(f"{Fore.GREEN}\nAdd NTP servers:{Fore.RESET}")
    pri_server_input = text("Enter primary NTP server address: ", "󱉊")
    sec_server_input = text("Enter secondary NTP server address: ", "󱉊")
    conf["ntp"] = {
        "primary": pri_server_input,
        "secondary": sec_server_input,
    }
    print(f"{Fore.GREEN}NTP servers added{Fore.RESET}")
    return conf


def setup_time_of_day(conf: dict) -> dict:
    """Setup/edit time of day configuration"""
    print(f"{Fore.GREEN}Creating time of day schedule{Fore.RESET}")
    tod_exceptions = []
    if "tod_schedule" not in conf:
        conf["tod_schedule"] = {}
    else:
        tod_exceptions = conf["tod_schedule"]["exceptions"]
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    hours = [f"{hour:02d}00" for hour in range(24)]
    tod_days = checkbox(
        "Select days NORMAL Time of Day schedule applies: ",
        days,
        "",
    )
    tod_hours = checkbox(
        "Select hours NORMAL Time of Day schedule applies (do not include hour schedule ends): ",
        hours,
        "",
    )
    tod_hours = [int(h[:-2]) for h in tod_hours]
    while True:
        add_exception = confirm("\nAdd schedule exceptions?")
        if not add_exception:
            break
        date_exception = text(
            "Enter schedule exception (use mm/dd/yyyy format): ",
            "",
            validation=validate_date,
        )
        if date_exception not in tod_exceptions:
            tod_exceptions.append(date_exception)
    print(f"{Fore.GREEN}Schedule added{Fore.RESET}")
    conf["tod_schedule"]["days"] = tod_days
    conf["tod_schedule"]["hours"] = tod_hours
    conf["tod_schedule"]["exceptions"] = tod_exceptions
    return conf


def add_miner(conf: dict) -> dict:
    """Add miner to config"""
    print(f"{Fore.GREEN}\nAdd miner:{Fore.RESET}")
    if "miners" not in conf:
        conf["miners"] = []
    ip_input = text("Enter miner IP: ", "󰩟")
    if any("ip" in v and v["ip"] == ip_input for v in conf["miners"]):
        print("miner already exists")
        return conf
    type_input = select("Select miner type: ", AVAIL_MINERS, "")
    login_input = text("Enter miner login: ", "")
    password_input = ""
    while True:
        password_input = password("Enter miner password  : ")
        password_input_conf = password("Confirm miner password: ")
        if password_input == password_input_conf:
            break
        else:
            print("Passwords do not match")
    tod_input = confirm("\nIs miner behind your Time of Day meter? ")
    pool_selections = conf["pools"].copy()
    if len(pool_selections) > 1:
        primary_pool_input = select("Select primary pool: ", pool_selections, "󰘆")
    else:
        primary_pool_input = pool_selections[0]
    pri_pool_user_input = text("Enter primary pool user: ", "")
    pri_pool_pw_input = text("Enter primary pool password: ", "")
    pool_selections.remove(primary_pool_input)
    secondary_pool_input = ""
    sec_pool_user_input = ""
    sec_pool_pw_input = ""
    if len(pool_selections) == 1:
        print(f"{Fore.GREEN}Secondary Pool: {pool_selections[0]}{Fore.RESET}")
        secondary_pool_input = pool_selections[0]
        sec_pool_user_input = text("Enter secondary pool user: ", "")
        sec_pool_pw_input = text("Enter secondary pool password: ", "")
    elif len(pool_selections) > 1:
        secondary_pool_input = select("Select secondary pool: ", pool_selections, "󰘆")
        sec_pool_user_input = text("Enter secondary pool user: ", "")
        sec_pool_pw_input = text("Enter secondary pool password: ", "")
    conf["miners"].append(
        {
            "ip": ip_input,
            "type": type_input,
            "login": login_input,
            "password": password_input,
            "tod": tod_input,
            "primary_pool": primary_pool_input,
            "primary_pool_user": pri_pool_user_input,
            "primary_pool_pass": pri_pool_pw_input,
            "secondary_pool": secondary_pool_input,
            "secondary_pool_user": sec_pool_user_input,
            "secondary_pool_pass": sec_pool_pw_input,
        }
    )
    miners = sorted(conf["miners"], key=lambda x: x.get("ip", ""))
    conf["miners"] = miners
    print(f"{Fore.GREEN}Miner added{Fore.RESET}")
    return conf


def choose_view(conf: dict) -> dict:
    """Choose view for miner status"""
    print(f"{Fore.GREEN}\nChoose view for miners:{Fore.RESET}")
    miner_stat = MinerStatus("127.0.0.1")
    print("Full")
    miner_stat.pprint()
    print("Small")
    miner_stat.print_small()
    view_input = select("Select view: ", ["small", "full"], "󱢈")
    conf["view"] = view_input
    print(f"{Fore.GREEN}View set{Fore.RESET}")
    return conf


def select_editor(conf: dict) -> dict:
    """Choose editor"""
    print(f"{Fore.GREEN}\nSelect editor for manually editing config:{Fore.RESET}")
    editor = select(
        "Select editor: ",
        ["vim", "emacs", "nano", "vi", "nvim", "notepad", "other"],
        "",
    )
    if editor == "other":
        editor = text("Enter editor: ", "")
    conf["editor"] = editor
    print(f"{Fore.GREEN}Editor set{Fore.RESET}")
    return conf


def add_pool(conf: dict) -> dict:
    """Add pools to config"""
    print(f"{Fore.GREEN}\nAdd pool:{Fore.RESET}")
    current_pools = []
    if "pools" not in conf:
        conf["pools"] = []
    else:
        current_pools = [pool["url"] for pool in conf["pools"] if "url" in pool]
        print(f"{Fore.GREEN}\nCurrent pools: {current_pools} {Fore.RESET}")
    pool_url_input = text("Enter pool url: ", "󰖟")
    conf["pools"].append(pool_url_input)
    print(f"{Fore.GREEN}Pool added{Fore.RESET}")
    return conf


def validate_date(s: str) -> bool:
    """simple empty validation"""
    if not s:
        return False
    try:
        datetime.strptime(s, "%m/%d/%Y")
    except ValueError:
        return False
    return True


def default_validate(s) -> bool:
    """simple empty validation"""
    return bool(s)


def confirm(prompt: str) -> bool:
    """Confirmation (y/n)"""
    answer = quest.confirm(prompt, qmark="").ask()
    if answer is None:
        raise KeyboardInterrupt
    return answer


def text(prompt: str, mark: str, validation=default_validate) -> str:
    """Text input"""
    answer = quest.text(prompt, qmark=mark, validate=validation).ask()
    if answer is None:
        raise KeyboardInterrupt
    return answer


def checkbox(prompt: str, options: list, mark: str, validation=default_validate) -> str:
    """Text input"""
    answer = quest.checkbox(
        prompt, options, qmark=mark, instruction="", validate=validation
    ).ask()
    if answer is None:
        raise KeyboardInterrupt
    return answer


def select(prompt: str, options: list, mark: str) -> str:
    """Text input"""
    answer = quest.select(prompt, options, qmark=mark).ask()
    if answer is None:
        raise KeyboardInterrupt
    return answer


def password(prompt: str, validation=default_validate) -> str:
    """Text input"""
    answer = quest.password(prompt, qmark="", validate=validation).ask()
    if answer is None:
        raise KeyboardInterrupt
    return answer
