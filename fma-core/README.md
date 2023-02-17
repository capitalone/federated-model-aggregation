# FMA-Core

The FMA-Core component is a collection of building blocks use for agnostically building an FMA service. 
Algorithms and workflows are agnostic in the sense that users can build their own algorithms/workflows 
and use them in the FMA Service.

Quick start
-----------
For installation:

```console
pip install fma-core
```


Testing
-------

Inside a virtualenv:
```
make install
make test
```

For testing and coverage reports:
```
make test-and-coverage
```

## FMA-Algorithms

A sub-part of FMA-Core is FMA-Algorithms. 
This component is an agnostic implementation of the model aggregation function for the FMA service.

## FMA-Workflows

FMA-Workflow is the principal component of the service: gluing together the 
`aggregator`, `api`, `model`, and `metadata` connectors for the various parts of the service 
to communicate with each other. 
