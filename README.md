# parallelize

`parallelize` is a Python package to simplify the process of parallelising your taks in Python. It takes advantage of the `multiprocessing` module to spawn new processes for your job.



### Requirements

- Python 3.X


### Usage

To parallelise a task in Python, you should wrap the entire code inside a function and have the first argument of your function receive the iterable your function will be operating over.





```python
from parallelize import parallelize

def foo(iterable: list) -> list:
	results = []
    for i in range(len(list)):
        # Functions that take long to process
        ...
    return results

parallelize.parallel(foo, list_of_items, *args, **kwargs)
```

