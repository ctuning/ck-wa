#
# Collective Knowledge (WA scenarios)
#
# See CK-WA LICENSE.txt for licensing details
# See CK-WA COPYRIGHT.txt for copyright details
#
# Developer: grigori.fursin@cTuning.org
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
# add scenario (semi-manual)

def add(i):
    """
    Input:  {
              (data_uoa) - scenario alias
              (repo_uoa) - repository where to record scenario

              (config)   - WA device config for this scenario
              (params)   - workload params for this scenario
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    o=i.get('out','')

    ruoa=i.get('repo_uoa','')

    # Checking scenario alias
    duoa=i.get('data_uoa','')
    if duoa=='':
        r=ck.inp({'text':'Enter name for your scenario (CK alias): '})
        if r['return']>0: return r

        duoa=r['string'].strip()

    if duoa=='':
        return {'return':1, 'error':'scenario alias is not specified'}

    # Asking for WA device config in JSON
    ck.out('')
    ck.out('Enter WA device config in JSON format for this scenario (press Enter to finish):')
    ck.out('')

    dc=i.get('config',{})
    if len(dc)==0:
        sc=''
        s='dummy'

        while s!='':
            r=ck.inp({'text':''})
            if r['return']>0: return r
            s=r['string'].strip()
            sc+=s+'\n'

        sc=sc.strip()
        if sc!='':
            r=ck.convert_json_str_to_dict({'str':sc, 'skip_quote_replacement':'yes'})
            if r['return']>0: return r
            dc=r['dict']

    # Asking for workload parameters (if needed)
    ck.out('')
    ck.out('Enter parameters in JSON required for this workload:')
    ck.out('')

    dp=i.get('params',{})
    if len(dp)==0:
        sp=''
        s='dummy'

        while s!='':
            r=ck.inp({'text':''})
            if r['return']>0: return r
            s=r['string'].strip()
            sp+=s+'\n'

        sp=sp.strip()
        if sp!='':
            r=ck.convert_json_str_to_dict({'str':sp, 'skip_quote_replacement':'yes'})
            if r['return']>0: return r
            dp=r['dict']

    # Check if scenario already exists
    duid=''
    r=ck.access({'action':'load',
                 'module_uoa':work['self_module_uid'],
                 'data_uoa':duoa})
    if r['return']==0:
        ck.out('')
        rx=ck.inp({'text':'Alias '+duoa+' already exists - overwrite (Y/n)? '})
        if rx['return']>0: return rx

        q=rx['string'].strip().lower()
        if q!='n' and q!='no':
            duid=r['data_uid']
            ruoa=r['repo_uid']

    # Adding/updating scenario
    dd={'config':dc,
        'params':dp}

    r=ck.access({'action':'update',
                 'module_uoa':work['self_module_uid'],
                 'data_uoa':duoa,
                 'data_uid':duid,
                 'repo_uoa':ruoa,
                 'dict':dd,
                 'substitute':'yes',
                 'sort_keys':'yes'})
    if r['return']>0: return r

    ck.out('')
    ck.out('Scenario '+duoa+' was successfully recorded in CK. You can specify it via --scenario='+duoa+' flag.')

    return {'return':0}
