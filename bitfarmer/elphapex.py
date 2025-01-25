#!/usr/bin/env python3


import json

import requests

from bitfarmer.miner import Miner, MinerStatus


def parse_duration(dur: float) -> str:
    """Parse duration float to string (hms)"""
    s = ""
    days = dur // 86400
    if days > 0:
        s += f"{days}d"
    hours = dur % 86400 // 3600
    if hours > 0:
        s += f"{hours}h"
    minutes = dur % 3600 // 60
    seconds = dur % 60
    return f"{s}{minutes}m{seconds}s"


class ElphapexDG1(Miner):
    """DG1+ and DG Home interface"""

    def get_miner_status(self) -> MinerStatus:
        """Gather and return MinerStatus"""
        stats_info = self.get_stats()
        net_info = self.get_network()
        full_pool_info = self.get_pool()
        pool, pool_user = "None", "None"
        pool_accepted, pool_rejected, pool_stale = 0, 0, 0
        for pool_info in full_pool_info["POOLS"]:
            if pool_info["status"] == "Alive":
                pool = pool_info["url"]
                pool_user = pool_info["user"]
                pool_accepted = pool_info["accepted"]
                pool_rejected = pool_info["rejected"]
                pool_stale = pool_info["stale"]
                break
        uptime = parse_duration(stats_info["STATUS"]["when"])
        hashrate_0 = stats_info["STATS"][0]["chain"][0]["hashrate"]
        hashrate_1 = stats_info["STATS"][0]["chain"][1]["hashrate"]
        hashrate_2 = stats_info["STATS"][0]["chain"][2]["hashrate"]
        hashrate_3 = stats_info["STATS"][0]["chain"][3]["hashrate"]
        hashrate_total_current = round(
            hashrate_0 + hashrate_1 + hashrate_2 + hashrate_3, 2
        )
        return MinerStatus(
            self.ip,
            hostname=net_info["conf_hostname"],
            miner_type=stats_info["INFO"]["type"],
            uptime=uptime,
            pool=pool,
            pool_user=pool_user,
            pool_accepted=pool_accepted,
            pool_rejected=pool_rejected,
            pool_stale=pool_stale,
            hashboards=4,
            fans=4,
            fan_0=stats_info["STATS"][0]["fan"][0],
            fan_1=stats_info["STATS"][0]["fan"][1],
            fan_2=stats_info["STATS"][0]["fan"][2],
            fan_3=stats_info["STATS"][0]["fan"][3],
            temp_0=stats_info["STATS"][0]["chain"][0]["temp_pic"][-1],
            temp_1=stats_info["STATS"][0]["chain"][1]["temp_pic"][-1],
            temp_2=stats_info["STATS"][0]["chain"][2]["temp_pic"][-1],
            temp_3=stats_info["STATS"][0]["chain"][3]["temp_pic"][-1],
            hashrate_0=hashrate_0,
            hashrate_1=hashrate_1,
            hashrate_2=hashrate_2,
            hashrate_3=hashrate_3,
            hashrate_total_current=hashrate_total_current,
            hashrate_total_avg=stats_info["STATS"][0]["rate_avg"],
        )

    def stop_mining(self) -> dict:
        """Unset mining pools"""
        payload = {
            "pools": [
                {
                    "url": "",
                    "pass": "",
                    "user": "",
                },
                {
                    "url": "",
                    "pass": "",
                    "user": "",
                },
                {
                    "url": "",
                    "pass": "",
                    "user": "",
                },
            ],
        }
        return self.post("/cgi-bin/set_miner_conf.cgi", payload)

    def start_mining(self) -> dict:
        """Set mining pools"""
        payload = {
            "pools": [
                {
                    "url": self.primary_pool,
                    "pass": self.primary_pool_pass,
                    "user": self.primary_pool_user,
                },
                {
                    "url": self.secondary_pool,
                    "pass": self.secondary_pool_pass,
                    "user": self.secondary_pool_user,
                },
                {
                    "url": "",
                    "pass": "",
                    "user": "",
                },
            ],
        }
        return self.post("/cgi-bin/set_miner_conf.cgi", payload)

    def reboot(self):
        """Reboot miner"""
        resp = requests.request(
            "GET", f"http://{self.ip}/cgi-bin/reboot.cgi", timeout=3
        )
        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()

    def get_pool(self) -> dict:
        """Get miner conf"""
        return self.get("/cgi-bin/pools.cgi")

    def get_network(self) -> dict:
        """Get miner network information"""
        return self.get("/cgi-bin/get_network_info.cgi")

    def get_stats(self) -> dict:
        """Get miner stats"""
        return self.get("/cgi-bin/stats.cgi")

    def get(self, uri: str) -> dict:
        """GET request"""
        resp = requests.request("GET", f"http://{self.ip}{uri}", timeout=3)
        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()
        return json.loads(resp.text)

    def post(self, uri: str, payload: dict) -> dict:
        """POST request"""
        payload = json.dumps(payload)
        headers = {
            "content-type": "application/json",
        }
        resp = requests.request(
            "POST",
            f"http://{self.ip}{uri}",
            headers=headers,
            data=payload,
            timeout=3,
        )
        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()
        return json.loads(resp.text)


if __name__ == "__main__":
    dg = ElphapexDG1(
        {
            "ip": "172.16.0.101",
            "type": "DG1+/DGHome",
            "login": "root",
            "password": "newsgrapefatopal",
            "tod": True,
            "primary_pool": "stratum+tcp://ltc.viabtc.io:3333",
            "primary_pool_user": "NCAV.worker1",
            "primary_pool_pass": "123",
            "secondary_pool": "",
            "secondary_pool_user": "",
            "secondary_pool_pass": "",
        }
    )
    stats = dg.get_miner_status()
    stats.pprint()
    # resp = dg.stop_mining()
    # resp = dg.start_mining()
    # print(json.dumps(resp, indent=2))
    # dg.reboot()
    # stats = dg.get_miner_status()
    # stats.pprint()
