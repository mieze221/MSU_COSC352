import sys

def print_greeting(name, count):

    print(f"Starting to greet {name}...")

    for i in range(count):
        print(f"Hello {name}!")

    print(f"Greeting process completed for {name}.")

def main():

    if len(sys.argv) != 3:
        print("Usage: python hello.py <name> <number>")
        sys.exit(1)

    name = sys.argv[1]
    try:
        count = int(sys.argv[2])
    except ValueError:
        print("Error: The number of greetings must be an integer.")
        sys.exit(1)

  
    if count <= 0:
        print("Error: The number of greetings must be a positive integer.")
        sys.exit(1)


    print_greeting(name, count)

if __name__ == "__main__":
    main()

