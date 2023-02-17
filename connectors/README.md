# Connectors 

Connectors are used to connect to data sources. Connectors specify both `Metadata`
and `Model Data` connector.

Currently implemented connectors are:
- Django
- Users can create their own!

## Metadata Connector 
The metadata connector is used to connect all the service's components to the 
metadata database, which is specified by the user in the `aggregator/fma_settings.py`
file. 


## Model Data Connector
The model data connector connects to the specified model storage location to query, 
load, and upload artifacts.
