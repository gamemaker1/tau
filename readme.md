# <div align="center"> <sup><sub> tiny, adorable, urls </sub></sup> </div>

> a url shortener, written in python using [`flask`](https://flask.palletsprojects.com/en/2.3.x/)
> and [`sqlite3`](https://docs.python.org/3/library/sqlite3.html)

## setup

> you'll need [`python3`](https://www.python.org/downloads/) and [`pip`](https://pip.pypa.io/en/stable/installation/) installed beforehand.

download the source code from github - either by [cloning the repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository#cloning-a-repository)
or by downloading the source archive directly from [this url](https://github.com/gamemaker1/tau/archives/refs/heads/trunk.zip).

once you have the source downloaded, run `python -m venv .venv` to activate the virtual
environment, followed by a `pip install -r requirements.txt` to install all dependencies.

run `flask --app source/server run` to start a development server.

## deploying

if you wish to deploy this app to production, follow [this guide](https://flask.palletsprojects.com/en/2.3.x/tutorial/deploy/).

## license

this code is licensed under the `agpl-3.0` license, a copy of which you can find [here](license.md).
