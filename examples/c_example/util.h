#ifndef UTIL_H
#define UTIL_H

/**
 * Adds two integers and returns the result
 */
int add(int a, int b);

/**
 * Subtracts the second integer from the first and returns the result
 */
int subtract(int a, int b);

/**
 * Multiplies two integers and returns the result
 */
int multiply(int a, int b);

/**
 * Divides the first integer by the second and returns the result
 * Will print an error and return 0 if the second integer is 0
 */
int divide(int a, int b);

/**
 * Calculates the factorial of a number recursively
 */
int factorial(int n);

/**
 * Performs a complex calculation using multiple utility functions
 */
int complexCalculation(int x, int y);

#endif /* UTIL_H */