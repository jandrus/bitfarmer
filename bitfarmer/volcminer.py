#!/usr/bin/env python3


import json
from urllib.parse import urlencode

import requests
from requests.auth import HTTPDigestAuth

from bitfarmer.miner import Miner, MinerStatus


def parse_volc_resp(text: str) -> dict:
    """Parse json responses for volcminers"""
    text = text.replace('"{', "{")
    text = text.replace('}"', "}")
    text = text.replace('"[', "[")
    text = text.replace(']"', "]")
    return json.loads(text)


def parse_to_int(s: str) -> int:
    """Parse int"""
    return int(s.replace(",", ""))


def parse_to_float(s: str, precision: int = 2) -> float:
    """Parse float"""
    return round(float(s.replace(",", "")), precision)


class VolcminerD1(Miner):
    """VolcMiner D1 interface"""

    def get_miner_status(self) -> MinerStatus:
        """Gather and return MinerStatus"""
        status_info = self.get_status()
        sys_info = self.get_system()
        pool, pool_user = "None", "None"
        pool_accepted, pool_rejected, pool_stale = 0, 0, 0
        for pool_info in status_info["data"]["pools"]["pool_dtls"]:
            if pool_info["status"] == "Alive":
                pool = pool_info["url"]
                pool_user = pool_info["user"]
                pool_accepted = parse_to_int(pool_info["accepted"])
                pool_rejected = parse_to_int(pool_info["rejected"])
                pool_stale = parse_to_int(pool_info["stale"])
                break
        temp_0, temp_1, temp_2 = 0, 0, 0
        hashrate_0, hashrate_1, hashrate_2 = 0.0, 0.0, 0.0
        for chain_info in status_info["data"]["chains"]:
            match chain_info["index"]:
                case "1":
                    temp_0 = parse_to_int(chain_info["temp"])
                    hashrate_0 = parse_to_float(chain_info["chain_rate"])
                case "2":
                    temp_1 = parse_to_int(chain_info["temp"])
                    hashrate_1 = parse_to_float(chain_info["chain_rate"])
                case "3":
                    temp_2 = parse_to_int(chain_info["temp"])
                    hashrate_2 = parse_to_float(chain_info["chain_rate"])
                case _:
                    pass
        hashrate_total_current = round(hashrate_0 + hashrate_1 + hashrate_2, 2)
        return MinerStatus(
            self.ip,
            hostname=sys_info["data"]["hostname"],
            miner_type=sys_info["data"]["minertype"],
            uptime=status_info["data"]["elapsed"],
            pool=pool,
            pool_user=pool_user,
            pool_accepted=pool_accepted,
            pool_rejected=pool_rejected,
            pool_stale=pool_stale,
            hashboards=3,
            fans=4,
            fan_0=parse_to_int(status_info["data"]["fan"]["fan1"]),
            fan_1=parse_to_int(status_info["data"]["fan"]["fan2"]),
            fan_2=parse_to_int(status_info["data"]["fan"]["fan3"]),
            fan_3=parse_to_int(status_info["data"]["fan"]["fan4"]),
            temp_0=temp_0,
            temp_1=temp_1,
            temp_2=temp_2,
            hashrate_0=hashrate_0,
            hashrate_1=hashrate_1,
            hashrate_2=hashrate_2,
            hashrate_total_current=hashrate_total_current,
            hashrate_total_avg=parse_to_float(status_info["data"]["ghsav"]),
        )

    def set_nonetrun(self):
        """Set nonetwork_run to 0 prior to miner config changes"""
        payload = {"_bb_nonetwork_run": 0}
        _ = self.post("/cgi-bin/set_nonetworkrun_mode.cgi", payload)

    def stop_mining(self) -> dict:
        """Unset mining pools"""
        self.set_nonetrun()
        payload = {
            "_bb_pool1url": "",
            "_bb_pool1user": "",
            "_bb_pool1pw": "",
            "_bb_pool2url": "",
            "_bb_pool2user": "",
            "_bb_pool2pw": "",
            "_bb_pool3url": "",
            "_bb_pool3user": "",
            "_bb_pool3pw": "",
            "_bb_nobeeper": "",
            "_bb_notempoverctrl": "true",
            "_bb_fan_customize_switch": "true",
            "_bb_fan_customize_value_front": "0",
            "_bb_fan_customize_value_back": "20",
            "_bb_freq": "1900",
            "_bb_coin_type": "ltc",
            "_bb_runmode": "0",
            "_bb_voltage_customize_value": "1245",
            "_bb_ema": "3",
            "_bb_debug": "false",
        }
        return self.post("/cgi-bin/set_miner_conf.cgi", payload)

    def start_mining(self) -> dict:
        """Set mining pools"""
        self.set_nonetrun()
        payload = {
            "_bb_pool1url": self.primary_pool,
            "_bb_pool1user": self.primary_pool_user,
            "_bb_pool1pw": self.primary_pool_pass,
            "_bb_pool2url": self.secondary_pool,
            "_bb_pool2user": self.secondary_pool_user,
            "_bb_pool2pw": self.secondary_pool_pass,
            "_bb_pool3url": "",
            "_bb_pool3user": "",
            "_bb_pool3pw": "",
            "_bb_nobeeper": "",
            "_bb_notempoverctrl": "true",
            "_bb_fan_customize_switch": "false",
            "_bb_fan_customize_value_front": "",
            "_bb_fan_customize_value_back": "",
            "_bb_freq": "1900",
            "_bb_coin_type": "ltc",
            "_bb_runmode": "0",
            "_bb_voltage_customize_value": "1245",
            "_bb_ema": "3",
            "_bb_debug": "false",
        }
        return self.post("/cgi-bin/set_miner_conf.cgi", payload)

    def reboot(self):
        """Reboot miner"""
        headers = {
            "Content-Length": "0",
            "Accept": "applicaton/json",
        }
        resp = requests.request(
            "POST",
            f"http://{self.ip}/cgi-bin/reboot.cgi",
            headers=headers,
            auth=HTTPDigestAuth(self.login, self.password),
            timeout=20,
        )
        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()

    def get_system(self) -> dict:
        """Get miner system info"""
        return self.get("/cgi-bin/get_system_infoV1.cgi")

    def get_status(self) -> dict:
        """Get miner status"""
        return self.get("/cgi-bin/get_miner_statusV1.cgi")

    def get_miner_conf(self) -> dict:
        """Get miner status USED FOR TESTING"""
        return self.get("/cgi-bin/get_miner_conf.cgi")

    def get(self, uri: str) -> dict:
        """GET request"""
        headers = {"Content-Length": "0"}
        resp = requests.request(
            "GET",
            f"http://{self.ip}{uri}",
            headers=headers,
            auth=HTTPDigestAuth(self.login, self.password),
            timeout=3,
        )
        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()
        return parse_volc_resp(resp.text)

    def post(self, uri: str, payload: dict) -> dict:
        """POST request (form)"""
        payload = urlencode(payload).encode("utf-8")
        headers = {
            "Content-Length": str(len(payload)),
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "applicaton/json",
        }
        resp = requests.request(
            "POST",
            f"http://{self.ip}{uri}",
            headers=headers,
            data=payload,
            auth=HTTPDigestAuth(self.login, self.password),
            timeout=20,
        )
        if resp.status_code != requests.codes.ok:
            resp.raise_for_status()
        return parse_volc_resp(resp.text)


if __name__ == "__main__":
    volc = VolcminerD1(
        {
            "ip": "172.16.0.105",
            "type": "test",
            "login": "root",
            "password": "newsgrapefatopal",
            "tod": True,
            "primary_pool": "stratum+tcp://americas.mining-dutch.nl:8888",
            "primary_pool_user": "avandy.worker5",
            "primary_pool_pass": "d=1920000",
            "secondary_pool": "stratum+tcp://ltc.viabtc.io:3333",
            "secondary_pool_user": "NCAV.worker5",
            "secondary_pool_pass": "123",
        }
    )
    stats = volc.get_miner_status()
    stats.pprint()
    # conf = volc.get_miner_conf()
    # print(json.dumps(conf, indent=2))

    # resp = volc.stop_mining()
    # resp = volc.start_mining()
    # print(json.dumps(resp, indent=2))

    # volc.reboot()

    # conf = volc.get_miner_conf()
    # print(json.dumps(conf, indent=2))
