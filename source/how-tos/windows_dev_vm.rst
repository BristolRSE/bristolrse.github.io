.. SPDX-FileCopyrightText: © 2020 Matt Williams <matt@milliams.com>
   SPDX-License-Identifier: CC-BY-SA-4.0

Windows development VMs
#######################

.. admonition:: What is this page about?

   How to set up a Windows development virtual machine


VM images are `available from Microsoft <https://developer.microsoft.com/en-us/windows/downloads/virtual-machines/>`_ for use with VMWare, Hyper-V, VirtualBox, and Parallels are available and are ~20 GB in size. 

The VM images expire after 60 days (the expiry date should be shown on the download page). The images are provided for evaluation and demonstration (see the terms linked on the download page) and do not require activation.

The image contains Windows 10 Enterprise with `Visual Studio <https://developer.microsoft.com/en-gb/windows/downloads/>`_ and `Visual Studio Code <https://code.visualstudio.com/>`_ preinstalled. `Developer mode <https://docs.microsoft.com/en-us/windows/apps/get-started/enable-your-device-for-development>`_ and `Windows Subsystem for Linux <https://docs.microsoft.com/en-us/windows/wsl/about>`_ are enabled (Ubuntu is pre-installed). This represents and excellent starting point for development or testing.

Setup on MacOS with Parallels Desktop for Mac
=============================================
.. admonition:: Caveat

   The following notes describe how to set up a Windows development VM as a guest on a MacOS host using `Parallels Desktop for Mac <https://www.parallels.com/products/desktop/>`_ 16.5.0. You will need to adapt the steps for different host OSes and hypervisors.

Download and initial setup
--------------------------
Download the Parallels virtual machine image `from Microsoft <https://developer.microsoft.com/en-us/windows/downloads/virtual-machines/>`_.

Check the file hash of the download against the image. The values under "FileHash" in the table of downloads `provided by Microsoft <https://developer.microsoft.com/en-us/windows/downloads/virtual-machines/>`_ are SHA256 hash values, the default algorithm used by ``Get-FileHash`` in PowerShell. On MacOS we can check the hash using ``shasum``, e.g.

.. code-block:: shell
   
   shasum -a 256 WinDev2104Eval.Parallels.zip

replacing ``WinDev2104Eval.Parallels.zip`` with the name of the downloaded zip archive containing the VM.

Unzip the file into your Parallels virtual machine folder, e.g.

.. code-block:: shell

   unzip WinDev2104Eval.Parallels.zip -d ~/Parallels

replacing ``~/Parallels`` with your Parallels virtual machine folder (this can be found in the Preferences menu for Parallels Desktop).

.. warning::

   The archive is ~20 GB in size and the extracted VM image is ~40 GB, so to extract the archive as above requires ~60 GB available disk space.

Start Parallels Desktop and from the "File" menu, select "Open" and select the ``.pvm`` file extracted into your Parallels virtual machine folder (this is in fact a directory containing files associated with the VM).

The development VM will now be available to start within Parallels.

Recommended configuration
-------------------------
The default options for the VM in Parallels Desktop are not well-suited for development. To modify the settings, open the configuration window for the VM ("Actions" → "Configure..." from the menu bar). 

Here are some recommended settings that will make the VM more suitable for development.

Hardware
^^^^^^^^
In the "Hardware" tab of the VM configuration window

* Under "CPU & Memory", set memory to 4 GB (the default of 1.5 GB is on the low side)

Sharing
^^^^^^^

Parallels offers impressive integration between the host MacOS system and guest Windows VM, and this is activated by default. However, this is unnecessary (and potentially confusing) for a short-lived development VM image.

Limit sharing to a single folder and disabling "Shared profile" (where MacOS and Windows both use some of the host machine's user folders). Select "Sharing" from the left of the "Options" tab of the VM configuration window and under "Share Mac"

* Change "Share folders" to "None"
* Click "Custom folders..." and add your preferred shared folder from the host macOS system to the list of shared folders (e.g. ``~/Parallels Shared``)
* Uncheck "Share Mac use folders with Windows"
* Uncheck "Share cloud folders with Windows"
* Uncheck "Map Mac volumes to Windows"

Under  "Share Windows"

* Uncheck "Access Windows folders from Mac"

Disable sharing of Windows applications with MacOS (and MacOS applications with Windows). This disables the ability for the host and guest operating systems to open applications from each other. Select "Applications" from the right of the "Options" tab of the VM configuration window and

* Uncheck "Share Windows applications with Mac"
* Uncheck "Show Windows notification area in Mac menu bar"
* Uncheck "Allow apps to auto-switch to full screen"
* Uncheck "Share Mac applications with Windows"

Backup
^^^^^^

The VM image is both large and will expire after 60 days. It is sensible to exclude this from Time Machine backups. To do this, open the Time Machine menu (from menu bar on MacOS 10.15 Catalina, Apple menu → "System Preferences..." → "Time Machine"), then select the "Options..." button in the Time Machine menu. Add the ``.pvm`` file for the Windows development VM to the list of excluded items. Parallels should inform you that the VM is not being backed up in the "Backup" tab of the VM configuration window.
   
Snapshots
^^^^^^^^^

It may be useful to enable automated snapshotting of the VM. This will allow changes to be rolled back if the VM gets into a broken state. To enable this, select the "Backup" tab of the VM configuration window and check "SmartGuard". To configure the frequency of snapshots and number of snapshots to keep, click "Details..." and modify the settings.

Hints and tips
--------------

License expiry
^^^^^^^^^^^^^^

The evaluation license for the VM expires on the date specified on the `download page <https://developer.microsoft.com/en-us/windows/downloads/virtual-machines/>`_. The VM should present a warning message on startup when it is nearing expiry.

A description of the VM, including the expiry date can be viewed when the VM is running by selecting the VM name from the MacOS menu bar and then selecting the "About" option (e.g. "WinDev2104Eval" → "About WinDev2104Eval").