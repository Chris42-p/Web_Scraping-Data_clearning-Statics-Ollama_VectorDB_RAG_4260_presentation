import argparse
from Modules.user_GUI.back_end.spider_service import run_spider_by_key

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spider-key", required=True)
    parser.add_argument("--settings-module", required=False, default=None)
    args = parser.parse_args()
    run_spider_by_key(args.spider_key)

if __name__ == "__main__":
    main()