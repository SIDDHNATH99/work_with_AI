"""
Calculator Module
A simple calculator with basic arithmetic operations
"""

def add(a, b):
    """Add two numbers"""
    return a + b

def subtract(a, b):
    """Subtract b from a"""
    return a - b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

def divide(a, b):
    """Divide a by b"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(a, b):
    """Raise a to the power of b"""
    return a ** b

def modulo(a, b):
    """Return the remainder of a divided by b"""
    if b == 0:
        raise ValueError("Cannot perform modulo with zero")
    return a % b

def calculator(operation, a, b):
    """
    Main calculator function that performs operations based on the input
    
    Parameters:
    operation (str): The operation to perform (+, -, *, /, **, %)
    a (float): First number
    b (float): Second number
    
    Returns:
    float: Result of the operation
    """
    operations = {
        '+': add,
        '-': subtract,
        '*': multiply,
        '/': divide,
        '**': power,
        '%': modulo
    }
    
    if operation not in operations:
        raise ValueError(f"Invalid operation: {operation}. Choose from {list(operations.keys())}")
    
    return operations[operation](a, b)


if __name__ == "__main__":
    # Example usage
    print("Calculator Examples:")
    print(f"5 + 3 = {calculator('+', 5, 3)}")
    print(f"10 - 4 = {calculator('-', 10, 4)}")
    print(f"6 * 7 = {calculator('*', 6, 7)}")
    print(f"20 / 4 = {calculator('/', 20, 4)}")
    print(f"2 ** 8 = {calculator('**', 2, 8)}")
    print(f"17 % 5 = {calculator('%', 17, 5)}")
