from typing import Union


class A:
    x = 1


class Calculator:
    def divide(self, x: Union[int, float], y: Union[int, float]) -> int | float:
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise TypeError("Both arguments shoud be numeric")
        if y == 0:
            raise ZeroDivisionError("Cannot devide by zero")

        return x / y

    def add(self, x: Union[int, float], y: Union[int, float]) -> int | float:
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise TypeError("Both arguments shoud be numeric")

        return x + y


if __name__ == "__main_test__":
    calculator = Calculator()
