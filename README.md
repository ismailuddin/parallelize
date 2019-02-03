# parallelize

<img src="logo.png" width="500px" style="justify:left">

`parallelize` is a Python package to simplify the process of parallelising your taks in Python. It takes advantage of the `multiprocessing` module to spawn new processes for your job.

### Requirements
- Python 3.X

### Installation
To install `parallelize`, first clone the repository. Then, run `python setup.py install` in the root directory.

### Documentation
To build the documentation, run `make html` inside the `docs/` folder. The documention will be found in the `docs/build/html` directory. 

### Usage

To parallelise a task in Python, you should wrap the entire code inside a function and have the first argument of your function receive the iterable your function will be operating over.

```python
>>> from parallelize import parallelize
>>> def foo(iterable: list) -> int:
...    output = 0
...    for i in iterable:
...        output = i**4
...    return output

>>> numbers = list(range(50000000))
>>> %time foo(numbers)
Wall time: 21.5 s
>>> parallelize.parallel(foo, numbers, 6)
Completed 'parallel' in 6.2743 secs
```

