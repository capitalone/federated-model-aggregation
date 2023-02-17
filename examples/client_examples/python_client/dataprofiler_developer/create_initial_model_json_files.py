"""Create and serialize the model's initial json files."""
import argparse
import copy
import json
import os
import sys

import model_utils

sys.path.insert(0, os.path.abspath("../"))

from utils import jsonify_array  # noqa: E402

default_nested_array_schema = {"type": "array", "prefixItems": [], "items": False}

default_array_schema = {
    "type": None,
    "minItems": None,
    "maxItems": None,
    "items": {"type": "number"},
}


def create_array_schema(arr):
    """
    Creates an array schema that provides metadata on the array that is passed in.

    :param arr: the array that is going to be used to create the array schema
    :type arr: Union[List, numpy.ndarray]

    :return: an array schema which provides metadata on the array
    :rtype: Dict
    """
    if not len(arr):
        return {}
    if (isinstance(arr, list) and not hasattr(arr[0], "__iter__")) or (
        hasattr(arr, "shape") and len(arr.shape) == 1
    ):
        layer_schema = copy.deepcopy(default_array_schema)
        layer_schema["type"] = "array"
        layer_schema["minItems"] = len(arr)
        layer_schema["maxItems"] = len(arr)
        return layer_schema

    layer_schema = copy.deepcopy(default_nested_array_schema)
    for sub_arr in arr:
        sub_arr_schema = create_array_schema(sub_arr)
        if not sub_arr_schema:
            continue
        layer_schema["prefixItems"].append(sub_arr_schema)
    return layer_schema


def get_weights(func_to_extract):
    """
    Wrapper function to extract the weights and then reformat them into json format.

    :param func_to_extract: the function that is used to extract the weights
    :type func_to_extract: Callable
    """
    weights = func_to_extract()
    jsonify_array(weights)
    return weights


def save_json_file(object, output_path):
    """
    Writes the passed in object to the output_path in json format.

    :param object: the object which will be serialized to JSON and written to a file
    :type object: Union[str, int, float, bool, None, List, Dict]
    :param output_path: the path to the file which will be written to
    :type output_path: str
    """
    with open(output_path, "w+") as f:
        json.dump(object, f, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start model file generation")
    parser.add_argument(
        "--weights_path",
        type=str,
        default="initial_model_weights.json",
        help="path to save out the model weights",
    )
    parser.add_argument(
        "--schema_path",
        type=str,
        default="initial_model_schema.json",
        help="path to save out the model schema",
    )
    parser.add_argument(
        "--weight_extraction_func",
        type=str,
        default="extract_data_profiler_weights",
        help="function in model_utils used to extract weights",
    )
    args = parser.parse_args()

    extract_weights = getattr(model_utils, args.weight_extraction_func)
    weights = get_weights(extract_weights)
    save_json_file(weights, args.weights_path)

    layer_schema = create_array_schema(weights)
    save_json_file(layer_schema, args.schema_path)
