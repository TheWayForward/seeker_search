from utils.config import search_result_batch
import math


def get_pages_from_result(total_result):
    return math.ceil(int(total_result) / search_result_batch)