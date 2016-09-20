#
# Preprocessing ARM WA workloads
#
# Developer: Grigori Fursin, cTuning foundation, 2016
#

import json
import os
import re

def ck_preprocess(i):

    ck=i['ck_kernel']
    rt=i['run_time']
    deps=i['deps']

    env=i['env']

    params=rt.get('params',{})

    b='\n'

    return {'return':0, 'bat':b}

# Do not add anything here!
