#!/bin/bash

python3 -m venv venv
source venv/bin/activate
cd ./dataprofiler_clients/
pip3 install -r requirements.txt

python3 client.py --model-id=$1 --uuid-save-path="uui_temp_$2.txt" --url=$3 --epochs=$4
