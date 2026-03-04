import os
from geometric_lib import circle, square

shape = os.getenv("SHAPE")
value = float(os.getenv("VALUE"))

if shape == "circle":
    print("Circle:")
    print("Area:", circle.area(value))
    print("Perimeter:", circle.perimeter(value))

elif shape == "square":
    print("Square:")
    print("Area:", square.area(value))
    print("Perimeter:", square.perimeter(value))

else:
    print("Unknown shape")