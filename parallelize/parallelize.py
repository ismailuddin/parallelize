import math
import time
import functools
import tempfile
import os
try:
    import cPickle as pickle
except:
    import pickle
import gc
from pathlib import Path
from multiprocessing import Process, Queue
from typing import Callable, List, Tuple, Any


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
        print(f"Completed in {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_time_function


@time_function
def parallel(
    func: Callable, iterable: list, n_jobs: int=2, write_to_file: bool=False,
    args: tuple=(), kwargs: dict={}
) -> Any:
    """
    Parallelises a function that operators on an iterable by splitting the
    iterable into a suitable divisions, and using multiprocessing module to
    spawn a new process for each division.

    Args:
        func (Callable): Function to be parallelised
        iterable (list): List which `func` will operate over
        n_jobs (int): Number of splits to make, or number of CPU cores to use
        write_to_file (bool): (Optional) Default False. Set to True if the
            output from the each file is a large object, in which case writing
            to disk can help speed up process in recovering data in main
            process.
        args (tuple): Arguments to pass to `func`
        kwargs (dict): Keyword arguments to pass to `func`

    Raises:
        TypeError: Raised if iterable is not a real iterable

    Returns:
        Any: The output of the original function or no output.
    """
    if not isinstance(iterable, list):
        raise TypeError('Iterable must be a list')
    divisions = make_divisions(iterable, n_jobs)

    queue = Queue()
    processes = []

    for index, i in enumerate(range(len(divisions) - 1)):
        start, end = divisions[i], divisions[i + 1]

        processes.append(Process(
            target=capture_output,
            args=(
                func,
                iterable[start:end],
                index,
                queue,
                write_to_file,
                *args
            ),
            kwargs=kwargs
        ))

    for process in processes:
        process.start()

    result_output = [queue.get() for process in processes]

    for process in processes:
        process.join()

    if write_to_file:
        output = retrieve_output(result_output)
    else:
        if all([isinstance(item[1], list) for item in result_output]):
            output = merge_results(result_output)
        else:
            _output = sorted(result_output, key=lambda x: x[0])
            output = [item[1] for item in _output]
    return output


@time_function
def merge_results(results: List[list]) -> list:
    """
    Merges a list of lists into a single list.

    Args:
        results (List[list]): List of lists to be merged.

    Returns:
        list: Flattened list of objects.
    """
    _sorted_results = sorted(results, key=lambda x: x[0])
    sorted_results = [result[1] for result in _sorted_results]
    return sum(sorted_results, [])


def capture_output(
    func: Callable, iterable: list, index: int, queue: Queue,
    write_to_file: bool=False, *args, **kwargs
) -> None:
    """
    Captures the output of the function to be parallelised. If specified,
    output is saved to a temporary file, which is later read in by the master
    process, to be ultimately merged into one object.

    Args:
        func (Callable): Function which is to be parallelised.
        iterable (list): List which `func` will operate over.
        index (int): Index number of current process. Used to sort order of
            results, since some processes may finish earlier than others.
        queue (Queue): Queue object to pass filepaths back to master process.
        write_to_file (bool): (Optional) Default False. Set to True if the
            output from the each file is a large object, in which case writing
            to disk can help speed up process in recovering data in main
            process.

    Returns:
        None: No output returned.
    """
    output = func(iterable, *args, **kwargs)
    if write_to_file:
        filepath = write_output_to_temp_file(output)
        queue.put((index, filepath))
    elif not write_to_file:
        queue.put((index, output))


@time_function
def write_output_to_temp_file(output: list) -> Path:
    """
    Writes the output from the function being parallelised, and saves it to a
    temporary file using `pickle`.

    Args:
        output (list): The output from the parallelised function.

    Returns:
        Path: File path to the temporary file.
    """
    fd, path = tempfile.mkstemp()
    gc.disable()
    pickle.dump(output, os.fdopen(fd, 'wb'), protocol=-1)
    gc.enable()
    return Path(path)


@time_function
def retrieve_output(file_paths: List[Tuple[int, Path]]) -> list:
    """
    Retrieves the outputs from the parallelised function which was saved to a
    temporary `pickle` file.

    Args:
        file_paths (List[Tuple[int, Path]]): List of file paths corresponding to the
            temporary files written by `pickle`.

    Returns:
        list: List of outputs from the parallelised function.
    """
    output = []
    for index, path in file_paths:
        _output = pickle.load(open(path, 'rb'))
        os.remove(path)
        output.append((index, _output))
    if all([isinstance(item, list) for item in output]):
        output = merge_results(output)
    return output


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
    divisions[-1] = len(iterable)
    return divisions
