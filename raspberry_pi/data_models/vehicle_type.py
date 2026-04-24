from enum import Enum


class VehicleType(str, Enum):
    """
    Defines different vehicle types supported in the parking system.
    Used to categorize vehicles and determine applicable parking rates.
    """
    BIKE  = "bike"
    CAR   = "car"
    LORRY = "lorry"


# Parking rates in Rs. per hour
PARKING_RATES = {
    VehicleType.BIKE:  50,
    VehicleType.CAR:   100,
    VehicleType.LORRY: 130,
}