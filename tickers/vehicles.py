"""
Tickers for vehicles.
"""

from typeclasses.vehicles import Vehicle

def move():
    """Move the vehicles around."""
    vehicles = Vehicle.objects.all()
    for vehicle in vehicles:
        vehicle.move()
