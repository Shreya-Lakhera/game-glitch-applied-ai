"""Run deterministic or live investigator demonstrations."""

import argparse
import json
from pathlib import Path

from investigator import investigate_turn


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="examples/cases.json")
    args = parser.parse_args()
    for number, case in enumerate(json.loads(Path(args.cases).read_text()), 1):
        result = investigate_turn(case)
        print(f"Case {number}: {result.mode}")
        print(json.dumps(result.as_dict(), indent=2))


if __name__ == "__main__":
    main()
