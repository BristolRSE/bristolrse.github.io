.. SPDX-FileCopyrightText: © 2021 James C. Womack <J.C.Womack@bristol.ac.uk>
   SPDX-License-Identifier: CC-BY-SA-4.0

Parallel R on HPC clusters
##########################

.. admonition:: What is this page about?

   How to write parallel `R <https://www.r-project.org/>`__ for high-performance computing (HPC) clusters 

.. contents:: Contents
   :local:

Introduction
============

There are many strategies for writing `R <https://www.r-project.org/>`__ programs that make use of parallelism.
The ``parallel`` package is part of base R (since R 2.14.0), enabling out-of-the-box multi-process parallelism (for single and multiple hosts). If you want to run R using of multiple cores on a single computer, or a small number of networked computers, this is a good place to start.
The CRAN Task View `High-Performance and Parallel Computing with R <https://cran.r-project.org/web/views/HighPerformanceComputing.html>`__ lists many packages relevant to employing parallelism in R. 

This how-to article is concerned with **running R in parallel on high-performance computing (HPC) clusters**, in which a `job scheduler <https://en.wikipedia.org/wiki/Job_scheduler>`__ distributes user-submitted jobs to compute nodes and `MPI <https://en.wikipedia.org/wiki/Message_Passing_Interface>`__ is used for communication in multi-node parallel jobs.
In particular, the how-to focuses on a small number of methods for running parallel R that have been tested on the `University of Bristol ACRC's HPC facilities <https://www.bristol.ac.uk/acrc/high-performance-computing/>`__.  

.. note::
   The example PBS-type job submission scripts in this how-to use environment modules (e.g. ``lib/openmpi/4.0.2-gcc`` and ``lang/r/4.0.2-gcc``) and set paths (e.g. ``R_LIBRARY_PATH``) specific to the `Blue Pebble cluster <https://www.bristol.ac.uk/acrc/high-performance-computing/>`__ at University of Bristol.
   These will need to be modified for other clusters.
   Similarly, the scripts will need modification for use on clusters using non-PBS-type schedulers, such as `SLURM <https://slurm.schedmd.com/documentation.html>`__.


.. _parallel-R-parallel-snow:

parallel + snow
=======================
``parallel`` is part of base R and supports multiprocess parallelism out-of-the-box.
``parallel`` does not come with MPI support, but supports this using the ``snow`` package, which is available via `CRAN <https://cran.r-project.org/package=snow>`__, e.g.

.. code-block:: R

   install.packages("snow")

.. note::

   The functionality of ``parallel`` and ``snow`` overlap significantly because ``parallel`` includes revised parts of ``snow``. 
   The packages share a number of function names, so it is useful to be explicit about which package we are using when both are loaded using ``::``, e.g. ``parallel::parSapply()``.
   
   In this example we use ``snow`` only where necessary for MPI parallelism, and use ``parallel`` otherwise.
   This allows the example code to be easily repurposed for non-MPI parallelism using ``parallel`` alone.  

The ``parallel`` package employs a manager/worker approach to parallelism, in which a manager R process orchestrates a number of worker R processes.
It provides a number of functions that, when called on the manager process, distribute computational work to worker processes.
Notably the package offers parallel analogues of R's built-in functions for mapping functions to arrays, e.g. ``parLapply()`` and ``parSapply()`` (analogues of ``lapply()`` and ``sapply()``, respectively).

The parallel mapping functions require a cluster object which specifies the pool of workers.
A cluster object can be created using the ``makeCluster()`` function.
On systems where process spawning is supported, MPI clusters can be created in an R session, for example

.. code-block:: R

   cl <- parallel::makeCluster(spec=4, type="MPI")

which creates 4 worker MPI processes (in addition to the running manager process).
Behind the scenes, ``parallel`` uses ``snow`` to create the MPI cluster.

During testing on ACRC's HPC facilities, spawning MPI processes using ``makeCluster`` was found to cause problems, particularly when submitting jobs to run across multiple compute nodes.
The recommended approach for creating an MPI cluster using ``parallel`` + ``snow`` on ACRC HPC facilities is to create the cluster prior to starting R using ``mpirun`` to run the ``RMPISNOW`` script distributed with the ``snow`` package (see `"MPI Clusters without Spawning" <http://www.stat.uiowa.edu/~luke/R/cluster/cluster.html>`__), e.g. in the job submission script use

.. code-block:: shell

   mpirun -np 5 RMPISNOW [...]

which will create a manager MPI process and 4 worker MPI processes represented by a cluster object.
The arguments following ``RMPISNOW``, ``[...]``, will be passed to the manager R process.

.. note:: 

   ``RMPISNOW`` is a shell script distributed with the ``snow`` R package.
   It is used to start a cluster of MPI processes (manager + workers) prior to running R code  using MPI parallelism via ``snow``.

   If ``RMPISNOW`` is not available on the system ``PATH``, it can be located in the R library tree in which ``snow`` is installed at the path ``<R library tree>/snow/RMPISNOW``. 
   Your ``<R library tree>`` can be found by running ``.libPaths()`` in an R session. 

   ``RMPISNOW`` invokes R with the ``R`` command, rather than ``Rscript``.
   Command line arguments to ``RMPISNOW`` are forwarded to ``R``. 
   For non-interactive job submission scripts, it is useful to run ``R`` in batch mode e.g.

   .. code-block:: shell

      mpirun -np 5 RMPISNOW CMD BATCH --no-save --no-echo input.R output.Rout

   where ``--no-save`` and ``--no-echo`` tell R to not save the workspace at the end of the session and to suppress output of input commands, respectively.

To obtain the MPI cluster object created by ``RMPISNOW``, use ``snow::getMPIcluster()``, rather than ``parallel::makeCluster()``, e.g.

.. code-block:: R

   cl <- snow::getMPIcluster()

Once the cluster object has been created (using ``parallel::makeCluster()`` or ``RMPISNOW`` with ``snow::getMPIcluster()``) this can be passed to the various functions provided by the ``parallel`` package for running parallel computations.
See the vignette for ``parallel`` (``vignette("parallel")``) for details of the available functions.

When the cluster is no longer required (usually at the end of the script), ``parallel::stopCluster()`` should be used to shut down the cluster and ensure that worker processes are stopped, e.g.

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
   This example imports the ``Rmpi`` package, though it is not generally necessary to import this when using ``parallel`` + ``snow`` for MPI parallelism.
   ``Rmpi`` provides low-level MPI wrapper functions used by ``snow``. 
   In this case, it is only used to obtain the rank of the MPI process running the "Hello world" function using ``mpi.comm.rank()``.

   The ``parallel::clusterExport()`` function is used to broadcast variable values from the manager process to the worker processes. 
   In this case, the function exports the handle for the default MPI communicator, ``MPI_COMM_WORLD``.

Here is an example of a submission script that could be used to submit the above R program to a PBS-type scheduler (e.g. `OpenPBS <https://www.openpbs.org/>`__, `TORQUE <https://adaptivecomputing.com/cherry-services/torque-resource-manager/>`__) with non-process-spawning MPI:

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

   
pbdMPI
======
The ``pbdMPI`` package is part of the `Programming with Big Data in R (pdbR) project <https://pbdr.org/>`__, a set of R packages designed for use in distributed computing and data science.
The package is available via `CRAN <https://cran.r-project.org/package=pbdMPI>`__, e.g.

.. code-block:: R

   install.packages("pbdMPI")

``pbdMPI`` is a low-level MPI wrapper, allowing R code to perform typical MPI operations like broadcasting, gathering, and reducing data distributed across MPI processes.
If you have written code using MPI in other languages (e.g. Fortran, C), then ``pbdMPI``'s API should be familiar to you.

Unlike :ref:`parallel-R-parallel-snow`, ``pbdMPI`` has no concept of manager and worker MPI processes.
Instead, ``pbdMPI`` uses a Single Program Multiple Data (SPMD) model, in which each MPI process runs an identical program, but works with different data (i.e. all processes are equal workers).
This is a common approach in parallel HPC software, and enables the development of sophisticated software in which parallel processes co-operatively exchange data as needed.

.. note::
   ``pbdMPI`` is designed for use in non-interactive (batch) mode, and should not be used within an interactive R session.
   Instead, run an R script using ``mpirun``, e.g.

   .. code-block:: shell

      mpirun -np 8 Rscript input.R > output.Rout

   Since all MPI processes are workers, R scripts using ``pbdMPI`` do not need to be started using a script like ``RMPISNOW`` (see :ref:`parallel-R-parallel-snow`) and can be run directly using ``mpirun``.
   
   In testing it was found that using ``R CMD BATCH`` caused problems with output to files, so it is 
   recommended to use ``Rscript`` to invoke R and redirect the output to a file (as above).

R scripts using ``pbdMPI`` must start by initialising MPI using ``pbdMPI::init()`` and end by finalising MPI using ``pbdMPI::finalize()``.
Between these two function calls, worker processes can perform computations, communicate data, and perform collective MPI operations (e.g. reduction).
Each MPI process has a integer "rank" which can be obtained by calling ``comm.rank()``.
The rank of the process is typically used to control the behaviour of the process, for example by selecting a chunk of input data to work on. 

Here is a short example R script that maps calls of a "Hello world" function (similar to the function used in :ref:`parallel-R-parallel-snow`) to data from an array of integers.
For each MPI process, the function is called on a chunk of data selected based on the process's rank.   

.. code-block:: R

   library(pbdMPI)

   fn <- function(n) { 
   info <- Sys.info()
   rank <- comm.rank()
   return(sprintf("Hello world! Node %s (rank %s) received value %d",
            info["nodename"], rank,  n))
   }

   init()

   values <- seq(1, 100)

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

In this example, each MPI process divides the ``values`` array into a number of chunks equal to the total number of MPI processes (``comm.size()``), then selects a chunk based on its rank (``comm.rank()``).
Each process calls the function on its chunk locally using the base ``lapply()`` function and then the result from each process is globally printed (``comm.print()``).
This is in contrast to the :ref:`parallel-R-parallel-snow` "Hello world" example, where a call to ``parallel::parSapply()`` on the manager process chunks the data, distributes function calls to worker processes, and returns the result to the manager process.

The (PBS-style) job submission script for a R script using ``pbdMPI`` is simpler than the example for :ref:`parallel-R-parallel-snow`, as R does not need to be invoked using ``RMPISNOW``:

.. code-block:: shell

   #!/bin/bash

   #PBS -N hello_mpi
   #PBS -l select=2:ncpus=8:mpiprocs=8:ompthreads=1:mem=500M
   #PBS -l walltime=00:01:00

   module load lib/openmpi/4.0.2-gcc
   module load lang/r/4.0.2-gcc

   R_SCRIPT_PATH="${PBS_O_WORKDIR}/hello_mpi.R"
   R_OUTPUT_PATH="${PBS_O_WORKDIR}/hello_mpi.Rout"

   mpirun -np 16 Rscript ${R_SCRIPT_PATH} > ${R_OUTPUT_PATH}

The script requests a walltime of 1 minute and 2 resource "chunks" with 8 cores, 8 MPI processes and 500 MB memory each.
The R script ``hello_mpi.R`` is run using ``Rscript`` with 16 MPI processes and (standard) output is redirected to the file ``hello_mpi.Rout`` (OpenMPI's ``mpirun`` `collects the standard output from all MPI processes <https://www.open-mpi.org/doc/current/man1/mpirun.1.php#sect17>`__ and this is redirected to the output file).
Each MPI process runs the same R code, but differs in the value returned by ``comm.rank()``.

.. note::
   ``pbdMPI`` is well-documented!
   If you are interested learning more about using the package, see the detailed `vignette <https://cran.r-project.org/web/packages/pbdMPI/vignettes/pbdMPI-guide.pdf>`__ (``vignette("pbdMPI-guide")``).
   This includes examples which compare scripts using ``parallel`` + ``snow`` to equivalent scripts using ``pbdMPI``.
   The package is also distributed with a number of demos (described in the vignette) and the source code for the demos can be viewed on `GitHub <https://github.com/RBigData/pbdMPI/tree/master/demo>`__.


foreach + doMPI
===============

The ``foreach`` package adds a `foreach loop <https://en.wikipedia.org/wiki/Foreach_loop>`__ construct to R.
This allows iterating over elements in a collection without using an explicit counter variable.
The iterations of a ``foreach`` loop can be executed in parallel and the construct is designed to be generic with respect to the form of parallelism, allowing the same R code to be run using a variety of computational backends.

The ``doMPI`` package provides a parallel backend for ``foreach``, allowing ``foreach`` loops to be parallelised using MPI .
As in ``snow`` (see :ref:`parallel-R-parallel-snow`), ``doMPI`` uses ``Rmpi`` for access to low-level MPI functions.

Both `foreach <https://cran.r-project.org/package=foreach>`__ and `doMPI <https://cran.r-project.org/package=doMPI>`__ are available via CRAN, e.g. 

.. code-block:: R

   install.packages(c("foreach", "doMPI"))

.. note::

   Other parallel backends for ``foreach`` are available, allowing ``foreach`` loop constructs to be parallelised using different methods. 
   For example, the ``doParallel`` package (available on `CRAN <https://cran.r-project.org/package=doParallel>`__) provides an interface between ``foreach`` and the the core R ``parallel`` package, allowing ``foreach`` loops to make use of multiprocess parallelism.
   
   While it may be possible to use a ``snow``-type MPI cluster with ``doParallel`` for MPI-parallelism with ``foreach``, this how-to focuses on ``doMPI``.
   The ``doMPI`` package is well-documented (see the `vignette <https://cran.r-project.org/web/packages/doMPI/vignettes/doMPI.pdf>`__) and, unlike :ref:`parallel-R-parallel-snow`, does not require R to be started using a wrapper script when using non-process-spawning MPI.

Similar to :ref:`parallel-R-parallel-snow`, ``foreach`` with ``doMPI`` uses a manager/worker approach to parallelism.
The manager process runs your R code and sends work to worker processes via parallel ``foreach`` loops.

Although ``doMPI`` can be used with process spawning MPI, it is recommended to use a non-process-spawning approach when running jobs on a HPC cluster using a job scheduler (`vignette("doMPI")` <https://cran.r-project.org/web/packages/doMPI/vignettes/doMPI.pdf>`_).
To do this, start R with ``mpirun``, e.g.

.. code-block:: shell

   mpirun -np 5 Rscript script.R > script.Rout

which will create 5 MPI processes, 1 manager and 4 workers, and run ``script.R``, sending output to ``script.Rout``.
It is important to note that invoking R in this way causes **all MPI processes to start by executing the same code** in the script.
The MPI processes are partitioned into manager and worker roles by calling ``startMPIcluster()`` in the script, which returns a cluster object.

.. code-block:: R

   cl <- startMPIcluster()

Worker processes stop executing the script at this point and will instead execute a worker loop, waiting for instructions from the manager process.
Only the manager process will continue executing the remainder of the script.
To avoid workers running code intended to be only run by the master, it ``startMPIcluster()`` should be called at the start of the script.

.. code-block:: R

   library(Rmpi)
   library(foreach)
   library(doMPI)

   cl <- startMPIcluster()

   MPI_COMM_WORLD <- cl$comm
   print(sprintf("Hello world, this is your manager speaking from rank %d",
         mpi.comm.rank(MPI_COMM_WORLD)))

   registerDoMPI(cl)

   fn <- function(n, comm = MPI_COMM_WORLD) {
     info <- Sys.info()
     rank <- mpi.comm.rank(comm)
     return(sprintf("Hello world! Node %s (rank %s) received value %d",
            info["nodename"], rank,  n))
   }

   values <- seq(1, 100)

   results <- foreach(i = values) %dopar% {
      fn(i)
   }

   for (s in results) {
     print(s)
   }

   closeCluster(cl)
   mpi.quit()

.. code-block:: shell

   #!/bin/bash

   #PBS -N hello_mpi
   #PBS -l select=4:ncpus=2:mpiprocs=2:ompthreads=1:mem=500M
   #PBS -l walltime=00:01:00

   module load lib/openmpi/4.0.2-gcc
   module load lang/r/4.0.2-gcc

   R_SCRIPT_PATH="${PBS_O_WORKDIR}/hello_mpi.R"
   R_OUTPUT_PATH="${PBS_O_WORKDIR}/hello_mpi.Rout"

   mpirun -np 8 Rscript ${R_SCRIPT_PATH} > ${R_OUTPUT_PATH}

future + snow
=============


batchtools
==========

