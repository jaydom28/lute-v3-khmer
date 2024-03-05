# Lute v3

[![tests](https://github.com/jzohrab/lute_v3/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/jzohrab/lute_v3/actions/workflows/ci.yml?query=branch%3Amaster)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/jzohrab/a15001ec2ff889f7be0b553df9881566/raw/covbadge.json)](https://github.com/jzohrab/lute_v3/actions/workflows/ci.yml?query=branch%3Amaster)
[![Discord Server](https://badgen.net/badge/icon/discord?icon=discord&label)](https://discord.gg/CzFUQP5m8u)


This repo contains code to add support for Khmer parsing to the original lutev3 project [here](https://github.com/jzohrab/lute-v3).

![Lute v3 demo](https://github.com/jzohrab/lute-manual/assets/1637133/7e7f5f66-20bb-4e94-a11c-7b7ffc43255a)

## Setting up a virtual environment
I recommend setting up a virtual environment for python and running lute from within the virtual environment. My favorite one is pyenv

### Installing pyenv
#### Installing pyenv on debian
```bash
$ curl https://pyenv.run | bash
```

#### Install pyenv on macos
```bash
$ brew install pyenv
```

### Setting up the virtual environment using pyenv
Execute the following commands from this project's root
```
$ pyenv install 3.9.2               # Install python 3.9.2 using pyenv
$ pyenv virtualenv 3.9.2 lute_khmer # Create a new env "lute_khmer" which uses python 3.9.2
$ pyenv local lute_khmer            # Creates a special file called ".python-version" which automatically sets this
                                    # environment when entering this directory
```

## Starting the server
This fork is still an infant and I don't recommend using your own database with it.

1. You should first go to the project root and activate your python environment
2. Next create a config file that uses a data directory other than your personal lute data directory, or execute the following script to create a config which creates a data folder in the project directory
```bash
$ bash create_config.sh
```
3. Start the server
```bash
$ python -m lute.main --port 5050   # If no port is provided, port 5000 will be used by default
```

# License
Lute uses the MIT license: [LICENSE](./LICENSE.txt)
