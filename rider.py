"""
The rider module contains the Rider class. It also contains
constants that represent the status of the rider.

=== Constants ===
WAITING: A constant used for the waiting rider status.
CANCELLED: A constant used for the cancelled rider status.
SATISFIED: A constant used for the satisfied rider status
"""

from location import Location

WAITING = "waiting"
CANCELLED = "cancelled"
SATISFIED = "satisfied"


class Rider:

    """A rider for a ride-sharing service.

    === Attributes ===
    id:
        A unique identifier for the rider
    origin:
        The origin from where the driver is picked up.
    destination:
        The rider's destination
    status:
        Rider's status states whether the rider is waiting, satisfied or has
        cancelled.
    patience:
        Number of time units the rider will wait to be picked up before
        cancelling

    === Representation Invariants ===
    status == SATISFIED or status == CANCELLED or status == WAITING
    patience >= 0
    """
    id: str
    patience: int
    origin: Location
    destination: Location
    status: str

    def __init__(self, identifier: str, patience: int, origin: Location,
                 destination: Location) -> None:
        """Initialize a Rider.

        """
        self.id = identifier
        self.patience = patience
        self.origin = origin
        self.destination = destination
        self.status = WAITING  # should I begin with WAITING?

    def __str__(self) -> str:
        """
        String representation of a rider
        """
        return self.id


if __name__ == '__main__':
    pass
    # import python_ta
    # python_ta.check_all(config={'extra-imports': ['location']})
