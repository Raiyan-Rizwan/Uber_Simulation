"""Locations for the simulation"""

from __future__ import annotations


class Location:
    """A two-dimensional location.

    === Attributes ===

    Do rows correspond to x coordinate or y coordinate?

    row:
        location in terms of y coordinate
    column:
        location in terms of x coordinate
    """

    def __init__(self, row: int, column: int) -> None:
        """Initialize a location.

        """
        self.row = row
        self.col = column

    def __str__(self) -> str:
        """Return a string representation.

        """
        return f'({self.row}, {self.col})'

    def __eq__(self, other: Location) -> bool:
        """Return True if self equals other, and false otherwise.

        """
        return self == other


def manhattan_distance(origin: Location, destination: Location) -> int:
    """Return the Manhattan distance between the origin and the destination.

    """
    return abs(origin.row - destination.row) + abs(origin.col - destination.col)


def deserialize_location(location_str: str) -> Location:
    """Deserialize a location.

    location_str: A location in the format 'row,col'
    """
    separated = location_str.split(',')
    return Location(int(separated[0]), int(separated[1]))


if __name__ == '__main__':
    pass
    # import python_ta
    # python_ta.check_all()
