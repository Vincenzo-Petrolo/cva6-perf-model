# Import your backend
from commit_unit import CommitUnit
from RF import RF

def simulate_backend(steps):
    # Instantiate the backend
    commit_unit = CommitUnit()
    register_file = RF()
    cdb = RF()

    commit_unit.connectRF(register_file)
    commit_unit.connectCDB(cdb)

    # Step through the simulation
    for step in range(steps):
        print(f"Cycle {step}")
        commit_unit.step()

if __name__ == "__main__":
    simulate_backend(100)
