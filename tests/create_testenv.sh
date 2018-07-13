#!/bin/bash
virtualenv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
