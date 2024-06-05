from argparse import ArgumentParser
from scheduler import Scheduler


def parse_args():
    #TODO make a nice parser with config file for LEN5 model
    parser = ArgumentParser()
    parser.add_argument("--test_name", type=str, required=True)
    parser.add_argument("--mem_name", type=str, required=True)
    args = parser.parse_args()

    return args

def main():
    args = parse_args()
    scheduler = Scheduler(args.test_name, args.mem_name)

    i = 0

    while i < 600: # Just for debugging
        print(f"Step {i}")
        scheduler.step()

        i += 1

if __name__ == "__main__":
    main()