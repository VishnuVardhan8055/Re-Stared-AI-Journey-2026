""" Class is a Blue-print of an Object and Template"""

class OOPS:
    def __init__(self, name, age):
        self.name = name
        self.age = age


    def details(self):
        return f"{self.name}, {self.age} "

name = "vishnu vardhan polanki"
age = 23
Obj = OOPS(name, age)
print("Here I am calling the class function which returns the values","\n",Obj.details())

""" Object is an Instance of a Class """
"Here object we defined Obj it is instance of an OOPS class."