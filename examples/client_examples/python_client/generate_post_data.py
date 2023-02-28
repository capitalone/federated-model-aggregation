"""Generate and serialize API POST data to disk."""
import argparse
import json


def get_json_contents(path):
    """
    Opens a json file of the given path and returns the contents.

    :param path: path of the json file
    :type path: str

    :return: a json object with the file contents
    :rtype: Union[str, int, float, bool, None, List, Dict]
    """
    with open(path) as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start POST data generation")
    parser.add_argument(
        "--allow_aggregation", type=bool, default=True, help="True or False"
    )
    parser.add_argument(
        "--aggregator",
        type=str,
        default="average_layers",
        help="number of training epochs",
    )
    parser.add_argument(
        "--requirement", type=str, default="all_clients", help="model id from server"
    )
    parser.add_argument(
        "--initial_model_weights_path",
        type=str,
        default="./dataprofiler_developer/initial_model_weights.json",
        help="path to json file containing model weights",
    )
    parser.add_argument(
        "--update_schema_path",
        type=str,
        default="./dataprofiler_developer/initial_model_schema.json",
        help="path to json file containing update schema",
    )
    parser.add_argument(
        "--name", type=str, default="model_test", help="name of the model"
    )
    parser.add_argument(
        "--requirement_args", type=str, default=None, help="name of the model"
    )
    parser.add_argument(
        "--developer",
        type=int,
        default=1,
        help="developer id on the server (an integer, not username)",
    )
    parser.add_argument(
        "--clients",
        action="append",
        default=[],
        help="developer id on the server (an integer, not username)",
    )

    args = parser.parse_args()
    initial_model_weights = get_json_contents(args.initial_model_weights_path)
    update_schema = get_json_contents(args.update_schema_path)

    # initial_model_weights = None
    # update_schema = None

    post_data = {
        "allow_aggregation": args.allow_aggregation,
        "aggregator": args.aggregator,
        "requirement": args.requirement,
        "initial_model": initial_model_weights,
        "name": args.name,
        "requirement_args": args.requirement_args,
        "update_schema": update_schema,
        "developer": args.developer,
        "clients": args.clients,
    }

    with open("post_data.json", "w") as outfile:
        json.dump(post_data, outfile)
