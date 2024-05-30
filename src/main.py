from argparse import ArgumentParser
from scheduler import Scheduler


def parse_args():
    #TODO make a nice parser with config file for LEN5 model
    parser = ArgumentParser()
    parser.add_argument("--test_name", type=str, required=True)
    args = parser.parse_args()

    return args

def main():
    args = parse_args()
    scheduler = Scheduler(args.test_name)

    i = 0

    while True:
        print(f"Step {i}")
        try:
            scheduler.step()
        except Exception as e:
            print(e)
            break

        i += 1