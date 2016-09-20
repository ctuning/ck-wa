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

    env=i.get('env',{})

    #######################################
    ck.out('Loading tmp-output1.tmp ...')

    r=ck.load_text_file({'text_file':'tmp-output1.tmp'})
    if r['return']>0: return r
    log=r['string']

    #######################################
    ck.out ('Loading tmp-output2.tmp ...')

    r=ck.load_text_file({'text_file':'tmp-output2.txt'})
    if r['return']>0: return r
    err=r['string']

    #######################################
    ck.out ('Loading wa_output/results.json ...')

    r=ck.load_json_file({'wa_output/results.json', 'r'})
    if r['return']>0:
       return {'return':1, 'error':'wa_output/results.json was not produced - program execution likely failed'}

    results=r['dict']

    # Searching 1 execution time
    ttp=0

    for x in results:
        metrics=x.get('metrics',[])
        for m in metrics:
            if m.get('name','')=='execution_time':
               ttp=m['value']
               break

    if ttp!=0:
       d['execution_time']=ttp
       d['execution_time_kernel_0']=ttp

    d['results']=results
    d['log_stdout']=log
    d['log_stderr']=err

    d['post_processed']='yes'

    # Write CK json
    r=ck.save_json_to_file({'json_file':'tmp-ck-timer.json', 'dict':d})
    if r['return']>0: return r

    return {'return':0}

# Do not add anything here!
