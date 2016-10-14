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

    raw_path=env.get('CK_WA_RAW_RESULT_PATH','')

    if raw_path=='':
       p=os.getcwd()
    else:
       p=raw_path

    pp=os.path.join(p,'wa-output') # otherwise WA overwrites .cm

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

    xerr=''
    traceback=False
    for l in err.split('\n'):
        l1=str(l.strip())

        if traceback or l1.startswith('Traceback '):
            xerr+=l1+'\n'
            traceback=True

        elif len(l1)>9:
            if l1.startswith('ERROR'):
                xerr+=l1[5:].strip()+'\n'
            elif l1[5:].startswith('ERROR'):
                xerr+=l1[10:].strip()+'\n'
            elif l1.startswith('CRITICAL'):
                xerr+=l1[8:].strip()+'\n'
            elif l1[5:].startswith('CRITICAL'):
                xerr+=l1[13:].strip()+'\n'

    #######################################
    ck.out ('Loading status.txt ...')

    r=ck.load_text_file({'text_file':os.path.join(pp,'status.txt')})
    if r['return']==0:
        ss=r['string']

        j=ss.find(' FAILED ')
        if j>=0:
            j1=ss.find('\n',j)
            if j1<0: j1=ss.length()

            xerr+='FAILURE: '+ss[j+8:j1]

    if xerr!='':
        return {'return':1, 'error':xerr}

    #######################################
    ck.out ('Loading results.json ...')

    pr=os.path.join(pp,'results.json')
    r=ck.load_json_file({'json_file':pr})
    if r['return']>0:
       return {'return':1, 'error':pr+' was not produced - program execution likely failed'}

    results=r['dict']

    # Searching 1 execution time
    ttp=0

    for x in results:
        metrics=x.get('metrics',[])
        for m in metrics:
            name=m.get('name','')
            if name!='':
                value=m.get('value',None)
                if m.get('name','')=='execution_time':
                    ttp=value
                    break
                d[name]=value

    if ttp!=0:
       d['execution_time']=ttp
       d['execution_time_kernel_0']=ttp

#    d['results']=results
#    d['log_stdout']=log
#    d['log_stderr']=err

#    d['post_processed']='yes'

    # Write CK json
    r=ck.save_json_to_file({'json_file':'tmp-ck-timer.json', 'dict':d})
    if r['return']>0: return r

    return {'return':0}

# Do not add anything here!
