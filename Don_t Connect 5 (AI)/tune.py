import bot.greedy_bot_move
import bot.strategy
import spsa
import hex_func
import bot.strategy as strategy
import bot.random_bot_move
import copy
import numpy as np
import matplotlib.pyplot as plt
import time
import json
import os

def loss():
    results = hex_func.run_game({"random":bot.strategy.spsa_pass, "spsa_p":bot.strategy.spsa_p, "spsa_m":bot.strategy.spsa_m})
    # gameid = str(time.time())
    # path = os.path.join("games", gameid + ".json")
    # with open(path, "w") as writer:
    #   json.dump(results, writer)
    results = results["scores"]
    print(results)
    if(results == [0, 0, 0]):
       return [0, 0]
    return [-results[1] / (results[1] + results[2]), -results[2] / (results[1] + results[2])]

spsa_iters = 10000
spsa_alpha = 0.602
spsa_gamma = 0.101
spsa_A = 1000
spsa_c = 0.2
spsa_a = 0.2

def spsa():
  theta = strategy.params
  theta_prev = copy.deepcopy(theta)
  theta_history = [[] for i in range(len(theta))]
  l_history = []
  _iters = []
  for i in range(1, spsa_iters+1):
     a_k = spsa_a/((i+spsa_A)**spsa_alpha)
     c_k = spsa_c/(i**spsa_gamma)

     d = 2*np.random.binomial(size=len(strategy.params), n=1, p=0.5)-1
    #  d *= 10
    #  d[3] *= 0.1

     theta_p = theta + c_k * d #* 0.1
     theta_m = theta - c_k * d #* 0.1

     strategy.spsa_p_params = theta_p
    #  print(theta_p)
     strategy.spsa_m_params = theta_m
    
     y0 = loss()
    #  print(y0)

     ghat = (y0[0] - y0[1]) / (2*c_k*d)
     theta = theta - a_k * ghat
     
    #  print(list(theta))
     if(i % 50 == 0):
      print("PROGRESS:" + str(i))
      print(list(theta))

      strategy.spsa_p_params = theta
      strategy.spsa_m_params = theta_prev
      # theta_prev = copy.deepcopy(theta)
      l = [0, 0, 0]
      for j in range(5):
        curr = hex_func.run_game_spsa({"pass":bot.random_bot_move.random_bot_move, "spsa_p":bot.strategy.spsa_p, "spsa_m":bot.strategy.spsa_m})
        l = [l[0]+curr[0], l[1]+curr[1], l[2]+curr[2]]
      print(l)

      _iters.append(i)
      l_history.append(l[1] / (l[1] + l[2]))
      for j in range(len(theta)):
          theta_history[j].append(theta[j])
      plt.plot(_iters, l_history)
      plt.savefig("tune.png")
      plt.clf()

spsa()
print("yay")





