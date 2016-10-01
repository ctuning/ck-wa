Workload Automation for ARM
===========================

Status
======
Heavy development phase ...

Prerequisites
=============
* Collective Knowledge framework ([@GitHub](http://github.com/ctuning/ck))
* (ARM WA) python2
* (ARM WA) pip (install via apt-get install python-pip)
* (ARM WA) yaml (install via apt-get install libyaml-dev)

Authors
=======

* Grigori Fursin, dividiti (UK)
* Anton Lokhmotov, dividiti (UK)
* Ed Plowman, ARM (UK)

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

First, you need to register a target machine in CK as 
described in detail in [https://github.com/ctuning/ck/wiki/Farms-of-CK-machines CK wiki]:

```
 $ ck add machine:my-target-machine
```

Please, select either ''2) WA: Android machine accessed via ARM's workload automation framework''
for Android based machine or ''3) WA: Linux machine accessed via ARM's workload automation''
for Linux based machine. 

Now you can try to run dhrystone workload via CK universal pipeline 
(results will be recorded in a local ''wa_output directory''):
```
 $ ck run wa:dhrystone --target=my-target-machine
```

Run dhrystone workload via CK and record results in the CK repository
(using experiment module):
```
 $ ck run wa:dhrystone --target=my-target-machine --record
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

You can replay a given WA run using above UIDs via
```
 $ ck replay wa:{UID}
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
on a 'cknowledge.ddns.net' host machine with 7344 port
(please, ping us in advance to start this service). 

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
