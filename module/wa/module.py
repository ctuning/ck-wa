#
# Collective Knowledge (ARM workload automation)
#
# See CK LICENSE for licensing details
# See CK COPYRIGHT for copyright details
#
# Developer: dividiti, http://dividiti.com
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings
line='*************************************************************************************'

##############################################################################
# Initialize module

def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return':0}

##############################################################################
# list workloads (using module "program" with tags "wa")

def wa_list(i):
    """
    Input:  {
              (data_uoa) - can be wild cards
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    o=i.get('out','')
    oo=''
    if o=='con': oo=o

    duoa=i.get('data_uoa','')

    ii={'action':'search',
        'module_uoa':cfg['module_deps']['program'],
        'tags':'wa',
        'add_meta':'yes'}
    rr=ck.access(ii)
    if rr['return']>0: return rr

    if o=='con':
       lst=rr['lst']
       for x in lst:
           duoa=x['data_uoa']
           duid=x['data_uid']

           meta=x['meta']
           desc=meta.get('wa_desc','')

           x=duoa+' ('+duid+')'
           if desc!='':
              x+=' - '+desc

           ck.out(x)

    return rr

##############################################################################
# run workload via CK pipeline

def run(i):
    """
    Input:  {
              (data_uoa)   - workload to run (see "ck list wa" or "ck search program --tags=wa")

              (target)     - device UOA (see "ck list device")

              (record)     - if 'yes', record result in repository in 'experiment' standard
              (record-raw) - if 'yes', record raw results
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import copy

    o=i.get('out','')
    oo=''
    if o=='con': oo=o

    # Check workload(s)
    duoa=i.get('data_uoa','')

    r=ck.access({'action':'search',
                 'module_uoa':cfg['module_deps']['program'],
                 'add_meta':'yes',
                 'data_uoa':duoa,
                 'tags':'wa'})
    if r['return']>0: return r
    lst=r['lst']

    if len(lst)==0:
       return {'return':1, 'error':'workload is not specified or found'}

    record=i.get('record','')
    record_raw=i.get('record-raw','')

    target=i.get('target','')

    # Iterate over workloads
    rrr={}
    for wa in lst:
        duoa=wa['data_uoa']
        duid=wa['data_uid']
        dw=wa['meta']
        dp=wa['path']

        meta={'program_uoa':duoa,
              'program_uid':duid,
              'target':target}

        if o=='con':
            ck.out('Running workload '+duoa+' ...')

        result_path=''
        if record_raw=='yes':
            if o=='con':
                ck.out('  Preparing wa_result entry to store raw results ...')

            ii={'action':'search',
                'module_uoa':cfg['module_deps']['wa-result'],
                'search_dict':{'meta':meta}}
            rx=ck.access(ii)

            lst=rx['lst']

            if len(lst)==0:
                rx=ck.access({'action':'add',
                              'module_uoa':cfg['module_deps']['wa-result'],
                              'dict':{'meta':meta}})
                if rx['return']>0: return rx
                result_uid=rx['data_uid']
                result_path=rx['path']
            else:
                result_uid=lst[0]['data_uid']
                result_path=lst[0]['path']

        # Prepare CK pipeline for a given workload
        ii={'action':'pipeline',

            'module_uoa':cfg['module_deps']['program'],
            'data_uoa':duid,

            'target':target,

            'prepare':'yes',

            'no_state_check':'yes',
            'no_compiler_description':'yes',
            'skip_info_collection':'yes',
            'skip_calibration':'yes',
            'cpu_freq':'',
            'gpu_freq':'',
            'env_speed':'yes',
            'energy':'no',
            'skip_print_timers':'yes',
            'generate_rnd_tmp_dir':'yes',

            'env':{'CK_WA_RAW_RESULT_PATH':result_path},

            'out':oo}
        r=ck.access(ii)
        if r['return']>0: return r

        fail=r.get('fail','')
        if fail=='yes':
            return {'return':10, 'error':'pipeline failed ('+r.get('fail_reason','')+')'}

        ready=r.get('ready','')
        if ready!='yes':
            return {'return':11, 'error':'couldn\'t prepare autotuning pipeline'}

        state=r['state']
        tmp_dir=state['tmp_dir']

        # Clean pipeline
        if 'ready' in r: del(r['ready'])
        if 'fail' in r: del(r['fail'])
        if 'return' in r: del(r['return'])

        pipeline=copy.deepcopy(r)

        # Run CK pipeline *****************************************************
        ii={'action':'autotune',
            'module_uoa':cfg['module_deps']['pipeline'],
            'data_uoa':cfg['module_deps']['program'],

            'iterations':1,
            'repetitions':1,

            'tmp_dir':tmp_dir,

            'pipeline':pipeline,

            'record':record,

            'meta':meta,

            'tags':'wa',

            "features_keys_to_process":["##choices#*"],

            "record_params": {
              "search_point_by_features":"yes"
            },

            "record_dict":{"subview_uoa":"3d9a4f4b03b1b257"},

            'out':oo}

        rrr=ck.access(ii)
        if rrr['return']>0: return rrr

    return rrr

##############################################################################
# ARM workload automation dashboard

def dashboard(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    i['action']='browser'
    i['cid']=''
    i['module_uoa']=''
    i['template']='arm-wa'

    return ck.access(i)

##############################################################################
# import workloads from original WA

def wa_import(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import copy

    o=i.get('out','')
    oo=''
    if o=='con': oo=o

    # Get platform params
    hos=i.get('host_os','')
    tos=i.get('target_os', '')
    tdid=i.get('device_id', '')

    ck.out('Detecting host and target platform info ...')
    ck.out('')

    ii={'action':'detect',
        'module_uoa':cfg['module_deps']['platform'],
        'out':oo,
        'host_os':hos,
        'target_os':tos,
        'target_device_id':tdid}
    rpp=ck.access(ii)
    if rpp['return']>0: return rpp

    hos=rpp['host_os_uoa']
    hosd=rpp['host_os_dict']

    tos=rpp['os_uoa']
    tosd=rpp['os_dict']
    tbits=tosd.get('bits','')

    remote=tosd.get('remote','')

    tdid=rpp['device_id']

    if hos=='':
       return {'return':1, 'error':'"host_os" is not defined or detected'}

    if tos=='':
       return {'return':1, 'error':'"target_os" is not defined or detected'}

    # Various host and target vars
    bbp=hosd.get('batch_bash_prefix','')
    rem=hosd.get('rem','')
    eset=hosd.get('env_set','')
    etset=tosd.get('env_set','')
    svarb=hosd.get('env_var_start','')
    svarb1=hosd.get('env_var_extra1','')
    svare=hosd.get('env_var_stop','')
    svare1=hosd.get('env_var_extra2','')
    scall=hosd.get('env_call','')
    sdirs=hosd.get('dir_sep','')
    sdirsx=tosd.get('remote_dir_sep','')
    if sdirsx=='': sdirsx=sdirs
    stdirs=tosd.get('dir_sep','')
    sext=hosd.get('script_ext','')
    sexe=hosd.get('set_executable','')
    se=tosd.get('file_extensions',{}).get('exe','')
    sbp=hosd.get('bin_prefix','')
    stbp=tosd.get('bin_prefix','')
    sqie=hosd.get('quit_if_error','')
    evs=hosd.get('env_var_separator','')
    envsep=hosd.get('env_separator','')
    envtsep=tosd.get('env_separator','')
    eifs=hosd.get('env_quotes_if_space','')
    eifsc=hosd.get('env_quotes_if_space_in_call','')
    eifsx=tosd.get('remote_env_quotes_if_space','')
    if eifsx=='': eifsx=eifsc
    wb=tosd.get('windows_base','')
    stro=tosd.get('redirect_stdout','')
    stre=tosd.get('redirect_stderr','')
    ubtr=hosd.get('use_bash_to_run','')
    no=tosd.get('no_output','')
    bex=hosd.get('batch_exit','')
    md5sum=hosd.get('md5sum','')

    # Set environment for WA
    ck.out('')
    ck.out('Setting CK environment for ARM workload automation ...')

    ii={'action':'set',
        'module_uoa':cfg['module_deps']['env'],
        'host_os':hos,
        'target_os':tos,
        'target_device_id':tdid,
        'tags':'wa'}
    r=ck.access(ii)
    if r['return']>0: return r

    bat=r['bat']

    # Prepare tmp bat file and tmp output file
    rx=ck.gen_tmp_file({'prefix':'tmp-', 'suffix':sext})
    if rx['return']>0: return rx
    fbat=rx['file_name']

    rx=ck.gen_tmp_file({'prefix':'tmp-', 'suffix':'.tmp'})
    if rx['return']>0: return rx
    ftmp=rx['file_name']

    # Write bat file
    bat+='\n'
    bat+='wa list workloads > '+ftmp

    rx=ck.save_text_file({'text_file':fbat, 'string':bat})
    if rx['return']>0: return rx

    y=''
    if sexe!='':
       y+=sexe+' '+fbat+envsep
    y+=' '+scall+' '+fbat

    if ubtr!='': y=ubtr.replace('$#cmd#$',y)

    ck.out('')
    ck.out('Executing '+bat+' ...')

    os.system(y)

    # Read and delete tmp file with WA description
    rz=ck.load_text_file({'text_file':ftmp, 'split_to_list':'yes', 'delete_after_read':'yes'})
    if rz['return']>0: return rz
    lst=rz['lst']

    # Delete fbat (temp)
    if os.path.isfile(fbat):
       os.remove(fbat)

    # Parse descriptions
    wa={}
    wk=''
    wv=''
    for l in lst:
        if l!='':
           j=l.find(': ')
           if j>0:
              if wk!='':
                 wa[wk]=wv
                 wk=''
                 wv=''
              wk=l[:j].strip()
              wv=l[j+2:].strip()
           else:
              wv+=' '+l.strip()
    if wk!='':
       wa[wk]=wv

    # Load WA template
    wt=os.path.join(work['path'],'wa-template.json')
    r=ck.load_json_file({'json_file':wt})
    if r['return']>0: return r

    wtd=r['dict']

    # Add entries
    for w in wa:
        wd=wa[w]

        duid=''
        d={}

        # First check, if such program exists
        s='Adding new'
        ii={'action':'load',
            'module_uoa':cfg['module_deps']['program'],
            'data_uoa':w}
        r=ck.access(ii)
        if r['return']==0:
           duid=r['data_uid']
           d=r['dict']
           s='Updating'
        else:
           rx=ck.gen_uid({})
           if rx['return']>0: return rx
           duid=rx['data_uid']

           d=copy.deepcopy(wtd)

        # Adding/updating entry
        ck.out('  '+s+' entry "'+w+'" ...')

        d["backup_data_uid"]=duid
        d["data_name"]=w

        # Cleaning up wd
        if wd.endswith('.'): wd=wd[:-1]
        if wd.startswith('Runs the '): wd=wd[9:]
        d["wa_desc"]=wd

        x=d["print_files_after_run"]
        xx=[]
        for y in x:
            xx.append(y.replace('$#wa_name#$',w))
        d["print_files_after_run"]=xx

        x=d["run_cmds"]["default"]["run_time"]["run_cmd_main"]
        d["run_cmds"]["default"]["run_time"]["run_cmd_main"]=x.replace('$#wa_name#$',w)

        x=d["tags"]
        xx=[]
        for y in x:
            xx.append(y.replace('$#wa_name#$',w))
        d["tags"]=xx

        ii={'action':'update',
            'module_uoa':cfg['module_deps']['program'],
            'data_uoa':w,
            'data_uid':duid,
            'repo_uoa':'ck-wa',
            'dict':d}
        r=ck.access(ii)
        if r['return']>0: return r

    return {'return':0}


##############################################################################
# run workload(s)

def runx(i):
    """
    Input:  {
              (device)     - device UOA (see "ck list device" or add new "ck add device")

              data_uoa     - workload name
                and/or
              workloads    - workload names separated by comma (to be run in parallel)






              agendas      - list of agenda files (.yaml/.json/entries)
                 or
              workloads    - list of multiple workloads executed in PARALLEL in one agenda template

              (agenda)     - agenda template (.yaml/.json/entries) or ck-agenda:default

              (params)     - params for agenda

              (iterations) - number of statistical repetitions (3 by default)

              (record)     - if 'yes', record to CK

              (verbose)    - if 'yes', use verbose WA mode
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import copy

    o=i.get('out','')

    pc=os.getcwd()

    # Device
    device=i.get('device','')
    rx=ck.access({'action':'search',
                  'module_uoa':cfg['module_deps']['device'],
                  'tags':'wa',
                  'data_uoa':device})
    if rx['return']>0: return rx
    lst=rx['lst']

    if len(lst)==0:
       return {'return':1, 'error':'no target device found (you can add one via "ck add device")'}
    elif len(lst)==1:
       device=lst[0].get('data_uid','')
    elif len(lst)>1:
       ck.out('More than one device found')
       ck.out('')
       r=ck.select_uoa({'choices':lst})
       if r['return']>0: return r
       device=r['choice']
       ck.out('')

    if device=='':
       return {'return':1, 'error':'no target device selected'}

    # Parallel workloads
    workloads=[]

    ww=i.get('workloads','').strip()
    if len(ww)>0:
       for w in ww.split(','):
           workloads.append(w)

    if i.get('data_uoa','')!='':
       workloads.append(i['data_uoa'])

    agenda=i.get('agenda',{})

    # Help
    if (len(workloads)==0 and len(agenda)==0):
       ck.out('Usage:')
       ck.out('  ck run wa:{name} --device={device name}')
       ck.out('                or')
       ck.out('  ck run wa --workloads={name1,name2,...} --device={device name}')
       ck.out('                or')
       ck.out('  ck run wa --agenda={} --device={device name} --workloads={w1,w2,w3} --agenda={template.yaml}')
       ck.out('')
       ck.out('Notes:')
       ck.out('  * You can list available workloads via "ck list wa"')
       ck.out('  * You can import all workloads from WA via "ck import wa"')
       ck.out('  * You can add more target devices via "ck add device"')

       return {'return':0}

    # Parameters
    if len(agenda)==0:
       agenda=cfg['default_agenda']

    params=i.get('params',{})

    iters=i.get('iterations','')
    if iters=='': iters=3
    iters=int(iters)

    record=i.get('record','')

    # Loading device configuration
    ck.out('Loading device configuration: '+device)
    r=ck.access({'action':'load',
                 'module_uoa':cfg['module_deps']['device'],
                 'data_uoa':device})
    if r['return']>0: return r
    dev_uid=r['data_uid']
    dev_uoa=r['data_uoa']

    dd=r['dict']

    ddc=dd.get('extra_cfg',{}).get('wa_config',{}) # default device meta
    ddf=dd.get('features',{})

    pd=r['path']

    pcfg=os.path.join(pd, cfg['device_cfg_file'])

    # Prepare agenda
    ck.out('')
    for w in workloads:
        ck.out('Adding workload: '+w)
        agenda['workloads'].append({'name':w, 'params': params})

    # Get first name of a workload in agenda (to record in CK)
    wname=''
    for q in agenda.get('workloads',[]):
        name=q.get('name','')
        if name!='':
           wname=name
           break

    # Run agenda and record if needed
    if 'global' not in agenda:
        agenda['global']={}

    ag=agenda['global']

    if ag.get('iterations','')=='':
        ag['iterations']=iters

    ck.out('')
    ck.out('Iterations: '+str(iters))

    if 'config' not in agenda:
        agenda['config']={}

    ac=agenda['config']

    ac.update(ddc) # Update config from device description

    if 'result_processors' not in ac:
        ac['result_processors']=[]

    acrp=ac['result_processors']
    if 'json'not in acrp:
        acrp.append('json')

    # Create CK entry (where to record results)
    p=pc
    if record=='yes':
        dd={'meta':{
                    'workload_name':wname,
                    'workloads':workloads,
                    'params':params,
                    'device_features':ddf,
                    'device_config':agenda,
                    'local_device_uid':dev_uid,
                    'local_device_uoa':dev_uoa
                   }}

        r=ck.access({'action':'add',
                     'module_uoa':cfg['module_deps']['wa-result'],
                     'dict':dd
                   })
        if r['return']>0: return r
        p=r['path']
        euid=r['data_uid']

        ck.out('Experiment UID: '+euid)

    px=p
    p=os.path.join(p,'results') # otherwise WA overwrites .cm
    if not os.path.isdir(p):
        os.makedirs(p)

    # Prepare temp yaml file
    if record=='yes':
        ta=os.path.join(px, cfg['agenda_file'])
    else:
        r=ck.gen_tmp_file({'prefix':'tmp-', 'suffix':'.yaml'})
        if r['return']>0: return r
        ta=r['file_name']

    # Save agenda as YAML
    r=ck.save_yaml_to_file({'yaml_file':ta, 'dict':agenda})
    if r['return']>0: return r

    # Prepare CMD
    cmd='wa run '+ta+' -c '+pcfg+' -fd '+p

    if i.get('verbose','')=='yes':
       cmd+=' --verbose'

    ck.out('CMD:            '+cmd)

    # Run WA
    ck.out('')
    r=os.system(cmd)

    return {'return':0}

##############################################################################
# replay a given experiment

def replay(i):
    """
    Input:  {
              data_uoa - experiment UID (see "ck list wa-result")
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os

    duoa=i.get('data_uoa','')

    # Help
    if (duoa==''):
       ck.out('Usage:')
       ck.out('  ck replay wa:{experiment UID}')
       ck.out('')
       ck.out('Notes:')
       ck.out('  * You can list available experiments via "ck list wa-result"')
       ck.out('  * You can view experiments via web-based WA dashboard ("ck dashboard wa"')

       return {'return':0}

    # Load meta
    r=ck.access({'action':'load',
                 'module_uoa':cfg['module_deps']['wa-result'],
                 'data_uoa':duoa})
    if r['return']>0: return r
    p=r['path']
    d=r['dict']

    dm=d.get('meta',{})

    lduid=dm.get('local_device_uid','')
    lduoa=dm.get('local_device_uoa','')
    lwname=dm.get('workload_name','')

    pagenda=os.path.join(p,cfg['agenda_file'])

    # Loading device configuration
    ck.out('Loading device configuration: '+lduoa)
    r=ck.access({'action':'load',
                 'module_uoa':cfg['module_deps']['wa-device'],
                 'data_uoa':lduid})
    if r['return']>0: return r
    dd=r['dict']
    pd=r['path']

    dev_uid=r['data_uid']
    dev_uoa=r['data_uoa']

    pcfg=os.path.join(pd, cfg['device_cfg_file'])

    # Prepare CMD
    cmd='wa run '+pagenda+' -c '+pcfg

    ck.out('CMD:            '+cmd)

    # Run WA
    ck.out('')
    r=os.system(cmd)

    return {'return':0}

##############################################################################
# configure device for WA

def configure(i):
    """
    Input:  {
              (wa_device)         - device name (obtained via "wa list devices")
              (wa_device_default) - default device
              (device_id)         - device ID (if via adb)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os

    o=i.get('out','')

    tdid=i.get('device_id','')

    ddevice=i.get('wa_device_default','')
    if ddevice=='': ddevice='generic_android'

    # Load default config (in CK JSON)
    pm=work['path']
    p=os.path.join(pm, cfg['default_device_cfg_file'])

    r=ck.load_json_file({'json_file':p})
    if r['return']>0: return r
    dcfg=r['dict']

    # Select WA device
    device=i.get('wa_device','')
    if device=='' and o=='con':
        ck.out('')

        ck.out('Available WA devices:')
        ck.out('')
        os.system('wa list devices')

        ck.out('')
        r=ck.inp({'text':'Enter WA device name from above list or press Enter to select "'+ddevice+'": '})
        device=r['string'].strip()

    if device=='': device=ddevice
    dcfg['device']=device

    if tdid!='':
        dcfg['device_config']['adb_name']=tdid

    # Generating config.py
    s='# WA config file automatically generated by CK\n'
    for k in sorted(dcfg):
        s+=k+' = '

        v=dcfg[k]

        if type(v)==list or type(v)==dict:
           r=ck.dump_json({'dict':v, 'sort_keys':'yes'})
           if r['return']>0: return r
#           s+=json.dumps(v, indent=2, sort_keys=True)+'\n'
           s+=r['string']+'\n'
        elif type(v)==int or type(v)==float:
           s+=str(v)+'\n'
        else:
           s+='"'+str(v)+'"\n'

    # Trick (not clean) to replace true with True for python
    s=s.replace(' true', ' True')

    return {'return':0, 'files':{cfg['device_cfg_file']:s}, 'cfg':dcfg}
