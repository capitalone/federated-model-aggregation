"""Model utilities for the python client."""


def extract_data_profiler_weights():
    """
    Retrieves the weights from the DataProfiler DataLabeler.

    :return: the weights from the DataLabeler
    :rtype: numpy.ndarray
    """
    import dataprofiler as dp

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

    return model_arch.model._model.get_weights()
