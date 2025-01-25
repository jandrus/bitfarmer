#!/usr/bin/env python3

import ntplib

NTP_CLIENT = ntplib.NTPClient()


def get_ts(server: str) -> int:
    """Get timestamp from ntp server"""
    resp = NTP_CLIENT.request(server, version=3)
    return int(resp.tx_time)


if __name__ == "__main__":
    ts = get_ts("0.us.pool.ntp.org")
    print(ts)
