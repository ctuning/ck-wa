#
# Collective Knowledge (configure device)
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
# add connected device

def add(i):
    """
    Input:  {
              (data_uoa)      - CK entry name
              (data_name)     - user-friendly name

              (wa_device)     - WA device name/interface (generic_android, generic_linux, ... - see "wa list devices")

              (target_os)     - target OS on the device (android19-arm by default)
              (device_id)     - device id if remote (such as adb)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import json

    o=i.get('out','')
    oo=''
    if o=='con': oo=o

    # Check target OS and ID
    hos=i.get('host_os','')
    tos=i.get('target_os','')
    tdid=i.get('device_id','')

    if tos=='': tos='android19-arm'

    # Detect platform features
    if o=='con':
       ck.out('Detecting your platform info ...')
       ck.out('')

    ii={'action':'detect',
        'module_uoa':cfg['module_deps']['platform'],
        'out':oo,
        'host_os':hos,
        'target_os':tos,
        'target_device_id':tdid,
        'exchange':'yes',
        'exchange_repo':'local',
        'exchange_subrepo':'',
#        'skip_info_collection':sic,
#        'quiet':quiet,
        'skip_gpu_info':'yes',
#        'platform_init_uoa':piuoa,
#        'force_platform_name':fpn
    }
    rpp=ck.access(ii)
    if rpp['return']>0: return rpp

    hos=rpp['host_os_uoa']
    hosd=rpp['host_os_dict']

    tos=rpp['os_uoa']
    tosd=rpp['os_dict']
    tbits=tosd.get('bits','')

    remote=tosd.get('remote','')

    tdid=rpp['device_id']
    device_features=rpp.get('features',{})
    tname=device_features.get('platform',{}).get('name','')

    if hos=='':
       return {'return':1, 'error':'"host_os" is not defined or detected'}

    if tos=='':
       return {'return':1, 'error':'"target_os" is not defined or detected'}

    # Load default config (in CK JSON)
    pm=work['path']
    p=os.path.join(pm, cfg['default_device_cfg_file'])

    r=ck.load_json_file({'json_file':p})
    if r['return']>0: return r
    dcfg=r['dict']

    # Choose CK alias for a given device (such as generic_linux, etc)
    duoa=i.get('data_uoa','')
    if duoa=='':
       tname1='' # simplified
       if tname!='':
          tname1=tname.lower().replace(' ','-')

       if o=='con':
          s='Enter device alias to be recored in the CK repository'
          if tname1!='':
             s+=' or press Enter to select "'+tname1+'"'
          s+=': '

          ck.out('')
          r=ck.inp({'text':s})

          duoa=r['string'].strip()
          if duoa=='' and tname1!='':
             duoa=tname1
       elif tname1!='':
          duoa=tname1

    # Choose CK user-friendly name
    dname=i.get('data_name','')
    if dname=='':
       if o=='con':
          s='Enter user-friendly device name'
          if tname!='':
             s+=' or press Enter to select "'+tname+'"'
          s+=': '

          ck.out('')
          r=ck.inp({'text':s})

          dname=r['string'].strip()
          if dname=='' and tname!='':
             dname=tname
       elif tname!='':
          dname=tname

    # Select WA device
    device=i.get('wa_device','')
    if device=='' and o=='con':
       ck.out('')

       ck.out('Available WA devices:')
       ck.out('')
       os.system('wa list devices')

       ck.out('')
       r=ck.inp({'text':'Enter WA device name from above list or press Enter to select "generic_android": '})
       device=r['string'].strip()
       if device=='': device='generic_android'

    # Updating default config
    dcfg['device']=device

    if 'device_config' not in dcfg:
       dcfg['device_config']={}

    if tdid!='':
       dcfg['device_config']['adb_name']=tdid

    dd={'device_config':dcfg,
        'target_os':tos,
        'device_id':tdid,
        'device_features':device_features}

    # Adding CK entry
    r=ck.access({'action':'add',
                 'module_uoa':work['self_module_uid'],
                 'data_uoa':duoa,
                 'data_name':dname,
                 'dict':dd,
                 'common_func':'yes'})
    if r['return']>0: return r

    # Generating config.py
    pp=r['path']
    px=os.path.join(pp,cfg['device_cfg_file'])

    s='# WA config file automatically generated by CK\n'
    for k in sorted(dcfg):
        s+=k+' = '

        v=dcfg[k]

        if type(v)==list or type(v)==dict:
           s+=json.dumps(v, indent=2, sort_keys=True)+'\n'
        elif type(v)==int or type(v)==float:
           s+=str(v)+'\n'
        else:
           s+='"'+str(v)+'"\n'

    # Trick (not clean) to replace true with True for python
    s=s.replace(' true', ' True')

    # Save config file in the new CK entry
    r=ck.save_text_file({'text_file':px, 'string':s})
    if r['return']>0: return r

    if o=='con':
       ck.out('')
       ck.out('CK entry and config file were successfully created in path '+pp)
       ck.out('  You can customize WA device config.py file there if needed!')

    return {'return':0}
