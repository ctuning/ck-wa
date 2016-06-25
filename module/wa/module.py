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

def list(i):
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

def runx(i):
    """
    Input:  {
              (data_uoa) - workload to run (see "ck list wa")

              (device)   - device UOA (see "ck list device")

              (record)   - if 'yes', record result in repository
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

    # Check device (search and select if one)
    device=i.get('device','')

    r=ck.access({'action':'search',
                 'module_uoa':cfg['module_deps']['device'],
                 'data_uoa':device})
    if r['return']>0: return r
    dl=r['lst']
    if len(dl)!=1:
       return {'return':1, 'error':'CK device name is not defined (ck run wa:{workload_name} --device={device_name})'}

    device=dl[0]['data_uid']
    device_uoa=dl[0]['data_uoa']

    # Load info about device (including configuration)
    r=ck.access({'action':'load',
                 'module_uoa':cfg['module_deps']['device'],
                 'data_uoa':device})
    if r['return']>0: return r
    dd=r['dict']
    pd=r['path']

    dcfg=os.path.join(pd, cfg['device_cfg_file'])

    # Check host/target OS/CPU
    hos=i.get('host_os','')
    tos=i.get('target_os','')
    tdid=i.get('device_id','')

    if tos=='': tos=dd.get('target_os','')
    if tdid=='': tdid=dd.get('device_id','')

    # Get some info about platforms
    ii={'action':'detect',
        'module_uoa':cfg['module_deps']['platform.os'],
        'host_os':hos,
        'target_os':tos,
        'device_id':tdid,
        'out':oo}
    r=ck.access(ii)
    if r['return']>0: return r

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
       return {'return':1, 'error':'workload is not found (ck run wa:{workload_name})'}

    record=i.get('record','')

    # Iterate over workloads
    rrr={}
    for wa in lst:
        duoa=wa['data_uoa']
        duid=wa['data_uid']
        dw=wa['meta']
        dp=wa['path']

        meta={'program_uoa':duoa,
              'program_uid':duid,
              'device_uoa':device_uoa,
              'device_uid':device}

        if o=='con':
           ck.out('Running workload '+duoa+' on device '+device_uoa+' ...')

        # Prepare CK pipeline for a given workload

        ii={'action':'pipeline',
            'module_uoa':cfg['module_deps']['program'],
            'data_uoa':duid,

            'prepare':'yes',

            'env':{'EXTRA_CMD':'-c '+dcfg},
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

    hosz=hosd.get('base_uoa','')
    if hosz=='': hosz=hos
    tosz=tosd.get('base_uoa','')
    if tosz=='': tosz=tos

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

    # Add entries
    for w in wa:
        wd=wa[w]

        # First check, if such program exists
        ii={'action':'load',
            'module_uoa':cfg['module_deps']['program'],
            'data_uoa':w}
        r=ck.access(ii)
        if r['return']>0:
           if r['return']!=16: return r # some other error (16 - entry not found)

           # Preparing meta in CK program format

           # Adding new entry
           ck.out('  Adding new entry '+w+' ...')

           rx=ck.gen_uid({})
           if rx['return']>0: return rx
           duid=rx['data_uid']

           d=copy.deepcopy(cfg['wa_template'])

           d["backup_data_uid"]=duid
           d["data_name"]=w
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

           ii={'action':'add',
               'module_uoa':cfg['module_deps']['program'],
               'data_uoa':w,
               'data_uid':duid,
               'repo_uoa':'ck-wa',
               'dict':d}
           r=ck.access(ii)
           if r['return']>0: return r

        else:
           ck.out('    Entry '+w+' already exists!')

    return {'return':0}


##############################################################################
# run workload(s)

def run(i):
    """
    Input:  {
              agendas      - list of agenda files (.yaml/.json/entries)
                 or
              workloads    - list of multiple workloads under 1 agenda template
              (agenda)     - agenda template (.yaml/.json/entries) or ck-agenda:default

              (params)     - params for agenda

              (iterations) - number of statistical repetitions (3 by default)

              (record)     - if 'yes', record to CK
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import copy
    import yaml

    o=i.get('out','')

    pc=os.getcwd()

    # Agendas
    a=i.get('agendas','')
    agendas=a.split(',')

    # Workloads
    w=i.get('workloads','')
    workloads=w.split(',')
    agenda=i.get('agenda','')

    # Parameters
    params=i.get('params',{})

    iters=i.get('iterations','')
    if iters=='': iters=3
    iters=int(iters)

    record=i.get('record','')

    # Check
    if a=='' and w=='':
       ck.out('Usage:')
       ck.out('  ck run wa --agendas=a1.yaml,a2.yaml,a3.json, ...')
       ck.out('                or')
       ck.out('  ck run wa --workloads=w1,w2,w3 --agenda=template.yaml')

       return {'return':0}

    # Prepare agendas as dict
    aa=[]

    # Iterate
    ck.out(line)
    if a!='':
       for a in agendas:
           ck.out('Reading agenda: '+a)

           r=ck.access({'action':'read',
                        'module_uoa':cfg['module_deps']['wa-agenda'],
                        'from':a})
           if r['return']>0: return r
           d=r['dict']

           aa.append(d)
    else:
       if agenda=='':
          agenda='default'

       ck.out('Reading agenda: '+agenda)

       r=ck.access({'action':'read',
                    'module_uoa':cfg['module_deps']['wa-agenda'],
                    'from':agenda})
       if r['return']>0: return r
       d=r['dict']

       # Iterating over workloads
       for w in workloads:
           ck.out('Adding workload: '+w)

           dd=copy.deepcopy(d)

           dd['workloads']=[{'name':w, 'params': params}]

           aa.append(dd)

    # Run agendas and record if needed
    for a in aa:
        ww=a.get('workloads',[])

        for w in ww:
            name=w.get('name','')
            params=w.get('params',{})

            ck.out(line)
            ck.out('Workload:       '+name)

            # Create CK entry (where to record results)
            dd={'meta':{
                        'workload_name':name
                       }}

            r=ck.access({'action':'add',
                         'module_uoa':cfg['module_deps']['wa-result'],
                         'dict':dd
                        })
            if r['return']>0: return r
            p=r['path']
            euid=r['data_uid']

            p=os.path.join(p,'results') # otherwise WA overwrites .cm
            os.makedirs(p)

            ck.out('Experiment UID: '+euid)

            # Prepare temporal agenda
            atmp=copy.deepcopy(a)
            atmp['workloads']=[w]

            if 'global' not in atmp:
               atmp['global']={}

            ag=atmp['global']

            if ag.get('iterations','')=='':
               ag['iterations']=iters

            if 'config' not in atmp:
               atmp['config']={}

            ac=atmp['config']

            if 'result_processors' not in ac:
               ac['result_processors']=[]

            acrp=ac['result_processors']
            if 'json'not in acrp:
               acrp.append('json')

            # Prepare temp yaml file
            r=ck.gen_tmp_file({'prefix':'tmp-', 'suffix':'.yaml'})
            if r['return']>0: return r
            ta=r['file_name']

            # Save agenda as YAML
            r=ck.save_yaml_to_file({'yaml_file':ta, 'dict':atmp})
            if r['return']>0: return r

            # Prepare CMD
            cmd='wa run '+ta+' -fd '+p

            ck.out('CMD:            '+cmd)

            # Run WA
            ck.out('')
            r=os.system(cmd)

    return {'return':0}
