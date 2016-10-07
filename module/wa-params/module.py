#
# Collective Knowledge (Cached WA parameters in CK format)
#
# See CK-WA LICENSE.txt for licensing details
# See CK-WA COPYRIGHT.txt for copyright details
#
# Developer: Grigori.Fursin@cTuning.org, cTuning foundation
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
