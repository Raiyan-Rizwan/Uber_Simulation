"""Dispatcher for the simulation"""

from typing import Optional
from driver import Driver
from rider import Rider, CANCELLED


class Dispatcher:
    """A dispatcher fulfills requests from riders and drivers for a
    ride-sharing service.

    When a rider requests a driver, the dispatcher assigns a driver to the
    rider. If no driver is available, the rider is placed on a waiting
    list for the next available driver. A rider that has not yet been
    picked up by a driver may cancel their request.

    When a driver requests a rider, the dispatcher assigns a rider from
    the waiting list to the driver. If there is no rider on the waiting list
    the dispatcher does nothing. Once a driver requests a rider, the driver
    is registered with the dispatcher, and will be used to fulfill future
    rider requests.

    === Private Attributes ===
    _available_drivers:

    _passenger_wait_list:

    """
    _available_drivers: list
    _passenger_wait_list: list

    def __init__(self) -> None:
        """Initialize a Dispatcher.

        """
        self._available_drivers = []
        self._passenger_wait_list = []

    def __str__(self) -> str:
        """Return a string representation.

        """
        return f'Available Drivers: {len(self._available_drivers)}, ' \
               f'Passenger Wait-list: {self._passenger_wait_list}'

    def request_driver(self, rider: Rider) -> Optional[Driver]:
        """Return a driver for the rider, or None if no driver is available.

        Add the rider to the waiting list if there is no available driver.

        """
        if len(self._available_drivers) > 0:
            # algorithm to get the fastest driver
            fastest_driver = self._available_drivers[0]
            fastest_driver_time = self._available_drivers[0].\
                get_travel_time(rider.origin)
            for i in range(len(self._available_drivers)):
                driver = self._available_drivers[i]  # driver we use to compare
                time_to_arrive = driver.get_travel_time(rider.origin)
                if time_to_arrive < fastest_driver_time:
                    fastest_driver = driver  # this driver is faster, so change
                    fastest_driver_time = time_to_arrive  # change time too
            self._available_drivers.remove(fastest_driver)
            return fastest_driver
        else:
            self._passenger_wait_list.append(rider)
            return None

    def request_rider(self, driver: Driver) -> Optional[Rider]:
        """Return a rider for the driver, or None if no rider is available.

        If this is a new driver, register the driver for future rider requests.

        """
        if len(self._passenger_wait_list) > 0:
            return self._passenger_wait_list.pop(0)
        else:
            if driver not in self._available_drivers:
                self._available_drivers.append(driver)
            return None

    def cancel_ride(self, rider: Rider) -> None:
        """Cancel the ride for rider.

        """
        rider.status = CANCELLED
        if rider in self._passenger_wait_list:
            self._passenger_wait_list.remove(rider)


if __name__ == '__main__':
    pass
    # import python_ta
    # python_ta.check_all(config={'extra-imports': ['typing', 'driver', 'rider']})
