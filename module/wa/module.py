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

ffstat='ck-stat-flat-characteristics.json'

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
              (data_uoa)            - workload to run (see "ck list wa").

              (target)              - machine UOA (see "ck list machine")

              (record)              - if 'yes', record result in repository in 'experiment' standard
              (skip-record-raw)     - if 'yes', skip record raw results
              (overwrite)           - if 'yes', do not record date and time in result directory, but overwrite wa-results

              (repetitions)         - statistical repetitions (default=1), for now statistical analysis is not used (TBD)

              (config)              - customize config
              (params)              - workload params
              (scenario)            - use pre-defined scenario (see ck list wa-scenario)

              (keep)                - if 'yes', keep tmp file in workload (program) directory

              (cache)               - if 'yes', cache params (to automate runs)
              (cache_repo_uoa)      - repo UOA where to cache params

              (share)               - if 'yes', share benchmarking results with public cknowledge.org/repo server
                                      (our crowd-benchmarking demo)
              (exchange_repo)       - which repo to record/update info (remote-ck by default)
              (exchange_subrepo)    - if remote, remote repo UOA
              (scenario_module_uoa) - UOA of the scenario (to share results)
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
    import shutil

    o=i.get('out','')
    oo=''
    if o=='con': oo=o

    cur_dir=os.getcwd()

    # Check if any input has . and convert to dict
    for k in i:
        if k.find('.')>0:
            v=i[k]

            kk='##'+k.replace('.','#')

            del(i[k])

            r=ck.set_by_flat_key({'dict':i, 'key':kk, 'value':v})
            if r['return']>0: return r

    # Check if share
    share=i.get('share','')
    user=i.get('user','')
    smuoa=i.get('scenario_module_uoa','')
    if smuoa=='': smuoa=cfg['module_deps']['experiment.bench.workload.android']

    er=i.get('exchange_repo','')
    if er=='': er=ck.cfg['default_exchange_repo_uoa']

    esr=i.get('exchange_subrepo','')
    if esr=='': esr=ck.cfg['default_exchange_subrepo_uoa']

    # Get device and workload params
    config=i.get('config',{})
    params=i.get('params',{})

    # Check scenarios
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
    if repetitions=='': repetitions=3
    repetitions=int(repetitions)

    cache=i.get('cache','')

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

    cparams=copy.deepcopy(params)
    for wa in lst:
        # Reset dir
        os.chdir(cur_dir)

        # Reset params
        params=copy.deepcopy(cparams)

        duoa=wa['data_uoa']
        duid=wa['data_uid']
        dw=wa['meta']
        dp=wa['path']

        apk_name=dw.get('apk',{}).get('name','')

        ww=dw['wa_alias']

        # If cache, check if params already exist
        if cache=='yes':
            # Check extra
            cruoa=i.get('cache_repo_uoa','')

            # Attempt to load
            r=ck.access({'action':'load',
                         'module_uoa':cfg['module_deps']['wa-params'],
                         'data_uoa':duoa,
                         'repo_uoa':cruoa})
            if r['return']>0 and r['return']!=16:
                return r

            if r['return']==0:
                cruoa=r['repo_uid']

                rx=ck.merge_dicts({'dict1':params, 'dict2':r['dict'].get('params',{})})
                if rx['return']>0: return rx

        # Check params here (there is another place in pre-processing scripts
        #  to be able to run WA via program pipeline directly) 
        dparams=dw.get('params',{})

        if len(dparams)>0:
            ck.out('Parameters needed for this workload:')
            ck.out('')

        for k in sorted(dparams):
            x=dparams[k]

            ds=x.get('desc','')

            dv=params.get(k,None)
            if dv==None:
                dv=x.get('default',None)

            if dv!=None:
                ck.out(k+': '+str(dv))
            elif x.get('mandatory',False):
                r=ck.inp({'text':k+' ('+ds+'): '})
                if r['return']>0: return r
                dv=r['string'].strip()
                if dv=='':
                    dv=None

            if dv!=None:
                params[k]=dv

        # Cache params if required
        if cache=='yes':
            r=ck.access({'action':'update',
                         'module_uoa':cfg['module_deps']['wa-params'],
                         'data_uoa':duoa,
                         'repo_uoa':cruoa,
                         'dict':{'params':params},
                         'sort_keys':'yes',
                         'substitute':'yes',
                         'ignore_update':'yes'})
            if r['return']>0:
                return r

            if o=='con':
                ck.out('')
                ck.out('Parameters were cached in '+r['path']+' ...')

        # Prepare high-level experiment meta
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

        aggregated_stats={} # Pre-load statistics ...

        result_path=''
        result_path0=''
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
            result_path0=result_path
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

            # Check stats ...
            fstat=os.path.join(result_path0,ffstat)
            if overwrite!='yes':
                # Check if file already exists (no check for parallel runs)
                if os.path.isfile(fstat):
                    r=ck.load_json_file({'json_file':fstat})
                    if r['return']==0:
                        aggregated_stats=r['dict']

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

            'collect_all':'yes',
            'process_multi_keys':['##characteristics#*'],

            'tmp_dir':tmp_dir,

            'pipeline':pipeline,

            'stat_flat_dict':aggregated_stats,

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
        state=ls.get('state',{})
        xchoices=copy.deepcopy(ls.get('choices',{}))
        lsa=rrr.get('last_stat_analysis',{})
        lsad=lsa.get('dict_flat',{})

        # Not very clean - trying to remove passes ...
        xparams=xchoices.get('params','').get('params',{})
        to_be_deleted=[]
        for k in xparams:
            if k.find('pass')>=0:
                to_be_deleted.append(k)

        for k in to_be_deleted:
            del(xparams[k])

        ddd['choices']=xchoices

        features=ls.get('features',{})
        apk_ver=''
        if apk_name!='':
            apk_ver=features.get('apk',{}).get(apk_name,{}).get('versionName','')

        deps=ls.get('dependencies',{})
        wa_ver=deps.get('wa',{}).get('cus',{}).get('version','')

        # Update meta
        ddd['meta']['apk_name']=apk_name
        ddd['meta']['apk_version']=apk_ver
        ddd['meta']['wa_version']=wa_ver

        # Clean tmp dir
        tmp_dir=state.get('tmp_dir','')
        if dp!='' and tmp_dir!='' and i.get('keep','')!='yes':
            shutil.rmtree(os.path.join(dp,tmp_dir))

        fail=ls.get('fail','')
        fail_reason=ls.get('fail_reason','')

        ch=ls.get('characteristics',{})

#        tet=ch.get('run',{}).get('total_execution_time',0)

        # Save pipeline
        ddd['state']={'fail':fail, 'fail_reason':fail_reason}
        ddd['characteristics']=ch

        if skip_record_raw!='yes':
            fpip=os.path.join(result_path,'ck-pipeline-out.json')
            r=ck.save_json_to_file({'json_file':fpip, 'dict':rrr})
            if r['return']>0: return r

            # Write stats ...
            r=ck.save_json_to_file({'json_file':fstat, 'dict':lsad})
            if r['return']>0: return r

            # Update meta
            rx=ck.access({'action':'update',
                          'module_uoa':cfg['module_deps']['wa-result'],
                          'data_uoa':result_uid,
                          'dict':ddd,
                          'substitute':'yes',
                          'sort_keys':'yes'})
            if rx['return']>0: return rx

        # Share results if crowd-benchmarking
        if share=='yes':
            ddd['user']=user

            if o=='con':
               ck.out('')
               ck.out('Saving results to the remote public repo ...')
               ck.out('')

            # Find remote entry
            rduid=''

            ii={'action':'search',
                'module_uoa':smuoa,
                'repo_uoa':er,
                'remote_repo_uoa':esr,
                'search_dict':{'meta':meta}}
            rx=ck.access(ii)

            lst=rx['lst']

            if len(lst)==1:
                rduid=lst[0]['data_uid']
            else:
                rx=ck.gen_uid({})
                if rx['return']>0: return rx
                rduid=rx['data_uid']

            # Update meta
            rx=ck.access({'action':'update',
                          'module_uoa':smuoa,
                          'data_uoa':rduid,
                          'repo_uoa':er,
                          'remote_repo_uoa':esr,
                          'dict':ddd,
                          'substitute':'yes',
                          'sort_keys':'yes'})
            if rx['return']>0: return rx

            # Push statistical characteristics
            if os.path.isfile(fstat):
                rx=ck.access({'action':'push',
                              'module_uoa':smuoa,
                              'data_uoa':rduid,
                              'repo_uoa':er,
                              'remote_repo_uoa':esr,
                              'filename':fstat,
                              'overwrite':'yes'})
                if rx['return']>0: return rx

            # Push latest results
            fx=os.path.join(result_path,'wa-output','results.json')
            if os.path.isfile(fx):
                rx=ck.access({'action':'push',
                              'module_uoa':smuoa,
                              'data_uoa':rduid,
                              'repo_uoa':er,
                              'remote_repo_uoa':esr,
                              'filename':fx,
                              'extra_path':'wa-output',
                              'overwrite':'yes'})
                if rx['return']>0: return rx

            # Info
            if o=='con':
                ck.out('Succesfully recorded results in repo repo (Entry UID='+rduid+')')

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
              (workload) or (data_uoa) - import only this workload
              (target_repo_uoa)        - where to record imported workloads
              (extra_target_repo_uoa)  - where to record imported tools and devices
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

    eruoa=i.get('extra_target_repo_uoa','')
    if eruoa=='':
        eruoa=ruoa

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
    if workload=='':
        workload=i.get('data_uoa','')

    wa={}
    wk=''
    wv=''

    ##############################################################################
    ck.out('Importing WA workloads to CK:')
    ck.out('')

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
            pname=None
            imported_params={}

            for name, obj in inspect.getmembers(cs):
                if name!='AndroidUxPerfWorkload' and inspect.isclass(obj):
                    try:
                        addr=getattr(cs, name)
                        pp=addr.parameters
                        pname=addr.package
                    except Exception as e:
                        pass

                    if pp!=None:
                        wa_name=name
                        break

            if pname!=None:
                if 'apk' not in d: d['apk']={}
                d['apk']['name']=pname

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

    ############################################################################
    ck.out('')
    ck.out('Importing WA tools to CK:')
    ck.out('')

    pd=os.path.join(pwlauto,'instrumentation')
    if os.path.isdir(pd):
        for px in os.listdir(pd):
            pdd=os.path.join(pd,px)
            if os.path.isdir(pdd):
                ck.out('  '+px)
                r=ck.access({'action':'update',
                             'module_uoa':cfg['module_deps']['wa-tool'],
                             'data_uoa':px,
                             'repo_uoa':eruoa})
                if r['return']>0: return r

                pnew=r['path']

                ck.out('    Path to CK entry: '+pnew)

                # Copying files to CK entry
                r=ck.list_all_files({'path':pdd})
                if r['return']>0: return r

                lst=r['list']

                for fn in lst:
                    p1=os.path.join(pdd,fn)
                    p2=os.path.join(pnew,fn)

                    pd2=os.path.dirname(p2)
                    if not os.path.isdir(pd2):
                        os.makedirs(pd2)

                    shutil.copy2(p1,p2)

    ############################################################################
    ck.out('')
    ck.out('Importing WA devices to CK:')
    ck.out('')

    devs=['android','linux']

    for dv in devs:
        pd=os.path.join(pwlauto,'devices',dv)
        if os.path.isdir(pd):
            for px in os.listdir(pd):
                pdd=os.path.join(pd,px)
                if os.path.isdir(pdd):
                    ck.out('  '+px)
                    r=ck.access({'action':'update',
                                 'module_uoa':cfg['module_deps']['wa-device'],
                                 'data_uoa':dv+'-'+px,
                                 'repo_uoa':eruoa})
                    if r['return']>0: return r

                    pnew=r['path']

                    ck.out('    Path to CK entry: '+pnew)

                    # Copying files to CK entry
                    r=ck.list_all_files({'path':pdd})
                    if r['return']>0: return r

                    lst=r['list']

                    for fn in lst:
                        p1=os.path.join(pdd,fn)
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

##############################################################################
# crowd benchmark Android workloads via CK public repository (cknowledge.org/repo)

def crowdbench(i):
    """
    Input:  {
              will be passed to "ck crowdsource experiment.bench.workload.android"
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    i['module_uoa']=cfg['module_deps']['experiment.bench.workload.android']
    i['action']='crowdsource'

    return ck.access(i)
