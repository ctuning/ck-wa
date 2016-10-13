#
# Collective Knowledge (WA results)
#
# See CK-WA LICENSE.txt for licensing details
# See CK-WA COPYRIGHT.txt for copyright details
#
# Developer: dividiti, grigori@dividiti.com, http://dividiti.com
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings
form_name='wa_web_form'
onchange='document.'+form_name+'.submit();'

hextra='<br>\n<br>\n<br>\n'
hextra+='[ Check <a href="https://github.com/ctuning/ck/wiki/Demo-ARM-TechCon\'16">ARM TechCon demo</a> and participate in crowd-benchmarking] '
hextra+='[ See CK-WA framework at <a href="https://github.com/ctuning/ck-wa">GitHub</a> ]'
hextra+='<br>\n<br>\n'

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
               (crowd_module_uoa) - if rendered from experiment crowdsourcing
               (crowd_key)        - add extra name to Web keys to avoid overlapping with original crowdsourcing HTML
               (crowd_on_change)  - reuse onchange doc from original crowdsourcing HTML
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os

    st=''

    cmuoa=i.get('crowd_module_uoa','')
    ckey=i.get('crowd_key','')

    conc=i.get('crowd_on_change','')
    if conc=='':
        conc=onchange

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
    ii={'action':'search',
        'module_uoa':work['self_module_uid'],
        'add_meta':'yes'}

    if cmuoa!='':
        ii['module_uoa']=cmuoa

    r=ck.access(ii)
    if r['return']>0: return r

    lst=r['lst']

    # Check unique entries
    selector=[{'name':'Scenario', 'key':'scenario'},
              {'name':'Workload', 'key':'workload_name'},
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
            kx=kk['key']
            k=ckey+kx

            if k not in choices: 
                choices[k]=[]
                wchoices[k]=[{'name':'','value':''}]

            v=meta.get(kx,'')
            if v!='':
                if v not in choices[k]: 
                    choices[k].append(v)
                    wchoices[k].append({'name':v, 'value':v})

    # Prepare query div ***************************************************************
    if cmuoa=='':
        # Start form + URL (even when viewing entry)
        r=ck.access({'action':'start_form',
                     'module_uoa':cfg['module_deps']['wfe'],
                     'url':url1,
                     'name':form_name})
        if r['return']>0: return r
        h+=r['html']

    for kk in selector:
        k=ckey+kk['key']
        n=kk['name']

        v=''
        if i.get(k,'')!='':
            v=i[k]
            kk['value']=v

        # Show hardware
        ii={'action':'create_selector',
            'module_uoa':cfg['module_deps']['wfe'],
            'data':wchoices.get(k,[]),
            'name':k,
            'onchange':conc, 
            'skip_sort':'no',
            'selected_value':v}
        r=ck.access(ii)
        if r['return']>0: return r

        h+='<b>'+n+':</b> '+r['html'].strip()+'\n'

    h+='<br><br>'

    # Prune list
    plst=[]
    for q in lst:
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

        if not skip:
            plst.append(q)

    # Check if too many
    lplst=len(plst)
    if lplst==0:
        h+='<b>No results found!</b>'+hextra
        return {'return':0, 'html':h, 'style':st}
    elif lplst>100:
        h+='<b>Too many entries to show ('+str(lplst)+') - please, prune list further!</b>'+hextra
        return {'return':0, 'html':h, 'style':st}

    # Prepare table
    h+='<table border="1" cellpadding="7" cellspacing="0">\n'

    ha='align="center" valign="top"'

    h+='  <tr>\n'
    h+='   <td '+ha+'><b>All raw files</b></td>\n'
    h+='   <td '+ha+'><b>Workload</b></td>\n'
    h+='   <td '+ha+'><b>Scenario</b></td>\n'
    h+='   <td '+ha+'><b>Platform</b></td>\n'
    h+='   <td '+ha+'><b>serial number / adb device ID</b></td>\n'
    h+='   <td '+ha+'><b>CPU</b></td>\n'
    h+='   <td '+ha+'><b>GPU</b></td>\n'
    h+='   <td '+ha+'><b>OS</b></td>\n'
    h+='   <td '+ha+'><b>APK</b></td>\n'
    h+='   <td '+ha+'><b>WA version</b></td>\n'
    h+='   <td '+ha+'><b>Fail?</b></td>\n'
    h+='   <td '+ha+'><b>Time</b></td>\n'
    h+='   <td '+ha+'><b>JSON results</b></td>\n'
    h+='  <tr>\n'

    # Dictionary to hold target meta
    tm={}

    for q in sorted(plst, key=lambda x: x.get('meta',{}).get('meta',{}).get('workload_name','')):
        duid=q['data_uid']
        path=q['path']

        d=q['meta']

        meta=d.get('meta',{})

        pname=meta.get('program_uoa','')
        wname=meta.get('workload_name','')
        wuid=meta.get('program_uid','')

        apk_name=meta.get('apk_name','')
        apk_ver=meta.get('apk_version','')

        wa_ver=meta.get('wa_version','')

        scenario=meta.get('scenario','')

        ltarget_uoa=meta.get('local_target_uoa','')
        ltarget_uid=meta.get('local_target_uid','')

        if ltarget_uid!='' and ltarget_uid not in tm:
            # Load machine meta
            rx=ck.access({'action':'load',
                          'module_uoa':cfg['module_deps']['machine'],
                          'data_uoa':ltarget_uid})
            if rx['return']==0:
                tm[ltarget_uid]=rx['dict']

        plat_name=meta.get('plat_name','')
        cpu_name=meta.get('cpu_name','')
        os_name=meta.get('os_name','')
        gpu_name=meta.get('gpu_name','')

        adb_id=tm.get(ltarget_uid,{}).get('device_id','')
        sn=meta.get('serial_number','')

        bgc='afffaf'
        fail=d.get('state',{}).get('fail','')
        fail_reason=d.get('state',{}).get('fail_reason','')
        if fail=='yes':
            if fail_reason=='': fail_reason='yes'
            bgc='ffafaf'

        bg=' style="background-color:#'+bgc+';"'

        tet=d.get('characteristics',{}).get('run',{}).get('total_execution_time',0)

        h+='  <tr'+bg+'>\n'

        x=work['self_module_uid']
        if cmuoa!='': x=cmuoa
        h+='   <td '+ha+'><a href="'+url0+'&wcid='+x+':'+duid+'">'+duid+'</a></td>\n'

        x=wname
        if wuid!='': x='<a href="'+url0+'&wcid='+cfg['module_deps']['program']+':'+wuid+'">'+x+'</a>'
        h+='   <td '+ha+'>'+x+'</td>\n'

        x=''
        if scenario!='':
            x='<a href="'+url0+'&wcid='+cfg['module_deps']['wa-scenario']+':'+scenario+'">'+scenario+'</a>'
        h+='   <td '+ha+'>'+x+'</td>\n'

        x=plat_name
        if ltarget_uid!='':
           x='<a href="'+url0+'&wcid='+cfg['module_deps']['machine']+':'+ltarget_uid+'">'+x+'</a>'
        h+='   <td '+ha+'>'+x+'</td>\n'

        x=sn
        if adb_id!='' and adb_id!=sn: x+=' / '+adb_id
        h+='   <td '+ha+'>'+x+'</td>\n'

        h+='   <td '+ha+'>'+cpu_name+'</td>\n'
        h+='   <td '+ha+'>'+gpu_name+'</td>\n'
        h+='   <td '+ha+'>'+os_name+'</td>\n'

        x=apk_name
        if apk_ver!='': x+=' (V'+apk_ver+')'
        h+='   <td '+ha+'>'+x+'</td>\n'

        h+='   <td '+ha+'>'+wa_ver+'</td>\n'

        h+='   <td '+ha+'>'+fail_reason+'</td>\n'

        x=''
        if tet>0: x=('%.3f'%tet)+' sec.'
        h+='   <td '+ha+'>'+x+'</td>\n'

        # Check directories with results
        x=''
        xf='wa-output/results.json'
        for d0 in os.listdir(path):
            d1=os.path.join(d0,xf)
            d2=os.path.join(path,d1)
            if os.path.isfile(d2):
                if x!='': x+='<br>\n'
                x+='[&nbsp;<a href="'+url0+'action=pull&common_action=yes&cid='+work['self_module_uid']+':'+duid+'&filename='+d1+'">'+d0+'</a>&nbsp;]\n'

        h+='   <td '+ha+'>'+x+'</td>\n'

        h+='  <tr>\n'

    h+='</table>\n'
    h+='</center>\n'

    if cmuoa=='':
        h+='</form>\n'

    h+=hextra

    return {'return':0, 'html':h, 'style':st}
