import sys

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.25) + 1):
        if n % i == 0:
            return False
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python is_prime.py <integer>")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        result = is_prime(n)
        print(result)
    except ValueError:
        print("Invalid input. Please provide an integer.")
        sys.exit(1)