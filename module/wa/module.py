#
# Collective Knowledge (ARM workload automation)
#
# See CK-WA LICENSE for licensing details
# See CK-WA COPYRIGHT for copyright details
#
# Developer: dividiti, grigori@dividiti.com, http://dividiti.com
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

def list_wa(i):
    """
    Input:  {
              (data_uoa) - workload names (can have wild cards)
              (repo_uoa) - repository
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
    if duoa!='':
        duoa='wa-'+duoa

    ruoa=i.get('repo_uoa','')

    ii={'action':'search',
        'module_uoa':cfg['module_deps']['program'],
        'tags':'wa',
        'data_uoa':duoa,
        'repo_uoa':ruoa,
        'add_meta':'yes'}
    rr=ck.access(ii)
    if rr['return']>0: return rr

    if o=='con':
       lst=rr['lst']
       for x in lst:
           duoa=x['data_uoa']
           if duoa.startswith('wa-'):
               duoa=duoa[3:]

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
              (data_uoa)        - workload to run (see "ck list wa").

              (target)          - machine UOA (see "ck list machine")

              (record)          - if 'yes', record result in repository in 'experiment' standard
              (skip-record-raw) - if 'yes', skip record raw results
              (overwrite)       - if 'yes', do not record date and time in result directory, but overwrite wa-results

              (repetitions)     - statistical repetitions (default=1), for now statistical analysis is not used (TBD)

              (config)          - customize config
              (params)          - workload params
              (scenario)        - use pre-defined scenario (see ck list wa-scenario)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import copy
    import time

    o=i.get('out','')
    oo=''
    if o=='con': oo=o

    # Check scenario
    config=i.get('config',{})
    params=i.get('params',{})

    scenario=i.get('scenario','')
    if scenario!='':
        r=ck.access({'action':'load',
                     'module_uoa':cfg['module_deps']['wa-scenario'],
                     'data_uoa':scenario})
        if r['return']>0: return r
        d=r['dict']

        r=ck.merge_dicts({'dict1':config, 'dict2':d.get('config',{})})
        if r['return']>0: return r

        r=ck.merge_dicts({'dict1':params, 'dict2':d.get('params',{})})
        if r['return']>0: return r

    # Check workload(s)
    duoa=i.get('data_uoa','')
    if duoa!='':
        duoa='wa-'+duoa

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
    skip_record_raw=i.get('skip-record-raw','')
    overwrite=i.get('overwrite','')

    repetitions=i.get('repetitions','')
    if repetitions=='': repetitions=1
    repetitions=int(repetitions)

    # Get target features
    target=i.get('target','')

    if target=='':
        # Check and possibly select target machines
        r=ck.search({'module_uoa':cfg['module_deps']['machine'], 'data_uoa':target, 'add_meta':'yes'})
        if r['return']>0: return r

        dlst=r['lst']

        # Prune search by only required devices
        rdat=['wa_linux', 'wa_android']

        xlst=[]

        if len(rdat)==0:
            xlst=dlst
        else:
            for q in dlst:
                if q.get('meta',{}).get('access_type','') in rdat:
                    xlst.append(q)

        if len(xlst)==0:
            return {'return':1, 'error':'no suitable target devices found (use "ck add machine" to register new target device)'}
        elif len(xlst)==1:
            target=xlst[0]['data_uoa']
        else:
            # SELECTOR *************************************
            ck.out('')
            ck.out('Please select target device to run your workloads on:')
            ck.out('')
            r=ck.select_uoa({'choices':xlst})
            if r['return']>0: return r
            target=r['choice']

    if target=='':
        return {'return':1, 'error':'--target machine is not specified (see "ck list machine")'}

    ck.out('')
    ck.out('Selected target machine: '+target)
    ck.out('')

    # Load target machine description
    r=ck.access({'action':'load',
                 'module_uoa':cfg['module_deps']['machine'],
                 'data_uoa':target})
    if r['return']>0: return r
    target_uoa=r['data_uoa']
    target_uid=r['data_uid']
    features=r['dict']['features']

    device_id=r['dict'].get('device_id','')

    fplat=features.get('platform',{})
    fos=features.get('os',{})
    fcpu=features.get('cpu',{})
    fgpu=features.get('gpu',{})

    plat_name=fplat.get('name','')
    os_name=fos.get('name','')
    cpu_name=fcpu.get('name','')
    if cpu_name=='': cpu_name='unknown-'+fcpu.get('cpu_abi','')
    gpu_name=fgpu.get('name','')
    sn=fos.get('serial_number','')

    # Iterate over workloads
    rrr={}
    for wa in lst:
        duoa=wa['data_uoa']
        duid=wa['data_uid']
        dw=wa['meta']
        dp=wa['path']

        ww=dw['wa_alias']

        meta={'program_uoa':duoa,
              'program_uid':duid,
              'workload_name':ww,
              'cpu_name':cpu_name,
              'os_name':os_name,
              'plat_name':plat_name,
              'gpu_name':gpu_name,
              'scenario':scenario,
              'serial_number':sn}

        mmeta=copy.deepcopy(meta)
        mmeta['local_target_uoa']=target_uoa
        mmeta['local_target_uid']=target_uid

        if o=='con':
            ck.out(line)
            ck.out('Running workload '+ww+' (CK UOA='+duoa+') ...')

            time.sleep(1)

        result_path=''
        if skip_record_raw!='yes':
            if o=='con':
                ck.out('  Preparing wa_result entry to store raw results ...')

            ddd={'meta':mmeta}

            ii={'action':'search',
                'module_uoa':cfg['module_deps']['wa-result'],
                'search_dict':{'meta':meta}}
            rx=ck.access(ii)

            lst=rx['lst']

            if len(lst)==0:
                rx=ck.access({'action':'add',
                              'module_uoa':cfg['module_deps']['wa-result'],
                              'dict':ddd,
                              'sort_keys':'yes'})
                if rx['return']>0: return rx
                result_uid=rx['data_uid']
                result_path=rx['path']
            else:
                result_uid=lst[0]['data_uid']
                result_path=lst[0]['path']

                # Load entry
                rx=ck.access({'action':'load',
                              'module_uoa':cfg['module_deps']['wa-result'],
                              'data_uoa':result_uid})
                if rx['return']>0: return rx
                ddd=rx['dict']

            # Possible directory extension (date-time)
            if overwrite!='yes':
                rx=ck.get_current_date_time({})
                if rx['return']>0: return rx

                aa=rx['array']

                ady=str(aa['date_year'])
                adm=str(aa['date_month'])
                adm=('0'*(2-len(adm)))+adm
                add=str(aa['date_day'])
                add=('0'*(2-len(add)))+add
                ath=str(aa['time_hour'])
                ath=('0'*(2-len(ath)))+ath
                atm=str(aa['time_minute'])
                atm=('0'*(2-len(atm)))+atm
                ats=str(aa['time_second'])
                ats=('0'*(2-len(ats)))+ats

                pe=ady+adm+add+'-'+ath+atm+ats

                result_path=os.path.join(result_path,pe)
                if not os.path.isdir(result_path):
                    os.makedirs(result_path)

            # Record input
            finp=os.path.join(result_path,'ck-input.json')
            r=ck.save_json_to_file({'json_file':finp, 'dict':i})
            if r['return']>0: return r

            ff=os.path.join(result_path,'ck-platform-features.json')
            r=ck.save_json_to_file({'json_file':ff, 'dict':features})
            if r['return']>0: return r

        # Prepare CK pipeline for a given workload
        ii={'action':'pipeline',

            'module_uoa':cfg['module_deps']['program'],
            'data_uoa':duid,

            'target':target,
            'device_id':device_id,

            'prepare':'yes',

            'params':{'config':config,
                      'params':params},

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
        rr=ck.access(ii)
        if rr['return']>0: return rr

        fail=rr.get('fail','')
        if fail=='yes':
            return {'return':10, 'error':'pipeline failed ('+rr.get('fail_reason','')+')'}

        ready=rr.get('ready','')
        if ready!='yes':
            return {'return':11, 'error':'couldn\'t prepare universal CK program workflow'}

        state=rr['state']
        tmp_dir=state['tmp_dir']

        # Clean pipeline
        if 'ready' in rr: del(rr['ready'])
        if 'fail' in rr: del(rr['fail'])
        if 'return' in rr: del(rr['return'])

        pipeline=copy.deepcopy(rr)

        # Save pipeline
        if skip_record_raw!='yes':
            fpip=os.path.join(result_path,'ck-pipeline-in.json')
            r=ck.save_json_to_file({'json_file':fpip, 'dict':pipeline})
            if r['return']>0: return r

        # Run CK pipeline *****************************************************
        ii={'action':'autotune',
            'module_uoa':cfg['module_deps']['pipeline'],
            'data_uoa':cfg['module_deps']['program'],

            'device_id':device_id,

            'iterations':1,
            'repetitions':repetitions,

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

        ls=rrr.get('last_iteration_output',{})
        fail=ls.get('fail','')
        fail_reason=ls.get('fail_reason','')

        ch=ls.get('characteristics',{})
        tet=ch.get('run',{}).get('total_execution_time',0)

        # Save pipeline
        if skip_record_raw!='yes':
            ddd['state']={'fail':fail, 'fail_reason':fail_reason}
            ddd['characteristics']={'total_execution_time':tet}

            fpip=os.path.join(result_path,'ck-pipeline-out.json')
            r=ck.save_json_to_file({'json_file':fpip, 'dict':rrr})
            if r['return']>0: return r

            # Update meta
            rx=ck.access({'action':'update',
                          'module_uoa':cfg['module_deps']['wa-result'],
                          'data_uoa':result_uid,
                          'dict':ddd,
                          'substitute':'yes',
                          'sort_keys':'yes'})
            if rx['return']>0: return rx

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

def import_wa(i):
    """
    Input:  {
              (workload)        - import only this workload
              (target_repo_uoa) - where to record imported workloads
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import copy
    import shutil
    import inspect

    o=i.get('out','')
    oo=''
    if o=='con': oo=o

    ruoa=i.get('target_repo_uoa','')

    # Get platform params
    target=i.get('target','')
    hos=i.get('host_os','')
    tos=i.get('target_os', '')
    tdid=i.get('device_id', '')

    ck.out('Detecting host and target platform info ...')
    ck.out('')

    ii={'action':'detect',
        'module_uoa':cfg['module_deps']['platform'],
        'out':oo,
        'host_os':hos,
        'target':target,
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

    pwlauto=r['env']['CK_ENV_TOOL_ARM_WA_WLAUTO']

    bat=r['bat']

    # Prepare tmp bat file
    rx=ck.gen_tmp_file({'prefix':'tmp-', 'suffix':sext})
    if rx['return']>0: return rx
    fbat=rx['file_name']

    rx=ck.gen_tmp_file({'prefix':'tmp-', 'suffix':'.tmp'})
    if rx['return']>0: return rx
    ftmp=rx['file_name']

    # Prepare cmd
    bat+='\n'
    bat+='wa list workloads > '+ftmp

    # Write bat file
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
    workload=i.get('workload','')

    wa={}
    wk=''
    wv=''
    for l in lst:
        if l!='':
            j=l.find(': ')
            if j>0:
                if wk!='':
                    if workload=='' or workload==wk:
                        wa[wk]=wv
                        wk=''
                        wv=''
                wk=l[:j].strip()
                wv=l[j+2:].strip()
            else:
                wv+=' '+l.strip()
    if wk!='':
        if workload=='' or workload==wk:  wa[wk]=wv

    # Load WA template
    wt=os.path.join(work['path'],'templates','wa-template.json')
    r=ck.load_json_file({'json_file':wt})
    if r['return']>0: return r

    wtd=r['dict']

    # Add entries
    ck.out('')
    for w in wa:
        xruoa=ruoa

        ww='wa-'+w

        wd=wa[w]

        duid=''
        d={}

        # First check, if such program exists
        s='Adding new'
        ii={'action':'load',
            'module_uoa':cfg['module_deps']['program'],
            'data_uoa':ww}
        r=ck.access(ii)
        if r['return']==0:
           duid=r['data_uid']
           d=r['dict']
           s='Updating'
           xruoa=r['repo_uid']
        else:
           rx=ck.gen_uid({})
           if rx['return']>0: return rx
           duid=rx['data_uid']

           d=copy.deepcopy(wtd)

        # Adding/updating entry
        ck.out('  '+s+' entry "'+ww+'" ...')

        d["backup_data_uid"]=duid
        d["data_name"]='WA workload: '+w
        d["wa_alias"]=w

        # Trying to find workload in WA (if installed from GitHub ia CK):
        pw=os.path.join(pwlauto,'workloads',w)

        # Check __init__.py - scary hacking - would be much simpler if WA used CK format directly
        cs=None
        rxx=ck.load_module_from_path({'path':pw, 'module_code_name':'__init__', 'skip_init':'yes'})
        if rxx['return']==0:
            cs=rxx['code']

            ck.out('      Obtaining params from __init__.py ...')

            wa_name=''
            pp=None
            imported_params={}

            for name, obj in inspect.getmembers(cs):
                if name!='AndroidUxPerfWorkload' and inspect.isclass(obj):
                    try:
                        addr=getattr(cs, name)
                        pp=addr.parameters
                    except Exception as e:
                        pass

                    if pp!=None:
                        wa_name=name
                        break

            if wa_name!='':
                ck.out('         WA class: '+wa_name)

                for p in pp:
                    for name, obj in inspect.getmembers(p):
                        if type(obj)==dict:
                            pn=obj['name']
                            pd=obj['default']
                            pk=obj['kind']
                            pm=obj['mandatory']
                            pdesc=obj['description'].replace('\n','').replace('                 ','').strip()
                            pa=obj['allowed_values']

                            imported_params[pn]={'default':pd, 'desc':pdesc, 'allowed_values':pa, 'type':str(pk.__name__), 'mandatory':pm}

                            break

                if len(imported_params)>0:
                    d['params']=imported_params

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
            'data_uoa':ww,
            'data_uid':duid,
            'repo_uoa':xruoa,
            'dict':d}
        r=ck.access(ii)
        if r['return']>0: return r

        pnew=r['path']
        print (pnew)

        if os.path.isdir(pw):
            # Copying files to CK entry
            if o=='con':
                ck.out('    Copying files ...')

            r=ck.list_all_files({'path':pw})
            if r['return']>0: return r

            lst=r['list']

            for fn in lst:
                p1=os.path.join(pw,fn)
                p2=os.path.join(pnew,fn)

                pd2=os.path.dirname(p2)
                if not os.path.isdir(pd2):
                    os.makedirs(pd2)

                shutil.copy2(p1,p2)

    return {'return':0}

##############################################################################
# replay a given experiment
# TBD: not finished!

def replay(i):
    """
    Input:  {
              data_uoa - experiment UID (see "ck list wa-result")
              (target) - force target machine
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os

    o=i.get('out','')
    oo=''
    if o=='con': oo=o

    duoa=i.get('data_uoa','')

    target=i.get('target','')

    # Help
    if (duoa==''):
       ck.out('Usage:')
       ck.out('  ck replay wa:{experiment UID}')
       ck.out('')
       ck.out('Notes:')
       ck.out('  * You can list available experiments via "ck list wa-result"')
       ck.out('  * You can view experiments via web-based WA dashboard "ck dashboard wa"')

       return {'return':0}

    # Load meta
    r=ck.access({'action':'load',
                 'module_uoa':cfg['module_deps']['wa-result'],
                 'data_uoa':duoa})
    if r['return']>0: return r
    p=r['path']
    d=r['dict']

    dm=d.get('meta',{})

    program_uoa=dm.get('program_uoa','')
    if target=='':
        target=dm.get('local_target_uoa','')

    ii={'data_uoa':program_uoa,
        'target':target,
        'out':oo}

    r=run(ii)
    if r['return']>0: return r

    return r

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
    p=os.path.join(pm, 'templates',cfg['default_device_cfg_file'])

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

    # Extra params
    if device in cfg['linux_based_wa_devices']:
        device_config=dcfg.get('device_config',{})

        ck.out('')
        r=ck.inp({'text':'Enter hostname (or press Enter for localhost): '})

        host=r['string'].strip()
        if host=='': host='localhost'
        device_config['host']=host

        ck.out('')
        r=ck.inp({'text':'Enter username (or press Enter for root): '})

        username=r['string'].strip()
        if username=='': username='root'
        device_config['username']=username

        ck.out('')
        r=ck.inp({'text':'Enter full path to public keyfile: '})

        keyfile=r['string'].strip()
        if keyfile!='':
            device_config['keyfile']=keyfile

        dcfg['device_config']=device_config

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
