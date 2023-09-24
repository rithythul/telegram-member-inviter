"""
The Platform is the environment that the program functionality is
based on and relied on its promises.

Copyright (C) 2023 @mjavadhpour. All Rights Reserved.
"""

__author__ = "M.J. HPour <@mjavadhpour>"
__status__ = "dev"
__version__ = "0.1"
__date__ = "20 September 2023"

__all__ = ['AbstractAction', 'Pipe']

from abc import ABC, abstractmethod
from typing import Any, NoReturn


class AbstractAction(ABC):
    @abstractmethod
    def invoke(self, value: Any) -> Any:
        pass

    def __or__(self, other: "AbstractAction") -> "Pipe":
        return Pipe(self, other)


class Pipe:
    def __init__(
        self, left: "AbstractAction|Pipe", right: "AbstractAction"
    ) -> NoReturn:
        self.left = left
        self.right = right

    def __or__(self, other: "AbstractAction") -> "Pipe":
        return Pipe(self, other)

    def invoke(self, value: Any) -> Any:
        if isinstance(self.left, Pipe):
            result = self.left.invoke(value)
        else:
            result = self.left.invoke(value)

        return self.right.invoke(result)
