#!/usr/bin/python3

import simpy
import itertools
from numpy import random


RANDOM_SEED = 42
RADIO_SIZE = 2

TX_BYTES = [0, 100]
T_INTER = [30, 300]        # Create a car every [min, max] seconds
SIM_TIME = 1000            # Simulation time in seconds


def ue_gen():
  i = random.randint(0,2)
  return(i)

def rach(env):
  while True:
    i = ue_gen()

    print("Time now:", env.now, "value:", i)
    yield env.timeout(1)

env = simpy.Environment()

env.process(rach(env))
env.run(until=20)

"""
def ue(name, env, base_station, radio_res):
  tx_bytes = random.randint(*TX_BYTES)
  
  with base_station.request() as req:
    start = env.now
    # Request one of the gas pumps
    yield req

    yield radio_res.get()

    # The "actual" refueling process takes some time
    yield env.timeout(bytes_sent / REFUELING_SPEED)

    print('%s finished refueling in %.1f seconds.' % (name, env.now-start))


def base_station_control(env, radio_res):

  while True:
    if radio_res.level / radio_res.capacity * 100 < THRESHOLD:
      # We need to call the tank truck now!
      print('Calling tank truck at %d' % env.now)
      # Wait for the tank truck to arrive and refuel the station
      yield env.process(tank_truck(env, radio_res))

    yield env.timeout(10)  # Check every 10 seconds


def ue_gen(env, base_station):
  for i in itertools.count():
    yield env.timeout(random.randint(*T_INTER))
    env.process(ue('UE %d' % i, env, base_station))


# Setup and start the simulation
print('Gas Station refuelling')
random.seed(RANDOM_SEED)

# Create environment and start processes
env = simpy.Environment()
base_station = simpy.Resource(env, 2)
radio_res = simpy.Container(env, RADIO_SIZE)
env.process(base_station_control(env, radio_res))
env.process(ue_gen(env, base_station, radio_res))

# Execute!
env.run(until=SIM_TIME)
"""