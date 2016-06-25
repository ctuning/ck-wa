#
# Collective Knowledge (WA agenda)
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
# read WA agenda from .yaml, .json or entry

def read(i):
    """
    Input:  {
              (data_uoa)
                or
              (from)     - either files (.yaml/.json) or entry
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              dict         - agenda as dictionary
            }

    """

    import os

    d={} # Agenda to prepare

    duoa=i.get('data_uoa','')

    fr=i.get('from','')
    if fr.endswith('.yaml'):
       duoa=''

       r=ck.load_yaml_file({'yaml_file':fr})
       if r['return']>0: return r
       d=r['dict']

    elif fr.endswith('.json'):
       duoa=''

       r=ck.load_json_file({'json_file':fr})
       if r['return']>0: return r
       d=r['dict']

    else:
       duoa=fr

    # If CK entry
    if duoa!='':
       # Load agenda from CK entry
       r=ck.access({'action':'load',
                    'module_uoa':work['self_module_uid'],
                    'data_uoa':duoa})
       if r['return']>0: return r
       d=r['dict']

    return {'return':0, 'dict':d}
