class VehicleError(Exception):
    """Vehicle exception class"""

    pass


class VehicleAsleep(VehicleError):
    pass


class VehicleTimeout(VehicleError):
    pass


class VehicleInvalidShare(VehicleError):
    pass


class CommandCooldown(Exception):
    def __init__(self, cooldown: int):
        super().__init__()
        self.cooldown = cooldown
