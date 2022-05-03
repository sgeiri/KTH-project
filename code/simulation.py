#!/usr/bin/python3

import simpy
import itertools
import pandas as pd
from numpy import random

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# ENV variables
# NUM_UE is the number of devices in the simulation environment
NUM_UE = 1000

# SIM_TIME the number of iteration over the simulation
# one unit is one millisecond i.e. one TTI - not yet
SIM_TIME = 10000

# AVG_IDLE is the average time between transmissions
# It is set to 5 minuttes or 300.000 ms
AVG_IDLE = 300

# AVG_BYTES is the average number of bytes transmitted per session
AVG_BYTES = 4e3

# AVG_TX is the average number of bytes transmitted per TTI
TX_AVG = 1000
TX_VAR = 20


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# MEAS VARIABLES
progRes = pd.DataFrame(columns=['ts','ue','txBytes','remainBytes','state'])

# UE's generated unconnected with exponentially distributed waiting time
# the average waiting time is 1 hour i.e. the device sends every hour some data
# NOTE: one constraint could be minimum 1 hour between transmissions
ueBase = { i :{'state':'idle', 'nextTx':round(random.exponential(AVG_IDLE)), 'txBytes':0} for i in range(NUM_UE) }

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# ue trying to connect to the RACH, it is here the collision
# is simulated, catched and registered
def ueRach(env, ueBase, progRes):
  rachAvail = 0

  # Pulling out the ue's trying to connect
  kList = [k for k, v in ueBase.items() if v['nextTx']==env.now and v['state']=='idle']
  random.shuffle(kList)

  for k in kList:
    if (rachAvail==0):
      rachAvail = 1
      ueBase[k]['state'] = 'rach'
      progRes.loc[len(progRes)] = [env.now, k, None, None, 'rach']
    else:
      progRes.loc[len(progRes)] = [env.now, k, None, None, 'collision']

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# ue connected to the RACH in last run, changing state and setting up
# the session parameters
def ueCon(env, ueBase, progRes):
  kList = [k for k, v in ueBase.items() if v['state']=='rach']

  for k in kList:
    ueBase[k]['state'] = 'connected'
    ueBase[k]['txBytes'] = round(random.exponential(AVG_BYTES))
    progRes.loc[len(progRes)] = [env.now, k, None, ueBase[k]['txBytes'], 'connected']

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# here the txBytes are transmitted and reduced until all are sent
# and the ue can change to idle state
def ueTx(env, ueBase, progRes):
  kList = [k for k, v in ueBase.items() if v['state']=='connected']

  for k in kList:
    tx = max(0, round(random.normal(TX_AVG, TX_AVG)))
    ueBase[k]['txBytes'] = max(0, ueBase[k]['txBytes']-tx)
    progRes.loc[len(progRes)] = [env.now, k, tx, ueBase[k]['txBytes'], 'connected']
    
    if (ueBase[k]['txBytes']==0):
      ueBase[k]['state'] = 'idle'
      ueBase[k]['nextTx'] = round(random.exponential(AVG_IDLE))
      progRes.loc[len(progRes)] = [env.now, k, None, None, 'idle']

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# SIMULATION environment
def simEnv(env, ueBase, progRes):
  while True:
    ueCon(env, ueBase, progRes)
    ueRach(env, ueBase, progRes)

    ueTx(env, ueBase, progRes)

    yield env.timeout(1)

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
env = simpy.Environment()

env.process(simEnv(env, ueBase, progRes))
env.run(until=SIM_TIME)

