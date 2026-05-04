from collections import deque
import heapq
from typing import Optional
from src.core.search_algorithm import SearchAlgorithm
from src.core.node import Node
from src.part_a.problem import RushHourProblem

import time

class BreadthFirstSearch(SearchAlgorithm):
    def search(self, problem: RushHourProblem, time_limit_ms: Optional[float] = None) -> Optional[Node]:
        self.metrics.start_timer()
        node = Node(state=problem.initial_state)
        self.metrics.increment_generated()
        self.metrics.update_depth(node.depth)

        if problem.is_goal(node.state):
            self.metrics.solution_depth = node.depth
            self.metrics.stop_timer()
            return node

        frontier = deque([node])
        explored = {node.state}

        while frontier:
            if time_limit_ms is not None:
                if (time.perf_counter() - self.metrics._start_time) * 1000.0 > time_limit_ms:
                    break

            current_node = frontier.popleft()
            self.metrics.increment_expanded()

            actions = problem.get_actions(current_node.state)
            if not actions:
                self.metrics.record_dead_end(current_node.depth)

            for action in problem.get_actions(current_node.state):
                child_state = problem.get_result(current_node.state, action)
                child_node = Node(
                    state=child_state,
                    parent=current_node,
                    action=action,
                    path_cost=current_node.path_cost + 1,
                    depth=current_node.depth + 1
                )
                self.metrics.increment_generated()
                self.metrics.update_depth(child_node.depth)

                if child_state not in explored:
                    if problem.is_goal(child_state):
                        self.metrics.solution_depth = child_node.depth
                        self.metrics.stop_timer()
                        return child_node
                    explored.add(child_state)
                    frontier.append(child_node)

        self.metrics.stop_timer()
        return None

class AStarSearch(SearchAlgorithm):
    def search(self, problem: RushHourProblem, time_limit_ms: Optional[float] = None) -> Optional[Node]:
        self.metrics.start_timer()
        
        h_initial = problem.calculate_heuristic(problem.initial_state)
        self.metrics.record_heuristic(h_initial)
        
        initial_node = Node(
            state=problem.initial_state,
            heuristic_value=h_initial
        )
        self.metrics.increment_generated()
        self.metrics.update_depth(initial_node.depth)

        # Priority queue for frontier: elements are nodes
        frontier = []
        heapq.heappush(frontier, initial_node)
        
        # explored mappings state -> minimum path cost found to that state
        explored = {initial_node.state: initial_node.path_cost}

        while frontier:
            if time_limit_ms is not None:
                if (time.perf_counter() - self.metrics._start_time) * 1000.0 > time_limit_ms:
                    break
                    
            current_node = heapq.heappop(frontier)

            if problem.is_goal(current_node.state):
                self.metrics.solution_depth = current_node.depth
                self.metrics.stop_timer()
                return current_node

            self.metrics.increment_expanded()

            if current_node.path_cost > explored.get(current_node.state, float('inf')):
                continue

            actions = problem.get_actions(current_node.state)
            if not actions:
                self.metrics.record_dead_end(current_node.depth)

            for action in actions:
                child_state = problem.get_result(current_node.state, action)
                child_cost = current_node.path_cost + 1
                
                if child_state not in explored or child_cost < explored[child_state]:
                    h_child = problem.calculate_heuristic(child_state)
                    self.metrics.record_heuristic(h_child)
                    
                    child_node = Node(
                        state=child_state,
                        parent=current_node,
                        action=action,
                        path_cost=child_cost,
                        depth=current_node.depth + 1,
                        heuristic_value=h_child
                    )
                    self.metrics.increment_generated()
                    self.metrics.update_depth(child_node.depth)
                    
                    explored[child_state] = child_cost
                    heapq.heappush(frontier, child_node)

        self.metrics.stop_timer()
        return None
