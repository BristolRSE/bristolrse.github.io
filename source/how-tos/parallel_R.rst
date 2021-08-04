.. SPDX-FileCopyrightText: © 2021 James C. Womack <J.C.Womack@bristol.ac.uk>
   SPDX-License-Identifier: CC-BY-SA-4.0

Parallel R on HPC clusters
##########################

.. admonition:: What is this page about?

   How to write parallel `R <https://www.r-project.org/>`_ for high-performance computing (HPC) clusters 

.. contents:: Contents
   :local:

Introduction
============

There are many strategies for writing `R <https://www.r-project.org/>`_ programs that make use of parallelism.
The ``parallel`` package is part of base R (since R 2.14.0), enabling out-of-the-box multi-process parallelism (for single and multiple hosts). If you want to run R using of multiple cores on a single computer, or a small number of networked computers, this is a good place to start.
The CRAN Task View `High-Performance and Parallel Computing with R <https://cran.r-project.org/web/views/HighPerformanceComputing.html>`_ lists many packages relevant to R in parallel using HPC resources. 

This how-to article is concerned with **running R in parallel on high-performance computing (HPC) clusters**, in which a `job scheduler <https://en.wikipedia.org/wiki/Job_scheduler>`_ distributes user-submitted jobs to compute nodes and `MPI <https://en.wikipedia.org/wiki/Message_Passing_Interface>`_ is used for communication in multi-node parallel jobs.
In particular, the how-to focuses on a small number of methods for running parallel R that have been tested on the `University of Bristol ACRC's HPC facilities <https://www.bristol.ac.uk/acrc/high-performance-computing/>`_.  

.. _parallel-R-parallel-snow:

parallel + snow
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
On systems where process spawning is supported, MPI clusters can be created in R, for example

.. code-block:: R

   cl <- parallel::makeCluster(spec=4, type="MPI")

which creates 4 worker MPI processes (in addition to the running manager process).
Behind-the-scenes, ``parallel`` uses ``snow`` to create the MPI cluster.

During testing on ACRC's HPC facilities, spawning MPI processes using ``makeCluster`` was found to cause problems, particularly when submitting jobs to run across multiple compute nodes.
The recommended approach for creating an MPI cluster using ``parallel`` + ``snow`` on ACRC HPC facilities is to create the cluster prior to starting R using ``mpirun`` to run the ``RMPISNOW`` script distributed with the ``snow`` package (see `"MPI Clusters without Spawning" <http://www.stat.uiowa.edu/~luke/R/cluster/cluster.html>`_), e.g. in the job submission script

.. code-block:: shell

   mpirun -np 5 RMPISNOW [...]

which will create a manager MPI process and 4 worker MPI processes represented by a cluster object.The arguments following ``RMPISNOW`` (``[...]``) will be passed to the manager R process.

.. note:: 

   ``RMPISNOW`` is a shell script distributed with the ``snow`` R package.
   It is used to start a cluster of MPI processes (manager + workers) prior to running R code  using MPI parallelism via ``snow``.

   If ``RMPISNOW`` is not available on the system ``PATH``, it can be located in the R library tree in which ``snow`` is installed at the path ``<R library tree>/snow/RMPISNOW`` (your ``<R library tree>`` can be found by running ``.libPaths()`` in a R session). 

   ``RMPISNOW`` invokes R with the ``R`` command, rather than ``Rscript``.
   Command line arguments to ``RMPISNOW`` are forwarded to ``R``. 
   For non-interactive job submission scripts, it is useful to run ``R`` in batch mode e.g.

   .. code-block:: shell

      mpirun -np 5 RMPISNOW CMD BATCH --no-save --no-echo input.R output.Rout

   where ``--no-save`` and ``--no-echo`` tell R to not save the workspace at the end of the session and to suppress output of input commands, respectively.

To obtain the MPI cluster object created by ``RMPISNOW``, use ``snow::getMPIcluster``, rather than ``parallel::makeCluster``, e.g.

.. code-block:: R

   cl <- snow::getMPIcluster()

Once the cluster object has been created, this can be passed to the various functions provided by the ``parallel`` package for running parallel computations.
When the cluster is no longer required (usually at the end of the script), ``parallel::stopCluster`` should be used to shut down the cluster and ensure that worker processes are stopped, e.g.

.. code-block:: R

   stopCluster(cl)

Here is a short example R script that maps a "Hello world" function to an array of integers,  distributes calls across worker processes, then outputs all results on the manager process:

.. code-block:: R

   library(Rmpi)
   library(snow)
   library(parallel)

   cl <- snow::getMPIcluster()

   parallel::clusterExport(cl, c("MPI_COMM_WORLD"))

   fn <- function(n, comm = MPI_COMM_WORLD) { 
     info <- Sys.info()
     rank <- mpi.comm.rank(comm)
     return(sprintf("Hello world! Node %s (rank %s) received value %d", info["nodename"], rank,  n))
   }

   values <- seq(1, 100)

   results <- parallel::parSapply(cl, values, fn)

   for(s in results) {
     print(s)
   }

   parallel::stopCluster(cl)  

.. note:: 
   This example imports the ``Rmpi`` package, though it is not necessary in general to use ``parallel`` + ``snow`` for MPI parallelism.
   ``Rmpi`` provides low-level MPI wrapper functions used by ``snow`` and in this case, it is only used to obtain the rank of the MPI process running the "Hello world" function using ``mpi.comm.rank``.
   The ``parallel::clusterExport`` function is used to broadcast variable values from the manager process to the worker processes, in this case exporting the handle for the default MPI communicator, ``MPI_COMM_WORLD``.

Here is an example of a submission script that could be used to submit the abobve to a PBS-type scheduler (e.g. `OpenPBS <https://www.openpbs.org/>`_, `TORQUE <https://adaptivecomputing.com/cherry-services/torque-resource-manager/>`_) with non-process-spawning MPI:

.. code-block:: shell

   #!/bin/bash

   #PBS -N hello_mpi
   #PBS -l select=2:ncpus=4:mpiprocs=4:ompthreads=1:mem=500M
   #PBS -l walltime=00:01:00

   module load lib/openmpi/4.0.2-gcc
   module load lang/r/4.0.2-gcc

   R_LIBRARY_PATH="/sw/lang/R-4.0.2-gcc/lib64/R/library"
   RMPISNOW_SH="${R_LIBRARY_PATH}/snow/RMPISNOW"

   R_SCRIPT_PATH="${PBS_O_WORKDIR}/hello_mpi.R"
   R_OUTPUT_PATH="${PBS_O_WORKDIR}/hello_mpi.Rout"

   mpirun -np 8 ${RMPISNOW_SH} CMD BATCH --no-save --no-echo ${R_SCRIPT_PATH} ${R_OUTPUT_PATH}

The script requests a walltime of 1 minute and 2 resource "chunks" with 4 cores, 4 MPI processes, and 500 MB memory each (resource chunks may or may not run on different physical nodes, depending on how the cluster is configured).
The R script ``hello_mpi.R`` is run in batch mode with 1 manager process and 7 worker processes (8 total MPI processes) created by ``RMPISNOW``. 
The result is output in ``hello_mpi.Rout``.

.. note::
   The environment modules (``lib/openmpi/4.0.2-gcc`` and ``lang/r/4.0.2-gcc``) and ``R_LIBRARY_PATH`` value are specific to the `Blue Pebble cluster <https://www.bristol.ac.uk/acrc/high-performance-computing/>`_ at University of Bristol.
   These will need to be modified for other clusters.
   Similarly, the script will need modification to use on clusters using non-PBS-type schedulers, such as `SLURM <https://slurm.schedmd.com/documentation.html>`_.

   
pbdMPI
======
The ``pbdMPI`` package is part of the `Programming with Big Data in R (pdbR) project <https://pbdr.org/>`_, a set of R packages designed for use in distributed computing and data science.
The package is available via `CRAN <https://cran.r-project.org/package=pbdMPI>`_, e.g.

.. code-block:: R

   install.packages("pbdMPI")

``pbdMPI`` is a low-level MPI wrapper, allowing R code to perform typical MPI operations like broadcasting, gathering, and reducing data distributed across MPI processes.
If you have written code using MPI in other languages (e.g. Fortran, C), then ``pbdMPI``'s API should be familiar to you.

Unlike :ref:`parallel-R-parallel-snow`, ``pbdMPI`` has no concept of manager and worker MPI processes.
Instead, ``pbdMPI`` uses a Single Program Multiple Data (SPMD) model, in which each MPI process runs an identical program, but works with different data (i.e. all processes are workers).
This is a common approach in parallel HPC software, and enables the development of software in which parallel processes co-operatively exchange data as needed.

.. note::
   ``pbdMPI`` is designed for use in non-interactive (batch) mode, and should not be used within an interactive R session.
   Instead, run a R script using ``mpirun``, e.g.

   .. code-block:: shell

      mpirun -np 8 Rscript input.R > output.Rout

   Since all MPI processes are workers, R scripts using ``pbdMPI`` do not need to be started using a script like ``RMPISNOW`` (see :ref:`parallel-R-parallel-snow`) and can be run directly using ``mpirun``.
   However, in testing it was found that using ``R CMD BATCH`` caused problems with text output, so it is 
   recommended to use ``Rscript`` to invoke R.

R scripts using ``pbdMPI`` must start by initialising MPI using ``pbdMPI::init()`` and end by finalising MPI using ``pbdMPI::finalize()``.
Between these two function calls, worker processes can perform computations, communicate data, and perform collective MPI operations (e.g. reduction).
Each MPI process has a integer "rank" which can be obtained by calling ``comm.rank()``.
The rank of the process is typically used to control the behaviour of the process, for example by selecting a rank of input data to work on. 

Here is a short example R script that maps calls of a "Hello world" function (similar to the function used in :ref:`parallel-R-parallel-snow`) to data from an array of integers.
On each MPI process, the function is called on a chunk of data selected based on the process's rank.   

.. code-block:: R

   library(pbdMPI)

   fn <- function(n) { 
   info <- Sys.info()
   rank <- comm.rank()
   return(sprintf("Hello world! Node %s (rank %s) received value %d",
            info["nodename"], rank,  n))
   }

   init()

   values <- seq(0, 100)

   # Break data into chunks based on MPI rank 
   # (highest numbered rank gets any remainder)
   chunk_size <- length(values) %/% comm.size() # %/% is integer division
   if (comm.rank() < comm.size() - 1) {
     start <- comm.rank() * chunk_size + 1  # + 1 since R uses 1-based indexing
     end <- start + chunk_size - 1
   } else {
     start <- comm.rank() * chunk_size + 1
     end <- length(values)
   }

   lines <- sapply(values[start:end], fn)

   comm.print(paste(lines, sep = "\n"), all.rank = TRUE)

   finalize()

In this example, each MPI process divides the values array into a number of chunks equal to the total number of MPI processes (``comm.size()``), then selects a chunk based on its rank (``comm.rank()``).
Each process calls the function on its chunk locally using the base ``lapply()`` function and then the result from each process is globally printed (``comm.print()``).
This is in contrast to the :ref:`parallel-R-parallel-snow` "Hello world" example, where a call to ``parallel::parSapply()`` on the manager process chunks the data, distributes function calls to worker processes, and returns the result to the manager process.

The (PBS-style) job submission script for a R script using ``pbdMPI`` is simpler than the example for :ref:`parallel-R-parallel-snow`, as R does not need to be invoked using ``RMPISNOW``:

.. code-block:: R

   # TODO ... job submission example for pbdMPI ...

.. note::
   ``pbdMPI`` is well-documented!
   If you are interested learning more about using the package, see the detailed `vignette <https://cran.r-project.org/web/packages/pbdMPI/vignettes/pbdMPI-guide.pdf>`_ (``vignette("pbdMPI-guide")``).
   This includes examples which compare scripts using ``parallel`` + ``snow`` to equivalent scripts using ``pbdMPI``.
   The package is also distributed with a number of demos (described in the vignette) and the source code for the demos can be viewed on `GitHub <https://github.com/RBigData/pbdMPI/tree/master/demo>`_.


foreach + doMPI
===============


future + snow
=============


batchtools
==========

