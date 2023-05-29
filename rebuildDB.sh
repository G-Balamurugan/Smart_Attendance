# Run this file if any modifications is done to the models

#!/bin/bash
export PIPENV_VERBOSITY=-1 # Ro supress stderr when the below command is run inside pipenv shell

pipenv run python3 ./rebuildDB.py 