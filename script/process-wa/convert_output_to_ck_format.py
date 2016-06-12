#
# Converting ARM Workload automation ouput 
# to CK universal autotuning and machine learning format
#
# Collective Knowledge (CK)
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#
# Developer: Grigori Fursin
#

import json

d={}

#######################################
print ('Loading tmp-output1.tmp ...')

log=''

try:
  f=open('tmp-output1.tmp', 'r')
except Exception as e:
  print ('')
  print ('Error: tmp-output1.tmp was not produced - program execution likely failed!')
  exit(1)

try:
  log=f.read()
  f.close()
except Exception as e:
  print ('')
  print ('Error: can\'t read tmp-output1.tmp!')
  exit(1)

#######################################
print ('Loading tmp-output2.tmp ...')

err=''

try:
  f=open('tmp-output2.tmp', 'r')
except Exception as e:
  print ('')
  print ('Error: tmp-output2.tmp was not produced - program execution likely failed!')
  exit(1)

try:
  err=f.read()
  f.close()
except Exception as e:
  print ('')
  print ('Error: can\'t read tmp-output2.tmp!')
  exit(1)

#######################################
print ('Loading wa_output/results.json ...')

try:
  f=open('wa_output/results.json', 'r')
except Exception as e:
  print ('')
  print ('Error: war_output/results.json was not produced - program execution likely failed!')
  exit(1)

try:
  sresults=f.read()
  f.close()
except Exception as e:
  print ('')
  print ('Error: can\'t read wa_output/results.json!')
  exit(1)

#######################################
results=json.loads(sresults)

# Searching 1 execution time
ttp=0

for x in results:
    metrics=x.get('metrics',[])
    for m in metrics:
        if m.get('name','')=='execution_time':
           ttp=m['value']
           break

if ttp!=0:
   d['execution_time']=ttp
   d['execution_time_kernel_0']=ttp

d['results']=results
d['log_stdout']=log
d['log_stderr']=err

# Write CK json
f=open('tmp-ck-timer.json','wt')
f.write(json.dumps(d, indent=2, sort_keys=True)+'\n')
f.close()
