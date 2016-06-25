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

    h+='<table border="1" cellpadding="7" cellspacing="0">\n'

    h+='  <tr>\n'
    h+='   <td><b>CK UID</b></td>\n'
    h+='   <td><b>WA</b></td>\n'
    h+='   <td><b>Results (json)</b></td>\n'
    h+='  <tr>\n'

    for q in lst:
        duid=q['data_uid']
        d=q['meta']

        meta=d.get('meta',{})
        wn=meta.get('workload_name','')

        h+='  <tr>\n'

        h+='   <td><a href="'+url0+'&wcid='+work['self_module_uid']+':'+duid+'">'+duid+'</a></td>\n'
        h+='   <td>'+wn+'</td>\n'
        h+='   <td><a href="'+url0+'action=pull&common_action=yes&cid='+work['self_module_uid']+':'+duid+'&filename=results/results.json">view</a></td>\n'

        h+='  <tr>\n'

    h+='</table>\n'
    h+='</center>\n'

    return {'return':0, 'html':h, 'style':st}
