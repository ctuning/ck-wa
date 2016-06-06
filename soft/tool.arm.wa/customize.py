#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE for licensing details
# See CK COPYRIGHT for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

##############################################################################
# parse software version

def parse_version(i):

    lst=i['output']

    ver=''

    for q in lst:
        q=q.strip()
        if q!='' and q.startswith('wa ') and len(q)>3:
           ver=q[3:]

    return {'return':0, 'version':ver}

##############################################################################
# setup environment setup

def setup(i):
    """
    Input:  {
              cfg              - meta of this soft entry
              self_cfg         - meta of module soft
              ck_kernel        - import CK kernel module (to reuse functions)

              host_os_uoa      - host OS UOA
              host_os_uid      - host OS UID
              host_os_dict     - host OS meta

              target_os_uoa    - target OS UOA
              target_os_uid    - target OS UID
              target_os_dict   - target OS meta

              target_device_id - target device ID (if via ADB)

              tags             - list of tags used to search this entry

              env              - updated environment vars from meta
              customize        - updated customize vars from meta

              deps             - resolved dependencies for this soft

              interactive      - if 'yes', can ask questions, otherwise quiet
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              bat          - prepared string for bat file
            }

    """

    import os

    # Get variables
    ck=i['ck_kernel']
    s=''

    cus=i['customize']
    env=i['env']

    host_d=i.get('host_os_dict',{})
    winh=host_d.get('windows_base','')

    ep=cus.get('env_prefix','')

    fp=cus.get('full_path','')
    if cus.get('force_path',''):
       fp=cus['force_path'] # usually passed from CK package

    if fp!='':
       p1=os.path.dirname(fp)
       pi=os.path.dirname(p1)

       env[ep]=pi
       env[ep+'_BIN']=p1

    if p1!='':
       ############################################################
       if winh=='yes':
          s+='\nset PATH='+p1+';%PATH%\n\n'
       else:
          s+='\nexport PATH='+p1+':$PATH\n\n'

    return {'return':0, 'bat':s}
