import random


def rm_space(s: str) -> str:
    """
    Remove space at the begin and the end of the given string, if they do exist.

    :param s: the string to be modified
    :return: the modified string

    """
    if not isinstance(s, str):
        return s
    return s.strip()


def sample_floats(low: int, high: int, k=1) -> list:
    """
    Return a k-length list of unique random floats in the range of low <= x <= high.

    :param low: lower bound of the range
    :param high: higher bound of the range
    :param k: the number of the random floats
    :return:
    """
    result = []
    seen = set()
    for i in range(k):
        x = random.uniform(low, high)
        while x in seen:
            x = random.uniform(low, high)
        seen.add(x)
        result.append(x)
    return result
