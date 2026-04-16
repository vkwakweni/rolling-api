import math
import statistics
from scipy.stats import ttest_ind

class StatisticsCalculator:
    """
    Responsibilities:
    - reusable statistical methods
    - no workflow logic
    - validate basic statistical conditions
    - return numeric/statistical outputs only
    """
    def mean(self, values):
        self.validate_numeric_sample(values)
        return statistics.mean(values)

    def median(self, values):
        self.validate_numeric_sample(values)
        return statistics.median(values)
        
    def standard_deviation(self, values):
        self.validate_numeric_sample(values)
        if len(values) <= 1:
            return None
        return statistics.stdev(values)
    
    def pooled_standard_deviation(self, group_a, group_b):
        """
        Pool standard deviation
        Source: https://www.statisticshowto.com/pooled-standard-deviation/
        """
        self.validate_numeric_sample(group_a)
        self.validate_numeric_sample(group_b)
        pooled_stdev = math.sqrt(
            ( self.standard_deviation(group_a)**2 + self.standard_deviation(group_b)**2 ) / 2
        )
        return pooled_stdev
    
    def cohen_pooled_standard_deviation(self, group_a, group_b):
        """
        Weighted pooled standard deviation
        Source: https://resources.nu.edu/statsresources/cohensd
        """
        stdev_a = self.standard_deviation(group_a)
        stdev_b = self.standard_deviation(group_b)
        pooled_stdev = math.sqrt(
            ((len(group_a) - 1) * stdev_a**2 + (len(group_b) - 1) * stdev_b**2) / (len(group_a) + len(group_b) - 2)
        )
        return pooled_stdev
    
    def cohen_pooled_standard_error(self, group_a, group_b): # TODO double check if pooled stdev should be here
        """
        Source: https://stats.libretexts.org/Bookshelves/Introductory_Statistics/Statistics%3A_Open_for_Everyone_(Peter)/08%3A_Independent_Samples_t-Tests/8.03%3A_The_Independent_Samples_t-Test_Formula
        """
        pooled_std_error = self.cohen_pooled_standard_deviation(group_a, group_b) * \
                                (math.sqrt(
                                    (len(group_a) + len(group_b)) / (len(group_a) * len(group_b))
                                ))
        return pooled_std_error


    def cohens_d(self, group_a, group_b):
        """
        Source: https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/hedgeg.htm
        TODO throw warning for length
        TODO look at the actual difference between this and Hedge's g
        """
        mean_diff = float(abs(self.mean(group_a) - self.mean(group_b)))
        pooled_stdev = self.cohen_pooled_standard_deviation(group_a, group_b)
        return mean_diff / pooled_stdev

    def welch_test(self, group_a, group_b):
        """
        Assumptions: group_a and group_b are normally distributed, independent samples with unequal variances
        Source: https://en.wikipedia.org/wiki/Welch%27s_t-test
        """
        self.validate_numeric_sample(group_a)
        self.validate_numeric_sample(group_b)
        t_result = ttest_ind(group_a, group_b, equal_var=False)
        return float(t_result.statistic)

    @staticmethod
    def validate_numeric_sample(values):
        if len(values) == 0:
            raise EmptySampleError()
        for value in values:
            try:
                float(value)
            except ValueError as e:
                raise NonNumericError(value)
    
    @staticmethod
    def safe_divide(denominator: float) -> float:
        """
        TODO this is should replace division in this logic, and handle 0's
        """
        if denominator == 0:
            raise ZeroDivisionError
        return denominator
    
    

class CalculatorError(Exception):
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(message)

class NonNumericError(CalculatorError):
    def __init__(self, value):
        super().__init__(f"Encountered invalid value: {value} is of type {type(value)}. All values must be numeric.")

class EmptySampleError(CalculatorError):
    def __init__(self):
        super().__init__("Empty sample submitted cannot be used for statistical calculation.")

class InsufficientSampleSizeError(CalculatorError):
    def __init__(self, sample_size, minimum_size): # TODO write a better message
        super().__init__(f"Sample size {sample_size} is below the minimum required size of {minimum_size}.")
