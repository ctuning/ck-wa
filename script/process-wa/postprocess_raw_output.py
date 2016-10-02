#
# Convert raw output of the Caffe 'time' command
# to the CK timing format.
#
# Developers:
#   - Grigori Fursin, cTuning foundation, 2016
#   - Anton Lokhmotov, dividiti, 2016
#

import json
import os
import re

def ck_postprocess(i):
    ck=i['ck_kernel']

    d={}

    #######################################
    ck.out('Loading tmp-output1.tmp ...')

    r=ck.load_text_file({'text_file':'tmp-output1.tmp'})
    if r['return']>0: return r
    log=r['string']

    #######################################
    ck.out ('Loading tmp-output2.tmp ...')

    r=ck.load_text_file({'text_file':'tmp-output2.tmp'})
    if r['return']>0: return r
    err=r['string']

    # Searching 1 execution time
    xttp=''

    ss=' run time: '
    j=log.find(ss)
    if j<0:
        ss='Total time: '
        j=log.find(ss)

    if j>=0:
        j1=log.find(' seconds.',j)
        if j1<0:
            j1=log.find(' s',j)

        if j1>=0:
            xttp=log[j+len(ss):j1].strip()

    if xttp=='':
        return {'return':1, 'error':'couldn\'t find total time in the output'}

    ttp=float(xttp)

    if ttp!=0:
       d['execution_time']=ttp
       d['execution_time_kernel_0']=ttp

    d['log_stdout']=log
    d['log_stderr']=err

    d['post_processed']='yes'

    # Write CK json
    r=ck.save_json_to_file({'json_file':'tmp-ck-timer.json', 'dict':d})
    if r['return']>0: return r

    return {'return':0}

# Do not add anything here!
