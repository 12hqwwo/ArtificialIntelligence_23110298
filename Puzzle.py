import tkinter as tk
from tkinter import messagebox, ttk
from collections import deque
import time
import function
import find1

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
            if not function.is_solvable(state):
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
            solution = find1.bfs_solve(start_state)
        elif algo == "UCS":
            solution = find1.ucs_solve(start_state)
        elif algo == "Greedy":
            solution = function.greedy_solve(start_state)
        elif algo == "A*":
            solution = function.astar_solve(start_state)
        elif algo == "DFS":
            solution = find1.dfs_solve(start_state)
        elif algo == "IDS":
            solution = find1.ids_solve(start_state)
        elif algo == "IDA*":
            solution = find1.ida_star_solve(start_state)
        elif algo == "SimpleHC":
            solution = function.simple_hill_climbing_solve(start_state)
        elif algo == "SteepestHC":
            solution = function.steepest_hill_climbing_solve(start_state)
        elif algo == "StochasticHC":
            solution = function.stochastic_hill_climbing_solve(start_state)
        elif algo == "SimAnneal":
            solution = function.simulated_annealing_solve(start_state, max_iterations=30000, initial_temp=1e5, alpha=0.95)
        elif algo == "BeamSearch":
            solution = function.beam_search_solve(start_state, beam_width=3)
        elif algo == "AndOr":
            solution = function.and_or_solve(start_state)
        elif algo == "SensorlessBFS":
            # For simplicity, treat the initial state as a belief state with one state
            belief_state = [start_state]
            solution = function.sensorless_bfs_solve(belief_state)
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
            solved = (final_state == function.GOAL_STATE)

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
        blank_x, blank_y = function.find_blank(state)
        dx, dy = function.MOVES[move]
        new_x, new_y = blank_x + dx, blank_y + dy
        new_state = [row[:] for row in state]
        new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
        return new_state

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()
