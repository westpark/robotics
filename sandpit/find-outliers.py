#!python3
import statistics

#
# Explanation from: http://www.wikihow.com/Calculate-Outliers
#

numbers = [1.0, 2.0, 2.3, 3.0, 3.2, 4.0, 100.0, 4.5, 5.11, 6.0, 8.0]
#~ numbers = [71.0, 70.0, 73.0, 70.0, 70.0, 69.0, 70.0, 72.0, 71.0, 300.0, 71.0, 69.0]
numbers_in_order = sorted(numbers)
print("Numbers:", numbers_in_order)
q2 = statistics.median(numbers)
print("Q2:", q2)

lower_half = [n for n in numbers_in_order if n < q2]
q1 = statistics.median(lower_half)
print("Q1:", q1)

upper_half = [n for n in numbers_in_order if n > q2]
q3 = statistics.median(upper_half)
print("Q3:", q3)

interquartile = q3 - q1
print("Interquartile:", interquartile)

inner_offset = interquartile * 1.5
inner_fences = q1 - inner_offset, q3 + inner_offset
print("Inner fences:", inner_fences)

outer_offset = interquartile * 3.0
lower_fence, higher_fence = outer_fences = q1 - outer_offset, q3 + outer_offset
print("Outer fences:", outer_fences)

data_without_outliers = [n for n in numbers if lower_fence <= n <= higher_fence]
print("Data without outliers:", data_without_outliers)
