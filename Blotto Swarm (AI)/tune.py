import spsa
import grader
import strategy
import copy
import numpy as np
import matplotlib.pyplot as plt
import time

def loss(strat1, strat2):
    _grader = grader.BlottoSwarmGrader(num_games=4)
    seed = time.time_ns()
    results = _grader.grade_spsa(strategy1=strat1, strategy2=strat2)
    print(results)
    return [-results[0] / (results[0] + results[1]), -results[1] / (results[0] + results[1])]

spsa_iters = 900
spsa_alpha = 0.602
spsa_gamma = 0.101
spsa_A = 90
spsa_c = np.array([0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.002, 0.002, 0.01, 0.01, 0.01, 0.08, 16])
spsa_a = np.array([0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.04, 0.008, 0.008, 0.04, 0.04, 0.04, 0.32, 64])
params_max = np.array([100, 100, 100, 100, 100, 100, 100, 1, 1, 100, 100, 100, 100, 1000])

def spsa():
  strategy.isLocal = True
  strategy.needDoubleStorage = True
  theta = strategy.params
  theta_prev = copy.deepcopy(theta)
  theta_history = [[] for i in range(len(theta))]
  l_history = []
  time = []
  for i in range(1, spsa_iters+1):
     a_k = spsa_a/((i+spsa_A)**spsa_alpha)
     c_k = spsa_c/(i**spsa_gamma)

     d = 2*np.random.binomial(size=len(strategy.params), n=1, p=0.5)-1
    #  d *= 10
    #  d[3] *= 0.1
     
     theta_p = theta + c_k * d #* 0.1
     theta_m = theta - c_k * d #* 0.1
     theta_p = np.minimum(theta_p, params_max)
     theta_m = np.minimum(theta_m, params_max)
     print(theta_p)
     print(theta_m)

     strategy.params_spsa_p = theta_p
     strategy.params_spsa_m = theta_m

     y0 = loss(strategy.strategy_spsa_p, strategy.strategy_spsa_m)
    #  print(y0)
     
     ghat = (y0[0] - y0[1]) / (2*c_k*d)
     for j in range(len(ghat)):
        if np.isnan(ghat[j]) or np.isinf(ghat[j]):
           ghat[j] = 0
     theta = theta - a_k * ghat
     theta = np.minimum(theta, params_max)
     
     print(list(theta))
     print(i)
     if(i % 50 == 0):
      print(i)
      print(list(theta))
      print(theta_prev)

      strategy.params_spsa_p = theta
      strategy.params_spsa_m = theta_prev
      # theta_prev = copy.deepcopy(theta)
      _grader = grader.BlottoSwarmGrader(num_games=1)
      l = _grader.grade_spsa(strategy1=strategy.strategy_spsa_p, strategy2=strategy.strategy_spsa_m)
      print(l)

      time.append(i)
      l_history.append(l[0] / (l[0] + l[1]))
      for j in range(len(theta)):
          theta_history[j].append(theta[j])
      plt.plot(time, l_history)
      plt.savefig("tune.png")
      plt.clf()

spsa()
print("yay")





