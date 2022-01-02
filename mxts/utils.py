from typing import Callable, List
import itertools


def id_gen() -> Callable[[], int]:
    __c = itertools.count()

    def _gen_id() -> int:
        return next(__c)

    return _gen_id
