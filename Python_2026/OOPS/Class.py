""" Class is a Blue-print of an Object and Template"""

class OOPS:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def details(self):
        return f"{self.name}, {self.age} "

name = "vishnu vardhan polanki"
age = 23
OBJ = OOPS(name, age)
print("Here I am calling the class itself i will call the function, And it is Constructor"," \n",OBJ.details())