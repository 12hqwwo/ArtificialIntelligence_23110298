import heapq
import random
import math
import time
from copy import deepcopy
from collections import deque, defaultdict

# ======= COMMON CONSTANTS AND HELPERS =======
goal_state = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

moves_list = [(-1, 0), (1, 0), (0, -1), (0, 1)]
moves_dict = {
    'U': (-1, 0),
    'D': (1, 0),
    'L': (0, -1),
    'R': (0, 1)
}
and_or_moves = {
    'up': (-1, 0),
    'down': (1, 0),
    'left': (0, -1),
    'right': (0, 1)
}

def find_empty(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j
    return None

def is_solvable(state):
    flat = [num for row in state for num in row if num != 0]
    inv_count = sum(1 for i in range(len(flat)) for j in range(i+1, len(flat)) if flat[i] > flat[j])
    return inv_count % 2 == 0

def matrix_to_tuple(matrix):
    return tuple(tuple(row) for row in matrix)

def get_states(state):
    empty_x, empty_y = find_empty(state)
    states = []
    for dx, dy in moves_list:
        new_x, new_y = empty_x + dx, empty_y + dy
        if 0 <= new_x < 3 and 0 <= new_y < 3:
            new_state = [row[:] for row in state]
            new_state[empty_x][empty_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[empty_x][empty_y]
            states.append(new_state)
    return states

def manhattan_distance(state):
    dist = 0
    for i in range(3):
        for j in range(3):
            val = state[i][j]
            if val != 0:
                target_x, target_y = divmod(val - 1, 3)
                dist += abs(target_x - i) + abs(target_y - j)
    return dist

def apply_action(state, action, moves=moves_dict):
    x, y = find_empty(state)
    dx, dy = moves[action]
    nx, ny = x + dx, y + dy
    if 0 <= nx < 3 and 0 <= ny < 3:
        new_state = deepcopy(state)
        new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
        return new_state
    return None

# ======= AND-OR SEARCH (and_or.py) =======
def and_or_search(start_state, max_depth=100):
    def explore(state, path, depth, visited):
        if state == goal_state:
            return path + [state]
        if depth >= max_depth:
            return None
        state_tuple = matrix_to_tuple(state)
        if state_tuple in visited:
            return None
        visited.add(state_tuple)

        empty_x, empty_y = find_empty(state)
        for move, (dx, dy) in and_or_moves.items():
            new_x, new_y = empty_x + dx, empty_y + dy
            if 0 <= new_x < 3 and 0 <= new_y < 3:
                new_state = [row[:] for row in state]
                new_state[empty_x][empty_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[empty_x][empty_y]
                result = explore(new_state, path + [state], depth + 1, visited)
                if result is not None:
                    return result
        return None

    visited = set()
    return explore(start_state, [], 0, visited)

# ======= CSPs (csps.py) =======
def backtrack_csp(state, path, visited, depth, max_depth):
    if state == goal_state:
        return path
    if depth >= max_depth:
        return None

    for action in moves_dict:
        new_state = apply_action(state, action)
        if new_state is None:
            continue
        state_tuple = matrix_to_tuple(new_state)
        if state_tuple in visited:
            continue
        visited.add(state_tuple)
        result = backtrack_csp(new_state, path + [new_state], visited, depth+1, max_depth)
        if result:
            return result
        visited.remove(state_tuple)

    return None

def backtrack_csp_fc(state, path, visited, depth, max_depth):
    if state == goal_state:
        return path
    # Forward checking pruning:
    if depth + manhattan_distance(state) > max_depth:
        return None

    for action in moves_dict:
        new_state = apply_action(state, action)
        if new_state is None:
            continue
        state_tuple = matrix_to_tuple(new_state)
        if state_tuple in visited:
            continue
        visited.add(state_tuple)
        result = backtrack_csp_fc(new_state, path + [new_state], visited, depth+1, max_depth)
        if result:
            return result
        visited.remove(state_tuple)

    return None

def min_conflicts(start_state, max_steps=20000):
    current_state = deepcopy(start_state)
    path = [start_state]
    stuck_counter = 0
    max_stuck_steps = 10000

    for _ in range(max_steps):
        if current_state == goal_state:
            return path
        next_states = get_states(current_state)
        if not next_states:
            continue
        min_conflict = float('inf')
        best_states = []
        for state in next_states:
            conf = manhattan_distance(state)
            if conf < min_conflict:
                min_conflict = conf
                best_states = [state]
            elif conf == min_conflict:
                best_states.append(state)
        chosen = random.choice(best_states)
        path.append(chosen)
        if manhattan_distance(chosen) >= manhattan_distance(current_state):
            stuck_counter += 1
        else:
            stuck_counter = 0
        current_state = chosen
        if stuck_counter >= max_stuck_steps:
            current_state = generate_random_state()
            path = [current_state]
            stuck_counter = 0
    return None

def generate_random_state():
    flat = list(range(9))
    while True:
        random.shuffle(flat)
        state = tuple(tuple(flat[i*3:(i+1)*3]) for i in range(3))
        if is_solvable(state):
            return state

def get_solution(start_state, algo):
    visited = set()
    visited.add(matrix_to_tuple(start_state))
    if algo == "Backtracking":
        path = backtrack_csp(start_state, [], visited, 0, 50)
    elif algo == "Backtracking with forward checking":
        path = backtrack_csp_fc(start_state, [], visited, 0, 30)
    else:
        path = None
    return path

# ======= INFORMED SEARCH (informed_search.py) =======
def greedy_best_first_search(start_state):
    priority_queue = [(manhattan_distance(start_state), start_state, [])]
    visited = set()
    while priority_queue:
        _, state, path = heapq.heappop(priority_queue)
        state_tuple = matrix_to_tuple(state)
        if state == goal_state:
            return path + [state]
        if state_tuple in visited:
            continue
        visited.add(state_tuple)
        for new_state in get_states(state):
            heapq.heappush(priority_queue, (manhattan_distance(new_state), new_state, path + [state]))
    return None

def ida_start(start_state):
    threshold = manhattan_distance(start_state)
    while True:
        stack = [(start_state, 0, [])]
        min_threshold = float('inf')
        while stack:
            state, cost, path = stack.pop()
            f = cost + manhattan_distance(state)
            if f > threshold:
                min_threshold = min(min_threshold, f)
                continue
            if state == goal_state:
                return path + [state]
            for new_state in get_states(state):
                if new_state not in path:
                    stack.append((new_state, cost+1, path + [state]))
        if min_threshold == float('inf'):
            return None
        threshold = min_threshold

def a_start(start_state):
    priority_queue = [(manhattan_distance(start_state), 0, start_state, [])]
    visited = set()
    while priority_queue:
        _, cost, state, path = heapq.heappop(priority_queue)
        state_tuple = matrix_to_tuple(state)
        if state == goal_state:
            return path + [state]
        if state_tuple in visited:
            continue
        visited.add(state_tuple)
        for new_state in get_states(state):
            new_cost = cost + 1
            heapq.heappush(priority_queue, (new_cost + manhattan_distance(new_state), new_cost, new_state, path + [state]))
    return None

# ======= LOCAL SEARCH (local_search.py) =======
def shc(start_state):
    current_state = start_state
    path = [current_state]
    while True:
        current_score = manhattan_distance(current_state)
        next_states = get_states(current_state)
        better_found = False
        for state in next_states:
            if manhattan_distance(state) < current_score:
                current_state = state
                path.append(current_state)
                better_found = True
                break
        if not better_found:
            break
        if current_state == goal_state:
            return path
    return None

def steepest_ahc(start_state):
    current_state = start_state
    path = [current_state]
    while True:
        current_score = manhattan_distance(current_state)
        next_states = get_states(current_state)
        best_state = None
        best_score = current_score
        for state in next_states:
            score = manhattan_distance(state)
            if score < best_score:
                best_score = score
                best_state = state
        if best_state is None:
            break
        path.append(best_state)
        current_state = best_state
        if current_state == goal_state:
            return path
    return None

def stochastic_hc(start_state):
    current_state = start_state
    path = [current_state]
    while True:
        current_score = manhattan_distance(current_state)
        next_states = get_states(current_state)
        better = [state for state in next_states if manhattan_distance(state) < current_score]
        if not better:
            break
        current_state = random.choice(better)
        path.append(current_state)
        if current_state == goal_state:
            return path
    return None

def simulated_annealing(start_state, max_steps=10000, initial_temp=10000.0, rate=0.999999):
    current_state = start_state
    path = [current_state]
    T = initial_temp
    for step in range(max_steps):
        current_score = manhattan_distance(current_state)
        if current_state == goal_state:
            return path
        next_states = get_states(current_state)
        if not next_states:
            break
        next_state = random.choice(next_states)
        next_score = manhattan_distance(next_state)
        delta_e = next_score - current_score
        if delta_e < 0 or random.uniform(0,1) < math.exp(-delta_e / T):
            current_state = next_state
            path.append(current_state)
        T *= rate
        if T < 1e-3:
            break
    return None

def beam_search(start_state, beam_width=5):
    beam = [(manhattan_distance(start_state), start_state, [start_state])]
    visited = set()
    for step in range(1000):
        new_beam = []
        for _, state, path in beam:
            state_tuple = matrix_to_tuple(state)
            if state_tuple in visited:
                continue
            visited.add(state_tuple)
            if state == goal_state:
                return path
            for next_state in get_states(state):
                heapq.heappush(new_beam, (manhattan_distance(next_state), next_state, path + [next_state]))
        if not new_beam:
            break
        beam = heapq.nsmallest(beam_width, new_beam)
    return None

def solution_for_ga(start_state):
    def create_population(size):
        population = []
        for _ in range(size):
            individual = [random.randint(0,3) for _ in range(30)]
            population.append(individual)
        return population

    def fitness(individual):
        state = [row[:] for row in start_state]
        for move in individual:
            empty_x, empty_y = find_empty(state)
            new_x, new_y = empty_x + moves_list[move][0], empty_y + moves_list[move][1]
            if 0 <= new_x < 3 and 0 <= new_y < 3:
                state[empty_x][empty_y], state[new_x][new_y] = state[new_x][new_y], state[empty_x][empty_y]
        return manhattan_distance(state), state

    def crossover(p1, p2):
        cut = random.randint(0, len(p1)-1)
        return p1[:cut] + p2[cut:]

    def mutate(individual, mutation_rate=0.05):
        for i in range(len(individual)):
            if random.random() < mutation_rate:
                individual[i] = random.randint(0,3)
        return individual

    def genetic_algorithm(population_size=100, generations=1000):
        population = create_population(population_size)
        for gen in range(generations):
            evaluated = []
            for individual in population:
                score, state = fitness(individual)
                evaluated.append((score, individual, state))
            evaluated.sort(key=lambda x: x[0])
            best_fitness, best_individual, best_state = evaluated[0]
            if best_fitness == 0:
                state = [row[:] for row in start_state]
                path = [start_state]
                for move in best_individual:
                    empty_x, empty_y = find_empty(state)
                    new_x, new_y = empty_x + moves_list[move][0], empty_y + moves_list[move][1]
                    if 0 <= new_x < 3 and 0 <= new_y < 3:
                        state[empty_x][empty_y], state[new_x][new_y] = state[new_x][new_y], state[empty_x][empty_y]
                        path.append([row[:] for row in state])
                        if state == goal_state:
                            break
                return path
            new_population = []
            while len(new_population) < population_size:
                p1 = random.choice(evaluated[:population_size//2])[1]
                p2 = random.choice(evaluated[:population_size//2])[1]
                child = crossover(p1, p2)
                child = mutate(child)
                new_population.append(child)
            population = new_population
        return None

    return genetic_algorithm()

# ======= SENSORLESS PROBLEM (sensorless_problem.py) =======
def move_blank_sensorless(state, action):
    dx = {'U': -1, 'D': 1, 'L': 0, 'R': 0}
    dy = {'U': 0, 'D': 0, 'L': -1, 'R': 1}
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                x, y = i + dx[action], j + dy[action]
                if 0 <= x < 3 and 0 <= y < 3:
                    new = [list(row) for row in state]
                    new[i][j], new[x][y] = new[x][y], new[i][j]
                    return tuple(tuple(row) for row in new)
    return None

def manhattan_sensorless(state, goal):
    pos = {val: (i,j) for i,row in enumerate(goal) for j,val in enumerate(row)}
    dist = 0
    for i in range(3):
        for j in range(3):
            val = state[i][j]
            if val != 0:
                gi, gj = pos[val]
                dist += abs(i - gi) + abs(j - gj)
    return dist

def heuristic_sensorless(belief, goal):
    return max(manhattan_sensorless(state, goal) for state in belief)

def sensorless_solve_astar(belief, goal):
    visited = set()
    heap = []
    heapq.heappush(heap, (heuristic_sensorless(belief, goal), 0, belief, []))

    while heap:
        _, cost, current, path = heapq.heappop(heap)
        current_set = set(current)
        if all(state == goal for state in current):
            return path + [current]

        for action in ['U', 'D', 'L', 'R']:
            next_states = []
            seen = set()
            for state in current_set:
                new_state = move_blank_sensorless(state, action)
                if new_state and new_state not in seen:
                    seen.add(new_state)
                    next_states.append(new_state)
            if next_states:
                next_tuple = tuple(sorted(next_states))
                if next_tuple not in visited:
                    visited.add(next_tuple)
                    g = cost + 1
                    h = heuristic_sensorless(next_states, goal)
                    heapq.heappush(heap, (g+h, g, next_states, path + [current]))
    return ["Không tìm thấy lời giải!"]

# ======= PARTIAL OBSERVATION (partial_obs.py) =======
def move_blank_partial(state, action):
    dx = {'U': -1, 'D': 1, 'L': 0, 'R': 0}
    dy = {'U': 0, 'D': 0, 'L': -1, 'R': 1}
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                x, y = i + dx[action], j + dy[action]
                if 0 <= x < 3 and 0 <= y < 3:
                    new = [list(row) for row in state]
                    new[i][j], new[x][y] = new[x][y], new[i][j]
                    return tuple(tuple(row) for row in new)
    return None

def match_observation(state, observation):
    for (i, j), val in observation.items():
        if state[i][j] != val:
            return False
    return True

def generate_initial_belief(observation, max_states=100):
    all_values = set(range(9))
    known_values = set(observation.values())
    unknown_values = list(all_values - known_values)
    unknown_positions = [(i,j) for i in range(3) for j in range(3) if (i,j) not in observation]
    belief = []
    for _ in range(max_states):
        perm = random.sample(unknown_values, len(unknown_values))
        state = [[-1]*3 for _ in range(3)]
        for (i,j), val in observation.items():
            state[i][j] = val
        for idx, (i,j) in enumerate(unknown_positions):
            state[i][j] = perm[idx]
        state_tuple = tuple(tuple(row) for row in state)
        if is_solvable(state_tuple) and state_tuple not in belief:
            belief.append(state_tuple)
    return belief

def heuristic_partial(belief, goal):
    return max(manhattan_distance(state) for state in belief)

def filter_belief_with_observation(belief, observation):
    return [s for s in belief if match_observation(s, observation)]

def observe_fn(belief, step):
    # Mô phỏng quan sát: giả sử biết toàn bộ trạng thái đầu tiên
    state = belief[0]
    observation = {}
    for i in range(3):
        for j in range(3):
            observation[(i,j)] = state[i][j]
    return observation

def solve_partial_observation_8puzzle(initial_observation, goal):
    belief = generate_initial_belief(initial_observation)
    visited = set()
    heap = []
    max_steps = 10000

    step = 0
    heapq.heappush(heap, (heuristic_partial(belief, goal), 0, belief, []))

    while heap:
        _, cost, current_belief, path = heapq.heappop(heap)
        if len(current_belief) == 1 and current_belief[0] == goal:
            return path
        current_key = tuple(sorted(current_belief))
        if current_key in visited:
            continue
        visited.add(current_key)
        for action in ['U', 'D', 'L', 'R']:
            next_states = []
            seen = set()
            for state in current_belief:
                new_state = move_blank_partial(state, action)
                if new_state and new_state not in seen:
                    seen.add(new_state)
                    next_states.append(new_state)
            if not next_states:
                continue
            new_observation = observe_fn(next_states, step+1)
            filtered = filter_belief_with_observation(next_states, new_observation)
            if not filtered:
                continue
            g = cost + 1
            h = heuristic_partial(filtered, goal)
            heapq.heappush(heap, (g+h, g, filtered, path + [action]))
        step += 1
        if step > max_steps:
            return ["Đạt giới hạn bước, không tìm thấy lời giải!"]
    return ["Không tìm thấy lời giải!"]

# ======= UNINFORMED SEARCH (uninformed_search.py) =======
def bfs_solve(start_state):
    open = deque([(start_state, [])])
    visited = set()
    visited.add(matrix_to_tuple(start_state))
    while open:
        current_state, path = open.popleft()
        if current_state == goal_state:
            return path
        for state in get_states(current_state):
            state_tuple = matrix_to_tuple(state)
            if state_tuple not in visited:
                visited.add(state_tuple)
                open.append((state, path + [state]))
    return None

def dfs(start_state):
    stack = [(start_state, [], 0)]
    visited = set()
    while stack:
        state, path, depth = stack.pop()
        state_tuple = matrix_to_tuple(state)
        if state == goal_state:
            return path + [state]
        if state_tuple in visited or depth > 30:
            continue
        visited.add(state_tuple)
        next_states = get_states(state)
        next_states.sort(key=manhattan_distance, reverse=True)
        for new_state in next_states:
            stack.append((new_state, path + [state], depth+1))
    return None

def depth_bound_search(state, depth_bound, visited):
    if state == goal_state:
        return [state]
    if depth_bound > 0:
        state_tuple = matrix_to_tuple(state)
        if state_tuple in visited:
            return None
        visited.add(state_tuple)
        next_states = get_states(state)
        next_states.sort(key=manhattan_distance, reverse=True)
        for new_state in next_states:
            res = depth_bound_search(new_state, depth_bound - 1, visited)
            if res:
                return [state] + res
    return None

def ids(start_state):
    for depth in range(30):
        visited = set()
        res = depth_bound_search(start_state, depth, visited)
        if res:
            return res
    return None

def ucs(start_state):
    priority_queue = [(0, start_state, [])]
    visited = set()
    while priority_queue:
        cost, state, path = heapq.heappop(priority_queue)
        state_tuple = matrix_to_tuple(state)
        if state == goal_state:
            return path + [state]
        if state_tuple in visited:
            continue
        visited.add(state_tuple)
        for new_state in get_states(state):
            heapq.heappush(priority_queue, (cost+1, new_state, path + [state]))
    return None

# ======= Q-LEARNING (q_learning.py) =======
actions_q = ['U', 'D', 'L', 'R']
moves_q = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
goal_state_q = ((1, 2, 3), (4, 5, 6), (7, 8, 0))

def find_empty_q(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j
    return None

def apply_action_q(state, action):
    x, y = find_empty_q(state)
    dx, dy = moves_q[action]
    nx, ny = x + dx, y + dy
    if 0 <= nx < 3 and 0 <= ny < 3:
        new_state = [list(row) for row in state]
        new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
        return tuple(tuple(row) for row in new_state)
    return None

alpha = 0.1
gamma = 0.9
epsilon = 0.2
episodes = 10000
Q = defaultdict(lambda: {a: 0.0 for a in actions_q})

def choose_action(state):
    if random.random() < epsilon:
        return random.choice(actions_q)
    else:
        return max(Q[state], key=Q[state].get)

def train_q_learning():
    solution_path = []
    for ep in range(episodes):
        state = ((1, 2, 3), (4, 0, 6), (7, 5, 8))
        path = [state]
        while state != goal_state_q:
            action = choose_action(state)
            next_state = apply_action_q(state, action)
            if next_state:
                reward = 100 if next_state == goal_state_q else -1
                max_q_next = max(Q[next_state].values())
            else:
                reward = -100
                next_state = state
                max_q_next = max(Q[next_state].values())
            Q[state][action] += alpha * (reward + gamma * max_q_next - Q[state][action])
            state = next_state
            path.append(state)
        solution_path.append(path)
    return solution_path

def play():
    state = ((1, 2, 3), (4, 0, 6), (7, 5, 8))
    path = [state]
    steps = 0
    while state != goal_state_q and steps < 50:
        action = max(Q[state], key=Q[state].get)
        state = apply_action_q(state, action)
        path.append(state)
        steps += 1
    return path

# solution_path_q = train_q_learning()
# final_path_q = play()
