# Empty tuple
empty = ()

# Single item (needs comma!)
single = (42,)     # NOT (42) - that's just int!

# Direct values
numbers = (1, 2, 3, 4, 5)
mixed = (1, "Vishnu", 3.14, True)

# From list/range
evens = tuple(range(0, 10, 2))       # (0, 2, 4, 6, 8)
chars = tuple("PYTHON")              # ('P', 'Y', 'T', 'H', 'O', 'N')

print("Numbers:", numbers)
print("Mixed:  ", mixed)
print("Length:", len(numbers))
