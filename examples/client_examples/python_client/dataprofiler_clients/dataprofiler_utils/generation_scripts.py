"""Functions used to randomly generate samples for testing and training."""
import numbers
import os
import pathlib
import random
import string

import pandas as pd

ACTIVE_DIR = pathlib.Path(__file__).parent.resolve()


def get_random_state(random_state):
    """
    Converts the random state into a valid random state for the random library.

    :param random_state: random state to be evaluated/returned
    :type random_state: Union[random.Random, numbers.Integral, int]

    :raises ValueError: random_state cannot be used to seed a random.Random instance

    :return: a valid random state for the random library
    :rtype: Union[random.Random, numbers.Integral]

    Parameters
    ----------
    seed : None | int | instance of Random
        If seed is None, return the Random singleton used by random.
        If seed is an int, return a new Random instance seeded with seed.
        If seed is already a Random instance, return it.
        Otherwise, raise ValueError.
    """
    if random_state is None or random_state is random:
        return random._inst
    if isinstance(random_state, numbers.Integral):
        return random.Random(random_state)
    if isinstance(random_state, random.Random):
        return random_state
    raise ValueError(
        "%r cannot be used to seed a random.Random instance" % random_state
    )


def random_mac_address(random_state):
    """
    Generate mac address given the format mac_format.

    :param random_state: a random state that is used to randomly generate the entity
    :type random_state: Union[random.Random, numbers.Integral]

    :return: generated mac address
    :rtype: str
    """
    delimiters = [":", "-", ".", ""]
    delimiter = random_state.choice(delimiters)
    seg_1 = random_state.randint(0, 255)
    seg_2 = random_state.randint(0, 255)
    seg_3 = random_state.randint(0, 255)
    seg_4 = random_state.randint(0, 255)
    seg_5 = random_state.randint(0, 255)
    seg_6 = random_state.randint(0, 255)

    mac_address = ""

    if delimiter == ":":
        mac_address = "%02x:%02x:%02x:%02x:%02x:%02x" % (
            seg_1,
            seg_2,
            seg_3,
            seg_4,
            seg_5,
            seg_6,
        )
    elif delimiter == "-":
        mac_address = "%02x-%02x-%02x-%02x-%02x-%02x" % (
            seg_1,
            seg_2,
            seg_3,
            seg_4,
            seg_5,
            seg_6,
        )
    elif delimiter == ".":
        mac_address = "%02x%02x.%02x%02x.%02x%02x" % (
            seg_1,
            seg_2,
            seg_3,
            seg_4,
            seg_5,
            seg_6,
        )
    elif delimiter == "":
        mac_address = "%02x%02x%02x%02x%02x%02x" % (
            seg_1,
            seg_2,
            seg_3,
            seg_4,
            seg_5,
            seg_6,
        )

    # 33% chance of lower case
    if random_state.randint(0, 3) == 0:
        return mac_address.lower()
    else:
        return mac_address.upper()


def generate_ssn(random_state):
    """
    Generates and returns a random SSN based on the random_state passed in.

    :param random_state: a random state that is used to randomly generate the entity
    :type random_state: Union[random.Random, numbers.Integral]

    :return: a single, randomly generated SSN
    :rtype: str
    """
    delimiters = ["-", "", " "]
    delimiter = random_state.choice(delimiters)
    part_one = "".join([str(random_state.randint(0, 9)) for x in range(3)])
    part_two = "".join([str(random_state.randint(0, 9)) for x in range(2)])
    part_three = "".join([str(random_state.randint(0, 9)) for x in range(4)])

    ssn = delimiter.join([part_one, part_two, part_three])
    return ssn


def create_cookie(random_state):
    """
    Generate cookie given the random_state.

    :param random_state: a random state that is used to randomly generate the entity
    :type random_state: Union[random.Random, numbers.Integral]

    :return: generated cookie
    :rtype: str
    """
    random_state = get_random_state(random_state)
    # [^\\s]
    valid_char_list_hash = string.ascii_letters + string.digits + string.punctuation
    # Invalid:
    # control character, Whitespace, double quotes, comma, semicolon, and backslash.
    invalid_chars = [",", '"', "\\", ";"]
    for invalid_char in invalid_chars:
        valid_char_list_hash.replace(invalid_char, "")
    cookies_str = ""
    length_of_str = random_state.randint(16, 250)
    for _ in range(length_of_str):
        cookies_str += random_state.choice(valid_char_list_hash)
    if random_state.choice([0, 1]):
        cookies_str += ";"
    for _ in range(random_state.randint(0, 7)):
        cookies_str += " "
    return cookies_str


def get_background_text(path=os.path.join(ACTIVE_DIR, "./background_text.txt")):
    """
    Grabs non-entity texts from a file to provide context to sensitive entities.

    :param path: path to the background text
    :type path: str, optional

    :return: the background text as strings
    :rtype: str
    """
    with open(path) as f:
        lines = f.readlines()
    return lines


def generate_datetime(random_state, date_format=None, start_date=None, end_date=None):
    """
    Generate datetime given the random_state, date_format, and start/end dates.

    :param random_state: a random state that is used to randomly generate the entity
    :type random_state: Union[random.Random, numbers.Integral]
    :param date_format: the format that the generated datatime will follow,
        defaults to None
    :type date_format: str, optional
    :param start_date: the earliest date that datetimes can be generated at,
        defaults to None
    :type start_date: pd.Timestamp, optional
    :param start_date: the latest date that datetimes can be generated at,
        defaults to None
    :type start_date: pd.Timestamp, optional

    :return: generated datetime
    :rtype: str
    """
    if not date_format:
        date_format = random_state.choice(
            [
                "%b %d, %Y %H:%M:%S",  # Nov 15, 2013 15:43:30
                "%B %d, %Y %H:%M:%S",  # November 15,  2013 15:43:30
                "%B %d %Y %H:%M:%S",  # November 15 2013 15:43:30
                "%b. %d %H:%M:%S",  # Nov. 15 15:43:30
                "%B %d %H:%M",  # November 15 15:43
                "%A, %b %d %H:%M:%S",  # Monday, Nov 15 15:43:30
                "%A %B %d %H:%M",  # Monday November 15 15:43
                "%a, %B %d %H:%M",  # Mon, November 15 15:43
                "%Y-%m-%d %H:%M:%S",  # 2013-03-5 15:43:30
                "%A %Y-%m-%d %H:%M:%S",  # Monday 2013-03-5 15:43:30
                "%a %Y-%m-%d %H:%M:%S",  # Mon 2013-03-5 15:43:30
                "%Y-%m-%dT%H:%M:%S",  # 2013-03-6T15:43:30
                "%Y-%m-%dT%H:%M:%S.%fZ",  # 2013-03-6T15:43:30.123456Z
                "%m/%d/%y %H:%M",  # 03/10/13 15:43
                "%m/%d/%Y %H:%M",  # 3/8/2013 15:43
                "%d/%m/%y %H:%M",  # 15/10/13 15:43
                "%d/%m/%Y %H:%M",  # 18/3/2013 15:43
                "%A %m/%d/%y %H:%M",  # Monday 03/10/13 15:43
                "%a %m/%d/%y %H:%M",  # Mon 03/10/13 15:43
                "%A %m/%d/%Y %H:%M",  # Monday 3/8/2013 15:43
                "%a %m/%d/%Y %H:%M",  # Mon 3/8/2013 15:43
                "%Y%m%dT%H%M%S",  # 2013036T154330
                "%Y%m%d%H%M%S",  # 20130301154330
                "%Y%m%d%H%M%S.%f",  # 20130301154330.123456
            ]
        )
    if not start_date:
        # 100 years in past
        start_date = pd.Timestamp(1920, 1, 1)
    if not end_date:
        # protection of 30 years in future
        end_date = pd.Timestamp(2049, 12, 31)
    t = random_state.random()
    ptime = start_date + t * (end_date - start_date)

    return ptime.strftime(date_format)


def generate_sample(entity_name, num_of_entities, seed=None, prob_of_bg=0.5):
    """
    Generates samples with entities based on the entity_name specified.

    :param entity_name: a random state that is used to randomly generate the entity
    :type entity_name: Union[random.Random, numbers.Integral]
    :param num_of_entities: the number of samples that will be generated
    :type num_of_entities: int
    :param seed: a random seed used to set the random state,
        defaults to None
    :type seed: int, optional
    :param prob_of_bg: the probability of an entity having background text around it,
        defaults to 0.5
    :type prob_of_bg: float, optional

    :return: a dictionary with the text and entities of each sample generated
    :rtype: Dict[str, Union[List[str], List[List]]]
    """
    random_state = get_random_state(seed)
    gen_data = {"text": [], "entities": []}

    for _ in range(num_of_entities):
        if entity_name == "SSN":
            entity = generate_ssn(random_state)
        elif entity_name == "MAC_ADDRESS":
            entity = random_mac_address(random_state)
        elif entity_name == "COOKIE":
            entity = create_cookie(random_state)
        elif entity_name == "DATETIME":
            entity = generate_datetime(random_state)

        entity_start = 0
        back_idx = 0
        text = []
        if random_state.random() < prob_of_bg:
            text = _BACKGROUND_TEXT[
                random_state.randint(0, len(_BACKGROUND_TEXT) - 1)
            ].split()
            back_idx = random_state.randint(0, len(text) - 1)
            start_text = " ".join(text[:back_idx])
            if back_idx:
                entity_start = len(start_text) + 1

        entity_end = entity_start + len(entity)
        text.insert(back_idx, entity)
        final_text = " ".join(text)
        gen_data["text"].append(final_text)
        gen_data["entities"].append([[entity_start, entity_end, entity_name]])

    return gen_data


_BACKGROUND_TEXT = get_background_text()
