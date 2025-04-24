import function
import heapq
from collections import deque

def bfs_solve(start_state):
    queue = deque([(start_state, [])])
    visited = set([tuple(map(tuple, start_state))])
    while queue:
        current_state, path = queue.popleft()
        if current_state == function.GOAL_STATE:
            return path
        for new_state, move in function.generate_states(current_state):
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
        if state == function.GOAL_STATE:
            return path
        for new_state, move in function.generate_states(state):
            new_cost = cost + 1
            new_tuple = tuple(map(tuple, new_state))
            if new_tuple not in visited or new_cost < visited[new_tuple]:
                visited[new_tuple] = new_cost
                heapq.heappush(pq, (new_cost, new_state, path + [move]))
    return None

def dfs_solve(start_state):
    stack = [(start_state, [])]
    visited = set([tuple(map(tuple, start_state))])
    while stack:
        state, path = stack.pop()
        if state == function.GOAL_STATE:
            return path
        for new_state, move in function.generate_states(state):
            state_tuple = tuple(map(tuple, new_state))
            if state_tuple not in visited:
                visited.add(state_tuple)
                stack.append((new_state, path + [move]))
    return None

def ids_solve(start_state):
    def dls(state, path, limit, visited):
        if state == function.GOAL_STATE:
            return path
        if limit == 0:
            return None
        for new_state, move in function.generate_states(state):
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
        f = g + function.manhattan_distance(state)
        if f > threshold:
            return f
        if state == function.GOAL_STATE:
            return path
        min_threshold = float('inf')
        for new_state, move in function.generate_states(state):
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

    threshold = function.manhattan_distance(start_state)
    visited = {tuple(map(tuple, start_state))}
    while True:
        result = search(start_state, 0, threshold, [], visited)
        if isinstance(result, list):
            return result
        if result == float('inf'):
            return None
        threshold = result

def ucs_solve(start_state):
    pq = []
    initial_tuple = tuple(map(tuple, start_state))
    heapq.heappush(pq, (0, start_state, []))
    visited = {initial_tuple: 0}
    while pq:
        cost, state, path = heapq.heappop(pq)
        if state == function.GOAL_STATE:
            return path
        for new_state, move in function.generate_states(state):
            new_cost = cost + 1
            new_tuple = tuple(map(tuple, new_state))
            if new_tuple not in visited or new_cost < visited[new_tuple]:
                visited[new_tuple] = new_cost
                heapq.heappush(pq, (new_cost, new_state, path + [move]))
    return None
