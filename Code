class GCounter:
    def __init__(self, replica_id):
        self.replica_id = replica_id
        self.state = {replica_id: 0}

    def increment(self):
        self.state[self.replica_id] += 1
        op = {"replica_id": self.replica_id, "delta": 1}
        return op

    def apply(self, operation):
        rid = operation["replica_id"]
        delta = operation["delta"]
        if rid not in self.state:
            self.state[rid] = 0
        self.state[rid] += delta

    @staticmethod
    def merge(state_a, state_b):
        merged = {}
        all_keys = set(state_a.keys()).union(state_b.keys())
        for k in all_keys:
            merged[k] = max(state_a.get(k, 0), state_b.get(k, 0))
        return merged

    def value(self):
        return sum(self.state.values())


# ---------------------------------------------------
# DEMO (THIS PART PRODUCES OUTPUT)
# ---------------------------------------------------

R1 = GCounter("A")
R2 = GCounter("B")

op1 = R1.increment()
op2 = R1.increment()
op3 = R2.increment()

R2.apply(op1)
R2.apply(op2)
R1.apply(op3)

merged_state = GCounter.merge(R1.state, R2.state)

print("Replica R1 State:", R1.state)
print("Replica R2 State:", R2.state)
print("Merged State:", merged_state)
print("Final Counter Value:", sum(merged_state.values()))
