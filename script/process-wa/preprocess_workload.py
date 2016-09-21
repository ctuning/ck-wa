#
# Preprocessing ARM WA workloads
#
# Developer: Grigori Fursin, cTuning foundation, 2016
#

import json
import os
import re

##########################################################
default_agenda={
    "config": {
      "instrumentation": [
        "~execution_time"
      ],
      "result_processors": [
        "json"
      ]
    },
    "workloads": []
}

##########################################################
def ck_preprocess(i):

    o=i.get('out','')

    ck=i['ck_kernel']
    rt=i['run_time']
    deps=i['deps']

    hosd=i['host_os_dict']

    set_env=hosd.get('env_set','')
    if set_env!='' and not set_env.endswith(' '):
        set_env+=' '

    env_quotes=hosd.get('env_quotes','')

    env=i['env']

    meta=i.get('meta',{})

    all_params=i.get('params',{})

    device_cfg=i.get('device_cfg',{})
    wa_config=device_cfg.get('wa_config',{})

    # How to pass agenda from outside or params + what to measure (choices???)+ extra workloads + name
    # TBD: WE ALSO NEED TO PASS PREPARE AGENDA TO OUTPUT (state?)
    agenda=default_agenda

    r=ck.merge_dicts({'dict1':agenda, 'dict2':all_params.get('agenda',{})})
    if r['return']>0: return 

    params=all_params.get('workload_params',{})

    wname=meta['data_name']
    agenda['workloads'].append({'name':wname, 'params': params})

    # Prepare agenda
    if 'global' not in agenda:
        agenda['global']={}

    ag=agenda['global']

    ag['iterations']=1 # We rely on our CK pipeline statistical repetitions to apply CK stat analysis

    if 'config' not in agenda:
        agenda['config']={}

    ac=agenda['config']

    ac.update(wa_config) # Update config from device description

    if 'result_processors' not in ac:
        ac['result_processors']=[]

    acrp=ac['result_processors']
    if 'json'not in acrp:
        acrp.append('json')

    cmd=''

    # Prepare temp yaml file
    r=ck.gen_tmp_file({'prefix':'tmp-', 'suffix':'.yaml', 'remove_dir':'yes'})
    if r['return']>0: return r
    ta=r['file_name']

    # Save agenda as YAML
    r=ck.save_yaml_to_file({'yaml_file':ta, 'dict':agenda})
    if r['return']>0: return r

    # Finish CMD
    cmd+=' '+ta

    cmd+=' --iterations=1'

    if all_params.get('verbose','')=='yes':
       cmd+=' --verbose'

    # Pass to CMD this file
    b=set_env+'CK_WA_CMD='+env_quotes+ta.strip()+env_quotes+'\n'

    # Print agenda
    if o=='con':
       r=ck.dump_json({'dict':agenda, 'sort_keys':'yes'})
       if r['return']>0: return r
       s=r['string']

       ck.out('---------------------------------------')
       ck.out('Prepared agenda in JSON:')
       ck.out('')
       ck.out(s)
       ck.out('---------------------------------------')

    return {'return':0, 'bat':b}

# Do not add anything here!
