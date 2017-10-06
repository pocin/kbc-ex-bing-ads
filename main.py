import traceback
import sys

def main():
    print("Hello")


if __name__ == "__main__":
    try:
        main()
    except ValueError:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    except:
        traceback.print_exc(file=sys.stderr)
        sys.exit(2)
    else:
        sys.exit(0)

