# Dataprofiler Example
A demonstration of the federated model aggregation service for the dataprofiler.

## Running the Example
1. Make sure the FMA service is up and running via this [server setup readme](../../django-deployment/README.md)

2. Upload custom model weight extraction function to [model_utils.py](./dataprofiler_developer/model_utils.py)
3. Run example, specifying the desired number of clients (n=3), user (abc123), the base url the service is at (http://localhost:8000),
the number of epochs to run the experiment (1), and the train entities (None) to be included in the experiment.
```
bash run_example.sh 3 abc123 http://localhost:8000 1 None
```
### Details on run_example.sh:
1. Generates initial model weights and schema via [create_initial_model_json_files.py](./dataprofiler_developer/create_initial_model_json_files.py)
2. POSTS model registration
3. Executes [run_client.sh](run_client.sh) (n) times
