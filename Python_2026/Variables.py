" Here we are discussing about the Variables in python."

""" A Variable is used to hold the address of the data, when ever you called the variable it will call's the address and fetches the address data."""
""" A holds memory address of string object """
"""" A ---> #120!@#0(address of string object) --> "Data" """

A = input()
print("it is printing the data which in Variable : A Hold's address :  --> ",A)

print(f"Data from variable A: {A}")
print(f"Variable A holds address: {hex(id(A))}")
print(f"Direct data object address: {hex(id(A))}")

"Note: Variable must be start with char only."