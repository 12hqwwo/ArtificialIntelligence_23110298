import tkinter as tk
from tkinter import messagebox, ttk
from collections import deque
import heapq
import time
import random
import math
import sys
sys.setrecursionlimit(10**6) 

# -----------------------------
# SUPPORT FUNCTIONS FOR 8-PUZZLE
# -----------------------------
GOAL_STATE = [[1, 2, 3],
              [4, 5, 6],
              [7, 8, 0]]  # 0 đại diện cho ô trống

def find_blank(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

MOVES = {
    'UP':    (-1,  0),
    'DOWN':  ( 1,  0),
    'LEFT':  ( 0, -1),
    'RIGHT': ( 0,  1)
}

def generate_states(state):
    blank_x, blank_y = find_blank(state)
    new_states = []
    for move, (dx, dy) in MOVES.items():
        new_x, new_y = blank_x + dx, blank_y + dy
        if 0 <= new_x < 3 and 0 <= new_y < 3:
            new_state = [row[:] for row in state]
            new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
            new_states.append((new_state, move))
    return new_states

def manhattan_distance(state):
    distance = 0
    for i in range(3):
        for j in range(3):
            val = state[i][j]
            if val != 0:
                goal_i = (val - 1) // 3
                goal_j = (val - 1) % 3
                distance += abs(i - goal_i) + abs(j - goal_j)
    return distance

def is_solvable(state):
    """
    Kiểm tra tính khả thi của puzzle 8-puzzle.
    Chỉ số đảo lộn (inversion count) của danh sách (loại trừ 0) phải chẵn.
    """
    arr = [num for row in state for num in row if num != 0]
    inv_count = 0
    for i in range(len(arr)):
        for j in range(i+1, len(arr)):
            if arr[i] > arr[j]:
                inv_count += 1
    return inv_count % 2 == 0



def greedy_solve(start_state):
    pq = []
    initial_tuple = tuple(map(tuple, start_state))
    h = manhattan_distance(start_state)
    heapq.heappush(pq, (h, start_state, []))
    visited = {initial_tuple}
    while pq:
        h, state, path = heapq.heappop(pq)
        if state == GOAL_STATE:
            return path
        for new_state, move in generate_states(state):
            new_tuple = tuple(map(tuple, new_state))
            if new_tuple not in visited:
                visited.add(new_tuple)
                new_h = manhattan_distance(new_state)
                heapq.heappush(pq, (new_h, new_state, path + [move]))
    return None

def astar_solve(start_state):
    pq = []
    initial_tuple = tuple(map(tuple, start_state))
    h = manhattan_distance(start_state)
    g = 0
    f = g + h
    heapq.heappush(pq, (f, g, start_state, []))
    visited = {initial_tuple: f}
    while pq:
        f, g, state, path = heapq.heappop(pq)
        if state == GOAL_STATE:
            return path
        for new_state, move in generate_states(state):
            new_g = g + 1
            new_h = manhattan_distance(new_state)
            new_f = new_g + new_h
            new_tuple = tuple(map(tuple, new_state))
            if new_tuple not in visited or new_f < visited[new_tuple]:
                visited[new_tuple] = new_f
                heapq.heappush(pq, (new_f, new_g, new_state, path + [move]))
    return None


# --- HILL CLIMBING VARIANTS ---
def simple_hill_climbing_solve(start_state):
    current = start_state
    path = []
    while True:
        if current == GOAL_STATE:
            return path
        current_h = manhattan_distance(current)
        found_improvement = False
        for neighbor_state, move in generate_states(current):
            neighbor_h = manhattan_distance(neighbor_state)
            if neighbor_h < current_h:
                path.append(move)
                current = neighbor_state
                found_improvement = True
                break
        if not found_improvement:
            return path

def steepest_hill_climbing_solve(start_state):
    current = start_state
    path = []
    while True:
        if current == GOAL_STATE:
            return path
        current_h = manhattan_distance(current)
        best_neighbor = None
        best_move = None
        best_h = current_h
        for neighbor_state, move in generate_states(current):
            neighbor_h = manhattan_distance(neighbor_state)
            if neighbor_h < best_h:
                best_h = neighbor_h
                best_neighbor = neighbor_state
                best_move = move
        if best_neighbor is None:
            return path
        path.append(best_move)
        current = best_neighbor

def stochastic_hill_climbing_solve(start_state):
    states = [start_state]
    moves = []
    backtrack_count = 2
    while True:
        current = states[-1]
        if current == GOAL_STATE:
            return moves
        current_h = manhattan_distance(current)
        better_neighbors = []
        for neighbor_state, move in generate_states(current):
            neighbor_h = manhattan_distance(neighbor_state)
            if neighbor_h < current_h:
                better_neighbors.append((neighbor_state, move))
        if better_neighbors:
            chosen_state, chosen_move = random.choice(better_neighbors)
            states.append(chosen_state)
            moves.append(chosen_move)
            print("Move:", chosen_move, "Heuristic:", manhattan_distance(chosen_state))
        else:
            if backtrack_count > 0 and len(states) > 1:
                print("No improvement. Backtracking...")
                states.pop()
                if moves:
                    moves.pop()
                backtrack_count -= 1
            else:
                return moves

def simulated_annealing_solve(start_state, max_iterations=30000, initial_temp=1e5, alpha=0.95):
    """
    Phiên bản này luôn trả về đường đi (partial moves) ngay cả khi không đạt goal.
    """
    current = [row[:] for row in start_state]
    current_h = manhattan_distance(current)
    path = []
    T = initial_temp
    for _ in range(max_iterations):
        if current == GOAL_STATE:
            return path
        neighbors = generate_states(current)
        next_state, next_move = random.choice(neighbors)
        next_h = manhattan_distance(next_state)
        if next_h < current_h:
            current = next_state
            current_h = next_h
            path.append(next_move)
        else:
            delta = next_h - current_h
            p = math.exp(-delta / T)
            if random.random() < p:
                current = next_state
                current_h = next_h
                path.append(next_move)
        T *= alpha
    return path

# --- BEAM SEARCH ALGORITHM ---
def beam_search_solve(start_state, beam_width=3):
    """
    Thuật toán Beam Search:
      - Ở mỗi cấp, sinh tất cả các trạng thái con từ các node hiện tại.
      - Sắp xếp theo giá trị heuristic (Manhattan distance) và giữ lại beam_width node tốt nhất.
      - Nếu một node đạt đến mục tiêu, trả về đường đi.
      - Nếu không tìm thấy, trả về đường đi partial từ node tốt nhất.
    """
    nodes = [(start_state, [])]
    visited = set([tuple(map(tuple, start_state))])
    while nodes:
        new_nodes = []
        for state, path in nodes:
            if state == GOAL_STATE:
                return path
            for new_state, move in generate_states(state):
                state_tuple = tuple(map(tuple, new_state))
                if state_tuple not in visited:
                    visited.add(state_tuple)
                    new_nodes.append((new_state, path + [move]))
        if not new_nodes:
            break
        new_nodes.sort(key=lambda x: manhattan_distance(x[0]))
        nodes = new_nodes[:beam_width]
    if nodes:
        return nodes[0][1]
    return None

# --- AND-OR SEARCH ALGORITHM ---
def and_or_solve(start_state, limit=50):
    def and_or(state, explored, depth):
        if state == GOAL_STATE:
            return []
        if depth > limit:
            return None  # Quá sâu thì cắt
        state_tuple = tuple(map(tuple, state))
        if state_tuple in explored:
            return None
        new_explored = explored.union({state_tuple})
        
        for new_state, move in generate_states(state):
            result = and_or(new_state, new_explored, depth + 1)
            if result is not None:
                return [move] + result
        return None

    return and_or(start_state, set(), 0)

# --- SENSORLESS BFS ALGORITHM ---
def sensorless_bfs_solve(initial_belief_state):
    """
    Sensorless BFS for 8-puzzle:
    - State is a belief state (set of possible states).
    - Transition: For each state s in belief state b, apply action to get s', then b' = union of all s'.
    - Goal: |b| = 1 and that state is GOAL_STATE.
    - Cost: Path cost (number of actions).
    """
    # Convert initial belief state to a set of tuples for uniqueness
    initial_belief_tuple = tuple(sorted([tuple(map(tuple, state)) for state in initial_belief_state]))
    queue = deque([(initial_belief_tuple, [])])
    visited = {initial_belief_tuple}
    
    while queue:
        current_belief_tuple, path = queue.popleft()
        # Convert back to list of states for processing
        current_belief = [list(map(list, state)) for state in current_belief_tuple]
        
        # Goal test: |b| = 1 and the state is GOAL_STATE
        if len(current_belief) == 1 and current_belief[0] == GOAL_STATE:
            return path
        
        # Try each possible action
        for action in MOVES.keys():
            new_belief = set()  # Use set to avoid duplicates
            for state in current_belief:
                # Apply the action to this state
                for new_state, move in generate_states(state):
                    if move == action:
                        new_belief.add(tuple(map(tuple, new_state)))
            
            # Convert new belief state to sorted tuple for queue
            new_belief_tuple = tuple(sorted(new_belief))
            if new_belief_tuple not in visited:
                visited.add(new_belief_tuple)
                queue.append((new_belief_tuple, path + [action]))
    
    return None 

