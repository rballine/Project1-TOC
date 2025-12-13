from src.helpers.turing_machine import TuringMachineSimulator
from collections import deque


# ==========================================
# PROGRAM 1: Nondeterministic TM [cite: 137]
# ==========================================
class NTM_Tracer(TuringMachineSimulator):
    def run(self, input_string, max_depth):
        """
        Performs a Breadth-First Search (BFS) trace of the NTM.
        Ref: Section 4.1 "Trees as List of Lists" [cite: 146]
        """
        # Print basic info
        print(f"Machine name: {self.machine_name}")
        print(f"Input string: {input_string}")

        # Initial Configuration: ["", start_state, input_string]
        # Note: Represent configuration as triples (left, state, right) [cite: 156]
        initial_config = ["", self.start_state, input_string]

        # Use a BFS queue with (config, depth)
        queue = deque()
        queue.append((initial_config, 0))
        depth = 0
        accepted = False

        # parent dictionary
        parents = { tuple(initial_config) : None}
        # visited set to avoid re-processing exact same configuration in BFS
        visited = set()
        visited.add(tuple(initial_config))

        # statistics
        # total_nodes counts configurations visited (includes root)
        total_nodes = 0
        # total_transitions counts all outgoing transitions inspected (sum of len(transitions))
        total_transitions = 0
        non_leaf_configs = 0

        max_seen_depth = 0
        all_rejected = True
        # list of lists to capture tree levels for display
        tree_levels = []
        # BFS traversal using a queue
        while queue and not accepted:
            config, depth = queue.popleft()
            # stop if reached max_depth
            if depth >= max_depth:
                print(f"Execution stopped after, {max_depth}, steps.")
                # print stats and tree snapshot when stopping due to step limit
                for i, lvl in enumerate(tree_levels):
                    print(f"Level {i}: {lvl}")
                break
            max_seen_depth = max(max_seen_depth, depth)

            # 1. Operate on single config popped from queue.
            left, state, right = config # initialize variables for each part of tuple
            # ensure tree_levels has a list for this depth
            while len(tree_levels) <= depth:
                tree_levels.append([])
            tree_levels[depth].append([left, state, right])
            total_nodes += 1
            # 2. Check if config is Accept (Stop and print success) [cite: 179]
            if state == self.accept_state:
                # Print final statistics and trace
                print(f"Depth: {depth}")
                print(f"String accepted in {depth} transitions")
                print("Here is the tree level configuration:")

                # print the level tree
                for i, lvl in enumerate(tree_levels):
                    print(f"Level {i}: {lvl}")

                # make parent map and final node available for printing
                self.parents = parents
                self.final_node = tuple(config)
                self.print_trace_path(config)
                accepted = True
                break

            # 3. Check if config is Reject (Stop this branch only) [cite: 181]
            if state == self.reject_state:
                continue

            # 4. If not Accept/Reject, find valid transitions in self.transitions.
            if right == "": # checks if symbol is a blank
                read_symbol = "_"
            else:
                read_symbol = right[0] # reads symbol under tape head

            transitions = self.get_transitions(state, (read_symbol,))
            total_transitions += len(transitions)

            # 5. If no explicit transition exists, treat as implicit Reject.
            if not transitions:
                # If there is no explicit transition, include a reject leaf node at the next depth
                reject_child = [left, self.reject_state, right]
                # add to tree_levels next depth
                while len(tree_levels) <= depth + 1:
                    tree_levels.append([])
                tree_levels[depth + 1].append(reject_child)
                total_nodes += 1
                # update the max seen depth to include this reject leaf at depth+1
                max_seen_depth = max(max_seen_depth, depth + 1)
                # set parent link for reject node
                child_t = (left, self.reject_state, right)
                if child_t not in parents:
                    parents[child_t] = tuple(config)
                # this is a leaf (reject) so we don't enqueue it
                continue

            # 6. Otherwise, node has outgoing transitions (non-leaf)
            all_rejected = False
            non_leaf_configs += 1
            parent_t = tuple(config)
            for x in transitions:
                next_state = x["next"]
                write_symbol = x["write"][0]
                move = x["move"][0]

                # Apply the write section
                if right == "":
                    new_right = write_symbol
                else:
                    new_right = write_symbol + right[1:]

                # now move head in left or right direction
                if move == "R":
                    new_left = left + write_symbol
                    new_right = right[1:] if len(right) > 1 else "_"
                elif move == "L":
                    new_left = left[:-1] if left else ""
                    pulled = left[-1] if left else "_"
                    new_right = pulled + new_right
                else: # stay at position
                    new_left = left

                new_config = [new_left, next_state, new_right]
                child_t = (new_left, next_state, new_right)
                # Ensure parent mapping is set for path reconstruction
                if child_t not in parents:
                    parents[child_t] = parent_t
                # Enqueue children for BFS if not seen before
                if child_t not in visited:
                    visited.add(child_t)
                    queue.append((new_config, depth + 1))
                    # ensure we consider the depth of queued nodes for max depth
                    max_seen_depth = max(max_seen_depth, depth + 1)

            # If queue is empty and we never accepted: all branches rejected
            # (we handle the actual print of rejection after the loop, because queue will be empty
            #  and thus the loop ends; printing here inside the loop won't run when queue is empty)
            pass

            # continue BFS; next nodes are already enqueued

        if depth >= max_depth:
            print(f"Execution stopped after, {max_depth}, steps.")  # [cite: 259]

        # After BFS completes: if we did not accept, print rejection statistics (queue drained)
        if not accepted and max_seen_depth < max_depth:
            print(f"Depth: {max_seen_depth}")
            print(f"String rejected in {max_seen_depth} transitions")
            for i, lvl in enumerate(tree_levels):
                print(f"Level {i}: {lvl}")

    def print_trace_path(self, final_node):
        """
        Backtrack and print the path from root to the accepting node.
        Ref: Section 4.2 [cite: 165]
        """

        parents = self.parents
        curr = tuple(final_node)
        path = []

        while curr is not None:
            path.append(curr)
            curr = parents.get(curr)
        
        path.reverse()

        print("Here is the accepted configuration:")
        for (left, state, right) in path:
            head = right[0] if right else "_"
            rest = right[1:] if len(right) > 1 else ""
            # Show values in double-quotes for readability, as in sample output
            print(f'Left: "{left}", State: "{state}", Head: "{head}", Right: "{rest}"')