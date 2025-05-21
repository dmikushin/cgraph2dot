#include "util.h"
#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

int multiply(int a, int b) {
    return a * b;
}

int divide(int a, int b) {
    if (b == 0) {
        printf("Error: Division by zero\n");
        return 0;
    }
    return a / b;
}

int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int helper_function(int x) {
    return x * x;
}

int complexCalculation(int x, int y) {
    int result = 0;
    
    // Use various utility functions to demonstrate a complex call graph
    int sum = add(x, y);
    int diff = subtract(x, y);
    int product = multiply(sum, diff);
    
    // Add factorial for a recursive function demonstration
    if (diff > 0 && diff < 10) {
        int fact = factorial(diff);
        result = divide(product, helper_function(fact % 10 + 1));
    } else {
        result = product;
    }
    
    return result;
}