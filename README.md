FlopFerret
==========
Texas Hold'em board texture analyzer.

Installation
------------

### Windows
Download the most recent release [here](https://github.com/JulianAndrews/flopferret/releases).

### Linux/OS X
Installation is currently largely manual. You'll need Python 2.6 or 2.7 and Cython. First get [pyEval7](https://github.com/JulianAndrews/pyeval7). After downloading the repo, install pyEval7 with:

    python setup.py install
 
or for single-user installation:

    python setup.py install --user

You will also need to install the `pyparsing` and `pyside` modules. Both of these modules and Cython are available via `easy_install` or `pip`, and also as packages in the Ubuntu repos.

OS X installation is untested, but theoretically should work. Let me know if you have any questions/comments!
