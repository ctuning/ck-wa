Workload Automation powered by Collective Knowledge
===================================================

[![logo](https://github.com/ctuning/ck-guide-images/blob/master/logo-powered-by-ck.png)](http://cKnowledge.org)
[![logo](https://github.com/ctuning/ck-guide-images/blob/master/logo-validated-by-the-community-simple.png)](http://cTuning.org)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

Introduction
============

This Collective Knowledge repository provides high level
front-end for [ARM Workload Automation framework (WA)](https://github.com/ARM-software/workload-automation).
It includes unified JSON API to WA, automated experimentation,
benchmarking and tuning across farms of machines (Android, Linux,
MacOS, Windows), web-based dashboard, optimization knowledge sharing, etc.
 Please, read [CK Getting Started Guide](http://github.com/ctuning/ck/wiki),
[DATE'16 paper](http://bit.ly/ck-date16) and 
[CPC'15 article](https://arxiv.org/abs/1506.06256)
for more details about CK and our vision of collaborative,
reproducible and systematic experimentation.

License
=======
* BSD, 3-clause 

Status
======
Relatively stable. 
Development is led by [dividiti](http://dividiti.com], 
the [cTuning foundation](http://cTuning.org) 
and [ARM](http://www.arm.com].

You can see some public crowd-benchmarking results at 
[CK public repo](http://cknowledge.org/repo) - just
select "crowd-benchmark shared workloads via ARM WA framework"
crowdsourcing scenario.

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
* trace-cmd (install via apt-get install trace-cmd) - useful for advanced scenarios

CK is very portable and can run on diverse platforms including Linux, Windows, MacOS with Python 2.7 and 3.2+.
WA can currently run only on Linux/MacOS with Python 2.7 - in the future, we plan to 
provide tighter integration of WA with the CK to make it run across any platform with Python 2.7 and 3.2+.

Authors
=======

* [Grigori Fursin](http://fursin.net/research.html), dividiti / cTuning foundation
* [Sergei Trofimov](https://uk.linkedin.com/in/sergei-trofimov-0206a55), ARM
* [Michael McGeagh](https://uk.linkedin.com/in/mcgeagh), ARM
* Dave Butcher, ARM
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
 $ ck list wa
```

Now you can try to run youtube workload via CK universal pipeline
using Android mobile device connected via ADB
(results will be recorded in a local ''wa_output directory''):
```
 $ ck run wa:youtube --target=my-target-machine
```

Note, that all raw and unified results will be automatically recorded 
in ''wa-result'' entries. You can see these entries via
```
 $ ck list wa-result
```

You can also browse results in a user-friendly way via web-based WA dashboard:
```
 $ ck dashboard wa
```

You can easily clean all results via:
```
 $ ck rm wa-result:* --force
```

Some workloads required mandatory parameters. You can cache 
and later reuse them via flag ''--cache'', i.e.
```
 $ ck run wa:skype --cache
```
You will be asked parameters only once. Note, that at this moment,
password parameters are openly recorded in CK repo, which is totally
insecure. We plan to develop a secure auth mechanism for such workloads
in the future: https://github.com/ARM-software/workload-automation/issues/267

We also provided ''scenario'' flag to pre-select device config (such as
used instruments) and parameters. You can see available WA scenarios via
```
 $ ck list wa-scenario
```

You can then run a given workload with a given scenario via
```
 $ ck run wa:youtube --scenario=cpu
```

Note that scenario ''cpu'' requires trace-cmd installed on your host machine.
''It may also require your mobile device to be rooted''!
On Ubuntu, you can install it via
```
 $ sudo apt install trace-cmd
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

Demo of crowd-benchmarking (remote collection of statistics)
============================================================

We prepared a demo to crowdsource benchmarking (and tuning)
of shared workloads. Any user can participate in crowd-benchmarking
simply as following

```
 $ ck crowdbench wa:dhyrstone
```

You can also attribute your public contributions using flag --user via
```
 $ ck crowdbench wa:googlephotos --user=grigori@dividiti.com
```

The results are aggregated in the [Collective Knowledge public repository](http://cknowledge.org/repo).
You just need to select crowdsourcing scenario "crowd-benchmark shared workloads via ARM WA framework".

At the same page, you can also see all participated platforms, CPU, GPU, OS, as well as user timeline.

You can also participate in crowd-tuning of other shared workloads simply via
```
 $ ck pull repo:ck-crowdtuning
 $ ck crowdsource experiment
```

Finally, you can participate in crowd-benchmarking and crowd-tuning 
using commodity mobile phones via two Android apps:
* [For small workloads](https://play.google.com/store/apps/details?id=openscience.crowdsource.experiments)
* [For large workloads including DNN libs such as Caffe](https://play.google.com/store/apps/details?id=openscience.crowdsource.video.experiments)

Updating WA via CK
==================

You can install or update latest WA from GitHub for a given target machine via CK via
```
 $ ck install package:arm-wa-github
```

Just follow online instructions to reinstall WA on your machine.

Using Windows devices
=====================

It is possible to run workloads (currently shared as sources in CK format)
on remote Windows devices using light-weight, standalone, open-source 
[CK crowd-node server](https://github.com/ctuning/ck-crowdnode) (similar to ADB).
Simply download the latest CK crowd-node version [here](https://ci.appveyor.com/project/gfursin/ck-crowdnode/build/artifacts), 
install and run it on your target Windows device,
and then register it in CK-WA using ''ck add machine''.

''Note that at this stage your client machine should also run Windows.
However, we may provide cross-compilation in the future.''

Using Docker image
==================

We have Docker automation in the CK. 

You can run the latest [CK-WA Docker image](https://hub.docker.com/r/ctuning/ck-wa/) via
```
 $ ck run docker:ck-wa
    or
 $ docker pull ctuning/ck-wa
 $ docker run ctuning-ck-wa

```

You can also build and run your local or customized CK-WA
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

Importing workloads, devices and instruments from CK
====================================================
To be able to easily share and reuse workloads, devices, instruments
and other WA artifacts, we automatically import them into CK format
(in the future, we hope to integrate CK to WA to avoid unnecessary imports).

You can find already imported workloads in the following repository
(automatically pulled with the ck-wa):
```
 $ ck find repo:ck-wa-workloads
 $ ck show repo:ck-wa-workloads
```

You can find already imported WA devices and instruments in
the following repository (also automatically pulled with the ck-wa):
```
 $ ck find repo:ck-wa-extra
 $ ck show repo:ck-wa-extra
```

You can import new workloads, devices and instruments as following:
```
 export CK_PYTHON=python2 ; ck import wa --target_repo_uoa=ck-wa-workloads --extra_target_repo_uoa=ck-wa-extra
```

If you want to import WA artifacts to other CK repositories (for example, private),
just change flags ''--target_repo_uoa'' and ''--extra_target_repo_uoa''. If omitted, 
already existing entries will be updated or new ones will be recorded in ''local'' repository.

Registering APK in local CK repo
================================
Various workloads may require specific versions of APK installed on Android devices.
If these APK are not installed, user has to manually find and install them.

We started automating this process. It is now possible to list all APK and their versions
via
```
 $ ck detect apk
   or
 $ ck detect apk:com.android.calendar
```

If you have found and downloaded a specific APK, you can register it in the CK via

```
 $ ck add apk:{name} --path
```

You can then install or uninstall a given APK via CK:
```
 $ ck install apk:{name}
 $ ck uninstall apk:{name}
```

Whenever you run a workload which require an APK, CK will search for it in the CK repo,
and will try to install it if found. Private CK repositories with a collection of APK
can be easily shared in companies' workgroups to automate workload benchmarking.

Future work
===========
* Current WA can work only with Python 2.x and does not support Windows. Hence, we plan to provide tighter integration with the CK to make WA support Python 3.x and all Linux/MacOS/Windows via CK unified routines.
* We continuing unifying high-level API to crowd-benchmark and crowd-tune shared workloads (see [1](http://bit.ly/ck-date16), [2](http://hal.inria.fr/hal-01054763) and [3](http://arxiv.org/abs/1506.06256) to know more about our vision).

Main reference
==============

If you found our collaborative approach to benchmarking and optimization
useful for your research, feel free to reference the following publication:


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
This concept has been described in the following publications:

* http://tinyurl.com/zyupd5v (DATE'16)
* http://arxiv.org/abs/1506.06256 (CPC'15)
* http://hal.inria.fr/hal-01054763 (Journal of Scientific Programming'14)

You can download all above references in the BibTex format [here](https://raw.githubusercontent.com/ctuning/ck-guide-images/master/collective-knowledge-refs.bib).

Feedback
========
If you have questions or comments, feel free to get in touch with us 
via our [public mailing list](http://groups.google.com/group/collective-knowledge).

Acknowledgments
===============
CK development is coordinated by [dividiti](http://dividiti.com), [cTuning
foundation](http://cTuning.org) and [ARM](http://www.arm.com).
We would like to thank all volunteers for their valuable feedback 
and contributions.
