#!/bin/bash

cd ./dataprofiler_developer/

python3 create_initial_model_json_files.py

cd ..
python3 generate_post_data.py

output=$(curl --data '@post_data.json' -H "Content-Type: application/json" --user $2 -X POST "$3/api/v1/models/")

id=$(echo $output | python -c "import sys, json; print(json.load(sys.stdin)['id'])")


echo "Model ID:" $id
echo "Number of clients:" $1

count=1
while [ $count -le $1 ]
do
  echo $count
  bash run_client.sh $id $count $3 $4 &
  count=$(( $count + 1))

done
