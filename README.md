Workload Automation for ARM
===========================

Status
======
Unstable - heavy development phase

Prerequisites
=============
* Collective Knowledge framework ([@GitHub](http://github.com/ctuning/ck))
* python2 (for ARM WA)
* pip (installed via apt-get install python-pip)

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
 $ ck install package:arm-wa-workload
```

Usage
=====

Check available workloads in CK format:
```
 $ ck list wa
```

Run dhrystone workload via CK:
```
 $ ck run wa:dhrystone
```
