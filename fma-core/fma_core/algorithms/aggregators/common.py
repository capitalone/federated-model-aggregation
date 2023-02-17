"""Functions stored here for use in model aggregation."""

import numpy as np


def avg_values_if_data(model, model_updates):
    """
    Averages values together if data exists within model_updates.

    :param model: Database FederatedModel object
    :type model: task_queue_base.models.FederatedModel
    :param model_updates: Database objects containing
        the original weights used to initialize the shape of the layers
    :type model_updates: task_queue_base.models.ModelUpdate

    :return: The average value for each update
    :rtype: List[Any]
    """
    data = [update.data for update in model_updates]
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.average(data, axis=0).tolist()


def average_layers(model, model_updates):
    """Takes in the weights of multiple models and averages across layers.

    :param model: Database FederatedModel object
    :type model: task_queue_base.models.FederatedModel
    :param model_updates: Database objects containing
        the original weights used to initialize the shape of the layers
    :type model_updates: task_queue_base.models.ModelUpdate
    :returns: A weights obj that is the average of all weights across layers
    :rtype: List[List[Any]]
    """
    if not model_updates:
        return None

    avg_model = []
    n_models = len(model_updates)
    n_layers = len(model_updates[0].data)

    for layer_ind in range(n_layers):
        layers = []
        for model_ind in range(n_models):
            layers.append(model_updates[model_ind].data[layer_ind])
        avg_model.append(np.average(layers, axis=0).tolist())

    return avg_model
