class VehicleError(Exception):
    """Vehicle exception class"""

    pass


class VehicleAsleep(VehicleError):
    pass


class VehicleTimeout(VehicleError):
    pass


class VehicleInvalidShare(VehicleError):
    pass
