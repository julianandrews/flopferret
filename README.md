FlopFerret
==========
Texas Hold'em board texture analyzer.

Installation
------------

### Windows
Download the release [here](https://github.com/JulianAndrews/flopferret/releases).

### Python 3.7 or 3.8 on Linux or MacOS

Make sure you have pip installed for python3.7 or python3.8 (`pip --version`
should let you know). Then:

    pip install flopferret

should be all you need. On Linux systems I recommend

    pip install --user flopferret

instead, or better yet, installing in a virtualenv and launching with a script.

### Other versions of Python

`flopferret` can be made to to work in Python 3.5+, but you'll have to compile
some parts manually. First install
[pyEval7](https://github.com/JulianAndrews/pyeval7), and
[PySide2](https://pypi.org/project/PySide2/). Once you have those installed,
the instructions for Debian/Ubuntu should work.

With some minor code changes, `flopferret` can be made to work on Python 2.6+,
but distribution and compilation is a pain, and I don't have the time to
maintain that!
