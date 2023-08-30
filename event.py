"""Simulation Events

This file should contain all of the classes necessary to model the different
kinds of events in the simulation.
"""
from __future__ import annotations
from typing import List
from rider import Rider, WAITING, CANCELLED, SATISFIED
from dispatcher import Dispatcher
from driver import Driver
from location import deserialize_location
from monitor import Monitor, RIDER, DRIVER, REQUEST, CANCEL, PICKUP, DROPOFF


class Event:
    """An event.

    Events have an ordering that is based on the event timestamp: Events with
    older timestamps are less than those with newer timestamps.

    This class is abstract; subclasses must implement do().

    You may, if you wish, change the API of this class to add
    extra public methods or attributes. Make sure that anything
    you add makes sense for ALL events, and not just a particular
    event type.

    Document any such changes carefully!

    === Attributes ===
    timestamp: A timestamp for this event.
    """

    timestamp: int

    def __init__(self, timestamp: int) -> None:
        """Initialize an Event with a given timestamp.

        Precondition: timestamp must be a non-negative integer.

        >>> Event(7).timestamp
        7
        """
        self.timestamp = timestamp

    # The following six 'magic methods' are overridden to allow for easy
    # comparison of Event instances. All comparisons simply perform the
    # same comparison on the 'timestamp' attribute of the two events.
    def __eq__(self, other: Event) -> bool:
        """Return True iff this Event is equal to <other>.

        Two events are equal iff they have the same timestamp.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first == second
        False
        >>> second.timestamp = first.timestamp
        >>> first == second
        True
        """
        return self.timestamp == other.timestamp

    def __ne__(self, other: Event) -> bool:
        """Return True iff this Event is not equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first != second
        True
        >>> second.timestamp = first.timestamp
        >>> first != second
        False
        """
        return not self == other

    def __lt__(self, other: Event) -> bool:
        """Return True iff this Event is less than <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first < second
        True
        >>> second < first
        False
        """
        return self.timestamp < other.timestamp

    def __le__(self, other: Event) -> bool:
        """Return True iff this Event is less than or equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first <= first
        True
        >>> first <= second
        True
        >>> second <= first
        False
        """
        return self.timestamp <= other.timestamp

    def __gt__(self, other: Event) -> bool:
        """Return True iff this Event is greater than <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first > second
        False
        >>> second > first
        True
        """
        return not self <= other

    def __ge__(self, other: Event) -> bool:
        """Return True iff this Event is greater than or equal to <other>.

        >>> first = Event(1)
        >>> second = Event(2)
        >>> first >= first
        True
        >>> first >= second
        False
        >>> second >= first
        True
        """
        return not self < other

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        raise NotImplementedError("Implemented in a subclass")

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Do this Event.

        Update the state of the simulation, using the dispatcher, and any
        attributes according to the meaning of the event.

        Notify the monitor of any activities that have occurred during the
        event.

        Return a list of new events spawned by this event (making sure the
        timestamps are correct).

        Note: the "business logic" of what actually happens should not be
        handled in any Event classes.

        """
        raise NotImplementedError("Implemented in a subclass")


class RiderRequest(Event):
    """A rider requests a driver.

    === Attributes ===
    rider: The rider.
    """

    rider: Rider

    def __init__(self, timestamp: int, rider: Rider) -> None:
        """Initialize a RiderRequest event.

        """
        super().__init__(timestamp)
        self.rider = rider

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Assign the rider to a driver or add the rider to a waiting list.
        If the rider is assigned to a driver, the driver starts driving to
        the rider.

        Return a Cancellation event. If the rider is assigned to a driver,
        also return a Pickup event.

        """
        monitor.notify(self.timestamp, RIDER, REQUEST,
                       self.rider.id, self.rider.origin)

        events = []
        driver = dispatcher.request_driver(self.rider)
        if driver is not None:
            travel_time = driver.start_drive(self.rider.origin)
            events.append(Pickup(self.timestamp + travel_time,
                                 self.rider, driver))
        events.append(Cancellation(self.timestamp + self.rider.patience,
                                   self.rider))
        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return "{} -- {}: Request a driver".format(self.timestamp, self.rider)


class DriverRequest(Event):
    """A driver requests a rider.

    === Attributes ===
    driver: The driver.
    """

    driver: Driver

    def __init__(self, timestamp: int, driver: Driver) -> None:
        """Initialize a DriverRequest event.

        """
        super().__init__(timestamp)
        self.driver = driver

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """Register the driver, if this is the first request, and
        assign a rider to the driver, if one is available.

        If a rider is available, return a Pickup event.

        """
        # Notify the monitor about the request.

        # Request a rider from the dispatcher.
        # If there is one available, the driver starts driving towards the
        # rider, and the method returns a Pickup event for when the driver
        # arrives at the riders location.
        monitor.notify(self.timestamp, DRIVER, REQUEST, self.driver.id,
                       self.driver.location)  # we want location of driver and
        # not passenger since our subject is the driver.
        events = []
        rider = dispatcher.request_rider(self.driver)
        if rider is not None:
            travel_time = self.driver.start_drive(rider.origin)
            if travel_time > rider.patience:
                events.append(Cancellation(self.timestamp + rider.patience,
                                           rider))
            events.append(Pickup(self.timestamp + travel_time, rider,
                                 self.driver))

        return events

    def __str__(self) -> str:
        """Return a string representation of this event.

        """
        return "{} -- {}: Request a rider".format(self.timestamp, self.driver)


class Cancellation(Event):
    """
    Event in which rider cancels the ride.

    === Attributes ===
    rider:
        rider who is doing the action of cancellation
    """
    rider: Rider

    def __init__(self, timestamp: int, rider: Rider) -> None:
        super().__init__(timestamp)
        self.rider = rider

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """
        Change a waiting rider to a cancelled rider, and remove from
        wait-list.
        """
        events = []
        if self.rider.status == WAITING:
            self.rider.status = CANCELLED
            monitor.notify(self.timestamp, RIDER, CANCEL, self.rider.id,
                           self.rider.origin)
            dispatcher.cancel_ride(self.rider)

        return events

    def __str__(self) -> str:
        """
        String representation of subclass Cancel.
        """
        return f"{self.timestamp} -- {self.rider}: Cancel Ride"


class Pickup(Event):
    """
    Event in which the rider is picked up.

    === Attributes ===
    rider:
        rider who is being picked up
    driver:
        driver who is picking the passenger up.
    """
    rider: Rider
    driver: Driver

    def __init__(self, timestamp: int, rider: Rider, driver: Driver) -> None:
        super().__init__(timestamp)
        self.rider = rider
        self.driver = driver

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """
        Sets the driver’s location to the rider’s location. If
        the rider is waiting,the driver begins giving them a trip and the
        driver’s destination becomes the rider’s destination. At the same time,
        a drop-off event is scheduled for the time they will arrive at the
        rider’s destination,and the rider becomes satisfied. If the rider has
        cancelled, a new event for the driver requesting arider is scheduled to
        take place immediately, and the driver has no destination for the
        moment.
        """
        events = []
        time_to_pickup = self.driver.start_drive(self.rider.origin)
        if self.rider.status == WAITING:
            self.driver.location = self.rider.origin
            self.driver.start_ride(self.rider)
            monitor.notify(self.timestamp, DRIVER, PICKUP, self.driver.id,
                           self.driver.location)
            monitor.notify(self.timestamp, RIDER, PICKUP, self.rider.id,
                           self.rider.origin)

        # as per my design, I decided to calculate the time from drivers current
        # location to customer's location, by which I will change the timestamp
            self.rider.status = SATISFIED
            events.append(Dropoff(self.timestamp + time_to_pickup, self.rider,
                                  self.driver))
            return events

        elif self.rider.status == CANCELLED:
            self.driver.location = self.rider.origin
            self.driver.destination = None
            events.append(DriverRequest(self.timestamp + time_to_pickup,
                                        self.driver))
            monitor.notify(self.timestamp, DRIVER, CANCEL,
                           self.driver.id, self.driver.location)

            return events

    def __str__(self) -> str:
        """
        String representation of child class, Pickup.
        """
        return f"{self.timestamp} -- {self.driver}: Pickup rider, {self.rider}"


class Dropoff(Event):
    """
    Event of dropping off a rider.

    === Attributes ===
    rider:

    driver:

    """
    rider: Rider
    driver: Driver

    def __init__(self, timestamp: int, rider: Rider, driver: Driver) -> None:
        super().__init__(timestamp)
        self.rider = rider
        self.driver = driver

    def do(self, dispatcher: Dispatcher, monitor: Monitor) -> List[Event]:
        """
        A drop-off event sets the driver’s location to the rider’s destination.
        The driver needs more work, so a new event for the driver requesting a
        rider is scheduled to take place immediately, and the driver has no
        destination for the moment.
        """
        events = []
        self.driver.location = self.rider.destination
        monitor.notify(self.timestamp, DRIVER, DROPOFF, self.driver.id,
                       self.driver.destination)
        monitor.notify(self.timestamp, RIDER, DROPOFF, self.rider.id,
                       self.rider.destination)
        self.driver.end_ride(self.rider)
        events.append(DriverRequest(self.timestamp, self.driver))
        return events

    def __str__(self) -> str:
        """
        String representation of child class, Pickup.
        """
        return f"{self.timestamp} -- {self.driver}: " \
               f"Drop-off rider, {self.rider}"


def create_event_list(filename: str) -> List[Event]:
    """Return a list of Events based on raw list of events in <filename>.

    Precondition: the file stored at <filename> is in the format specified
    by the assignment handout.

    filename: The name of a file that contains the list of events.
    """
    events = []
    with open(filename, "r") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                # Skip lines that are blank or start with #.
                continue

            # Create a list of words in the line, e.g.
            # ['10', 'RiderRequest', 'Cerise', '4,2', '1,5', '15'].
            # Note that these are strings, and you'll need to convert some
            # of them to a different type.
            tokens = line.split()
            timestamp = int(tokens[0])
            event_type = tokens[1]

            # HINT: Use Location.deserialize to convert the location string to
            # a location.

            if event_type == "DriverRequest":
                # Create a DriverRequest event.
                driver_id = tokens[2]
                driver_speed = int(tokens[4])
                driver_location = deserialize_location(tokens[3])
                driver = Driver(driver_id, driver_location, driver_speed)
                event = DriverRequest(timestamp, driver)

            elif event_type == "RiderRequest":
                # Create a RiderRequest event.
                rider_id = tokens[2]
                rider_patience = int(tokens[5])
                rider_origin = deserialize_location(tokens[3])
                rider_destination = deserialize_location(tokens[4])
                rider = Rider(rider_id, rider_patience, rider_origin,
                              rider_destination)
                event = RiderRequest(timestamp, rider)
            events.append(event)

    return events


if __name__ == '__main__':
    pass
    # import python_ta
    # python_ta.check_all(
    #     config={
    #         'allowed-io': ['create_event_list'],
    #         'extra-imports': ['rider', 'dispatcher', 'driver',
    #                           'location', 'monitor']})
