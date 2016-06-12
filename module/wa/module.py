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
# run workload

def run(i):
    """
    Input:  {
              (device)   - device UOA (see "ck list device")
              (data_uoa) - workload to run (see "ck list wa")

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
       return {'return':1, 'error':'workload name is not defined (ck run wa:{workload_name})'}

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

            'meta':meta,

            'tmp_dir':tmp_dir,

            'pipeline':pipeline,

            'record':'yes',

            "features_keys_to_process":["##choices#*"],

            "record_params": {
              "search_point_by_features":"yes"
            },

            'out':oo}

        rrr=ck.access(ii)
        if rrr['return']>0: return rrr

    return rrr

##############################################################################
# WA dashboard

def show(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    h='TBD'
    st=''

    return {'return':0, 'html':h, 'style':st}

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
