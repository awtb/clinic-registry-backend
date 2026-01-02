from dataclasses import dataclass
from typing import Generic
from typing import TypeVar


@dataclass
class BaseDTO:
    """Base data-transfer object."""


T = TypeVar("T", bound=BaseDTO)


@dataclass
class PageDTO(
    BaseDTO,
    Generic[T],
):
    items: list[T]
    page_size: int
    total_pages: int
    total_items: int
    page: int
