from argparse import ArgumentParser
from scheduler import Scheduler


def parse_args():
    #TODO make a nice parser with config file for LEN5 model
    parser = ArgumentParser()
    parser.add_argument("--test_name", type=str, required=True)
    parser.add_argument("--mem_name", type=str, required=True)
    parser.add_argument("--mem_dump", action="store_true", help="Dump the memory after at each cycle into memory.log file")
    parser.add_argument("--commit_history_dump", action="store_true", help="Dump the commit history at each cycle into a commit.log file")
    parser.add_argument("--rob_dump", action="store_true", help="Dump the ROB at each cycle into a rob.log file")
    parser.add_argument("--max_cycles", type=int, help="Maximum Cycles", default=100_000)

    args = parser.parse_args()

    return args

def main():
    args = parse_args()
    scheduler = Scheduler(args.test_name, args.mem_name, args.mem_dump, args.commit_history_dump, args.rob_dump)

    i = 0

    while i < args.max_cycles:
        try:
            scheduler.step(i)
        except Exception as e:
            if (str(e) != "Simulation is over"):
                print(f"Exception: {e}")
            break

        i += 1

if __name__ == "__main__":
    main()