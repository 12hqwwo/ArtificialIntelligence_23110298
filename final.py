import tkinter as tk
from tkinter import messagebox, ttk
from collections import deque
import heapq
import time
import random
import math
import sys
sys.setrecursionlimit(10**6)  # Ví dụ đặt lên 1 triệu


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

# ------------------
# SEARCH ALGORITHMS
# ------------------

def bfs_solve(start_state):
    queue = deque([(start_state, [])])
    visited = set([tuple(map(tuple, start_state))])
    while queue:
        current_state, path = queue.popleft()
        if current_state == GOAL_STATE:
            return path
        for new_state, move in generate_states(current_state):
            state_tuple = tuple(map(tuple, new_state))
            if state_tuple not in visited:
                visited.add(state_tuple)
                queue.append((new_state, path + [move]))
    return None

def ucs_solve(start_state):
    pq = []
    initial_tuple = tuple(map(tuple, start_state))
    heapq.heappush(pq, (0, start_state, []))
    visited = {initial_tuple: 0}
    while pq:
        cost, state, path = heapq.heappop(pq)
        if state == GOAL_STATE:
            return path
        for new_state, move in generate_states(state):
            new_cost = cost + 1
            new_tuple = tuple(map(tuple, new_state))
            if new_tuple not in visited or new_cost < visited[new_tuple]:
                visited[new_tuple] = new_cost
                heapq.heappush(pq, (new_cost, new_state, path + [move]))
    return None

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

def dfs_solve(start_state):
    stack = [(start_state, [])]
    visited = set([tuple(map(tuple, start_state))])
    while stack:
        state, path = stack.pop()
        if state == GOAL_STATE:
            return path
        for new_state, move in generate_states(state):
            state_tuple = tuple(map(tuple, new_state))
            if state_tuple not in visited:
                visited.add(state_tuple)
                stack.append((new_state, path + [move]))
    return None

def ids_solve(start_state):
    def dls(state, path, limit, visited):
        if state == GOAL_STATE:
            return path
        if limit == 0:
            return None
        for new_state, move in generate_states(state):
            new_tuple = tuple(map(tuple, new_state))
            if new_tuple not in visited:
                visited.add(new_tuple)
                result = dls(new_state, path + [move], limit - 1, visited)
                if result is not None:
                    return result
                visited.remove(new_tuple)
        return None

    depth = 0
    while True:
        visited = {tuple(map(tuple, start_state))}
        result = dls(start_state, [], depth, visited)
        if result is not None:
            return result
        depth += 1

def ida_star_solve(start_state):
    def search(state, g, threshold, path, visited):
        f = g + manhattan_distance(state)
        if f > threshold:
            return f
        if state == GOAL_STATE:
            return path
        min_threshold = float('inf')
        for new_state, move in generate_states(state):
            new_tuple = tuple(map(tuple, new_state))
            if new_tuple in visited:
                continue
            visited.add(new_tuple)
            result = search(new_state, g + 1, threshold, path + [move], visited)
            if isinstance(result, list):
                return result
            if result < min_threshold:
                min_threshold = result
            visited.remove(new_tuple)
        return min_threshold

    threshold = manhattan_distance(start_state)
    visited = {tuple(map(tuple, start_state))}
    while True:
        result = search(start_state, 0, threshold, [], visited)
        if isinstance(result, list):
            return result
        if result == float('inf'):
            return None
        threshold = result

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


# -------------------
# TKINTER GUI APPLICATION
# -------------------
class PuzzleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver")
        # Đặt kích thước cố định (bạn có thể điều chỉnh)
        self.root.geometry("600x600")
        
        # Cấu hình grid cho root: các frame sẽ không giãn nếu không cần
        self.root.grid_rowconfigure(0, weight=0)  # input_frame
        self.root.grid_rowconfigure(1, weight=0)  # control_frame
        self.root.grid_rowconfigure(2, weight=0)  # puzzle_frame
        self.root.grid_columnconfigure(0, weight=1)
        
        self.initial_state = None
        self.state = None
        self.buttons = [[None]*3 for _ in range(3)]
        self.create_ui()

    def create_ui(self):
        self.root.configure(bg='#FFF0F5')
        
        # --- Input Frame ---
        input_frame = tk.Frame(self.root, bg='#FFF0F5')
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        tk.Label(input_frame, text="Enter initial state (0 represents blank):",
                 bg='#FFF0F5', font=('Comic Sans MS', 14)
                ).grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        self.input_entries = [[None]*3 for _ in range(3)]
        default_values = [['2', '6', '5'],
                          ['8', '0', '7'],
                          ['4', '3', '1']]
        for i in range(3):
            for j in range(3):
                e = tk.Entry(input_frame, width=4, font=('Comic Sans MS', 16), justify='center')
                e.grid(row=i+1, column=j, padx=5, pady=5)
                e.insert(0, default_values[i][j])
                self.input_entries[i][j] = e
        
        update_button = tk.Button(input_frame, text="Update State", font=('Comic Sans MS', 14),
                                  bg='#FFB6C1', command=self.update_initial_state)
        update_button.grid(row=4, column=0, columnspan=3, pady=10)
        
        # --- Control Frame ---
        control_frame = tk.Frame(self.root, bg='#FFF0F5')
        control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="n")
        tk.Label(control_frame, text="Select algorithm:", bg='#FFF0F5',
                 font=('Comic Sans MS', 14)).grid(row=0, column=0, padx=5, pady=5)
        
        self.algorithms = [
            ("BFS", "BFS"),
            ("Uniform Cost Search", "UCS"),
            ("Greedy Search", "Greedy"),
            ("A* Search", "A*"),
            ("DFS", "DFS"),
            ("IDS", "IDS"),
            ("IDA* Search", "IDA*"),
            ("Simple Hill Climbing", "SimpleHC"),
            ("Steepest Hill Climbing", "SteepestHC"),
            ("Stochastic Hill Climbing", "StochasticHC"),
            ("Simulated Annealing", "SimAnneal"),
            ("Beam Search", "BeamSearch"),
            ("And-Or Search", "AndOr"), 
            ("Sensorless BFS", "SensorlessBFS")
        ]
        
        self.algo_var = tk.StringVar()
        self.algo_combo = ttk.Combobox(control_frame, textvariable=self.algo_var, 
                                       state="readonly", font=('Comic Sans MS', 12))
        self.algo_combo['values'] = [item[0] for item in self.algorithms]
        self.algo_combo.current(0)
        self.algo_combo.grid(row=0, column=1, padx=5, pady=5)
        
        solve_button = tk.Button(control_frame, text="Solve Puzzle", font=('Comic Sans MS', 14),
                                 bg='#AED581', command=self.solve_puzzle)
        solve_button.grid(row=1, column=0, columnspan=2, pady=10)
        
        # --- Puzzle Frame ---
        self.puzzle_frame = tk.Frame(self.root, bg='#FFF0F5')
        self.puzzle_frame.grid(row=2, column=0, columnspan=3, pady=10)
        for i in range(3):
            for j in range(3):
                b = tk.Label(
                    self.puzzle_frame,
                    text="",
                    width=3,
                    height=1,
                    font=('Comic Sans MS', 20),
                    relief="solid",
                    bg="white",
                    anchor="center"
                )
                b.grid(row=i, column=j, padx=2, pady=2)
                self.buttons[i][j] = b

        self.update_initial_state()

    def update_initial_state(self):
        try:
            state = []
            for i in range(3):
                row = []
                for j in range(3):
                    value = int(self.input_entries[i][j].get())
                    row.append(value)
                state.append(row)
            self.initial_state = state
            if not is_solvable(state):
                messagebox.showerror("Error", "Puzzle unsolvable!")
                return
            self.state = [r[:] for r in state]
            self.update_puzzle_display()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integers!")

    def update_puzzle_display(self):
        for i in range(3):
            for j in range(3):
                val = self.state[i][j]
                display_val = "" if val == 0 else str(val)
                self.buttons[i][j].config(text=display_val, bg="white")

    def solve_puzzle(self):
        if self.initial_state is None:
            messagebox.showerror("Error", "Initial state not updated!")
            return

        selected_text = self.algo_var.get()
        algo = None
        for display_name, mode_name in self.algorithms:
            if display_name == selected_text:
                algo = mode_name
                break

        start_state = [row[:] for row in self.initial_state]
        start_time = time.time()

        if algo == "BFS":
            solution = bfs_solve(start_state)
        elif algo == "UCS":
            solution = ucs_solve(start_state)
        elif algo == "Greedy":
            solution = greedy_solve(start_state)
        elif algo == "A*":
            solution = astar_solve(start_state)
        elif algo == "DFS":
            solution = dfs_solve(start_state)
        elif algo == "IDS":
            solution = ids_solve(start_state)
        elif algo == "IDA*":
            solution = ida_star_solve(start_state)
        elif algo == "SimpleHC":
            solution = simple_hill_climbing_solve(start_state)
        elif algo == "SteepestHC":
            solution = steepest_hill_climbing_solve(start_state)
        elif algo == "StochasticHC":
            solution = stochastic_hill_climbing_solve(start_state)
        elif algo == "SimAnneal":
            solution = simulated_annealing_solve(start_state, max_iterations=30000, initial_temp=1e5, alpha=0.95)
        elif algo == "BeamSearch":
            solution = beam_search_solve(start_state, beam_width=3)
        elif algo == "AndOr":
            solution = and_or_solve(start_state)
        elif algo == "SensorlessBFS":
            # For simplicity, treat the initial state as a belief state with one state
            belief_state = [start_state]
            solution = sensorless_bfs_solve(belief_state)
        else:
            solution = None

        elapsed = time.time() - start_time

        if solution is None:
            solution = []
            solved = False
        else:
            final_state = [row[:] for row in self.initial_state]
            for move in solution:
                final_state = self.move_blank(final_state, move)
            solved = (final_state == GOAL_STATE)

        print("Algorithm:", algo, "Solution:", solution, "Elapsed time:", elapsed)
        if solved:
            messagebox.showinfo("Result", f"Solution found in {len(solution)} moves.\nTime: {elapsed:.2f} seconds.\nMoves: {solution}")
        else:
            messagebox.showinfo("Result", f"No complete solution found after {len(solution)} moves.\nTime: {elapsed:.2f} seconds.")
        self.state = [row[:] for row in self.initial_state]
        self.update_puzzle_display()
        self.root.after(1000, lambda: self.animate_solution(solution, solved))

    def animate_solution(self, moves, solved):
        if not moves:
            if not solved:
                messagebox.showinfo("Result", "No complete solution was reached.")
            return
        move = moves.pop(0)
        self.state = self.move_blank(self.state, move)
        self.update_puzzle_display()
        self.root.after(500, lambda: self.animate_solution(moves, solved))

    def move_blank(self, state, move):
        blank_x, blank_y = find_blank(state)
        dx, dy = MOVES[move]
        new_x, new_y = blank_x + dx, blank_y + dy
        new_state = [row[:] for row in state]
        new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
        return new_state

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
