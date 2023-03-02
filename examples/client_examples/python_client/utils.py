"""General utilities for the python client example."""
import logging
import time

import numpy as np
import pandas as pd
import requests


def service_retry_wrapper(retries=10, sleep_time=10, logger=None):
    """
    A decorator for retrying api calls when call fails from connection errors.

    Should not go around functions with more than 1 api call within.

    :param retries: number of times to retry the api call.
    :type retries: int
    :param sleep_time: how long to wait between api calls.
    :type sleep_time: int
    :param logger: method used to print out messages
        (print function used as default).
    :type logger: Callable

    :return: decorator
    :rtype: Callable
    """
    print_fcn = print
    if logger is not None:
        print_fcn = logger.info

    def wrap(function):
        """
        Wrapper which allows input arguments for the connection error decorator.

        :param function: the api function call
        :type function: Callable

        :return: the wrapped function.
        :rtype: Callable
        """

        def decorator(*args, **kwargs):
            """
            Decorator which checks for rate limiting and retries based on inputs.

            :param args: function args for the decorated function
            :type args: any
            :param kwargs: kwargs for the decorated function
            :type kwargs: any

            :return: The results of the decorated function.
            :rtype: Callable
            """
            for i in range(retries):
                try:
                    return function(*args, **kwargs)

                except requests.exceptions.ReadTimeout as e:
                    print_fcn(e)
                    print_fcn("Connection lost: ReadTimeout " f"retry attempt {i + 1}")

                except requests.exceptions.ConnectionError as e:
                    print_fcn(e)
                    print_fcn(
                        "Connection lost: ConnectionError " f"retry attempt {i + 1}"
                    )

                except OSError as e:
                    if "Errno 41" not in e:
                        raise e
                    print_fcn(e)
                    print_fcn("Connection lost: OSError " f"retry attempt {i + 1}")

                finally:
                    time.sleep(sleep_time)
            print_fcn(
                f"Connection attempts exceeded: attempts {i + 1},"
                " can not connect to service, closing script"
            )
            raise f"""Connection attempts exceeded: attempts {i + 1},
                    can not connect to service, closing script"""

        return decorator

    return wrap


def intialize_logger(logger, filename):
    """
    Adds a console logger and a file logger.

    :param logger: method used to print out messages
        (print function used as default).
    :type logger: Callable
    :param filename: the name of the file where the logs will be stored
    :type filename: str
    """
    # Allow all messaged to be caught
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler(filename)
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)


def numpify_array(data):
    """
    Helper function for converting list of lists to a numpy array.

    :param data: a list to be converted to a numpy array
    :type data: List[List[Union[float, int]]]
    """
    for i, arr in enumerate(data):
        data[i] = np.array(arr)


def jsonify_array(data):
    """
    Helper function for converting list of numpy arrays to a list of lists.

    :param data: a list to be converted to a numpy array
    :type data: List[any]
    """
    for i, arr in enumerate(data):
        data[i] = arr.tolist()


def print_results(data, results, logger):
    """
    Helper function to get data labels for each labeled piece of text.

    :param data: the data used to get the training results
    :type data: Iterable
    :param results: a dictionary which holds the result predictions from training
    :type results: Dict[str, Iterable]
    :param logger: method used to print out messages
    :type logger: Callable
    """
    labeled_data = []
    for text, text_pred in zip(data, results["pred"]):
        for pred in text_pred:
            labeled_data.append([text[pred[0] : pred[1]], pred[2]])
    label_df = pd.DataFrame(labeled_data, columns=["Text", "Labels"])
    logger.info(
        "\n=========================Prediction========================" f"\n {label_df}"
    )


def wrap_text_in_color(text, color):
    """
    Puts color codes in front text provided.

    :param text: text that corresponds to predictions
    :type text: str
    :param color: color number
    :type color: int

    :return: the base text encoded as a color
    :rtype: str
    """
    return "\033[38;5;{num}m{text}\033[0;0m".format(text=text, num=str(color))


def color_text(text, pred, ent_to_color):
    """
    Creates print out of color coded predictions on the text provided.

    :param text: text that corresponds to predictions
    :type text: str
    :param pred: object that contains predictions for text
    :type pred: Dict
    :param ent_to_color: mapping of labels to color numbers
    :type ent_to_color: Dict
    """
    color_text = []
    for t, p in zip(text, pred["pred"]):
        s = ""
        num_entities = len(p)
        entity_ind = 0
        text_ind = 0
        while entity_ind < num_entities:
            s += t[text_ind : p[entity_ind][0]]
            s += wrap_text_in_color(
                t[p[entity_ind][0] : p[entity_ind][1]], ent_to_color[p[entity_ind][2]]
            )
            text_ind = p[entity_ind][1]
            entity_ind += 1
        s += t[text_ind:]
        color_text.append(s)

    for c_text in color_text:
        print(c_text)
