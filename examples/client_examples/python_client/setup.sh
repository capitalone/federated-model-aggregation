# Setup of client API connection
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# dev tools
pip3 install -r requirements-dev.txt

# Setup of dataprofiler example
pip3 install -r ./dataprofiler_clients/requirements.txt
cd ./dataprofiler_developer
python3 create_initial_model_json_files.py
cd ../../..
