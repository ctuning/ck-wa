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
hextra+='<center>\n'
hextra+='[ Check <a href="https://github.com/ctuning/ck/wiki/Demo-ARM-TechCon\'16">ARM TechCon\'16 demo</a> and participate in crowd-benchmarking] '
hextra+='[ See CK-WA framework at <a href="https://github.com/ctuning/ck-wa">GitHub</a> ]'
hextra+='</center>\n'
hextra+='<br>\n<br>\n'

selector=[{'name':'Scenario', 'key':'scenario'},
          {'name':'Workload', 'key':'workload_name'},
          {'name':'Platform', 'key':'plat_name'},
          {'name':'CPU', 'key':'cpu_name'},
          {'name':'OS', 'key':'os_name'},
          {'name':'GPU', 'key':'gpu_name'}]

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
    h+='\n\n<script language="JavaScript">function copyToClipboard (text) {window.prompt ("Copy to clipboard: Ctrl+C, Enter", text);}</script>\n\n' 

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
    elif lplst>50:
        h+='<b>Too many entries to show ('+str(lplst)+') - please, prune list further!</b>'+hextra
        return {'return':0, 'html':h, 'style':st}

    # Prepare table
    h+='<table border="1" cellpadding="7" cellspacing="0">\n'

    ha='align="center" valign="top"'
    hb='align="left" valign="top"'

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
    h+='   <td '+hb+'><b>Choices</b></td>\n'
    h+='   <td '+hb+'><b>Characteristics</b></td>\n'
    h+='   <td '+ha+'><b>JSON results</b></td>\n'
    h+='   <td '+ha+'><b>Replay</b></td>\n'
    h+='  <tr>\n'

    # Dictionary to hold target meta
    tm={}

    ix=0
    bgraph={"0":[]} # Just for graph demo

    for q in sorted(plst, key=lambda x: x.get('meta',{}).get('meta',{}).get('workload_name','')):
        ix+=1

        duid=q['data_uid']
        path=q['path']

        d=q['meta']

        meta=d.get('meta',{})

        params=d.get('choices',{}).get('params',{}).get('params',{})

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

        te=d.get('characteristics',{}).get('run',{})
        tet=te.get('total_execution_time',0)

        bgc='afffaf'
        fail=d.get('state',{}).get('fail','')
        fail_reason=d.get('state',{}).get('fail_reason','')
        if fail=='yes':
            if fail_reason=='': fail_reason='yes'

            bgc='ffafaf'
        else:
            if i.get(ckey+'workload_name','')!='' and i.get(ckey+'scenario','')!='':
                bgraph['0'].append([ix,tet])

        bg=' style="background-color:#'+bgc+';"'

        h+='  <tr'+bg+'>\n'

        x=work['self_module_uid']
        if cmuoa!='': x=cmuoa
        h+='   <td '+ha+'>'+str(ix)+')&nbsp;<a href="'+url0+'&wcid='+x+':'+duid+'">'+duid+'</a></td>\n'

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

        # APK
        x=apk_name
        if apk_ver!='': x+=' (V'+apk_ver+')'
#        x=x.replace("'","\'").replace('"',"\\'").replace('\n','\\n')
        x=x.replace("\'","'").replace("'","\\'").replace('\"','"').replace('"',"\\'").replace('\n','\\n')

        x1=''
        if x!='':
            x1='<input type="button" class="ck_small_button" onClick="alert(\''+x+'\');" value="See">'

        h+='   <td '+ha+'>'+x1+'</td>\n'

        h+='   <td '+ha+'>'+wa_ver+'</td>\n'

        x=fail_reason
        if x=='': 
            x='No'
        else:
            fail_reason=fail_reason.replace("\'","'").replace("'","\\'").replace('\"','"').replace('"',"\\'").replace('\n','\\n')
            x='Yes <input type="button" class="ck_small_button" onClick="alert(\''+fail_reason+'\');" value="Log">'

        h+='   <td '+ha+'>'+x+'</td>\n'

        # Params
#        x='<table border="0" cellpadding="0" cellspacing="2">\n'
        x=''
        for k in sorted(params):
            v=params[k]
            x+=str(k)+'='+str(v)+'\n'
#            x+='<tr><td>'+str(k)+'=</td><td>'+str(v)+'</td></tr>\n'
#        x+='</table>\n'
#        x=x.replace("'","\'").replace('"',"\\'").replace('\n','\\n')
        x=x.replace("\'","'").replace("'","\\'").replace('\"','"').replace('"',"\\'").replace('\n','\\n')

        x1=''
        if x!='':
            x1='<input type="button" class="ck_small_button" onClick="alert(\''+x+'\');" value="See">'

        h+='   <td '+hb+'>'+x1+'</td>\n'

        # Characteristics
        # Check if has statistics
        dstat={}
        fstat=os.path.join(path,'ck-stat-flat-characteristics.json')
        if os.path.isfile(fstat):
            r=ck.load_json_file({'json_file':fstat, 'dict':dstat})
            if r['return']>0: return r
            dstat=r['dict']

        x=''
        if tet>0: x=('%.1f'%tet)+' sec.'

        # Check if has stats
        x1=dstat.get("##characteristics#run#total_execution_time#center",None)
        x2=dstat.get("##characteristics#run#total_execution_time#halfrange",None)
        if x1!=None and x2!=None:
            x=('%.1f'%x1)+' &PlusMinus; '+('%.1f'%x2)+' sec.'

        # Check all
        x5=''
        for k in sorted(te):
            v=te[k]

            kx="##characteristics#run#"+k

            kx1=dstat.get(kx+'#center',None)
            kx2=dstat.get(kx+'#halfrange',None)

            x6=''
            if type(v)==int:
                if kx1!=None and kx2!=None:
                    x6=str(kx1)+' +- '+str(kx2)
                else:
                    x6=str(v)
            elif type(v)==float:
                if kx1!=None and kx2!=None:
                    x6=('%.1f'%kx1)+' +- '+('%.1f'%kx2)
                else:
                    x6=('%.1f'%v)

            if x6!='':
                x5+=str(k)+'='+x6+'\n'

#        x5=x5.replace("'","\'").replace('"',"\\'").replace('\n','\\n')
        x5=x5.replace("\'","'").replace("'","\\'").replace('\"','"').replace('"',"\\'").replace('\n','\\n')
        if x5!='':
            x+='<br><input type="button" class="ck_small_button" onClick="alert(\''+x5+'\');" value="All">'

        h+='   <td '+ha+'>'+x+'</td>\n'

        # Check directories with results
        x=''
        xf1='wa-output'
        xf2='results.json'
        xf=xf1+'/'+xf2
        for d0 in os.listdir(path):
            found=False
            brk=False

            d1=os.path.join(d0,xf)
            d2=os.path.join(path,d1)

            if os.path.isfile(d2):
                found=True
            else:
                d1=xf
                d2=os.path.join(path,d1)

                if os.path.isfile(d2):
                    d0=xf1
                    found=True
                    brk=True

            if found:
                if x!='': x+='<br>\n'
                x1=work['self_module_uid']
                if cmuoa!='':
                    x1=cmuoa
                x+='[&nbsp;<a href="'+url0+'action=pull&common_action=yes&cid='+x1+':'+duid+'&filename='+d1+'">'+d0+'</a>&nbsp;]\n'

                if brk:
                    break
        h+='   <td '+ha+'>'+x+'</td>\n'

        h+='   <td '+ha+'><input type="button" class="ck_small_button" onClick="copyToClipboard(\'ck replay wa:'+wname+'\');" value="Replay"></td>\n'

        h+='  <tr>\n'

    h+='</table>\n'
    h+='</center>\n'

    if cmuoa=='':
        h+='</form>\n'

    if len(bgraph['0'])>0:
       ii={'action':'plot',
           'module_uoa':cfg['module_deps']['graph'],

           "table":bgraph,

           "h_lines":[1.0],

           "ymin":0,

           "ignore_point_if_none":"yes",

           "plot_type":"d3_2d_bars",

           "display_y_error_bar":"no",

           "title":"Powered by Collective Knowledge",

           "axis_x_desc":"Platform",
           "axis_y_desc":"Execution time (sec.)",

           "plot_grid":"yes",

           "d3_div":"ck_interactive",

           "image_width":"900",
           "image_height":"400",

           "wfe_url":url0}

       r=ck.access(ii)
       if r['return']==0:
          x=r.get('html','')
          if x!='':
             st+=r.get('style','')

             h+='<br>\n'
             h+='<center>\n'
             h+='<div id="ck_box_with_shadow" style="width:920px;">\n'
             h+=' <div id="ck_interactive" style="text-align:center">\n'
             h+=x+'\n'
             h+=' </div>\n'
             h+='</div>\n'
             h+='</center>\n'

    h+=hextra

    return {'return':0, 'html':h, 'style':st}
