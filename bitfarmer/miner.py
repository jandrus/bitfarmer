#!/usr/bin/env python3

from abc import abstractmethod
from dataclasses import dataclass

from colorama import Fore

PRIMARY_COLOR = Fore.BLUE
SECONDARY_COLOR = Fore.MAGENTA
ACCENT_COLOR = Fore.CYAN


def sec_color(s):
    return f"{SECONDARY_COLOR}{s}{PRIMARY_COLOR}"


def acc_color(s):
    return f"{ACCENT_COLOR}{s}{PRIMARY_COLOR}"


class Miner:
    """Master miner class"""

    def __init__(self, conf: dict):
        self.ip = conf["ip"]
        self.login = conf["login"]
        self.password = conf["password"]
        self.tod = conf["tod"]
        self.primary_pool = conf["primary_pool"]
        self.primary_pool_user = conf["primary_pool_user"]
        self.primary_pool_pass = conf["primary_pool_pass"]
        self.secondary_pool = conf["secondary_pool"]
        self.secondary_pool_user = conf["secondary_pool_user"]
        self.secondary_pool_pass = conf["secondary_pool_pass"]

    @abstractmethod
    def get_miner_status(self):
        """Abstract method to be implemented by subclasses"""
        pass

    @abstractmethod
    def stop_mining(self):
        """Abstract method to be implemented by subclasses"""
        pass

    @abstractmethod
    def start_mining(self):
        """Abstract method to be implemented by subclasses"""
        pass

    @abstractmethod
    def reboot(self):
        """Abstract method to be implemented by subclasses"""
        pass


@dataclass
class MinerStatus:
    ip: str
    hostname: str = "HOSTNAME"
    miner_type: str = "MINER_TYPE"
    uptime: str = "uptime"
    pool: str = "POOL_URL"
    pool_user: str = "POOL_WORKER_NAME"
    pool_accepted: int = 0
    pool_rejected: int = 0
    pool_stale: int = 0
    hashboards: int = 0
    fans: int = 0
    fan_0: int = 0
    fan_1: int = 0
    fan_2: int = 0
    fan_3: int = 0
    temp_0: int = 0
    temp_1: int = 0
    temp_2: int = 0
    temp_3: int = 0
    hashrate_0: float = 0.0
    hashrate_1: float = 0.0
    hashrate_2: float = 0.0
    hashrate_3: float = 0.0
    hashrate_total_current: float = 0.0
    hashrate_total_avg: float = 0.0

    def fans_ok(self) -> bool:
        """Get fan status for system"""
        match self.hashboards:
            case 0:
                return False
            case 1:
                return self.fan_0 != 0
            case 2:
                return self.fan_0 != 0 and self.fan_1 != 0
            case 3:
                return self.fan_0 != 0 and self.fan_1 != 0 and self.fan_2 != 0
            case _:
                return (
                    self.fan_0 != 0
                    and self.fan_1 != 0
                    and self.fan_2 != 0
                    and self.fan_3 != 0
                )

    def get_avg_temp(self) -> float:
        """Get average temp for system"""
        match self.hashboards:
            case 0:
                return 0.0
            case 1:
                return self.temp_0
            case 2:
                return round((self.temp_0 + self.temp_1) / 2, 2)
            case 3:
                return round((self.temp_0 + self.temp_1 + self.temp_2) / 3, 2)
            case _:
                return round(
                    (self.temp_0 + self.temp_1 + self.temp_2 + self.temp_3) / 4, 2
                )

    def print_small(self):
        """Print condensed status"""
        current_hr = f"{self.hashrate_total_current / 1000:,.2f} GH/s"
        avg_hr = f"{self.hashrate_total_avg / 1000:,.2f} GH/s"
        fans_ok = "" if self.fans_ok() else ""
        pool_ok = "" if self.pool != "None" else ""
        avg_temp = self.get_avg_temp()
        info = f"{self.ip:<13} {self.miner_type:<13}   {sec_color(self.uptime):<22}   {sec_color(avg_temp):<15}   󰈐 {sec_color(fans_ok)}  Pool {sec_color(pool_ok)}    {sec_color(current_hr)}  (Avg: {sec_color(avg_hr)})"
        print(PRIMARY_COLOR + info + Fore.RESET)

    def pprint(self):
        """Print miner status for display"""
        current_hr = f"{self.hashrate_total_current / 1000:,.2f} GH/s"
        avg_hr = f"{self.hashrate_total_avg / 1000:,.2f} GH/s"
        rejection_rate = (
            f"{self.pool_rejected / (self.pool_accepted + self.pool_rejected):.2%}"
            if self.pool_accepted > 0
            else "0.0"
        )
        header = f"{self.ip:<13}   {self.hostname:<10} [{acc_color(self.miner_type)}]  {sec_color('')} {acc_color(self.uptime)}\n"
        pool = f"\t\tPool:     {sec_color('󰢷')} {acc_color(self.pool)}  {sec_color('󰖵')} {acc_color(self.pool_user)}\n"
        shares = f"\t\tShares:   {sec_color('')} {acc_color(self.pool_accepted)}  {sec_color('')} {acc_color(self.pool_rejected)}  {sec_color('')} {acc_color(self.pool_stale)}  (Rejection rate {acc_color(rejection_rate)})\n"
        hashrate = f"\t\tHashrate: {sec_color('')} {acc_color(current_hr)}  (Avg: {acc_color(avg_hr)})\n"
        hardware = f"\t\tHardware: {sec_color('󰈐')} [{acc_color(self.fan_0)}, {acc_color(self.fan_1)}, {acc_color(self.fan_2)}, {acc_color(self.fan_3)}]rpm  {sec_color('')} [{acc_color(self.temp_0)}, {acc_color(self.temp_1)}, {acc_color(self.temp_2)}, {acc_color(self.temp_3)}]C"
        print(PRIMARY_COLOR + header + pool + shares + hashrate + hardware + Fore.RESET)

    def __str__(self):
        return f"{self.ip:<13}, {self.miner_type:<13}, {self.hostname:<9}, {self.uptime:<12}, {self.hashrate_total_current:9.2f}, {self.hashrate_total_avg:9.2f}, {self.hashrate_0:7.2f}, {self.hashrate_1:7.2f}, {self.hashrate_2:7.2f}, {self.hashrate_3:7.2f}, {self.fan_0:>5}, {self.fan_1:>5}, {self.fan_2:>5}, {self.fan_3:>5}, {self.temp_0:5}, {self.temp_1:5}, {self.temp_2:5}, {self.temp_3:5}, {self.pool:<32}, {self.pool_user}"
