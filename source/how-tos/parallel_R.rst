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

This how-to article is concerned with **running R in parallel on high-performance computing (HPC) clusters**, in which a `job scheduler <https://en.wikipedia.org/wiki/Job_scheduler>`_ distributes user-submitted jobs to compute nodes and `MPI <https://en.wikipedia.org/wiki/Message_Passing_Interface>`_ is used for communication in multi-node parallel jobs.

The CRAN Task View `High-Performance and Parallel Computing with R <https://cran.r-project.org/web/views/HighPerformanceComputing.html>`_ lists many packages relevant to R in parallel using HPC resources. 
This how-to focuses on a subset of these packages that have been tested on the `University of Bristol ACRC's HPC facilities <https://www.bristol.ac.uk/acrc/high-performance-computing/>`_.  

parallel + Rmpi + snow
======================


pbdMPI
======


foreach + doMPI
===============


future + snow
=============


batchtools
==========

