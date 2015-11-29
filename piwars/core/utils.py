try:
    import statistics
except ImportError:
    statistics = None

if statistics:
    def without_outliers(iterator):
        #
        # Discard major outliers
        # (Explanation from: http://www.wikihow.com/Calculate-Outliers)
        #
        numbers = list(iterator)
        q2 = statistics.median(numbers)
        q1 = statistics.median(n for n in numbers if n < q2)
        q3 = statistics.median(n for n in numbers if n > q2)
        interquartile = q3 - q1
        inner_offset = interquartile * 1.5 # inner fence; use 3.0 for outer fence
        lower_fence, higher_fence = q1 - inner_offset, q3 + inner_offset
        return [n for n in numbers if lower_fence <= d <= higher_fence]
else:
    def without_outliers(iterator): return list(iterator)