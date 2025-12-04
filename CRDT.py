import collections

class GCounter:
    """
    Implements a Conflict-Free Replicated Data Type (CRDT):
    Operation-Based Grow-Only Counter (G-Counter).
    
    The state is a vector clock-like map of replica_id -> count.
    """

    def __init__(self, replica_id: str, initial_state: dict = None):
        """
        Initializes a G-Counter replica.

        :param replica_id: A unique identifier for this specific replica (e.g., 'node_A').
        :param initial_state: An optional dictionary representing the initial state 
                              from other replicas (for syncing at start).
        """
        self.replica_id = replica_id
        # State: {replica_id: count}, storing all known increments.
        self.state = collections.defaultdict(int)
        
        if initial_state:
            # Ensure any initial state is merged correctly
            self.state = self.merge(self.state, initial_state)

    # --- Task 1: Data Structure is the self.state dictionary/map ---

    # --- Task 2: Implement the 'Increment' operation ---
    def increment(self, amount: int = 1) -> dict:
        """
        Applies an increment locally and generates an operation object (op).
        In an Op-based CRDT, the 'op' is what is sent over the network.
        
        :param amount: The amount to increment by (must be >= 0 for G-Counter).
        :return: An 'operation object' (a dictionary) to be broadcast.
        """
        if amount < 0:
            raise ValueError("G-Counter can only grow (increment amount must be >= 0)")

        # 1. Apply the increment locally
        self.state[self.replica_id] += amount
        
        # 2. Generate the operation object (the delta to send)
        # For simplicity in this G-Counter, the op is just the replica's new total count.
        # More generally, an op-based CRDT might send a delta, but for G-Counter,
        # sending the new total count for the local ID is sufficient for merge.
        # The true 'op' is just a single vector entry update: {self.replica_id: self.state[self.replica_id]}
        return {self.replica_id: self.state[self.replica_id]}

    # --- Helper: Apply a received operation/state update ---
    def apply_update(self, update_state: dict):
        """
        Receives an update (either a full state or a single op) from another replica 
        and merges it into the local state.
        
        :param update_state: The state/operation received from a remote replica.
        """
        self.state = self.merge(self.state, update_state)

    # --- Task 3: Implement the 'merge' function ---
    @staticmethod
    def merge(state1: dict, state2: dict) -> dict:
        """
        Merges two G-Counter states by taking the maximum count for each replica ID.
        This is the core convergence logic.

        :param state1: The first G-Counter state (e.g., local state).
        :param state2: The second G-Counter state (e.g., received state/op).
        :return: The new, converged G-Counter state.
        """
        # Collect all unique replica IDs from both states
        all_ids = set(state1.keys()) | set(state2.keys())
        
        merged_state = {}
        for replica_id in all_ids:
            # Find the value for this replica_id in state1 (default to 0 if not present)
            count1 = state1.get(replica_id, 0)
            # Find the value for this replica_id in state2 (default to 0 if not present)
            count2 = state2.get(replica_id, 0)
            
            # The convergence function: max(count1, count2)
            merged_state[replica_id] = max(count1, count2)
            
        return merged_state

    # --- Task 4: Implement the function to retrieve the total value ---
    def value(self) -> int:
        """
        Calculates the total value of the counter by summing all observed increments.

        :return: The total counter value.
        """
        # Sum the values (counts) across all replica IDs in the state vector.
        return sum(self.state.values())

# --- Example Usage ---
print("--- Initializing Replicas ---")
# Node A and Node B start simultaneously
node_A = GCounter("A")
node_B = GCounter("B")

# A increments twice
op_A1 = node_A.increment()
op_A2 = node_A.increment()
print(f"Node A: State: {dict(node_A.state)} | Total Value: {node_A.value()}")

# B increments once concurrently
op_B1 = node_B.increment()
print(f"Node B: State: {dict(node_B.state)} | Total Value: {node_B.value()}")

print("\n--- Simulating Network Exchange and Merge ---")

# A sends its final op to B
print(">> Node A sends update to Node B...")
node_B.apply_update(op_A2) 
print(f"Node B (After Merge): State: {dict(node_B.state)}")

# B sends its final op to A
print(">> Node B sends update to Node A...")
node_A.apply_update(op_B1) 
print(f"Node A (After Merge): State: {dict(node_A.state)}")

print("\n--- Final Check ---")
print(f"Convergence Check: Node A value ({node_A.value()}) == Node B value ({node_B.value()})")
