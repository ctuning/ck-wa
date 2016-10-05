Workload Automation powered by Collective Knowledge
===================================================

Introduction
============

This Collective Knowledge repository provides high level
abstraction for [ARM Workload Automation framework (WA)](https://github.com/ARM-software/workload-automation).
It includes unified JSON API to WA, automated experimentation,
benchmarking and tuning across farms of machines, 
optimization knowledge sharing, etc. Please, read
[CK Getting Started Guide](http://github.com/ctuning/ck/wiki),
[DATE'16 paper](http://bit.ly/ck-date16) and 
[CPC'15 article](https://arxiv.org/abs/1506.06256)
for more details about CK and our vision of collaborative,
reproducible and systematic experimentation.

License
=======
* BSD, 3-clause 

Status
======
Heavy development phase lead by [dividiti](http://dividiti.com). 

News
====
* Upcoming CK presentation and demo at [ARM TechCon'16 (Oct. 27)](http://schedule.armtechcon.com/session/know-your-workloads-design-more-efficient-systems);
* Press-release: ARM and dividiti use CK to accelerate computer engineering (2016, [HiPEAC Info'45](https://www.hipeac.net/assets/public/publications/newsletter/hipeacinfo45.pdf), page 17)

Prerequisites
=============
* Collective Knowledge framework ([@GitHub](http://github.com/ctuning/ck))

[ARM WA](https://github.com/ARM-software/workload-automation) will be automatically installed by CK. 
It requires:
* python2
* pip (install via apt-get install python-pip)
* yaml (install via apt-get install libyaml-dev)

In the future, we plan to provide support for python 3+ and Windows/Linux/MacOS host platforms in the WA via CK unified routines.

Authors
=======

* [Grigori Fursin](http://fursin.net/research.html), dividiti / cTuning foundation
* [Anton Lokhmotov](https://www.hipeac.net/~anton), dividiti
* [Ed Plowman](https://uk.linkedin.com/in/ed-plowman-b3738b1), ARM

Installation
============
Obtain CK repository for Workload Automation:

```
 $ ck pull repo:ck-wa
```

Note that other CK repositories (dependencies) will be also
automatically pulled. For example, ''[ck-wa-workloads](https://github.com/ctuning/ck-wa-workloads)'' repository 
with all WA workloads shared in the CK format will also be installed
from GitHub. We expect that later other users will be able to easily 
share, plug in and reuse their workloads (or use them in private workgroups).

Usage
=====

First, you need to register a target machine in the CK as 
described in detail in the [CK wiki](https://github.com/ctuning/ck/wiki/Farms-of-CK-machines CK wiki):

```
 $ ck add machine:my-target-machine
```

Please, select either ''2) WA: Android machine accessed via ARM's workload automation framework''
for Android based machine or ''3) WA: Linux machine accessed via ARM's workload automation''
for Linux based machine. 

Now you can see available WA workloads via
```
 $ ck search program --tags=wa
   or
 $ ck list program:wa-*
```

Now you can try to run youtube workload via CK universal pipeline
using Android mobile device connected via ADB
(results will be recorded in a local ''wa_output directory''):
```
 $ ck run wa:wa-youtube --target=my-target-machine
```

You can also record all raw results using flat ''--record-raw'':
```
 $ ck run wa:wa-youtube --target=my-target-machine --record-raw
```

Raw results as well as unified JSON meta description will be recorded
using ck-result module. You can see them via
```
 $ ck list wa-result
```

Note, that results for the same workload will be currently rewritten
in ''wa-result''. Later we plan to add statistical analysis of multiple results.

You can also browse results in a user-friendly way via web-based WA dashboard:
```
 $ ck dashboard wa
```

Workloads which have C sources (currently '''dhrystone''' and '''memcpy''') 
are converted into universal CK program format. This allows users to
reuse powerful crowd-benchmarking, autotuning and crowd-tuning functionality
in the CK which works across different hardware, operating systems and compilers.

For example, you can compile dhrystone workload via
```
 $ ck compile program:dhrystone --speed --target=my-target-machine
```

You can then run dhrystone workload via CK and record results in the tmp directory via
```
 $ ck run program:dhrystone --target=my-target-machine
 $ ck ls `ck find program:dhrystone`/tmp
```

You can autotune above program (using shared autotuning plugins) via
```
 $ ck autotune program:dhrystone --target=my-target-machine
```

When autotuning/exploration is finished, you will see information
how to plot a graph with results.

You can also replay a given WA run using above UIDs via
```
 $ ck replay wa-result:{UID}
```

You can delete all above results via
```
 $ ck rm wa-result:* --force
```

Updating WA via CK
==================

You can install latest WA from GitHub for a given target machine via CK via
```
 $ ck install package:arm-wa-github --target={machine name}
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





Remote Access - NEED TO BE UPDATED using new functionality!!!
=============================================================

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

Future work
===========
* Current WA can work only with Python 2.x and does not support Windows. Hence, we plan to provide tighter integration with the CK to make WA support Python 3.x and all Linux/MacOS/Windows via CK unified routines.
* We continuing unifying high-level API to crowd-benchmark and crowd-tune shared workloads (see [1](http://bit.ly/ck-date16), [2](http://hal.inria.fr/hal-01054763) and [3](http://arxiv.org/abs/1506.06256) to know more about our vision).

Main reference
==============

```
 @inproceedings{cm:29db2248aba45e5:9671da4c2f971915,
   title =     {Collective Knowledge: towards R&D sustainability},
   author =    {Fursin, Grigori and Lokhmotov, Anton and Plowman, Ed},
   booktitle = {Proceedings of DATE 2016 (Design, Automation and Test in Europe)},
   year =      {2016},
   month =     {March},
   keys =      {http://www.date-conference.com},
   url =       {http://bit.ly/ck-date16}
 }
```

Publications
============
The concepts has been described in the following publications:

* http://bit.ly/ck-date16 (DATE'16)
* http://arxiv.org/abs/1506.06256 (CPC'15)
* http://hal.inria.fr/hal-01054763 (Journal of Scientific Programming'14)

You can download all above references in the BibTex format [here](https://raw.githubusercontent.com/ctuning/ck-guide-images/master/collective-knowledge-refs.bib).

Feedback
========
If you have questions or comments, feel free to get in touch with us 
via our [public mailing list](http://groups.google.com/group/collective-knowledge).

