import sys

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):  # Change n**0.25 to n**0.5
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

import pytest

def test_is_prime_negative():
    assert not is_prime(-5)

def test_is_prime_zero():
    assert not is_prime(0)

def test_is_prime_one():
    assert not is_prime(1)

def test_is_prime_prime():
    assert is_prime(7)

def test_is_prime_not_prime():
    assert not is_prime(9)

def test_is_prime_large_prime():
    assert is_prime(104729)

def test_is_prime_large_not_prime():
    assert not is_prime(104728)