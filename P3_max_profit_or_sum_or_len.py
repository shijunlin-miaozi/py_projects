import numpy as np
import time

# Design an algorithm that determines the maximum profit that could have been made by 
# buying and then selling a single share over a given day range, subject to the constraint
# that the buy and the sell have to take place at the start of the day.

# input prices array is generated using random numbers as below:
prices = np.random.randint(1, 81, 100)
print(prices)

def method_1(prices):
    # brute-force method - run thru all possible buy-sell price pairs
    # O(nˆ2) algarithm - inefficient for large price array
    n, max_profit = len(prices), 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            profit = prices[j] - prices[i]
            if profit > max_profit:
                max_profit = profit
    return max_profit

def method_2(prices):
    # run thru price array only once - O(n)
    max_profit, min_price = 0, prices[0]
    for price in prices:
        max_profit_today = price - min_price
        max_profit = max(max_profit, max_profit_today)
        min_price = min(min_price, price)
    return max_profit

if __name__ == '__main__':
    start_time = time.time()
    print(method_1(prices))
    print(f'--- method1 {(time.time() - start_time): .4f} s seconds ---')

    start_time = time.time()
    print(method_2(prices))
    print(f'--- method2 {(time.time() - start_time): .4f} s seconds ---')



# Variant1 of the problem:
# The maximum sum subarray problem - finding a contiguous subarray with the largest sum, 
# within a given one-dimensional array A[1...n] of numbers.

# input array is generated as below:
array = np.random.randint(-100, 100, 80)
print(array)

def max_subarray(array):
    max_sum, current_sum = float('-inf'), 0
    for x in array:
        current_sum = x if current_sum <= 0 else current_sum + x
        max_sum = max(max_sum, current_sum)
    return max_sum

if __name__ == '__main__':
    print(max_subarray(array))



# Variant2 of the problem:
# Write a program that takes an array of integers and finds the length of a 
# longest subarray all of whose entries are equal.

# input array is generated as below:
numbers = np.random.randint(1, 5, 20)
print(numbers)

def longest_subarray(numbers):
    max_len = current_len = 1
    for i in range(1, len(numbers)):
        if numbers[i] == numbers[i - 1]:
            current_len += 1
            max_len = max(max_len, current_len)
        else:
            current_len = 1
    return max_len

if __name__ == '__main__':
    print(longest_subarray(numbers))
