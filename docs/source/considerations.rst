.. considerations:

Considerations with using ``multiprocessing``
=============================================

Python's ``multiprocessing`` module enables parallel processing by spawning new
processes, within which your code can run. Once completed, the processes are
joined back into the main process. This approach introduces a number of
potential problems discussed below.

Potential considerations
-------------------------

Functions must support pickling
................................

The method by which Python spawns new processes includes pickling the object
using the ``pickle`` module. Certain types of classes and objects may not be
able to be pickled, in which case using this module or the ``multiprocessing``
will fail.


Large outputs add a significant overhead
.........................................

Since parallel processing is achieved by spawning new processes, which have
their own memory, the output of the function needs to be transferred as well
back to the main process. If this object is particularly large, the transfer
process can become very slow. This can sometimes mean despite using multiple
cores to speed up the computation, the data transfer ends up taking as long or
longer to take place. The end result being no benefit from parallel processing,
or worse an even longer wait time.

To circumvent this issue, ``parallelize`` offers the option to pickle the
output to a temporary file using the ``cPickle`` module and the fastest
pickling protocol. The files are then read back by the main process and merged
into one file. This can sometimes offer a speed up, however the process of
pickling an object is still relatively slow.

This option can be enabled using the argument ``write_to_file`` in the
``parallelize.parallel()`` function::

    >>> from parallelize import parallelize

    >>> def foo(iterable: list) -> int:
    ...    output = 0
    ...    for i in iterable:
    ...        output = i**4
    ...    return output

    >>> parallelize.parallel(foo, numbers, n_jobs=6, write_to_file=True)


