import sys
from crawl import run

def main(args):
    if len(args)>2:
        sys.exit("too many arguments provided")
    if len(args)<2:
        sys.exit("no website provided")

    print(f"starting crawl at: {args[1]}")
    run(args[1])

if __name__ == "__main__":
    main(sys.argv)
