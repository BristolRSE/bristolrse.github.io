.. SPDX-FileCopyrightText: © 2021 James C. Womack <J.C.Womack@bristol.ac.uk>
   SPDX-License-Identifier: CC-BY-SA-4.0

Parallel R on HPC clusters
##########################

.. admonition:: What is this page about?

   How to write parallel `R <https://www.r-project.org/>`_ for high-performance computing (HPC) clusters 

Introduction
============

There are many strategies for writing `R <https://www.r-project.org/>`_ programs that make use of parallelism.
The ``parallel`` package is part of base R (since R 2.14.0), enabling out-of-the-box multi-process parallelism (for single and multiple hosts). If you want to run R using of multiple cores on a single computer, or a small number of networked computers, this is a good place to start.
The CRAN Task View `High-Performance and Parallel Computing with R <https://cran.r-project.org/web/views/HighPerformanceComputing.html>`_ lists many packages relevant to R in parallel using HPC resources. 

This how-to article is concerned with **running R in parallel on high-performance computing (HPC) clusters**, in which a `job scheduler <https://en.wikipedia.org/wiki/Job_scheduler>`_ distributes user-submitted jobs to compute nodes and `MPI <https://en.wikipedia.org/wiki/Message_Passing_Interface>`_ is used for communication in multi-node parallel jobs.
In particular, the how-to focuses on a small number of methods for running parallel R that have been tested on the `University of Bristol ACRC's HPC facilities <https://www.bristol.ac.uk/acrc/high-performance-computing/>`_.  


``parallel`` + ``snow``
=======================
``parallel`` is part of base R and supports multiprocess parallelism out-of-the-box.
``parallel`` does not come with MPI support, but supports this using the ``snow`` package, which is available via `CRAN <https://cran.r-project.org/package=snow>`_, e.g.

.. code-block:: R

   install.packages("snow")

.. note::

   The functionality of ``parallel`` and ``snow`` overlap significantly because ``parallel`` includes revised parts of ``snow``. 
   The packages share a number of function names, so we must be explicit about which package we are using when both are loaded using ``::``, e.g. ``parallel::parSapply()``.
   
   In this example we use ``snow`` only where necessary for MPI parallelism, and use ``parallel`` otherwise.
   This allows the example code to be repurposed for non-MPI parallelism using ``parallel`` alone.  

The ``parallel`` package employs a manager/worker approach to parallelism, in which a manager R process orchestrates a number of worker R processes.
It provides a number of functions that, when called on the manager process, distribute computational work to worker processes.
Notably the package offers parallel analogues of R's built-in functions for mapping functions to arrays, e.g. ``parLapply()`` and ``parSapply()`` (analogues of ``lapply()`` and ``sapply()``, respectively).

The parallel mapping functions require a cluster object which specifies the pool of workers.
A cluster object can be created using the ``makeCluster()`` function.

pbdMPI
======


foreach + doMPI
===============


future + snow
=============


batchtools
==========

