"""
Test Suite for Calculator Module
Tests all functions in calculator.py
"""

import unittest
from calculator import add, subtract, multiply, divide, power, modulo, calculator


class TestBasicOperations(unittest.TestCase):
    """Test individual calculator functions"""
    
    def test_add_positive_numbers(self):
        """Test addition with positive numbers"""
        self.assertEqual(add(5, 3), 8)
        self.assertEqual(add(10, 20), 30)
        self.assertEqual(add(0, 5), 5)
    
    def test_add_negative_numbers(self):
        """Test addition with negative numbers"""
        self.assertEqual(add(-5, -3), -8)
        self.assertEqual(add(-10, 5), -5)
        self.assertEqual(add(10, -5), 5)
    
    def test_add_floats(self):
        """Test addition with floating point numbers"""
        self.assertAlmostEqual(add(2.5, 3.7), 6.2)
        self.assertAlmostEqual(add(0.1, 0.2), 0.3)
    
    def test_subtract_positive_numbers(self):
        """Test subtraction with positive numbers"""
        self.assertEqual(subtract(10, 4), 6)
        self.assertEqual(subtract(100, 50), 50)
        self.assertEqual(subtract(5, 5), 0)
    
    def test_subtract_negative_numbers(self):
        """Test subtraction with negative numbers"""
        self.assertEqual(subtract(-5, -3), -2)
        self.assertEqual(subtract(-10, 5), -15)
        self.assertEqual(subtract(10, -5), 15)
    
    def test_multiply_positive_numbers(self):
        """Test multiplication with positive numbers"""
        self.assertEqual(multiply(6, 7), 42)
        self.assertEqual(multiply(5, 0), 0)
        self.assertEqual(multiply(1, 100), 100)
    
    def test_multiply_negative_numbers(self):
        """Test multiplication with negative numbers"""
        self.assertEqual(multiply(-5, 3), -15)
        self.assertEqual(multiply(-5, -3), 15)
        self.assertEqual(multiply(0, -10), 0)
    
    def test_multiply_floats(self):
        """Test multiplication with floating point numbers"""
        self.assertAlmostEqual(multiply(2.5, 4), 10.0)
        self.assertAlmostEqual(multiply(1.5, 2.5), 3.75)
    
    def test_divide_positive_numbers(self):
        """Test division with positive numbers"""
        self.assertEqual(divide(20, 4), 5)
        self.assertEqual(divide(10, 2), 5)
        self.assertAlmostEqual(divide(7, 2), 3.5)
    
    def test_divide_negative_numbers(self):
        """Test division with negative numbers"""
        self.assertEqual(divide(-20, 4), -5)
        self.assertEqual(divide(-20, -4), 5)
        self.assertEqual(divide(20, -4), -5)
    
    def test_divide_by_zero(self):
        """Test that division by zero raises ValueError"""
        with self.assertRaises(ValueError) as context:
            divide(10, 0)
        self.assertIn("Cannot divide by zero", str(context.exception))
    
    def test_power_positive_numbers(self):
        """Test power/exponentiation with positive numbers"""
        self.assertEqual(power(2, 8), 256)
        self.assertEqual(power(5, 2), 25)
        self.assertEqual(power(10, 0), 1)
        self.assertEqual(power(2, 3), 8)
    
    def test_power_negative_numbers(self):
        """Test power with negative numbers"""
        self.assertEqual(power(-2, 3), -8)
        self.assertEqual(power(-2, 2), 4)
        self.assertAlmostEqual(power(2, -2), 0.25)
    
    def test_power_fractional(self):
        """Test power with fractional exponents"""
        self.assertAlmostEqual(power(4, 0.5), 2.0)
        self.assertAlmostEqual(power(27, 1/3), 3.0)
    
    def test_modulo_positive_numbers(self):
        """Test modulo with positive numbers"""
        self.assertEqual(modulo(17, 5), 2)
        self.assertEqual(modulo(10, 3), 1)
        self.assertEqual(modulo(20, 5), 0)
    
    def test_modulo_negative_numbers(self):
        """Test modulo with negative numbers"""
        self.assertEqual(modulo(-17, 5), 3)
        self.assertEqual(modulo(17, -5), -3)
    
    def test_modulo_by_zero(self):
        """Test that modulo by zero raises ValueError"""
        with self.assertRaises(ValueError) as context:
            modulo(10, 0)
        self.assertIn("Cannot perform modulo with zero", str(context.exception))


class TestCalculatorFunction(unittest.TestCase):
    """Test the main calculator function"""
    
    def test_calculator_addition(self):
        """Test calculator function with addition"""
        self.assertEqual(calculator('+', 5, 3), 8)
        self.assertEqual(calculator('+', -5, 10), 5)
    
    def test_calculator_subtraction(self):
        """Test calculator function with subtraction"""
        self.assertEqual(calculator('-', 10, 4), 6)
        self.assertEqual(calculator('-', 5, 10), -5)
    
    def test_calculator_multiplication(self):
        """Test calculator function with multiplication"""
        self.assertEqual(calculator('*', 6, 7), 42)
        self.assertEqual(calculator('*', -3, 4), -12)
    
    def test_calculator_division(self):
        """Test calculator function with division"""
        self.assertEqual(calculator('/', 20, 4), 5)
        self.assertAlmostEqual(calculator('/', 7, 2), 3.5)
    
    def test_calculator_power(self):
        """Test calculator function with power"""
        self.assertEqual(calculator('**', 2, 8), 256)
        self.assertEqual(calculator('**', 3, 3), 27)
    
    def test_calculator_modulo(self):
        """Test calculator function with modulo"""
        self.assertEqual(calculator('%', 17, 5), 2)
        self.assertEqual(calculator('%', 10, 3), 1)
    
    def test_calculator_invalid_operation(self):
        """Test calculator with invalid operation"""
        with self.assertRaises(ValueError) as context:
            calculator('^', 5, 3)
        self.assertIn("Invalid operation", str(context.exception))
    
    def test_calculator_division_by_zero(self):
        """Test calculator division by zero through main function"""
        with self.assertRaises(ValueError):
            calculator('/', 10, 0)
    
    def test_calculator_modulo_by_zero(self):
        """Test calculator modulo by zero through main function"""
        with self.assertRaises(ValueError):
            calculator('%', 10, 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_operations_with_zero(self):
        """Test operations with zero"""
        self.assertEqual(add(0, 0), 0)
        self.assertEqual(subtract(0, 0), 0)
        self.assertEqual(multiply(0, 100), 0)
        self.assertEqual(multiply(100, 0), 0)
    
    def test_operations_with_large_numbers(self):
        """Test operations with large numbers"""
        self.assertEqual(add(1000000, 2000000), 3000000)
        self.assertEqual(multiply(1000, 1000), 1000000)
    
    def test_operations_with_very_small_numbers(self):
        """Test operations with very small numbers"""
        self.assertAlmostEqual(add(0.0001, 0.0002), 0.0003)
        self.assertAlmostEqual(multiply(0.1, 0.1), 0.01)
    
    def test_identity_operations(self):
        """Test identity operations"""
        self.assertEqual(add(5, 0), 5)  # Additive identity
        self.assertEqual(multiply(5, 1), 5)  # Multiplicative identity
        self.assertEqual(subtract(5, 0), 5)
        self.assertEqual(divide(5, 1), 5)
        self.assertEqual(power(5, 1), 5)


def run_tests():
    """Run all tests and display results"""
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBasicOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestCalculatorFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result


if __name__ == "__main__":
    # Run all tests
    run_tests()
