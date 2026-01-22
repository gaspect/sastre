import argparse
from .scaffold import Scaffold

def main():
    parser = argparse.ArgumentParser(description="Sastre - A simple Astro project scaffolder")
    parser.add_argument("path", nargs="?", default=".", help="Directory to create the project in (default: current directory)")
    args = parser.parse_args()
    scaffold = Scaffold(args.path)
    scaffold.project()


if __name__ == "__main__":
    main()
    