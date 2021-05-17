.. SPDX-FileCopyrightText: © 2020 Matt Williams <matt@milliams.com>
   SPDX-License-Identifier: CC-BY-SA-4.0

Python packages
###############

When you do something like:

.. code-block:: python

   import some_package

in a Python script, in the background Python goes away to try to find that package somewhere on your computer.
If it's a standard, built-in package like :py:mod:`math` or :py:mod:`sys` then it knows exactly where to look.

For any third-party packages like :py:mod:`pandas`, :py:mod:`tensorflow` or :py:mod:`matplotlib`, it will look in a set number of known locations.
This set of known locations is referred to as the "Python path".
They are usually located around wherever Python itself was installed.

If you are on a shared computer, like the University's HPC systems then the Python path will be pointing at a bunch of directories that you have no control over.
If you want to have Python be able to find a new package, one option would be to ask the systems administrators to install it for you.

The alternative option is to change the Python path.
There are fiddly ways to do this that you might come across if you search online but these days the only method you should use is "virtual environments".

Virtual environments
====================

A virtual environments is little more than a directory into which you can install any Python packages you want.
They come with a little bit of automation which allows you to automatically have Python set the Python path correctly to make them available.

This means that you can have a separate virtual environment for each different project you work on.
If they require different packages, or even different version of the same package, you can do it without any clashes.

Creating and using a virtual environment on BluePebble
------------------------------------------------------

The first step is to get a base version of Python to use.
You could download this yourself (e.g. from python.org or use Miniconda) but BluePebble comes with versions of Python available.

Getting Python
^^^^^^^^^^^^^^

To search for all available Python modules, run:

.. code-block:: shell-session

   $ module spider python


You'll see a whole bunch under the ``lang/python/anaconda`` prefix.
Chose one with a recent version of Python (the 3.x.y number) and without a suffix (like -AM, as they are special copies for certain groups).
In my case I will use ``lang/python/anaconda/3.8-2020.07``:

.. code-block:: shell-session

   $ module load lang/python/anaconda/3.8-2020.07

Now if you do `python3 --version`, you should get ``Python 3.8.3``.

Creating a virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now that you've got the version of Python you want, you can create a virtual environment.
This is managed by the built-in `venv <https://docs.python.org/3/library/venv.html>`_ module.
There are other tools available which manage environments in a slightly different way (e.g. conda or poetry) but we won't cover them here.

When creating a virtual environment, you need to give the directory a name, in this case I will call it :file:`my_venv` but you can name it after the project you are working on if you like:

.. code-block:: shell-session

   $ python3 -m venv my_venv

You should now see a directory called :file:`my_venv` in your current working directory.

Inside that directory you will see a few subdirectories.
Of note are the :file:`bin` directory which is where any tools you install into the virtual environment will go (if you peek in there now you'll see there's already a copy of `python` and `pip`) and the :file:`lib` directory which is where any modules you install will go (actually all the way under :file:`lib/python3.8/site-packages`).

One of the first things to do with a new virtual environment is to make sure `pip` itself is up-to-date with:

.. code-block:: shell-session

   $ my_venv/bin/pip install --upgrade pip

You'll need to do this every time you create a new virtual environment.

Installing packages
^^^^^^^^^^^^^^^^^^^

You can now go ahead and install any packages you want into this virtual environment.
You do this using the copy of `pip` in the environment.
For example, if you wanted to install the package :py:mod:`rich`, you would do:

.. code-block:: shell-session

   $ my_venv/bin/pip install rich

For managing your required packages properly, see the section below on "Reproducibility".

Using a virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to run a script using the virtual environment you have made, you can specify the copy of Python within explicitly.
So, instead of writing:

.. code-block:: shell-session

   $ python3 my_script.py

you would write

.. code-block:: shell-session

   $ ~/my_venv/bin/python my_script.py

This will work on the interactive terminal as well as in job scripts.

Deleting a virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can delete a virtual environment by deleting the folder that was created at the beginning. In our case:

.. code-block:: shell-session

   $ rm -r my_venv

Reproducibility
===============

A benefit of using virtual environment is that it gives you control over exactly which packages, and at which version, you install.

You should treat each virtual environment as ephemeral and feel able to destroy and recreate it at any time.
If you make it easy for yourself to recreate the environment, it will be easy for other people to do the same and get a matching environment to you.

The primary way to do this is to create a plain text file called :file:`requirements.txt` which lists all the packages you need, along with their versions.

.. code-block:: text

   rich==10.2.0
   requests==2.25.1

you can then use this file as an argument to `pip` to install all those packages:

.. code-block:: shell-session

   $ my_venv/bin/pip install -r requirements.txt

and this will install the packages, at the required versions, into the virtual environment.

Using a :file:`requirements.txt` file like this is the recommended way to manage your Python packages.

You can find a lot more information about `pip` in `its documentation <https://pip.pypa.io/en/stable/>`_.
