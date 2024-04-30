GRID_RADIUS = 4
node_coordinates = []
ALL_NEIGHBOR = lambda x, y, z: ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)) # make this more efficient?
SELECT_VALID = lambda lis: [(x, y, z) for (x, y, z) in lis if 1 <= x + y + z <= 2 and -GRID_RADIUS + 1 <= x <= GRID_RADIUS and -GRID_RADIUS + 1 <= y <= GRID_RADIUS and -GRID_RADIUS + 1 <= z <= GRID_RADIUS] # keep those within-bound

for x in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
    for y in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
        for z in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
            # Check if node is valid
            if 1 <= x + y + z <= 2:
                node_coordinates.append((x, y, z))
# print(node_coordinates)
NEIGHBOR_LIST = dict(zip(node_coordinates, [SELECT_VALID(ALL_NEIGHBOR(*(node))) for node in node_coordinates]))
def get_diameter(board, start_node, visit): 
    def neighbors(node):
        #return SELECT_VALID(ALL_NEIGHBOR(*(node)))
        return NEIGHBOR_LIST[node]
    def con(node): # Find connected component and respective degrees
        visit[node] = 1
        connected[node] = -1
        cnt = 0
        for neighbor in neighbors(node):
            if neighbor in board and board[neighbor] == player:
                cnt += 1
                if neighbor not in connected:
                    con(neighbor)
        connected[node] = cnt
    def dfs(node, visited = set()):
        visited.add(node)
        max_path_length = 0
        for neighbor in neighbors(node):
            if neighbor in board and board[neighbor] == player and neighbor not in visited:
                path_length = dfs(neighbor, visited.copy())
                max_path_length = max(max_path_length, path_length)
        return max_path_length + 1
    
    try:
        player = board[start_node]
    except Exception as exc:
        print("node empty?")
        print(exc)
        return 0

    connected = dict()
    con(start_node)
    #print(connected)
    if len(connected) <= 3: # must be a line
        return len(connected)
    if 4 <= len(connected) <= 5: # a star if we have a deg-3 node, a line otherwise
        if 3 in connected.values(): # It's a star!
            return len(connected) - 1
        return len(connected)
    if 6 == len(connected):
        three = list(connected.values())
        if 3 in three:
            three.remove(3)
            if 3 in three:
                return 4 # this is a shape x - x - x - x
                        #                     x   x
        return 5 # diameter is 5 otherwise

    # For the larger(>6) ones, diameter must be larger than 5 so we just return 5
    return 5
    # maxl = 0

def score(board, gen1_params): # return current score for each player
    visit = {pos:0 for pos in node_coordinates}
    scores = {0:0 , 1:0, 2:0}
    for pos in board.keys():
        if not visit[pos]:
            d = get_diameter(board, pos, visit)
            if d:
                scores[board[pos]] += gen1_params[d]
    return scores


def gen1_eval(board_copy, us, node, gen1_params):
  curr_eval = 0
  if node != (0, 0, 0):
    curr_eval += max(abs(max(node)), abs(min(node))) * gen1_params[9] + gen1_params[10]
  visit = {pos:0 for pos in node_coordinates}
  for pos in board_copy.keys():
      for neighbor in NEIGHBOR_LIST[pos]:
        if not neighbor in board_copy:
            curr_eval += gen1_params[6]
        elif board_copy[neighbor] == us:
            curr_eval += gen1_params[7]
        else:
            curr_eval += gen1_params[8]
      if not visit[pos]:
          d = get_diameter(board_copy.copy(), pos, visit)
          if d:
              if board_copy[pos] == us:
                curr_eval += gen1_params[d]
              else:
                curr_eval -= gen1_params[d]
  return curr_eval

params = [-0.0024133293192017445, -0.222520520130363, -0.010977614937323223, 1.0741776636479716, 3.022484131064219, -0.16436472455133644, 0.46857345780258214, 0.3964576576709093, 0.20117824603874412, 0, 0]

spsa_p_params = [0, 0.25, 0.5, 1, 3, 0]
def spsa_p(board_copy, player):
  return gen1(board_copy, player, spsa_p_params)
spsa_m_params = [0, 0.25, 0.5, 1, 3, 0]
def spsa_m(board_copy, player):
  return gen1(board_copy, player, spsa_m_params)

def gen1(board_copy, player, gen1_params = [-0.002449539648230067, -0.19135969047977056, -0.045039929609612096, 1.0838090083941172, 3.034394592156924, -0.16928581904027837, 0.5625388240404815, 0.33003666332113546, 0.1546460127975072, 0.125120472584208, 0.005530622318734832]):
  #Eval if we don't make a move
  evals = []
  evals.append([(0, 0, 0), gen1_eval(board_copy, player, (0, 0, 0), gen1_params)])

  for node in node_coordinates:
      if(not node in board_copy):
          moved_board = board_copy.copy()
          moved_board[node] = player
          if(score(board_copy, gen1_params) == score(moved_board, gen1_params)):
              continue
          evals.append([node, gen1_eval(moved_board, player, node, gen1_params)])
  
  final_result = max(enumerate(evals), key=lambda x: x[1][1])[0] 

  # print(evals[final_result][1])
  final_result = evals[final_result][0]

  if(final_result == (0, 0, 0)):
    return None
  if(not ((not final_result in board_copy) and (final_result in node_coordinates))):
      print(final_result)
  # print(board_copy)
  return final_result

def strategy(board_copy, player):
    return gen1(board_copy, player)

def spsa_pass(board_copy, current_player_idx):
    return None


