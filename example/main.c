#include <stdio.h>
#include "util.h"

void display_result(int result) {
    printf("Result: %d\n", result);
}

void run_calculations() {
    int a = 10;
    int b = 5;
    
    // Perform some simple calculations
    int sum = add(a, b);
    display_result(sum);
    
    int difference = subtract(a, b);
    display_result(difference);
    
    int product = multiply(a, b);
    display_result(product);
    
    int quotient = divide(a, b);
    display_result(quotient);
    
    // Calculate factorial
    int fact = factorial(5);
    display_result(fact);
    
    // Run a complex calculation
    int complex = complexCalculation(a, b);
    display_result(complex);
}

int main() {
    printf("CGrah2Dot Example Program\n");
    printf("=========================\n\n");
    
    run_calculations();
    
    return 0;
}