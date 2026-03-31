import math
import statistics

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
            raise InsufficientSampleSizeError(len(values)) # TODO should this just return None
        return statistics.stdev(values)
    
    def pooled_standard_deviation(self, group_a, group_b):
        """
        Weighted pooled standard deviation
        Source: https://resources.nu.edu/statsresources/cohensd
        """
        self.validate_numeric_sample(group_a)
        self.validate_numeric_sample(group_b)
        variance_group_a = statistics.variance(group_a)
        variance_group_b = statistics.variance(group_b)
        pooled_stdev = math.sqrt(
            ((len(group_a) - 1) * variance_group_a + (len(group_b) - 1) * variance_group_b) / (len(group_a) + len(group_b) - 2)
        )
        return pooled_stdev
    
    def pooled_standard_error(self, group_a, group_b):
        """
        Source: https://stats.libretexts.org/Bookshelves/Introductory_Statistics/Statistics%3A_Open_for_Everyone_(Peter)/08%3A_Independent_Samples_t-Tests/8.03%3A_The_Independent_Samples_t-Test_Formula
        """
        pooled_std_error = self.pooled_standard_deviation(group_a, group_b) * \
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
        mean_diff = self.mean(group_a) - self.mean(group_b)
        pooled_stdev = math.sqrt(
            (self.standard_deviation(group_a) + self.standard_deviation(group_b)) / 2
        ) # TODO can this be 0?
        return mean_diff / pooled_stdev

    def hedges_g(self, group_a, group_b):
        """
        This is best for smaller sample sizes
        """
        mean_diff = self.mean(group_a) - self.mean(group_b)
        pooled_stdev = self.pooled_standard_deviation(group_a, group_b)
        return mean_diff / pooled_stdev

    def independent_t_test(self, group_a, group_b):
        """
        TODO I don't think this is what we used in the paper
        """
        mean_diff = self.mean(group_a) - self.mean(group_b)
        pooled_sterror = self.pooled_standard_error(group_a, group_b)
        return mean_diff / pooled_sterror

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
    def safe_divide(numerator, denominator: float):
        """
        TODO this is should replace division in this logic, and handle 0's
        """
        if denominator == 0:
            raise ZeroDivisionError
    

class CalculatorError(Exception):
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(message)

class NonNumericError(CalculatorError):
    def __init__(self, value):
        super().__init__(f"Encountered invalid value: {value} is of type {type(value)}. All values must be numeric.")

class EmptySampleError(CalculatorError):
    def __init__(self):
        super().__init__("Empty sample cannot be used for statistical calculation.") # TODO write a better exception

class InsufficientSampleSizeError(CalculatorError):
    def __init__(self, sample_size): # TODO write a better message
        super().__init__(f"There are not sufficient values given. Sample size: {sample_size}.")
