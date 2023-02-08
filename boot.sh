#!/bin/bash

export FLASK_APP=./app.py
export PATH="/home/asif/.local/bin:$PATH"

pipenv run flask --debug run -h 0.0.0.0