# Empty set (MUST use set()!)
empty = set()      # NOT {} - that's empty dict!

# Direct values (auto-deduplicates)
numbers = {1, 2, 3, 2, 1}     # {1, 2, 3}
mixed = {1, "Vishnu", 3.14, True, 1}  # Duplicates gone!

# From other collections
evens = set(range(0, 10, 2))   # {0, 2, 4, 6, 8}
chars = set("PYTHON")          # {'P', 'Y', 'T', 'H', 'O', 'N'}

print("Numbers:", numbers)
print("Mixed:  ", mixed)
print("Length:", len(numbers))
D = {9,8,7,6,4,4,3,9}
mixed.update(D)
print("Usine update function to  the data : ",mixed)

#Mathematical

set1 = {1, 2, 3, 4}
set2 = {3, 4, 5, 6}

print("Union     :", set1 | set2)      # {1,2,3,4,5,6}
print("Intersect :", set1 & set2)      # {3,4}
print("Diff1-2   :", set1 - set2)      # {1,2}
print("Diff2-1   :", set2 - set1)      # {5,6}
print("Symmetric :", set1 ^ set2)       # {1,2,5,6}
print("Subset    :", set1 <= set2)     # False
