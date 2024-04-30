"""
Edit this file! This is the file you will submit.
"""

import random
import math
import copy
import time

"""
NOTE: Each soldier's memory in the final runner will be separate from the others.

WARNING: Do not print anything to stdout. It will break the grading script!
"""
params = [0.4351517611523791, 0.7833879317888328, 0.49178275867633003, 1.3233627449469976, 0.6488581609787087, 0.8544959747933414, 1.1008355060526755, 0.8703594078226374, 0.8330922507096964, 0.44744366524947554, 0.4849963315571727, 1.118757416408244, 1.2, 50]
# params = [1] * 9
isLocal = False
needDoubleStorage = False

def random_strategy(ally: list, enemy: list, offset: int) -> int:
    # A random strategy to use in your game
    return random.randint(-1, 1)

params_spsa_p = [-0.12212150262650567, 0.5266190087763135, 0.06393862176318527, 0.8279598450108844, 0.9555628540109334, 1.3389070401374379, 1.3318860184599657, -0.32880006806825857, 0.243816257747022]
params_spsa_m = [0.3928440446748247, 0.7836039594976211, 0.6, 1.3686080743435067, 0.7293341776305587, 1.0334895406418478, 1.045303899621579, 0.95, 0.95]

def strategy_spsa_p(ally: list, enemy: list, offset: int):
  return dev(ally, enemy, offset, params_spsa_p)

def strategy_spsa_m(ally: list, enemy: list, offset: int):
  return dev(ally, enemy, offset, params_spsa_m)

dev_storage = [[[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, 0] for i in range(60 * (needDoubleStorage + 1))]

dev_sld_id = 0

def dev(ally: list, enemy: list, offset: int, dev_params = [0.4351517611523791, 0.7833879317888328, 0.49178275867633003, 1.3233627449469976, 0.6488581609787087, 0.8544959747933414, 1.1008355060526755, 0.8703594078226374, 0.8330922507096964, 0.44744366524947554, 0.4849963315571727, 1.118757416408244]):
  #V0.1 Score against gen8 at 4/24 9:20PM After 0.95 instead of 1 stability required to trigger hard-coded isntructions: 152.5-57.5   +169 (+/-53) elo
  #V0.2 Score against V0.1 at 4/25 4:06PM After fixing SPSA: 87.5-12.5   +338 (+/-112) elo
  #V0.3 After adding more hardcode - elo gain negligible
  #V0.4 Score against V0.3 at 4/25 7:54PM After more hardcode (if at castle and all castles which we have info are we are outnumbered, head towards the one we are least outnumbered on)    155.0-45.0    +215(+/-59) elo
  #V0.5 Score against V0.4 at 4/25 10:35PM After account for opponent move   132-68  +115(+/-51) elo
  #V0.6 Score against V0.5 at 4/28 10:16AM after Return offset on move 1 and set original stab_denom to max(old, new)  193.5-148.5  +46 (+/-37) elo
  #V0.7 Score against V0.6 at 4/28 12:01PM after more SPSA: 68.5-31.5   +135(+/-75) elo
  #V0.8 Score against V0.7 at 4/28 5:36PM after account for enemy on nearest castle:   64.5-35.5   +104(+/-72) elo
  #V0.9 Score against V0.8 at 4/28 7:22PM after opponent stability + tune    175-125  +58(+/-40) elo
  #V0.10 Score against V0.9 at 4/29 9:08PM after factor in neighbor positions when calculating value   117-83   +60(+/-49) elo
  global dev_sld_id
  global isLocal
  global needDoubleStorage

  action_scores = [0, 0, 0]

  castle_pos = [i for i in range(7) if (i % 3) == (offset % 3)]

  enemy.append(0) #both 6+1 and 0-1 refrence this

  ally_soldiers = []
  enemy_soldiers = []
  for i in range(7):
     for j in range(ally[i]):
        ally_soldiers.append([0, i])
     for j in range(enemy[i]):
        enemy_soldiers.append([0, i])

  random.shuffle(ally_soldiers)

  stability = [0] * 7
  stab_denom = [0] * 7
  for i in range(7):
    index_old = i + dev_storage[dev_sld_id][2]
    if(index_old >= 0 and index_old <= 6):
      val = min(dev_storage[dev_sld_id][0][index_old], ally[i])
      for j in range(7):
        stability[j] += val * dev_params[4]**abs(i-j)
        stab_denom[j] += max(dev_storage[dev_sld_id][0][index_old], ally[i]) * dev_params[4]**abs(i-j)
  opp_stability = [0] * 7
  opp_stab_denom = [0] * 7
  for i in range(7):
    index_old = i + dev_storage[dev_sld_id][2]
    if(index_old >= 0 and index_old <= 6):
      val = min(dev_storage[dev_sld_id][1][index_old], enemy[i])
      for j in range(7):
        opp_stability[j] += val * dev_params[4]**abs(i-j)
        opp_stab_denom[j] += max(dev_storage[dev_sld_id][1][index_old], enemy[i]) * dev_params[4]**abs(i-j)
  # print(stability)
  grouped = [0] * 7
  grouped_denom = [0] * 7
  total = 0
  for i in range(7):
    total += ally[i]
  for i in range(7):
    for j in range(7):
      grouped[i] += ((abs(ally[j] - total / 7))**2) * abs(i-j)

  dev_storage[dev_sld_id][0] = copy.deepcopy(ally)
  dev_storage[dev_sld_id][1] = copy.deepcopy(enemy)

    # for j in range(7):
    #   if(final_action == 0):
    #     stability[j] += dev_params[5]**abs(i-j)
    #   stab_denom[j] += dev_params[5]**abs(i-j)
  
  # enemy[3 + offset] += 0.5 * (enemy[2 + offset] + enemy[4 + offset])
  # enemy[0 + offset] += 0.5 * (enemy[1 + offset] + enemy[-1 + offset])
  # enemy[0 + offset] += 0.5 * (enemy[1 + offset] + enemy[-1 + offset])

  # choices = []
  # probs = []
  # for i in range(1, ally[3] + 1):
  #   choices.append(i)
  #   final_stability = 0
  #   if(stab_denom[3] == 0):
  #     final_stability = 1
  #   else:
  #     final_stability = stability[3] / stab_denom[3]
  #   probs.append(((final_stability*dev_params[12] + dev_params[13]) / dev_params[13]) ** i)
    # probs.append(1)
  sol_num = random.randint(1, ally[3])
  # sol_num = random.choices(choices, weights=probs)[0]
  curr_sol_num = 0
  
  index = 0

  ally_left = copy.deepcopy(ally)

  while curr_sol_num < sol_num:
    
    action_scores = [0.0, 0.0, 0.0]
    pos = ally_soldiers[index][1]

    for i in castle_pos:
      final_stability = 0
      if(stab_denom[i] + opp_stab_denom[i] == 0):
        final_stability = 1
      else:
        final_stability = (stability[i] + opp_stability[i]) / (stab_denom[i] + opp_stab_denom[i])
      num_ally_sols = ally[i]
      num_enemy_sols = enemy[i]
      if(i-1 >= 0):
        num_ally_sols += dev_params[9] * ally_left[i-1]
        num_enemy_sols += dev_params[10] * enemy[i-1]
      if(i+1 <= 6):
        num_ally_sols += dev_params[9] * ally_left[i+1]
        num_enemy_sols += dev_params[10] * enemy[i+1]
      val = ((num_enemy_sols >= num_ally_sols)*(final_stability)*dev_params[3] + 1) * (dev_params[0] ** max(abs(num_ally_sols - num_enemy_sols), dev_params[1])) * (dev_params[2] ** (abs(i - pos)))
      if i == pos:
        if(enemy[3] > num_ally_sols):
          action_scores[1] -= 0.01 * 1.3 ** ally[3]
        action_scores[0] -= val
        action_scores[2] -= val
      elif i < pos:
        action_scores[0] += val
        action_scores[2] -= val
      elif i > pos:
        action_scores[0] -= val
        action_scores[2] += val

    final_stability = 0
    if(stab_denom[3] == 0):
      final_stability = 1
    else:
      final_stability = stability[3] / stab_denom[3]
    if(pos == 3 and 3 in castle_pos and enemy[3] > ally[3] and final_stability >= dev_params[7]):
      if(enemy[6] - ally[6] >= 0 and enemy[6] - ally[6] >= enemy[0] - ally[0]):
        action_scores[2] = 100000
      elif(enemy[0] - ally[0] >= 0 and enemy[0] - ally[0] >= enemy[6] - ally[6]):
        action_scores[0] = 100000
    if(pos == 3 and 3 in castle_pos and ally[3] - 1 > enemy[3] and enemy[6] >= ally[6] and stability[3] == stab_denom[3] and enemy[2] == 0 and enemy[4] == 0):
      action_scores[2] = 100000
    if(pos == 3 and 3 in castle_pos and ally[3] - 1 > enemy[3] and enemy[0] >= ally[0] and final_stability >= dev_params[8]):
      action_scores[0] = 100000
      action_scores[2] = 0
    # print(action_scores)
    final_action = max(enumerate(action_scores), key=lambda x: x[1])[0] - 1

    ally[pos] -= dev_params[6]
    ally_left[pos] -= dev_params[11]
    if (pos + final_action >= 0) and (pos + final_action <= 6):
      ally[pos + final_action] += dev_params[6]

    for j in range(7):
      if(final_action == 0):
        stability[j] += dev_params[5]*dev_params[4]**abs(i-j)
      stab_denom[j] += dev_params[5]*dev_params[4]**abs(i-j)
      
    if(pos == 3):
       curr_sol_num += 1
    index += 1
  # print(str(action_scores) + " " + str(ally))

  if(dev_storage[dev_sld_id][3] == 0):
    final_action = offset
  dev_storage[dev_sld_id][2] = final_action
  dev_storage[dev_sld_id][3] += 1
  dev_storage[dev_sld_id][3] = dev_storage[dev_sld_id][3] % 100
  if(isLocal):
    if len(dev_storage) < (needDoubleStorage * 60 + 60):
      for i in range((needDoubleStorage * 60 + 60) - len(dev_storage)):
        dev_storage.append([[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, 0])
    dev_sld_id += 1
    dev_sld_id = dev_sld_id % (60 * (needDoubleStorage + 1))

  return final_action

base_storage = [[[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, 0] for i in range(60 * (needDoubleStorage + 1))]

base_sld_id = 0

def base(ally: list, enemy: list, offset: int, base_params = [0.4351517611523791, 0.7833879317888328, 0.49178275867633003, 1.3233627449469976, 0.6488581609787087, 0.8544959747933414, 1.1008355060526755, 0.8703594078226374, 0.8330922507096964, 0.44744366524947554, 0.4849963315571727, 1.118757416408244]):
  #V0.1 Score against gen8 at 4/24 9:20PM After 0.95 instead of 1 stability required to trigger hard-coded isntructions: 152.5-57.5   +169 (+/-53) elo
  #V0.2 Score against V0.1 at 4/25 4:06PM After fixing SPSA: 87.5-12.5   +338 (+/-112) elo
  #V0.3 After adding more hardcode - elo gain negligible
  #V0.4 Score against V0.3 at 4/25 7:54PM After more hardcode (if at castle and all castles which we have info are we are outnumbered, head towards the one we are least outnumbered on)    155.0-45.0    +215(+/-59) elo
  #V0.5 Score against V0.4 at 4/25 10:35PM After account for opponent move   132-68  +115(+/-51) elo
  #V0.6 Score against V0.5 at 4/28 10:16AM after Return offset on move 1 and set original stab_denom to max(old, new)  193.5-148.5  +46 (+/-37) elo
  #V0.7 Score against V0.6 at 4/28 12:01PM after more SPSA: 68.5-31.5   +135(+/-75) elo
  #V0.8 Score against V0.7 at 4/28 5:36PM after account for enemy on nearest castle:   64.5-35.5   +104(+/-72) elo
  #V0.9 Score against V0.8 at 4/28 7:22PM after opponent stability + tune    175-125  +58(+/-40) elo
  #V0.10 Score against V0.9 at 4/29 9:08PM after factor in neighbor positions when calculating value   117-83   +60(+/-49) elo
  global base_sld_id
  global isLocal
  global needDoubleStorage

  action_scores = [0, 0, 0]

  castle_pos = [i for i in range(7) if (i % 3) == (offset % 3)]

  enemy.append(0) #both 6+1 and 0-1 refrence this

  ally_soldiers = []
  enemy_soldiers = []
  for i in range(7):
     for j in range(ally[i]):
        ally_soldiers.append([0, i])
     for j in range(enemy[i]):
        enemy_soldiers.append([0, i])

  random.shuffle(ally_soldiers)

  stability = [0] * 7
  stab_denom = [0] * 7
  for i in range(7):
    index_old = i + base_storage[base_sld_id][2]
    if(index_old >= 0 and index_old <= 6):
      val = min(base_storage[base_sld_id][0][index_old], ally[i])
      for j in range(7):
        stability[j] += val * base_params[4]**abs(i-j)
        stab_denom[j] += max(base_storage[base_sld_id][0][index_old], ally[i]) * base_params[4]**abs(i-j)
  opp_stability = [0] * 7
  opp_stab_denom = [0] * 7
  for i in range(7):
    index_old = i + base_storage[base_sld_id][2]
    if(index_old >= 0 and index_old <= 6):
      val = min(base_storage[base_sld_id][1][index_old], enemy[i])
      for j in range(7):
        opp_stability[j] += val * base_params[4]**abs(i-j)
        opp_stab_denom[j] += max(base_storage[base_sld_id][1][index_old], enemy[i]) * base_params[4]**abs(i-j)
  # print(stability)
  grouped = [0] * 7
  grouped_denom = [0] * 7
  total = 0
  for i in range(7):
    total += ally[i]
  for i in range(7):
    for j in range(7):
      grouped[i] += ((abs(ally[j] - total / 7))**2) * abs(i-j)

  base_storage[base_sld_id][0] = copy.deepcopy(ally)
  base_storage[base_sld_id][1] = copy.deepcopy(enemy)

    # for j in range(7):
    #   if(final_action == 0):
    #     stability[j] += base_params[5]**abs(i-j)
    #   stab_denom[j] += base_params[5]**abs(i-j)
  
  # enemy[3 + offset] += 0.5 * (enemy[2 + offset] + enemy[4 + offset])
  # enemy[0 + offset] += 0.5 * (enemy[1 + offset] + enemy[-1 + offset])
  # enemy[0 + offset] += 0.5 * (enemy[1 + offset] + enemy[-1 + offset])

  sol_num = random.randint(1, ally[3])
  curr_sol_num = 0
  
  index = 0

  ally_left = copy.deepcopy(ally)

  while curr_sol_num < sol_num:
    
    action_scores = [0.0, 0.0, 0.0]
    pos = ally_soldiers[index][1]

    for i in castle_pos:
      final_stability = 0
      if(stab_denom[i] + opp_stab_denom[i] == 0):
        final_stability = 1
      else:
        final_stability = (stability[i] + opp_stability[i]) / (stab_denom[i] + opp_stab_denom[i])
      num_ally_sols = ally[i]
      num_enemy_sols = enemy[i]
      if(i-1 >= 0):
        num_ally_sols += base_params[9] * ally_left[i-1]
        num_enemy_sols += base_params[10] * enemy[i-1]
      if(i+1 <= 6):
        num_ally_sols += base_params[9] * ally_left[i+1]
        num_enemy_sols += base_params[10] * enemy[i+1]
      val = ((enemy[i] >= ally[i])*(final_stability)*base_params[3] + 1) * (base_params[0] ** max(abs(num_ally_sols - num_enemy_sols), base_params[1])) * (base_params[2] ** (abs(i - pos)))
      if i == pos:
        action_scores[0] -= val
        action_scores[2] -= val
      elif i < pos:
        action_scores[0] += val
        action_scores[2] -= val
      elif i > pos:
        action_scores[0] -= val
        action_scores[2] += val

    final_stability = 0
    if(stab_denom[3] == 0):
      final_stability = 1
    else:
      final_stability = stability[3] / stab_denom[3]
    if(pos == 3 and 3 in castle_pos and enemy[3] > ally[3] and final_stability >= base_params[7]):
      if(enemy[6] - ally[6] >= 0 and enemy[6] - ally[6] >= enemy[0] - ally[0]):
        action_scores[2] = 100000
      elif(enemy[0] - ally[0] >= 0 and enemy[0] - ally[0] >= enemy[6] - ally[6]):
        action_scores[0] = 100000
    if(pos == 3 and 3 in castle_pos and ally[3] - 1 > enemy[3] and enemy[6] >= ally[6] and stability[3] == stab_denom[3] and enemy[2] == 0 and enemy[4] == 0):
      action_scores[2] = 100000
    if(pos == 3 and 3 in castle_pos and ally[3] - 1 > enemy[3] and enemy[0] >= ally[0] and final_stability >= base_params[8]):
      action_scores[0] = 100000
      action_scores[2] = 0

    final_action = max(enumerate(action_scores), key=lambda x: x[1])[0] - 1

    ally[pos] -= base_params[6]
    ally_left[pos] -= base_params[11]
    if (pos + final_action >= 0) and (pos + final_action <= 6):
      ally[pos + final_action] += base_params[6]

    for j in range(7):
      if(final_action == 0):
        stability[j] += base_params[5]*base_params[4]**abs(i-j)
      stab_denom[j] += base_params[5]*base_params[4]**abs(i-j)
      
    if(pos == 3):
       curr_sol_num += 1
    index += 1
  # print(str(action_scores) + " " + str(ally))

  if(base_storage[base_sld_id][3] == 0):
    final_action = offset
  base_storage[base_sld_id][2] = final_action
  base_storage[base_sld_id][3] += 1
  base_storage[base_sld_id][3] = base_storage[base_sld_id][3] % 100
  if(isLocal):
    if len(base_storage) < (needDoubleStorage * 60 + 60):
      for i in range((needDoubleStorage * 60 + 60) - len(base_storage)):
        base_storage.append([[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0, 0])
    base_sld_id += 1
    base_sld_id = base_sld_id % (60 * (needDoubleStorage + 1))

  return final_action

gen8_storage = [[[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0] for i in range(60 * (needDoubleStorage + 1))]

gen8_sld_id = 0

def gen8(ally: list, enemy: list, offset: int, gen8_params = [0.5098840647444923, 0.733569853474559, 0.44973769163216587, 1.2966552749525806, 0.6428900882041341, 0.8496326082129316, 1.1074458423132096]):
  #V0.1 Score against gen7 at 4/23 9:50PM After bugfix for hard-coded instructions: 181.5-117.5  +76 (+/-40) elo
  #V0.2 Score against V0.1 at 4/24 2:45PM After another SPSA tune with more parameters and some not sensible parameter values manually reverted
  #     (my SPSA is probably very broken lol but it's kinda working so idk): 182.5-117.5   +76 (+/-40) elo
  global gen8_sld_id

  action_scores = [0, 0, 0]

  castle_pos = [i for i in range(7) if (i % 3) == (offset % 3)]

  enemy.append(0) #both 6+1 and 0-1 refrence this

  ally_soldiers = []
  enemy_soldiers = []
  for i in range(7):
     for j in range(ally[i]):
        ally_soldiers.append([0, i])
     for j in range(enemy[i]):
        enemy_soldiers.append([0, i])

  random.shuffle(ally_soldiers)

  stability = [0] * 7
  stab_denom = [0] * 7
  for i in range(7):
    index_old = i + gen8_storage[gen8_sld_id][2]
    if(index_old >= 0 and index_old <= 6):
      val = min(gen8_storage[gen8_sld_id][0][index_old], ally[i])
      for j in range(7):
        stability[j] += val * gen8_params[5]**abs(i-j)
        stab_denom[j] += gen8_storage[gen8_sld_id][0][index_old] * gen8_params[5]**abs(i-j)
  # print(stability)

  gen8_storage[gen8_sld_id][0] = copy.deepcopy(ally)
  gen8_storage[gen8_sld_id][1] = copy.deepcopy(enemy)

    # for j in range(7):
    #   if(final_action == 0):
    #     stability[j] += gen8_params[5]**abs(i-j)
    #   stab_denom[j] += gen8_params[5]**abs(i-j)

  sol_num = random.randint(1, ally[3])
  curr_sol_num = 0

  enemy[3] += 0.5 * (enemy[2] + enemy[4])

  index = 0

  while curr_sol_num < sol_num:
    action_scores = [0.0, 0.0, 0.0]
    pos = ally_soldiers[index][1]

    for i in castle_pos:
      final_stability = 0
      if(stab_denom[i] == 0):
        final_stability = 1
      else:
        final_stability = stability[i] / stab_denom[j]

      val = ((enemy[i] >= ally[i])*(final_stability)*gen8_params[3] + 1) * (gen8_params[0] ** max(abs(ally[i] - enemy[i]), gen8_params[1])) * (gen8_params[2] ** abs(i - pos))
      if i == pos:
        action_scores[0] -= val
        action_scores[2] -= val
      elif i < pos:
        action_scores[0] += val
        action_scores[2] -= val
      elif i > pos:
        action_scores[0] -= val
        action_scores[2] += val

    if(pos == 3 and 3 in castle_pos and enemy[3] > ally[3] and stability[3] == stab_denom[3]):
      if(enemy[6] - ally[6] >= 0 and enemy[6] - ally[6] >= enemy[0] - ally[0]):
        action_scores[2] = 100000
      elif(enemy[0] - ally[0] >= 0 and enemy[0] - ally[0] >= enemy[6] - ally[6]):
        action_scores[0] = 100000
    if(pos == 3 and 3 in castle_pos and ally[3] - 1 > enemy[3] and enemy[0] >= ally[0] and stability[3] == stab_denom[3]):
      action_scores[0] = 100000

    final_action = max(enumerate(action_scores), key=lambda x: x[1])[0] - 1

    ally[pos] -= gen8_params[6]
    if (pos + final_action >= 0) and (pos + final_action <= 6):
      ally[pos + final_action] += gen8_params[6]

    for j in range(7):
      if(final_action == 0):
        stability[j] += gen8_params[5]*gen8_params[4]**abs(i-j)
      stab_denom[j] += gen8_params[5]*gen8_params[4]**abs(i-j)
      
    if(pos == 3):
       curr_sol_num += 1
    index += 1
  # print(str(action_scores) + " " + str(ally))

  gen8_storage[gen8_sld_id][2] = final_action
  if(isLocal):
    gen8_sld_id += 1
    gen8_sld_id %= 60 * (needDoubleStorage + 1)

  return final_action

gen7_storage = [[[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0] for i in range(60 * (needDoubleStorage + 1))]

gen7_sld_id = 0

def gen7(ally: list, enemy: list, offset: int, gen7_params = [0.3902405433900335, 0.7672356797634815, 0.600875314533423, 0.01723663228552476, 1.033691828655783, 0.7689663792627915]):
  #V1 Score against gen6 at 4/23 2:58PM: 127.5-71.5  +100 (+/-51) elo
  #V2 Score against gen6 at 4/23 3:35PM after SPSA tune: 163.5-35.5   +265 (+/-65) elo
  #V3 Score against gen6 at 4/23 4:44PM after longer SPSA tune and cherry-picked set of params from iteration 8950:  183.5-15.5    +429 (+/-97) elo
  #V3 Confirmation run against gen7V2: 130.0-69.0   +110 (+/-51) elo
  global gen7_sld_id

  action_scores = [0, 0, 0]

  castle_pos = [i for i in range(7) if (i % 3) == (offset % 3)]

  ally_soldiers = []
  for i in range(7):
     for j in range(ally[i]):
        ally_soldiers.append([0, i])

  random.shuffle(ally_soldiers)

  stability = [0] * 7
  stab_denom = [0] * 7
  for i in range(7):
    index_old = i + gen7_storage[gen7_sld_id][2]
    if(index_old >= 0 and index_old <= 6):
      val = min(gen7_storage[gen7_sld_id][0][index_old], ally[i])
      for j in range(7):
        stability[j] += val * gen7_params[5]**abs(i-j)
        stab_denom[j] += gen7_storage[gen7_sld_id][0][index_old] * gen7_params[5]**abs(i-j)
  # print(stability)

  gen7_storage[gen7_sld_id][0] = copy.deepcopy(ally)
  gen7_storage[gen7_sld_id][1] = copy.deepcopy(enemy)

  sol_num = random.randint(1, ally[3])
  curr_sol_num = 0

  index = 0

  while curr_sol_num < sol_num:
    action_scores = [0.0, 0.0, 0.0]
    pos = ally_soldiers[index][1]

    for i in castle_pos:
      final_stability = 0
      if(stab_denom[i] == 0):
        final_stability = 1
      else:
        final_stability = stability[i] / stab_denom[j]

      val = ((enemy[i] >= ally[i])*(final_stability)*gen7_params[4] + 1) * (gen7_params[0] ** max(abs(ally[i] - enemy[i]), gen7_params[1])) * (((gen7_params[2] + final_stability*gen7_params[3]) / (1 + final_stability*gen7_params[3])) ** abs(i - pos))
      if i == pos:
        action_scores[0] -= val
        action_scores[2] -= val
      elif i < pos:
        action_scores[0] += val
        action_scores[2] -= val
      elif i > pos:
        action_scores[0] -= val
        action_scores[2] += val

    if(pos == 3 and 3 in castle_pos and enemy[3] > ally[3] and enemy[6] >= ally[6] and stability[3] == stab_denom[3]):
      action_scores[2] = 100000
    if(pos == 3 and 3 in castle_pos and ally[3] - 1 > enemy[3] and enemy[0] >= ally[0] and stability[3] == stab_denom[3]):
      action_scores[0] = 100000

    final_action = max(enumerate(action_scores), key=lambda x: x[1])[0] - 1

    ally[pos] -= 1
    if (pos + final_action >= 0) and (pos + final_action <= 6):
      ally[pos + final_action] += 1

    for j in range(7):
      if(final_action == 0):
        stability[j] += gen7_params[5]**abs(i-j)
      stab_denom[j] += gen7_params[5]**abs(i-j)
      
    if(pos == 3):
       curr_sol_num += 1
    index += 1
  # print(str(action_scores) + " " + str(ally))

  gen7_storage[gen7_sld_id][2] = final_action
  if(isLocal):
    gen7_sld_id += 1
    gen7_sld_id %= 60 * (needDoubleStorage + 1)

  return final_action

gen6_storage = [[[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0] for i in range(60 * (needDoubleStorage + 1))]

gen6_sld_id = 0

def gen6(ally: list, enemy: list, offset: int, gen6_params = [0.5118766689257184, 0.4339071582948457, 0.5106516576611354, 1, 1]):
  #Score against gen5 at 4/23 1:49PM: [148.0, 51.0] +185 (+/-56) elo

  global gen6_sld_id

  action_scores = [0, 0, 0]

  castle_pos = [i for i in range(7) if (i % 3) == (offset % 3)]

  soldiers = []
  for i in range(7):
     for j in range(ally[i]):
        soldiers.append([0, i])

  random.shuffle(soldiers)

  left_stability = 0
  right_stability = 0
  left_stability_denominator = 0
  right_stability_denominator = 0
  for i in range(7):
    index_old = i + gen6_storage[gen6_sld_id][2]
    if(index_old >= 3 and index_old <= 6):
        right_stability += min(gen6_storage[gen6_sld_id][0][index_old], ally[i])
        right_stability += min(gen6_storage[gen6_sld_id][1][index_old], enemy[i])
        right_stability_denominator += gen6_storage[gen6_sld_id][0][index_old]
        right_stability_denominator += gen6_storage[gen6_sld_id][1][index_old]
    if(index_old <= 3 and index_old >= 0):
        left_stability += min(gen6_storage[gen6_sld_id][0][index_old], ally[i])
        left_stability += min(gen6_storage[gen6_sld_id][1][index_old], enemy[i])
        left_stability_denominator += gen6_storage[gen6_sld_id][0][index_old]
        left_stability_denominator += gen6_storage[gen6_sld_id][1][index_old]
  # print(stability)

  gen6_storage[gen6_sld_id][0] = copy.deepcopy(ally)
  gen6_storage[gen6_sld_id][1] = copy.deepcopy(enemy)

  sol_num = random.randint(1, ally[3])
  curr_sol_num = 0

  index = 0

  while curr_sol_num < sol_num:
    action_scores = [0.0, 0.0, 0.0]
    pos = soldiers[index][1]
    for i in castle_pos:
      final_stability = 0
      if(i > 3):
        if(right_stability_denominator == 0):
          final_stability = 1
        else:
          final_stability = right_stability / right_stability_denominator
      elif(i == 3):
        if(left_stability_denominator + right_stability_denominator == 0):
          final_stability = 1
        else:
          final_stability = (left_stability + right_stability) / (left_stability_denominator + right_stability_denominator) 
      else:
        if(left_stability_denominator == 0):
          final_stability = 1
        else:
          final_stability = left_stability / left_stability_denominator
      val = ((enemy[i] >= ally[i])*(final_stability)*gen6_params[4] + 1) * (gen6_params[0] ** max(abs(ally[i] - enemy[i]), gen6_params[1])) * (((gen6_params[2] + final_stability*gen6_params[3]) / (1 + final_stability*gen6_params[3])) ** abs(i - pos))
      if i == pos:
        action_scores[0] -= val
        action_scores[2] -= val
      elif i < pos:
        action_scores[0] += val
        action_scores[2] -= val
      elif i > pos:
        action_scores[0] -= val
        action_scores[2] += val
    if(3 in castle_pos and enemy[3] > ally[3] and enemy[6] >= ally[6] and left_stability == left_stability_denominator and right_stability == right_stability_denominator):
      action_scores[2] = 100000
    if(3 in castle_pos and ally[3] - 1 > enemy[3] and enemy[0] >= ally[0] and left_stability == left_stability_denominator and right_stability == right_stability_denominator):
      action_scores[0] = 100000
    final_action = max(enumerate(action_scores), key=lambda x: x[1])[0] - 1
    ally[pos] -= 1
    if (pos + final_action >= 0) and (pos + final_action <= 6):
      ally[pos + final_action] += 1
    if (pos > 3):
      if(final_action == 0):
        right_stability += 1
      right_stability_denominator += 1
    elif (pos == 3):
      if(final_action == 0):
        left_stability += 1
        right_stability += 1
      left_stability_denominator += 1
      right_stability_denominator += 1
    else:
      if(final_action == 0):
        left_stability += 1
      left_stability_denominator += 1
      
    if(pos == 3):
       curr_sol_num += 1
    index += 1
  # print(str(action_scores) + " " + str(ally))

  gen6_storage[gen6_sld_id][2] = final_action
  if(isLocal):
    gen6_sld_id += 1
    gen6_sld_id %= 60 * (needDoubleStorage + 1)

  return final_action

gen5_storage = [[[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0] for i in range(60 * (needDoubleStorage + 1))]

gen5_sld_id = 0

def gen5(ally: list, enemy: list, offset: int, gen5_params = [0.5118766689257184, 0.4339071582948457, 0.5106516576611354, 1, 1]):
  global gen5_sld_id

  action_scores = [0, 0, 0]

  castle_pos = [i for i in range(7) if (i % 3) == (offset % 3)]

  soldiers = []
  for i in range(7):
     for j in range(ally[i]):
        soldiers.append([0, i])

  random.shuffle(soldiers)

  left_stability = 0
  right_stability = 0
  left_stability_denominator = 0
  right_stability_denominator = 0
  for i in range(7):
     index_old = i + gen5_storage[gen5_sld_id][2]
     if(index_old > 3 and index_old <= 6):
        right_stability += min(gen5_storage[gen5_sld_id][0][index_old], ally[i])
        right_stability += min(gen5_storage[gen5_sld_id][1][index_old], enemy[i])
        right_stability_denominator += gen5_storage[gen5_sld_id][0][index_old]
        right_stability_denominator += gen5_storage[gen5_sld_id][1][index_old]
     if(index_old <= 3 and index_old >= 0):
        left_stability += min(gen5_storage[gen5_sld_id][0][index_old], ally[i])
        left_stability += min(gen5_storage[gen5_sld_id][1][index_old], enemy[i])
        left_stability_denominator += gen5_storage[gen5_sld_id][0][index_old]
        left_stability_denominator += gen5_storage[gen5_sld_id][1][index_old]

  # print(stability)

  gen5_storage[gen5_sld_id][0] = copy.deepcopy(ally)
  gen5_storage[gen5_sld_id][1] = copy.deepcopy(enemy)

  sol_num = random.randint(1, ally[3])
  curr_sol_num = 0

  index = 0

  while curr_sol_num < sol_num:
    action_scores = [0.0, 0.0, 0.0]
    pos = soldiers[index][1]
    for i in castle_pos:
      final_stability = 0
      if(i > 3):
        if(right_stability_denominator == 0):
          final_stability = 1
        else:
          final_stability = right_stability / right_stability_denominator
      else:
        if(left_stability_denominator == 0):
          final_stability = 1
        else:
          final_stability = left_stability / left_stability_denominator       
      val = ((enemy[i] >= ally[i])*(final_stability)*gen5_params[4] + 1) * (gen5_params[0] ** max(abs(ally[i] - enemy[i]), gen5_params[1])) * (((gen5_params[2] + final_stability*gen5_params[3]) / (1 + final_stability*gen5_params[3])) ** abs(i - pos))
      if i == pos:
        action_scores[0] -= val
        action_scores[2] -= val
      elif i < pos:
        action_scores[0] += val
        action_scores[2] -= val
      elif i > pos:
        action_scores[0] -= val
        action_scores[2] += val
    if(3 in castle_pos and enemy[3] > ally[3] and enemy[6] > ally[6] and left_stability == left_stability_denominator and right_stability == right_stability_denominator):
      action_scores[2] = 100000
    final_action = max(enumerate(action_scores), key=lambda x: x[1])[0] - 1
    ally[pos] -= 1
    if (pos + final_action >= 0) and (pos + final_action <= 6):
      ally[pos + final_action] += 1
    if (pos > 3):
      if(final_action == 0):
        right_stability += 1
      right_stability_denominator += 1
    else:
      if(final_action == 0):
        left_stability += 1
      left_stability_denominator += 1
      
    if(pos == 3):
       curr_sol_num += 1
    index += 1
  # print(str(action_scores) + " " + str(ally))

  gen5_storage[gen5_sld_id][2] = final_action
  if(isLocal):
    gen5_sld_id += 1
    gen5_sld_id %= 60 * (needDoubleStorage + 1)

  return final_action

gen4_storage = [[[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0] for i in range(60 * (needDoubleStorage + 1))]

gen4_sld_id = 0

def gen4(ally: list, enemy: list, offset: int, gen4_params = [0.5118766689257184, 0.4339071582948457, 0.5106516576611354, 1, 1]):
  global gen4_sld_id

  action_scores = [0, 0, 0]

  castle_pos = [i for i in range(7) if (i % 3) == (offset % 3)]

  soldiers = []
  for i in range(7):
     for j in range(ally[i]):
        soldiers.append([0, i])

  random.shuffle(soldiers)

  stability = 0
  stability_denominator = 0
  for i in range(7):
     index_old = i + gen4_storage[gen4_sld_id][2]
     if(index_old >= 0 and index_old <= 6):
        stability += min(gen4_storage[gen4_sld_id][0][index_old], ally[i])
        stability += min(gen4_storage[gen4_sld_id][1][index_old], enemy[i])
        stability_denominator += gen4_storage[gen4_sld_id][0][index_old]
        stability_denominator += gen4_storage[gen4_sld_id][1][index_old]

  # print(stability)

  gen4_storage[gen4_sld_id][0] = copy.deepcopy(ally)
  gen4_storage[gen4_sld_id][1] = copy.deepcopy(enemy)

  sol_num = random.randint(1, ally[3])
  curr_sol_num = 0

  index = 0

  while curr_sol_num < sol_num:
    action_scores = [0.0, 0.0, 0.0]
    pos = soldiers[index][1]
    final_stability = 0
    if(stability_denominator == 0):
      final_stability = 1
    else:
      final_stability = stability / stability_denominator
    for i in castle_pos:
      val = ((enemy[i] >= ally[i])*final_stability*gen4_params[4] + 1) * (gen4_params[0] ** max(abs(ally[i] - enemy[i]), gen4_params[1])) * (((gen4_params[2] + final_stability*gen4_params[3]) / (1 + final_stability*gen4_params[3])) ** abs(i - pos))
      if i == pos:
        action_scores[0] -= val
        action_scores[2] -= val
      elif i < pos:
        action_scores[0] += val
        action_scores[2] -= val
      elif i > pos:
        action_scores[0] -= val
        action_scores[2] += val

    final_action = max(enumerate(action_scores), key=lambda x: x[1])[0] - 1
    ally[pos] -= 1
    if (pos + final_action >= 0) and (pos + final_action <= 6):
      ally[pos + final_action] += 1
    if (final_action == 0):
       stability += 1
    stability_denominator += 1
      
    if(pos == 3):
       curr_sol_num += 1
    index += 1
  # print(str(action_scores) + " " + str(ally))

  gen4_storage[gen4_sld_id][2] = final_action
  if(isLocal):
    gen4_sld_id += 1
    gen4_sld_id %= 60 * (needDoubleStorage + 1)

  return final_action

gen3_storage = [[[0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], 0] for i in range(60 * (needDoubleStorage + 1))]

gen3_sld_id = 0

def gen3(ally: list, enemy: list, offset: int, gen3_params = [0.5118766689257184, 0.4339071582948457, 0.5106516576611354, 1]):
  global gen3_sld_id

  action_scores = [0, 0, 0]

  castle_pos = [i for i in range(7) if (i % 3) == (offset % 3)]

  soldiers = []
  for i in range(7):
     for j in range(ally[i]):
        soldiers.append([0, i])

  random.shuffle(soldiers)

  stability = 0
  stability_denominator = 0
  for i in range(7):
     index_old = i + gen3_storage[gen3_sld_id][2]
     if(index_old >= 0 and index_old <= 6):
        stability += min(gen3_storage[gen3_sld_id][0][index_old], ally[i])
        stability += min(gen3_storage[gen3_sld_id][1][index_old], enemy[i])
        stability_denominator += gen3_storage[gen3_sld_id][0][index_old]
        stability_denominator += gen3_storage[gen3_sld_id][1][index_old]

  if(stability_denominator == 0):
     stability = 1
  else:
     stability = stability / stability_denominator

  # print(stability)

  gen3_storage[gen3_sld_id][0] = copy.deepcopy(ally)
  gen3_storage[gen3_sld_id][1] = copy.deepcopy(enemy)

  sol_num = random.randint(1, ally[3])
  curr_sol_num = 0

  index = 0

  while curr_sol_num < sol_num:
    action_scores = [0.0, 0.0, 0.0]
    pos = soldiers[index][1]
    final_stability = 0
    if(stability_denominator == 0):
      final_stability = 1
    else:
      final_stability = stability / stability_denominator
    for i in castle_pos:
      val = (gen3_params[0] ** max(abs(ally[i] - enemy[i]), gen3_params[1])) * (((gen3_params[2] + final_stability*gen3_params[3]) / (1 + final_stability*gen3_params[3])) ** abs(i - pos))
      if i == pos:
        action_scores[0] -= val
        action_scores[2] -= val
      elif i < pos:
        action_scores[0] += val
        action_scores[2] -= val
      elif i > pos:
        action_scores[0] -= val
        action_scores[2] += val

    final_action = max(enumerate(action_scores), key=lambda x: x[1])[0] - 1
    ally[pos] -= 1
    if (pos + final_action >= 0) and (pos + final_action <= 6):
      ally[pos + final_action] += 1
    if (final_action == 0):
       stability += 1
    stability_denominator += 1
      
    if(pos == 3):
       curr_sol_num += 1
    index += 1
  # print(str(action_scores) + " " + str(ally))

  gen3_storage[gen3_sld_id][2] = final_action
  if(isLocal):
    gen3_sld_id += 1
    gen3_sld_id %= 60 * (needDoubleStorage + 1)

  return final_action

def gen2(ally: list, enemy: list, offset: int, gen2_params = [0.5118766689257184, 0.4339071582948457, 0.5106516576611354]):
  action_scores = [0, 0, 0]

  castle_pos = [i for i in range(7) if (i % 3) == (offset % 3)]

  soldiers = []
  for i in range(7):
     for j in range(ally[i]):
        soldiers.append([0, i])

  random.shuffle(soldiers)

  sol_num = random.randint(1, ally[3])
  curr_sol_num = 0

  index = 0

  while curr_sol_num < sol_num:
    action_scores = [0.0, 0.0, 0.0]
    pos = soldiers[index][1]
    for i in castle_pos:
      val = (gen2_params[0] ** max(abs(ally[i] - enemy[i]), gen2_params[1])) * (gen2_params[2] ** abs(i - pos))
      if i == pos:
        action_scores[0] -= val
        action_scores[2] -= val
      elif i < pos:
        action_scores[0] += val
        action_scores[2] -= val
      elif i > pos:
        action_scores[0] -= val
        action_scores[2] += val

    final_action = max(enumerate(action_scores), key=lambda x: x[1])[0] - 1
    ally[pos] -= 1
    if (pos + final_action >= 0) and (pos + final_action <= 6):
      ally[pos + final_action] += 1
      
    if(pos == 3):
       curr_sol_num += 1
    index += 1
  # print(str(action_scores) + " " + str(ally))

  return final_action

def gen1(ally: list, enemy: list, offset: int):
  action_scores = [0, 0, 0]
  for i in range(3):
     action_scores[i] += 100

  final_action = max(enumerate(action_scores), key=lambda x: x[1])[0] - 1
  return final_action
    #  action_scores += random.random() * params[693]
    #  for j in range(7):
    #     index = (min(max(ally[j] - enemy[j], -5), 5) + 5) + 11 * j + 77 * (offset + 1) + 231 * i
    #     action_scores[i] += params_spsa_m[index]

def prizeCutoffKnockoff(ally: list, enemy: list, offset: int):
  action_scores = [0, 0, 0]

  castle_pos = [i for i in range(7) if (i % 3) == (offset % 3)]

  soldiers = []
  for i in range(7):
     for j in range(ally[i]):
        soldiers.append([0, i])

  random.shuffle(soldiers)

  sol_num = random.randint(1, ally[3])
  curr_sol_num = 0

  index = 0

  while curr_sol_num < sol_num:
    action_scores = [0.0, 0.0, 0.0]
    pos = soldiers[index][1]
    if pos + 1 in castle_pos:
      pass
    # for i in castle_pos:
    #   if i == pos:
    #     action_scores[0] -= val
    #     action_scores[2] -= val
    #   elif i < pos:
    #     action_scores[0] += val
    #     action_scores[2] -= val
    #   elif i > pos:
    #     action_scores[0] -= val
    #     action_scores[2] += val

    final_action = max(enumerate(action_scores), key=lambda x: x[1])[0] - 1
    ally[pos] -= 1
    if (pos + final_action >= 0) and (pos + final_action <= 6):
      ally[pos + final_action] += 1
      
    if(pos == 3):
       curr_sol_num += 1
    index += 1
  # print(str(action_scores) + " " + str(ally))

  return final_action

def get_strategies():
    """
    Returns a list of strategies to play against each other.

    In the local tester, all of the strategies will be used as separate players, and the 
    pairwise winrate will be calculated for each strategy.

    In the official grader, only the first element of the list will be used as your strategy.
    """
    strategies = [dev, base]

    return strategies
