"""Drivers for the simulation"""

from location import Location, manhattan_distance
from rider import Rider
from typing import Optional


class Driver:
    """A driver for a ride-sharing service.

    === Attributes ===
    id:
        A unique identifier for the driver.
    location:
        The current location of the driver.
    is_idle:
        True if the driver is idle and False otherwise.
    speed:
        Speed of the car (Constant)
    destination:
        Location that the driver needs to reach. Can be None.
    """
    id: str
    location: Location
    is_idle: bool
    speed: int
    destination: Optional[Location]

    def __init__(self, identifier: str, location: Location, speed: int) -> None:
        """Initialize a Driver.

        """
        self.id = identifier
        self.location = location
        self.is_idle = True
        self.speed = speed
        self.destination = None

    def __str__(self) -> str:
        """Return a string representation.

        """
        return f'Driver is {self.id}, drives at speed {self.speed}, ' \
               f'located at {self.location} Idle?:{self.is_idle}'

    def __eq__(self, other: object) -> bool:
        """Return True if self equals other, and false otherwise.

        """
        return self.id == other.id

    def get_travel_time(self, destination: Location) -> int:
        """Return the time it will take to arrive at the destination,
        rounded to the nearest integer.

        """
        # distance / time is speed -> distance / speed gives us time
        return round(manhattan_distance(self.location, destination) /
                     self.speed)

    def start_drive(self, location: Location) -> int:
        """Start driving to the location.
        Return the time that the drive will take.

        """
        self.is_idle = False
        return self.get_travel_time(location)

    def end_drive(self) -> None:
        """End the drive and arrive at the destination.

        Precondition: self.destination is not None.

        """
        self.is_idle = True

    def start_ride(self, rider: Rider) -> int:
        """Start a ride and return the time the ride will take.

        (As per my design, start_ride will be called only when driver starts
        going to pick up the rider.)
        """
        self.is_idle = False
        self.location = rider.origin
        self.destination = rider.destination

        return self.get_travel_time(rider.destination)

    def end_ride(self, rider: Rider) -> None:
        """End the current ride, and arrive at the rider's destination.

        Precondition: The driver has a rider.
        Precondition: self.destination is not None.

        """
        self.is_idle = True
        self.location = rider.destination
        self.destination = None
        # self.location =  (when do I change the location? when starting or
        # ending?) I changed it here!


if __name__ == '__main__':
    pass
    # import python_ta
    # python_ta.check_all(
    #     config={'extra-imports': ['location', 'rider']})
