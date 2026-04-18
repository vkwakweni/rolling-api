import math
import statistics
from scipy.stats import ttest_ind

class StatisticsCalculator:
    """
    A utility class for performing various statistical calculations on numeric data samples.

        The StatisticsCalculator class provides methods to calculate the mean, median, standard
    deviation, pooled standard deviation, Cohen's d, and Welch's t-test statistic for given
    numeric samples. It also includes validation to ensure that the input data is appropriate
    for these calculations.

        Each method assumes that the input samples are lists of numeric values and will raise
    exceptions if the samples are empty or contain non-numeric values.

    Methods
    -------
    mean(values)
        Returns the arithmetic mean of a set of values.
    median(values)
        Returns the median of a set of values.
    standard_deviation(values)
        Returns the standard deviation of a set of values.
    pooled_standard_deviation(group_a, group_b)
        Returns the pooled standard deviation of two groups, assuming equal variances and sample sizes.
    cohen_pooled_standard_deviation(group_a, group_b)
        Returns the pooled standard deviation of two groups, assuming equal variances but potentially unequal sample sizes.
    cohen_pooled_standard_error(group_a, group_b)
        Returns the pooled standard error of two groups, assuming equal variances but potentially unequal sample sizes.
    cohens_d(group_a, group_b)
        Returns Cohen's d, a measure of effect size that quantifies the difference between two groups in terms of standard deviations.
    welch_test(group_a, group_b)
        Returns the t-statistic from Welch's t-test, which is used to determine if there is a significant difference between the means of two groups.
    """
    def mean(self, values):
        """Returns the arithmetic mean of a set of values."""
        self.validate_numeric_sample(values)
        return statistics.mean(values)

    def median(self, values):
        """Returns the median of a set of values."""
        self.validate_numeric_sample(values)
        return statistics.median(values)
        
    def standard_deviation(self, values):
        """Returns the standard deviation of a set of values."""
        self.validate_numeric_sample(values)
        if len(values) <= 1:
            return None
        return statistics.stdev(values)
    
    def pooled_standard_deviation(self, group_a, group_b):
        """
        Returns the pooled standard deviation of two groups, assuming equal variances and sample sizes.

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
        Returns the pooled standard deviation of two groups, assuming equal variances but potentially unequal sample sizes.
        
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
        Returns the pooled standard error of two groups, assuming equal variances but potentially unequal sample sizes.

        Source: https://stats.libretexts.org/Bookshelves/Introductory_Statistics/Statistics%3A_Open_for_Everyone_(Peter)/08%3A_Independent_Samples_t-Tests/8.03%3A_The_Independent_Samples_t-Test_Formula
        """
        pooled_std_error = self.cohen_pooled_standard_deviation(group_a, group_b) * \
                                (math.sqrt(
                                    (len(group_a) + len(group_b)) / (len(group_a) * len(group_b))
                                ))
        return pooled_std_error


    def cohens_d(self, group_a, group_b):
        """
        Returns Cohen's d, a measure of effect size that quantifies the difference between two groups in terms of standard deviations.

        Cohen's d assumes that the two groups have equal variances and is calculated as the difference between the means of the two groups
        divided by the pooled standard deviation.

        Source: https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/hedgeg.htm
        TODO throw warning for length
        """
        mean_diff = float(self.mean(group_a) - self.mean(group_b))
        pooled_stdev = self.cohen_pooled_standard_deviation(group_a, group_b)
        return mean_diff / pooled_stdev
    
    def hedges_g(self, group_a, group_b):
        """
        Returns Hedge's g, a measure of effect size that quantifies the difference between two groups in terms of standard deviations, adjusted for small sample sizes.

        Hedge's g is similar to Cohen's d but includes a correction factor for small sample sizes. It is calculated as the difference between the means of the two groups
        divided by the pooled standard deviation, multiplied by a correction factor.

        Source: https://www.statisticshowto.com/hedges-g/; https://en.wikipedia.org/wiki/Effect_size
        TODO throw warning for length
        """
        mean_diff = float(self.mean(group_a) - self.mean(group_b))
        pooled_stdev = self.cohen_pooled_standard_deviation(group_a, group_b)
        correction_factor = 1 - (3 / (4 * (len(group_a) + len(group_b)) - 9))
        if len(group_a) < 50 and len(group_b) < 50:
            return (mean_diff / pooled_stdev) * correction_factor
        return mean_diff / pooled_stdev

    def welch_test(self, group_a, group_b):
        """
        Returns the t-statistic from Welch's t-test, which is used to determine if there is a significant difference between the means of two groups.

        It assumes that group_a and group_b are normally distributed, independent samples with unequal variances
        Source: https://en.wikipedia.org/wiki/Welch%27s_t-test
        """
        self.validate_numeric_sample(group_a)
        self.validate_numeric_sample(group_b)
        t_result = ttest_ind(group_a, group_b, equal_var=False)
        return float(t_result.statistic)

    @staticmethod
    def validate_numeric_sample(values):
        """Validates that the input is a non-empty list of numeric values."""
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
        Safely divides two numbers, handling division by zero.

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
