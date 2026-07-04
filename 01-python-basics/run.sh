#!/bin/bash

set -x

if ! command -v python3 &> /dev/null; then
    echo "Python 3 не установлен"
    exit 1
fi

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

mkdir -p data reports logs
python3 run.py

deactivate