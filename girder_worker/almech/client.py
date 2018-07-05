# Import the fib task from almech package
from almech.calculations.tasks import fibonacci


if __name__ == '__main__':
    # Distribute the task to calculate the fibonacci number of 25
    async_result = fibonacci.delay(26)

    # Print the result of fib call
    print(async_result.get())
