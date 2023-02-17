"""Used to specify requirements for the aggregation functionality to run."""


def all_clients(model, model_updates):
    """Requires all clients to push update before aggregation is executed.

    :param model: Database FederatedModel object
    :type model: task_queue_base.models.FederatedModel
    :param model_updates: Database objects containing
        the original weights used to initialize the shape of the layers
    :type model_updates: task_queue_base.models.ModelUpdate
    :return: A boolean assertion that indicates if all clients have pushed updates
    :rtype: bool
    """
    if not set(model.clients.all()).issubset(
        set([update.client for update in model_updates])
    ):
        return False
    return True


def require_x_updates(model, model_updates, x):
    """Requires x clients to push update before aggregation is executed.

    :param model: Database FederatedModel object
    :type model: task_queue_base.models.FederatedModel
    :param model_updates: Database objects containing
        the original weights used to initialize the shape of the layers
    :type model_updates: task_queue_base.models.ModelUpdate
    :param x: The number of client updates needed
    :type x: int
    :return: A boolean assertion that indicates if x clients have pushed updates
    :rtype: bool
    """
    if len(model_updates) < x:
        return False
    return True
