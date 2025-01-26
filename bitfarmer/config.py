#!/usr/bin/env python3

import json
import os
import subprocess
from datetime import datetime

import questionary as quest
from platformdirs import user_config_dir, user_data_dir

import bitfarmer.coloring as coloring
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
    coloring.print_primary("Creating initial configuration")
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
    write_config(conf)
    coloring.print_secondary(json.dumps(conf, indent=2))
    edit = confirm("\nManually make edits to config?")
    if edit:
        conf = manually_edit_conf(conf)
    coloring.print_success("Configuration created")
    return conf


def edit_conf(conf: dict) -> dict:
    """Edit configuration manually or guided"""
    how_edit = select("Edit config manually or guided: ",
                      ["guided", "manual"], "?")
    if how_edit == "manual":
        return manually_edit_conf(conf)
    avail_params = [
        "time of day",
        "view",
        "ntp servers",
        "available pools",
        "add miner",
        "delete miners",
        "editor",
        "DONE",
    ]
    while True:
        edit_param = select("Select parameter to edit: ", avail_params, "?")
        match edit_param:
            case "time of day":
                conf = setup_time_of_day(conf)
            case "view":
                conf = choose_view(conf)
            case "ntp servers":
                conf = set_ntp(conf)
            case "available pools":
                conf = add_pool(conf)
            case "add miner":
                conf = add_miner(conf)
            case "delete miners":
                conf = delete_miners(conf)
            case "editor":
                conf = select_editor(conf)
            case _:
                break
    coloring.print_success("Configuration edited successfully")
    return reload_config(conf)


def manually_edit_conf(conf: dict) -> dict:
    """Open conf file in selected editor"""
    subprocess.run([conf["editor"], f"{CONF_DIR}{CONF_FILE}"])
    return read_conf()


def set_ntp(conf: dict) -> dict:
    """Set ntp servers"""
    coloring.print_primary("Set NTP servers")
    pri_server_input = text("Enter primary NTP server address: ", "󱉊")
    sec_server_input = text("Enter secondary NTP server address: ", "󱉊")
    conf["ntp"] = {
        "primary": pri_server_input,
        "secondary": sec_server_input,
    }
    coloring.print_success("NTP servers added")
    return conf


def setup_time_of_day(conf: dict) -> dict:
    """Setup/edit time of day configuration"""
    coloring.print_primary("Create Time of Day schedule")
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
    if tod_exceptions:
        coloring.print_info(f"Current Exceptions: {tod_exceptions}")
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
    conf["tod_schedule"]["days"] = tod_days
    conf["tod_schedule"]["hours"] = tod_hours
    conf["tod_schedule"]["exceptions"] = tod_exceptions
    coloring.print_success("Time of Day schedule created")
    return conf


def add_miner(conf: dict) -> dict:
    """Add miner to config"""
    coloring.print_primary("Add miner")
    if "miners" not in conf:
        conf["miners"] = []
    ip_input = text("Enter miner IP: ", "󰩟")
    if any("ip" in v and v["ip"] == ip_input for v in conf["miners"]):
        coloring.print_warn("Miner IP already exists")
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
            coloring.print_warn("Passwords do not match")
    tod_input = confirm("\nIs miner behind your Time of Day meter? ")
    pool_selections = conf["pools"].copy()
    if len(pool_selections) > 1:
        primary_pool_input = select(
            "Select primary pool: ", pool_selections, "󰘆")
    else:
        primary_pool_input = pool_selections[0]
    pri_pool_user_input = text("Enter primary pool user: ", "")
    pri_pool_pw_input = text("Enter primary pool password: ", "")
    pool_selections.remove(primary_pool_input)
    secondary_pool_input = ""
    sec_pool_user_input = ""
    sec_pool_pw_input = ""
    if len(pool_selections) == 1:
        coloring.print_info(f"Secondary Pool: {pool_selections[0]}")
        secondary_pool_input = pool_selections[0]
        sec_pool_user_input = text("Enter secondary pool user: ", "")
        sec_pool_pw_input = text("Enter secondary pool password: ", "")
    elif len(pool_selections) > 1:
        secondary_pool_input = select(
            "Select secondary pool: ", pool_selections, "󰘆")
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
    coloring.print_success("Miner added")
    return conf


def choose_view(conf: dict) -> dict:
    """Choose view for miner status"""
    coloring.print_primary("Choose view for miners")
    miner_stat = MinerStatus("127.0.0.1")
    coloring.print_info("Full")
    miner_stat.pprint()
    coloring.print_info("Small")
    miner_stat.print_small()
    view_input = select("Select view: ", ["small", "full"], "󱢈")
    conf["view"] = view_input
    coloring.print_success("View set")
    return conf


def select_editor(conf: dict) -> dict:
    """Choose editor"""
    coloring.print_primary("Select editor for manually editing config")
    editor = select(
        "Select editor: ",
        ["vim", "emacs", "nano", "vi", "nvim", "notepad", "other"],
        "",
    )
    if editor == "other":
        editor = text("Enter editor: ", "")
    conf["editor"] = editor
    coloring.print_success("Editor set")
    return conf


def add_pool(conf: dict) -> dict:
    """Add pools to config"""
    coloring.print_primary("Add mining pools")
    current_pools = []
    if "pools" not in conf:
        conf["pools"] = []
    else:
        current_pools = [pool["url"]
                         for pool in conf["pools"] if "url" in pool]
        coloring.print_info(f"Current pools: {current_pools}")
    pool_url_input = text("Enter pool url: ", "󰖟")
    conf["pools"].append(pool_url_input)
    coloring.print_success("Pool added")
    return conf


def delete_miners(conf: dict) -> dict:
    """Delete miners from config"""
    if "miners" not in conf.keys():
        coloring.print_warn("No miners to delete")
        return conf
    current_ips = [conf["miners"][i]["ip"] for i in range(len(conf["miners"]))]
    del_ips = checkbox("Choose miners to delete: ", current_ips, "󰗨")
    coloring.print_warn(f"Delete miners: {del_ips}")
    if confirm("Are you sure you want to delete these miners?"):
        miners = []
        for miner in conf["miners"]:
            if miner["ip"] not in del_ips:
                miners.append(miner)
        conf["miners"] = miners
    coloring.print_success("Miners deleted")
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
        prompt,
        options,
        qmark=mark,
        instruction="(Spacebar to select/deselect)",
        validate=validation,
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


if __name__ == "__main__":
    try:
        conf = read_conf()
        print(json.dumps(conf, indent=2))
    except Exception as e:
        print(f"{type(e).__name__} -> {str(e)}")
