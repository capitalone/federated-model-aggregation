"""FMA Client helper functions used for the examples."""
import argparse
import logging
import os
import random
import sys
import time
from typing import Any, List

import dataprofiler as dp
import pandas as pd
import sklearn
from _typing import EntitiesDictType, EntityArrayType
from dataprofiler_utils.generation_scripts import generate_sample

sys.path.insert(0, os.path.abspath(".."))
from utils import jsonify_array  # noqa: E402
from utils import (  # noqa: E402
    color_text,
    intialize_logger,
    numpify_array,
    print_results,
    service_retry_wrapper,
)

sys.path.insert(0, os.path.abspath("../../../../clients/python_client"))
import fma_connect  # noqa: E402

# Global settings
logger = logging.getLogger(__name__)
intialize_logger(logger, "logfile.log")
pd.set_option("display.width", 100)
pd.set_option("display.max_rows", None)


def create_label_char_array_from_entity_array(
    entity_array: EntityArrayType,
    _entities_dict: EntitiesDictType,
    data_raw: List[str],
):
    """
    Converts list with ranges of entities to a character level label list.

    :param entity_array: List that holds entity ranges
    :type entity_array: EntityArrayType
    :param _entities_dict: Dict of entities and their indices
    :type _entities_dict: EntitiesDictType
    :param data_raw: the raw data used for creation of entity_array
    :type data_raw: List[str]

    :return: An character level label array (label per character)
    :rtype: List[int]
    """
    char_label_array = []
    len_of_text = sum([len(text) for text in data_raw])
    for text_section_index in range(len(entity_array)):
        index = 0
        for entity in entity_array[text_section_index]:
            while index < entity[0]:
                char_label_array.append(1)
                index += 1
            while index < entity[1]:
                char_label_array.append(_entities_dict[str(entity[2])])
                index += 1
            while index < len(data_raw[text_section_index]):
                char_label_array.append(1)
                index += 1
    # Final length check
    while len(char_label_array) < len_of_text:
        char_label_array.append(1)
    return char_label_array


def initialize_model():
    """
    Initializes and returns a DataLabeler.

    :return: an initialized DataLabeler
    :rtype: dp.DataLabeler
    """
    model_arch = dp.DataLabeler(labeler_type="unstructured", trainable=True)
    model_arch.set_labels(
        {
            "PAD": 0,
            "UNKNOWN": 1,
            "DATETIME": 2,
            "COOKIE": 3,
            "MAC_ADDRESS": 4,
            "SSN": 5,
        }
    )
    model_arch.model._reconstruct_model()

    # Setting post process params for human-readable format
    model_arch.set_params(
        {"postprocessor": {"output_format": "ner", "use_word_level_argmax": True}}
    )
    return model_arch


def generate_train_data(entity_name, num_of_train_entities):
    """
    Calls generate_sample specifically for the purpose of generating training data.

    :param entity_name: name of the entity type that will be generated
    :type entity_name: str
    :param num_of_train_entities: the number of entities which will be generated
    :type num_of_train_entities: int

    :return: the generated training data
    :rtype: Dict[str, Union[List[str], List[List]]]
    """
    return generate_sample(entity_name, num_of_train_entities)


def generate_val_data(num_of_val_entities, validation_seed, entity_names):
    """
    Calls generate_sample to generate validation data on each entity_name passed in.

    :param num_of_val_entities: the number of entities which will be generated
    :type num_of_val_entities: int
    :param validation_seed: the seed that is used to generate the random state
    :type validation_seed: int
    :param entity_names: name of the entity type that will be generated
    :type entity_names: List[str]

    :return: the generated validation data
    :rtype: Dict[str, Union[List[str], List[List]]]
    """
    val_dataset_split = [
        generate_sample(entity, num_of_val_entities, validation_seed)
        for entity in entity_names
    ]

    return {
        k: [item for dic in val_dataset_split for item in dic[k]]
        for k in val_dataset_split[0]
    }


@service_retry_wrapper(logger=logger)
def check_for_latest_model(client: fma_connect.clients.WebClient) -> dict:
    """
    Checks FMA for latest model for specific federated model id.

    :param client: the object used to interface with the FMA service
    :type client: fma_connect.clients.WebClient

    :return: a tuple containing the current weights of the model and the
    base aggregate they are from
    :rtype: Union[str, int, float, bool, None, List, Dict]
    (None if weights are from a ModelArtifact object)
    """
    model_obj = client.check_for_latest_model()
    while not model_obj:
        logger.info("Received None response...")
        time.sleep(5)
        model_obj = client.check_for_latest_model()
    logger.info("Received valid response...")
    numpify_array(model_obj["values"])
    return model_obj


@service_retry_wrapper(logger=logger)
def send_update(
    client: fma_connect.clients.WebClient, weights: Any, base_aggregate=None
):
    """
    Sends updates to the FMA service.

    :param client: the object used to interface with the FMA service
    :type client: fma_connect.clients.WebClient
    :param weights: the updates to the weights you intend of sending to FMA
    :type weights: Any
    :param base_aggregate: the starting aggregate your updates are based from,
        defaults to None
    :type base_aggregate: Any, optional
    """
    client.send_update(weights, base_aggregate)


@service_retry_wrapper(logger=logger)
def get_current_artifact(client):
    """
    Retrieves the latest artifact for the model.

    :param client: the object used to interface with the FMA service
    :type client: fma_connect.clients.WebClient

    :return: response of the API in json format
        :id: id of the artifact object
        :values: model weights of the published artifact
        :version: version of the model artifact published to production environment
        :created_on: timestamp
        :federated_model: id of the base federated model object}
    :rtype: Optional[Dict[('id': int),
                            ('values': Any),
                            ('created_on': str),
                            ('federated_model': int)]]
    """
    return client.get_current_artifact()


@service_retry_wrapper(logger=logger)
def register(client):
    """
    Registers the client with the FMA service.

    :param client: the object used to interface with the FMA service
    :type client: fma_connect.clients.WebClient
    """
    client.register()


@service_retry_wrapper(logger=logger)
def send_val_results(client, val_results, agg_id):
    """
    Sends validation results to the service.

    :param client: the object used to interface with the FMA service
    :type client: fma_connect.clients.WebClient
    :param val_results: the validation info collected from running val w/ aggregate
    :type val_results: numpy.ndarray
    :param agg_id: the id of the aggregate validation was run on
    :type agg_id: int

    :return: response from the service
    :rtype: Dict
    """
    val_results["f1_score"] = val_results["f1_score"].tolist()
    return client.send_val_results(val_results, agg_id)


def connect_to_server(uuid_storage_path, federated_model_id, url):
    """
    Connects the client to the FMA server.

    :param uuid_storage_path: the path to the uuid of the client
    :type uuid_storage_path: str
    :param federated_model_id: the federated model id which
        is used to build the WebClient
    :type federated_model_id: int
    :param url: the url used to build the WebClient
    :type url: str

    :return: The newly created client that has been connected to the server
    :rtype: fma_connect.clients.WebClient
    """
    try:
        with open(uuid_storage_path) as f:
            uuid = f.read()
            logger.info(f"Connecting with {uuid} as UUID")
            client = fma_connect.WebClient(
                federated_model_id=federated_model_id, url=url, uuid=uuid
            )
    except FileNotFoundError:
        logger.info("Connecting without UUID")
        client = fma_connect.WebClient(federated_model_id=federated_model_id, url=url)
    finally:
        register(client)
        uuid = client.uuid
        with open(uuid_storage_path, "w+") as f:
            f.write(uuid)
        logger.info(f"{uuid} stored as UUID")

    return client


def run_validation(
    predictions: EntityArrayType,
    val_dataset_array: EntityArrayType,
    label_mapping: EntitiesDictType,
    data_raw: List[str],
):
    """
    Runs validation for a specific set of predictions and labels.

    :param predictions: the predictions of a model
    :type predictions: EntityArrayType
    :param val_dataset_array: the actual labels of the dataset
    :type val_dataset_array: EntityArrayType
    :param label_mapping: the Dict of labels and their indices
    :type label_mapping: EntitiesDictType
    :param data_raw: the raw data used for creation of entity_array
    :type data_raw: List[str]

    :return: the calculated validation results
    :rtype: Dict[str, Union[float, str]]
    """
    # Convert to sklearn specified format
    pred_array = create_label_char_array_from_entity_array(
        predictions["pred"], label_mapping, data_raw
    )
    val_results = {
        "f1_score": sklearn.metrics.f1_score(
            val_dataset_array, pred_array, average=None
        ),
        "description": sklearn.metrics.classification_report(
            val_dataset_array, pred_array
        ),
    }
    return val_results


def main(
    url: str,
    num_epochs: int,
    federated_model_id: int,
    uuid_storage_path: str,
    entity_names: List[str],
    train_entity: str,
    num_of_train_entities=200,
    num_of_val_entities=10,
    validation_seed=0,
    verbose=True,
):
    """
    The main function that creates a client for federated training of a model.

    :param url: the url to connect your client to the FMA service
    :type url: str
    :param num_epochs: the number of epochs for training locally
    :type num_epochs: int
    :param federated_model_id: the model id within FMA service
    :type federated_model_id: int
    :param uuid_storage_path: the storage path to your uuid save file
    :type uuid_storage_path: str
    :param entity_names: the names of possible entities in the dataset
    :type entity_names: List[str]
    :param train_entity: the entity you will be training on locally
    :type train_entity: str
    :param num_of_train_entities: the number of train datapoints
        defaults to 200
    :type num_of_train_entities: int, optional
    :param num_of_val_entities: the number of validation datapoints per entity,
        defaults to 10
    :type num_of_val_entities: int, optional
    :param validation_seed: the seed to use for generation of datasets,
        defaults to 0
    :type validation_seed: int, optional
    :param verbose: the verbosity of the printouts in your run,
        defaults to True
    :type verbose: bool, optional
    """
    # Connection to API establishment
    client = connect_to_server(uuid_storage_path, federated_model_id, url)

    # Model set up
    model_arch = initialize_model()
    model_obj = check_for_latest_model(client)
    new_weights, base_aggregate = model_obj["values"], model_obj["aggregate"]
    model_arch.model._model.set_weights(new_weights)
    logger.info("New initial model weights set")
    logger.info(f"Base aggregate Received: {base_aggregate}")

    # Create background object for dataset generation
    start = time.time()
    end = time.time()
    logger.info(f"background loaded in {end - start} seconds")

    # Create validation dataset
    val_dataset = generate_val_data(num_of_val_entities, validation_seed, entity_names)
    length_of_dataset = 0
    for text in val_dataset["text"]:
        length_of_dataset += len(text)
    # Convert to sklearn specified format
    val_dataset_array = create_label_char_array_from_entity_array(
        val_dataset["entities"], model_arch.label_mapping, val_dataset["text"]
    )

    # Run validation with new weights
    if base_aggregate:
        logger.info("Aggregated model weights eval started...")
        predictions = model_arch.predict(val_dataset["text"])
        val_results = run_validation(
            predictions,
            val_dataset_array,
            model_arch.label_mapping,
            val_dataset["text"],
        )
        logger.info("Aggregated model weights eval complete!")

        logger.info("Sending validation results to service")
        resp = send_val_results(client, val_results, base_aggregate)
        logger.info(f"Validation results sent! {resp}")
    training_idx = 0

    # Train
    while True:
        logger.info(f"Training loop: {training_idx}")
        start = time.time()
        train_dataset = generate_sample(train_entity, num_of_train_entities)
        end = time.time()
        logger.info(f"Train set generated in {end - start} seconds")

        logger.info("Training model...")
        model_arch.fit(
            x=train_dataset["text"], y=train_dataset["entities"], epochs=num_epochs
        )
        logger.info("Training complete!!!")

        # Run validation with trained weights
        logger.info("Eval after local training started...")
        predictions = model_arch.predict(val_dataset["text"])
        logger.info("Eval after local training complete!")
        if verbose:
            print_results(val_dataset["text"], predictions, logger)
        color_text(val_dataset["text"], predictions, model_arch.label_mapping)

        # Data preparation for sending to service API
        weights = model_arch.model._model.get_weights()
        jsonify_array(weights)

        # Send data to service
        send_update(client, weights, base_aggregate)
        logger.info("Weights updates sent")

        # Check for model weights updates from service
        logger.info("Checking for updated weights")
        model_obj = check_for_latest_model(client)
        weights_updates = model_obj["values"]
        base_aggregate = model_obj["aggregate"]
        logger.info("New model weights set")
        logger.info(f"Base aggregate Received: {base_aggregate}")

        model_arch.model._model.set_weights(weights_updates)

        # Run validation with new weights
        logger.info("Aggregated model weights eval started...")
        predictions = model_arch.predict(val_dataset["text"])
        val_results = run_validation(
            predictions,
            val_dataset_array,
            model_arch.label_mapping,
            val_dataset["text"],
        )
        logger.info("Aggregated model weights eval complete!")

        logger.info("Sending validation results to service")
        resp = send_val_results(client, val_results, base_aggregate)
        logger.info(f"Validation results sent! {resp}")

        if verbose:
            print_results(val_dataset["text"], predictions, logger)
        color_text(val_dataset["text"], predictions, model_arch.label_mapping)

        training_idx += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start data-feeder client")
    parser.add_argument(
        "--url",
        type=str,
        default="http://127.0.0.1:8000",
        help="url to connect to server",
    )
    parser.add_argument(
        "--epochs", type=int, default=1, help="number of training epochs"
    )
    parser.add_argument("--model-id", type=int, default=1, help="model id from server")
    parser.add_argument(
        "--uuid-save-path",
        type=str,
        default="./uui_temp.txt",
        help="UUID used for the client in to connect to service"
        "(UUID will be appended to name)",
    )
    parser.add_argument(
        "--train-entity",
        type=str,
        default=None,
        help="Entity that the client will be trained on",
    )
    parser.add_argument("--verbose", action="store_true", help="verbose printouts")

    args = parser.parse_args()

    entity_names = ["COOKIE", "MAC_ADDRESS", "SSN", "DATETIME"]

    if args.train_entity is None:
        args.train_entity = random.choice(entity_names)
    logger.info(f"all args {args.__dict__}")
    logger.info(f"Entity chosen for this client {args.train_entity}")

    if args.train_entity not in entity_names:
        logger.info(f"{args.train_entity} not in {entity_names}")
        raise f"{args.train_entity} not in {entity_names}"

    main(
        args.url,
        args.epochs,
        args.model_id,
        args.uuid_save_path,
        entity_names=entity_names,
        train_entity=args.train_entity,
        verbose=args.verbose,
    )
