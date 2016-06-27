Workload Automation for ARM
===========================

Status
======
Unstable - heavy development phase

Prerequisites
=============
* Collective Knowledge framework ([@GitHub](http://github.com/ctuning/ck))
* (ARM WA) python2
* (ARM WA) pip (install via apt-get install python-pip)
* (ARM WA) yaml (install via apt-get install libyaml-dev)

Authors
=======

* Anton Lokhmotov, dividiti (UK)
* Grigori Fursin, dividiti (UK)

License
=======
* BSD, 3-clause

Installation
============
Obtain CK repository for Workload Automation:

```
 $ ck pull repo --url=https://github.com/dividiti/ck-wa
```
or
```
 $ ck pull repo --url=git@github.com:dividiti/ck-wa
```

Install Workload Automation via CK:
```
 $ ck install package:arm-wa-github
```

Local Usage
===========

First, add a description of a connected Android-based device to CK
(main properties will be automatically detected by CK).
```
 $ ck add wa-device
```

Check that your device was recorded in CK:
```
 $ ck list wa-device
```

For example, if you have Samsung Galaxy S7 conected, 
you should see CK entry "samsung-sm-g930f".

Check available workloads in CK format:
```
 $ ck list wa
```

Run dhrystone workload via CK:
```
 $ ck run wa:dhrystone --device=samsung-sm-g930f
```

Run dhrystone workload via CK and record results in CK repository
(using experiment module):
```
 $ ck run wa:dhrystone --device=samsung-sm-g930f --record
```

Raw results as well as unified JSON meta description will be recorded
using ck-result module. You can see them via
```
 $ ck list wa-result
```

You can also browse results in a user-friendy way via web-based WA dashboard:
```
 $ ck dashboard wa
```

You can delete all above results via
```
 $ ck rm wa-result:* --force
```

Using Docker image
==================

We have Docker automation in the CK. You can now build and run CK-powered WA
instance (on Linux and Windows) using the following commands:
```
 $ ck build docker:ck-wa
 $ ck run docker:ck-wa
```

You can find Docker image description in CK format in the following CK entry:
```
 $ ck find docker:ck-wa
```

This Docker image include Android SDK and NDK, and supports mobile devices connected via ADB.

If you would like to deploy above image on Windows, please follow instructions
from the 'ck-docker' repository:
```
 $ ck show repo:ck-docker
```

Remote Access
=============

WA can be accessed via CK web service with unified JSON API.

For internal tests, we have a CK-powered WA service running 
on a 'cknowledge.ddns.net' host machine with 7344 port. 

You can see CK dashboard via http://cknowledge.ddns.net:7344/?template=arm-wa

To be able to access above service via local CK instance, 
we already provided a proxy repository "remote-wa". 

You can now list devices connected to a remote machine via
```
 $ ck list remote-wa:device:*
```

You can now list workloads available in this remote service via
```
 $ ck list remote-wa:wa:*
```

You can run dhrystone workload on this remote machine (and connected mobile phone) via
```
 $ ck run remote-wa:wa:dhrystone --remote
```

You can run dhrystone workload on this remote machine (and connected mobile phone) 
and save output in JSON via
```
 $ ck run remote-wa:wa:dhrystone --remote --out=json_file --out_file=results.json
```

If you want to deploy Docker container with CK-powered WA web service on your own machine 
with "workgroup-hostname" IP, you should run it as following:
```
 $ ck run docker:ck-ubuntu-16.04 --WFE_HOST=workgroup-hostname"
```

You should then register this repository (for example with name "workgroup-wa-repo") 
on client machines with CK as following
```
 $ ck add repo:workgroup-wa-repo --remote --hostname=workgroup-hostname --port=3344 --quiet
```

It will then be possible to list and run workloads on the remote server via
```
 $ ck list workgroup-wa-repo:wa:
 $ ck run workgroup-wa-repo:wa:dhrystone
```
