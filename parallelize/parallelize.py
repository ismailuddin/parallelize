import functools
import math
import time
from multiprocessing import Process, Queue
from typing import Callable


def time_function(func: Callable) -> Callable:
    """
    Use as a decorator to time a function.

    Args:
        func (Callable): Function to be timed

    Returns:
        Callable: Wrapped function
    """
    @functools.wraps(func)
    def wrapper_time_function(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_time_function


@time_function
def parallel(func: Callable, iterable: list, n_splits: int, *args, **kwargs):
    """
    Parallelises a function that operators on an iterable by splitting the
    iterable into a suitable divisions, and using multiprocessing module to
    spawn a new process for each division.

    Args:
        func (Callable): Function to be parallelised
        iterable (list): Iterable which `func` will operate over
        n_splits (int): Number of splits to make, or number of CPU cores to use

    Raises:
        TypeError: Raised if iterable is not a real iterable

    Returns:
        Iterable: The output of the original function
    """
    if not isinstance(iterable, list):
        raise TypeError('Iterable must be a list')
    divisions = make_divisions(iterable, n_splits)

    queue = Queue()
    processes = []

    def capture_output(iterable: list, *args, **kwargs) -> Callable:
        output = func(iterable, *args, **kwargs)
        queue.put(output)

    for i in range(len(divisions) - 1):
        start, end = divisions[i], divisions[i + 1] + 1
        processes.append(Process(
            target=capture_output,
            args=(iterable[start:end], *args),
            kwargs=kwargs
        ))

    for process in processes:
        process.start()

    results = [queue.get() for process in processes]

    for process in processes:
        process.join()

    # return functools.reduce(lambda x, y: x + y, results)
    return results


def make_divisions(iterable: list, n_splits: int) -> list:
    """
    Generates indices to divide iterable into equal portions.    

    Args:
        iterable (list): Iterable to divide.
        n_splits (int): Number of splits to make.

    Raises:
        ValueError: Raised if number of splits is more than the number of items
            in the iterable.

    Returns:
        list: The list of indices
    """
    if n_splits >= len(iterable):
        raise ValueError(
            'Number of splits must not be greater than length of iterable'
        )

    length = len(iterable)
    _unit = length / n_splits
    unit = int(_unit)
    divisions = list(range(0, length, unit))
    divisions[-1] = len(iterable) + 1
    return divisions
