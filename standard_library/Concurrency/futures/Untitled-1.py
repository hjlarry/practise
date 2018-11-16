#%% [markdown]
# ## Using map() with a Basic Thread Pool

#%%
from concurrent import futures
import threading
import time
import os

def task(n):
    return (n, os.getpid())

ex = futures.ProcessPoolExecutor(max_workers=2)
results = ex.map(task , range(5,0,-1))
for n, pid in results:
    print(f'ran task{n} in {pid}')


#%%
import signal

with futures.ProcessPoolExecutor(max_workers=2) as ex:
    print('getting the pid for one worker')
    f1 = ex.submit(os.getpid)
    pid1 = f1.result()
    
    print('killing process ', pid1)
    os.kill(pid1, signal.SIGHUP)
    
    print('submiting another task')
    f2 = ex.submit(os.getpid)
    try:
        pid2 = f2.result()
    except futures.process.BrokenProcessPool as e:
        print('could not start new tasks ', e)


