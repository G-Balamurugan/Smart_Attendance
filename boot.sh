
#!/bin/bash

export FLASK_APP=./db.py

pipenv run flask --debug run -h 0.0.0.0