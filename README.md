# Lute v3

[![tests](https://github.com/jzohrab/lute_v3/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/jzohrab/lute_v3/actions/workflows/ci.yml?query=branch%3Amaster)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/jzohrab/a15001ec2ff889f7be0b553df9881566/raw/covbadge.json)](https://github.com/jzohrab/lute_v3/actions/workflows/ci.yml?query=branch%3Amaster)
[![Discord Server](https://badgen.net/badge/icon/discord?icon=discord&label)](https://discord.gg/CzFUQP5m8u)


This repo contains code to add support for Khmer parsing to the original lutev3 project [here](https://github.com/jzohrab/lute-v3).

![Lute v3 demo](https://github.com/jzohrab/lute-manual/assets/1637133/7e7f5f66-20bb-4e94-a11c-7b7ffc43255a)

# Starting the project in developer mode
This fork is still an infant and I don't recommend using your own database with it. I also at the moment only know how to run it in developer mode.

1. You should first go to the project root and activate your python environment
2. Next create a config file that uses a data directory other than your personal lute data directory
```bash
$ bash create_config.sh
```
3. Start the developer server
```bash
$ python -m devstart # will use port 5000 by default
$ python -m devstart --port 5050 # use some other port if you are already running lute
```

# License

Lute uses the MIT license: [LICENSE](./LICENSE.txt)
