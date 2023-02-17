.. federated-model-aggregation documentation master file, created by
   sphinx-quickstart on Tue Nov 29 10:48:57 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Federated Model Aggregation's documentation!
================================================================
.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Getting Started:

   Intro <self>
   Setup <setup.rst>
   Examples <examples>
   Roadmap <roadmap.rst>
   API Endpoints <api_endpoints.rst>

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Components:

   Aggregator <http://localhost/replaceme>
   API Service <http://localhost/replaceme>
   FMA Django <http://localhost/replaceme>
   FMA Connect <http://localhost/replaceme>
   FMA Core <http://localhost/replaceme> 

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Community:

   Changelog<https://github.com/capitalone/federated-model-aggregation/releases>
   Feedback<https://github.com/capitalone/federated-model-aggregation/issues>
   GitHub<https://github.com/capitalone/federated-model-aggregation>
   Contributing<https://github.com/capitalone/federated-model-aggregation/blob/master/.github/CONTRIBUTING.md>

Purpose
=======

The Federated Model Aggregation (FMA) Service is a collection of installable python components that make up the generic
workflow/infrastructure needed for federated learning.
The main goal is to take a distributed model training workflow and convert it into a federated learning paradigm with
very little changes to your training code.
Each component can be used by changing a few settings within the components and then simply deploying with a terraform
based deployment script.
The main components that make up the FMA Service are: 

* FMA Core
* FMA Connectors
* FMA Clients
* Aggregator
* API Service

Full System Diagram
=======================
.. image:: /_images/Abstract_FMA_Diagram.png
  :width: 600
