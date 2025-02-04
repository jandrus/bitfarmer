<div align="center">
  <h1>bitfarmer :man_farmer:</h1>
  <h2>CLI ASIC Manager</h2>
</div>

## Features :sparkles:
 - Terminal based
 - Time of Day ASIC management
 - Manual ASIC management
 - Manage Pools
 - Status Logging and Printout
 
## Supported Miners :robot:
 - Elphapex DG1
 - Elphapex DG1+
 - Elphapex DG Home
 - Volcminer D1
 - Volcminer D1 Lite

## Demo
<img src="https://github.com/jandrus/bitfarmer/blob/main/demo/status.png?raw=true">
<img src="https://github.com/jandrus/bitfarmer/blob/main/demo/stopping_tod.png?raw=true">
<img src="https://github.com/jandrus/bitfarmer/blob/main/demo/edit_conf.png?raw=true">

## Installation

## Logs :file_cabinet:

### bitfarmer.log
The log file is located at:
 - Linux: `$HOME/.local/share/bitfarmer/bitfarmer.log`
 
Contains `INFO`, `WARNING`, `ERROR`, and `CRITICAL` messages. Detailed troubleshooting messages can be found here.


### minerstats.csv
The stats file is located at:
 - Linux: `$HOME/.local/share/bitfarmer/minerstats.csv`

Contains miner parameters in CSV format. Stats logged are as follows:

``` csv
TS        , IP           , TYPE         , HOSTNAME , UPTIME      ,    HR NOW,    HR AVG,    HR 0,    HR 1,    HR 2,    HR 3, FAN 0, FAN 1, FAN 2, FAN 3, TMP 0, TMP 1, TMP 2, TMP 3, POOL                            , POOL USER
1737674539, 172.16.0.101 , DG1+         , DG1plus-1, 28m33s      ,      0.00,      0.00,    0.00,    0.00,    0.00,    0.00,  3420,  3420,  3480,  3480,    66,    66,    66,    66, stratum+tcp://ltc.viabtc.io:3333, XXXX.worker1
1737674543, 172.16.0.105 , VolcMiner D1 , VolcMiner, 14m47s      ,  15386.02,  15409.69, 5126.88, 5175.20, 5083.94,    0.00,  3300,  3240,  3210,  3240,    60,    62,    61,     0, stratum+tcp://ltc.viabtc.io:3333, XXXX.worker5
```

`

## Configuration
`bitfarmer` can be configured through the guided prompts or manually with the editor provided. If no configuration has been saved, the user will be prompted to create one with the guided prompts. It is recommended to use the guided menus to edit the configuration rather than manually.

The configuration file is located at:
 - Linux: `$HOME/.config/bitfarmer/conf.json`

### Configuration Variables:
 - `tod_schedule`: Time of Day (TOD) schedule to turn miners that are designated as `tod[true|false]` on or off. 
   - `days` are a list that contains the days the TOD applies ([Monday - Sunday]). 
   - `hours` are a list of integers that correspond to the 24 hour clock ([0 - 23]). Minutes are not available. 
   - `exceptions` are a list of days in the format `mm/dd/yyyy` that are days where the TOD schedule does not apply.
 - `view`: How will the stats be viewed in the terminal (`full|small`).
 - `icons`: Enable icons (`true|false`). Requires nerd fonts to be installed.
 - `editor`: Editor to be used when manually editing the configuration (Use `vim`).
 - `ntp`: NTP servers `bitfarmer` uses to get accurate time.
 - `pools`: List of mining pool urls to assign miners to.
 - `miners`: List of machines to be controlled and monitored by `bitfarmer`.
   - `ip`: IP address of machine. Must be online when adding via the guided method.
   - `type`: Miner type (DG1+/Volcminer)
   - `login`: Login user (usually `root`)
   - `password`: Login user password
   - `tod`: Is miner behind TOD meter (`true|false`)
   - `primary_pool`: Pool url that will be set as the primary pool url in the miner.
   - `primary_pool_user`: Pool username that will be set as the primary pool username in the miner.
   - `primary_pool_pass`: Pool password that will be set as the primary pool password in the miner.
   - `secondary_pool`: Pool url that will be set as the secondary pool url in the miner.
   - `secondary_pool_user`: Pool username that will be set as the secondary pool username in the miner.
   - `secondary_pool_pass`: Pool password that will be set as the secondary pool password in the miner.

### Example Configuration
``` json
{
    "tod_schedule": {
        "days": [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday"
        ],
        "hours": [
            6,
            7,
            8
        ],
        "exceptions": [
            "01/01/2025",
            "04/18/2025",
            "07/04/2025",
            "09/01/2025",
            "11/27/2025",
            "11/28/2025",
            "12/24/2025",
            "12/25/2025"
        ]
    },
    "view": "full",
    "icons": false,
    "editor": "nvim",
    "ntp": {
        "primary": "NTP_SERVER_1",
        "secondary": "NTP_SERVER_2"
    },
    "pools": [
        "stratum+tcp://POOL_URL:PORT",
        "stratum+tcp://POOL_URL:PORT",
    ],
    "miners": [
        {
            "ip": "MINER_IP",
            "type": "DG1+/DGHome",
            "login": "MINER_LOGIN",
            "password": "MINER_LOGIN_PASSWORD",
            "tod": true,
            "primary_pool": "stratum+tcp://POOL_URL:PORT",
            "primary_pool_user": "POOL_WORKER_NAME",
            "primary_pool_pass": "POOL_PASSWORD",
            "secondary_pool": "stratum+tcp://POOL_URL:PORT",
            "secondary_pool_user": "POOL_WORKER_NAME",
            "secondary_pool_pass": "POOL_PASSWORD"
        },
        {
            "ip": "MINER_IP",
            "type": "VolcMiner D1",
            "login": "MINER_LOGIN",
            "password": "MINER_LOGIN_PASSWORD",
            "tod": true,
            "primary_pool": "stratum+tcp://POOL_URL:PORT",
            "primary_pool_user": "POOL_WORKER_NAME",
            "primary_pool_pass": "POOL_PASSWORD",
            "secondary_pool": "stratum+tcp://POOL_URL:PORT",
            "secondary_pool_user": "POOL_WORKER_NAME",
            "secondary_pool_pass": "POOL_PASSWORD"
        }
    ]
}
```


## Donate :hugs:
 - **BTC**: `bc1qvx8q2xxwesw22yvrftff89e79yh86s56y2p9x9`
 - **Lightning**: `lightning:lnurl1dp68gurn8ghj7urjd9kkzmpwdejhgtewwajkcmpdddhx7amw9akxuatjd3cz76tkdae8jmrpv3ukyat88y48qmzv`

## TODO :construction_worker_man:
 - [x] Guided edit of configuration
 - [x] Volcminer
   - [x] Cap fan speed when stopped mining
 - [ ] Manual mode:
   - [ ] Start subset of machines
   - [ ] Stop subset of machines
 - [ ] Integrate pool stats
   - [ ] API key in configuration file
 - [x] Ping test when adding miners (ip)
 - [x] Improve error handling (could still be better)
 - [ ] Improve README
   - [ ] Installation
   - [x] Configuration explanation
   - [ ] Demo
 - [x] Move colors to file
 - [x] Prints to logging
   - [x] Move detailed errors to log
 - [x] Icons optional

## License
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
