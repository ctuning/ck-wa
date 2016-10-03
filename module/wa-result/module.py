#
# Collective Knowledge (WA results)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: dividiti, grigori@dividiti.com, http://dividiti.com
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings
form_name='wa_web_form'
onchange='document.'+form_name+'.submit();'

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
# WA dashboard (show results)

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

    st=''

    h='<center>\n'
    h+='<h2>All WA results</h2>\n'

    # Check host URL prefix and default module/action
    rx=ck.access({'action':'form_url_prefix',
                  'module_uoa':'wfe',
                  'host':i.get('host',''), 
                  'port':i.get('port',''), 
                  'template':i.get('template','')})
    if rx['return']>0: return rx
    url0=rx['url']
    template=rx['template']

    url=url0
    action=i.get('action','')
    muoa=i.get('module_uoa','')

    st=''

    url+='action=index&module_uoa=wfe&native_action='+action+'&'+'native_module_uoa='+muoa
    url1=url

    # List entries
    r=ck.access({'action':'search',
                 'module_uoa':work['self_module_uid'],
                 'add_meta':'yes'})
    if r['return']>0: return r

    lst=r['lst']

    # Check unique entries
    selector=[{'name':'Workload', 'key':'workload_name'},
              {'name':'Platform', 'key':'plat_name'},
              {'name':'CPU', 'key':'cpu_name'},
              {'name':'OS', 'key':'os_name'},
              {'name':'GPU', 'key':'gpu_name'}]
    choices={}
    wchoices={}

    for q in lst:
        d=q['meta']
        meta=d.get('meta',{})

        for kk in selector:
            k=kk['key']

            if k not in choices: 
                choices[k]=[]
                wchoices[k]=[{'name':'','value':''}]

            v=meta.get(k,'')
            if v!='':
                if v not in choices[k]: 
                    choices[k].append(v)
                    wchoices[k].append({'name':v, 'value':v})

    # Prepare query div ***************************************************************
    # Start form + URL (even when viewing entry)
    r=ck.access({'action':'start_form',
                 'module_uoa':cfg['module_deps']['wfe'],
                 'url':url1,
                 'name':form_name})
    if r['return']>0: return r
    h+=r['html']

    for kk in selector:
        k=kk['key']
        n=kk['name']

        if i.get(k,'')!='':
            v=i[k]
            kk['value']=v

        # Show hardware
        ii={'action':'create_selector',
            'module_uoa':cfg['module_deps']['wfe'],
            'data':wchoices[k],
            'name':k,
            'onchange':onchange, 
            'skip_sort':'no',
            'selected_value':v}
        r=ck.access(ii)
        if r['return']>0: return r

        h+='<b>'+n+':</b> '+r['html']+'\n'

    h+='<br><br>'

    # Prepare table
    h+='<table border="1" cellpadding="7" cellspacing="0">\n'

    h+='  <tr>\n'
    h+='   <td align="center"><b>All raw files</b></td>\n'
    h+='   <td align="center"><b>Workload</b></td>\n'
    h+='   <td align="center"><b>Platform</b></td>\n'
    h+='   <td align="center"><b>CPU</b></td>\n'
    h+='   <td align="center"><b>GPU</b></td>\n'
    h+='   <td align="center"><b>OS</b></td>\n'
    h+='   <td align="center"><b>Fail?</b></td>\n'
    h+='   <td align="center"><b>Time</b></td>\n'
    h+='   <td align="center"><b>JSON results</b></td>\n'
    h+='  <tr>\n'

    for q in sorted(lst, key=lambda x: x.get('meta',{}).get('meta',{}).get('workload_name','')):
        duid=q['data_uid']
        d=q['meta']

        meta=d.get('meta',{})

        # Check selector
        skip=False
        for kk in selector:
            k=kk['key']
            n=kk['name']
            v=kk.get('value','')

            if v!='' and meta.get(k,'')!=v:
                skip=True

        if skip:
            continue

        pname=meta.get('program_uoa','')
        wname=meta.get('workload_name','')
        wuid=meta.get('program_uid','')

        ltarget_uoa=meta.get('local_target_uoa','')
        ltarget_uid=meta.get('local_target_uid','')

        plat_name=meta.get('plat_name','')
        cpu_name=meta.get('cpu_name','')
        os_name=meta.get('os_name','')
        gpu_name=meta.get('gpu_name','')

        bgc='afffaf'
        fail=d.get('state',{}).get('fail','')
        fail_reason=d.get('state',{}).get('fail_reason','')
        if fail=='yes':
            if fail_reason=='': fail_reason='yes'
            bgc='ffafaf'

        bg=' style="background-color:#'+bgc+';"'

        tet=d.get('characteristics',{}).get('total_execution_time',0)

        h+='  <tr'+bg+'>\n'

        h+='   <td align="center"><a href="'+url0+'&wcid='+work['self_module_uid']+':'+duid+'">'+duid+'</a></td>\n'

        x=wname
        if wuid!='': x='<a href="'+url0+'&wcid='+cfg['module_deps']['program']+':'+wuid+'">'+x+'</a>'
        h+='   <td align="center">'+x+'</td>\n'

        x=plat_name
        if ltarget_uid!='':
           x='<a href="'+url0+'&wcid='+cfg['module_deps']['machine']+':'+ltarget_uid+'">'+x+'</a>'
        h+='   <td align="center">'+x+'</td>\n'

        h+='   <td align="center">'+cpu_name+'</td>\n'
        h+='   <td align="center">'+gpu_name+'</td>\n'
        h+='   <td align="center">'+os_name+'</td>\n'

        h+='   <td align="center">'+fail_reason+'</td>\n'

        x=''
        if tet>0: x=('%.3f'%tet)+' sec.'
        h+='   <td align="center">'+x+'</td>\n'

        h+='   <td align="center"><a href="'+url0+'action=pull&common_action=yes&cid='+work['self_module_uid']+':'+duid+'&filename=wa-output/results.json">view</a></td>\n'

        h+='  <tr>\n'

    h+='</table>\n'
    h+='</center>\n'

    h+='</form>\n'

    return {'return':0, 'html':h, 'style':st}
