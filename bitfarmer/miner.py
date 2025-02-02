#!/usr/bin/env python3

from abc import abstractmethod
from dataclasses import dataclass

import bitfarmer.coloring as coloring


def get_style(name: str, icons_enabled: bool):
    """get icon if enabled"""
    match name:
        case "OK":
            output = "" if icons_enabled else "OK"
            return coloring.success_color(output)
        case "ERR":
            output = "" if icons_enabled else "Err"
            return coloring.err_color(output)
        case "UPTIME":
            output = "" if icons_enabled else "Uptime:"
            return coloring.secondary_color(output)
        case "TEMP":
            output = "" if icons_enabled else "Temp:"
            return coloring.secondary_color(output)
        case "FANS":
            output = "󰈐" if icons_enabled else "Fans:"
            return coloring.secondary_color(output)
        case "POOL":
            output = "󰘆" if icons_enabled else "Pool:"
            return coloring.secondary_color(output)
        case "WORKER":
            output = "󰖵" if icons_enabled else "Worker:"
            return coloring.secondary_color(output)
        case "HR":
            output = "󰢷" if icons_enabled else "HR:"
            return coloring.secondary_color(output)
        case "ACCEPTED":
            output = "" if icons_enabled else "Accepted:"
            return coloring.secondary_color(output)
        case "REJECTED":
            output = "" if icons_enabled else "Rejected:"
            return coloring.secondary_color(output)
        case "STALE":
            output = "" if icons_enabled else "Rejected:"
            return coloring.secondary_color(output)
        case _:
            return "None"


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
                return round((self.temp_0 + self.temp_1) / 2, 1)
            case 3:
                return round((self.temp_0 + self.temp_1 + self.temp_2) / 3, 1)
            case _:
                return round(
                    (self.temp_0 + self.temp_1 + self.temp_2 + self.temp_3) / 4, 1
                )

    def get_rejection_rate(self) -> str:
        """Get rejection rate from pool"""
        return (
            f"{self.pool_rejected / (self.pool_accepted + self.pool_rejected):.2%}"
            if self.pool_accepted > 0
            else "0.0"
        )

    def print_small(self, icons: bool):
        """Print condensed status"""
        fans_ok = get_style("OK", icons) if self.fans_ok(
        ) else get_style("ERR", icons)
        pool_ok = (
            get_style("OK", icons)
            if self.pool != "None" and self.pool != "POOL_URL"
            else get_style("ERR", icons)
        )
        uptime = (
            f"{get_style('UPTIME', icons)} {coloring.info_color(self.uptime):<29} "
            if icons
            else ""
        )
        print(
            f"{coloring.primary_color(self.ip):<32} {coloring.primary_color(self.miner_type):<30} "
            + uptime
            + f"{get_style('TEMP', icons)} {coloring.info_color(self.get_avg_temp()):<15} "
            + get_style("FANS", icons)
            + " "
            + fans_ok
            + " "
            + get_style("POOL", icons)
            + " "
            + pool_ok
            + " "
            + coloring.primary_color("(Rejection %: ")
            + coloring.err_color(self.get_rejection_rate())
            + coloring.primary_color(") ")
            + get_style("HR", icons)
            + " "
            + coloring.info_color(f"{self.hashrate_total_current / 1000:,.2f} GH/s ")
            + coloring.primary_color("(Avg: ")
            + coloring.info_color(f"{self.hashrate_total_avg / 1000:,.2f} GH/s")
            + coloring.primary_color(")")
        )

    def pprint(self, icons: bool):
        """Print miner status for display"""
        print(
            f"{coloring.primary_color(self.ip):<32}  "
            + f"{coloring.primary_color(self.miner_type):<30} "
            + get_style("UPTIME", icons)
            + " "
            + coloring.info_color(self.uptime)
            + "  "
            + get_style("FANS", icons)
            + " "
            + coloring.info_color(
                f"[{self.fan_0}, {self.fan_1}, {self.fan_2}, {self.fan_3}]"
            )
            + coloring.primary_color("rpm  ")
            + get_style("TEMP", icons)
            + " "
            + coloring.info_color(
                f"[{self.temp_0}, {self.temp_1}, {self.temp_2}, {self.temp_3}]"
            )
            + coloring.primary_color("C\n")
            + f"\t\t{coloring.primary_color('Pool:'):31}"
            + get_style("POOL", icons)
            + " "
            + coloring.info_color(self.pool)
            + "  "
            + get_style("WORKER", icons)
            + " "
            + coloring.info_color(self.pool_user)
            + "\n"
            + f"\t\t{coloring.primary_color('Shares:'):31}"
            + get_style("ACCEPTED", icons)
            + " "
            + coloring.info_color(self.pool_accepted)
            + "  "
            + get_style("REJECTED", icons)
            + " "
            + coloring.info_color(self.pool_rejected)
            + "  "
            + get_style("STALE", icons)
            + " "
            + coloring.info_color(self.pool_stale)
            + coloring.primary_color("  (Rejection rate ")
            + coloring.err_color(self.get_rejection_rate())
            + coloring.primary_color(")")
            + "\n"
            + f"\t\t{coloring.primary_color('Hashrate:'):31}"
            + get_style("HR", icons)
            + " "
            + coloring.info_color(f"{self.hashrate_total_current / 1000:,.2f} GH/s")
            + coloring.primary_color(" (Avg: ")
            + coloring.info_color(f"{self.hashrate_total_avg / 1000:,.2f} GH/s")
            + coloring.primary_color(")")
        )

    def __str__(self):
        return f"{self.ip:<13}, {self.miner_type:<13}, {self.hostname:<9}, {self.uptime:<12}, {self.hashrate_total_current:9.2f}, {self.hashrate_total_avg:9.2f}, {self.hashrate_0:7.2f}, {self.hashrate_1:7.2f}, {self.hashrate_2:7.2f}, {self.hashrate_3:7.2f}, {self.fan_0:>5}, {self.fan_1:>5}, {self.fan_2:>5}, {self.fan_3:>5}, {self.temp_0:5}, {self.temp_1:5}, {self.temp_2:5}, {self.temp_3:5}, {self.pool:<32}, {self.pool_user}"


if __name__ == "__main__":
    stats = MinerStatus("127.0.0.1")
    print("FULL")
    stats.pprint(False)
    print("SMALL")
    stats.print_small(False)
