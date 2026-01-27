""" Python lists are mutable, ordered collections that store multiple items using square brackets []. """

# Empty List [] --> We are assigning to Variable A = []

A = []

"| Method    | Syntax                   | Example                      | Result              |"
"| --------- | ------------------------ | ---------------------------- | ------------------- |"
"| append()  | list.append(item)        | nums = [1,2]; nums.append(3) | [1,2,3]             |"
"| extend()  | list.extend(iterable)    | nums.extend([4,5])           | [1,2,3,4,5]         |"
"| insert()  | list.insert(index, item) | nums.insert(0, 0)            | [0,1,2,3,4,5]       |"
"| pop()     | list.pop([index])        | nums.pop()                   | 5, list=[0,1,2,3,4] |"
"| remove()  | list.remove(item)        | nums.remove(1)               | [0,2,3,4]           |"
"| clear()   | list.clear()             | nums.clear()                 | []                  |"
"| sort()    | list.sort()              | nums.sort(reverse=True)      | Sorted list         |"
"| reverse() | list.reverse()           | nums.reverse()               | Reversed order      |"

# How to add the data in to the list. we can use append method, or insert method.
"append method will always add the data at end of the list , while insert method add's based on the user defiend position (index) "
"And more Extend method this one will add a sequence data at the end of the list"

#Note : A list have a Index value based on that it will store the data in the list. Indexing it is concept of where the data placed in list.

" [ |1|, |2|, |3|, |4|, |5|, |6| ] "  # len of list is 5
"    ^    ^    ^    ^    ^    ^    "
"    0    1    2    3    4    5    "  # It is Index of the each data placed in the list. By using index we can get, place, update, or delete data in the list.

Input = input(" Enter the input data to add into the list : ")

A.append(Input)

print("Data Append to the list : ",A)

Input = input(" Enter the input data to add into the list : ")

A.insert(1,Input)

print("Data Insert to the list : ",A)
B = A.copy()

A.extend(A)
print("Data Extended to the list : ",A)


# We can delete the data in list in 3 ways. 1. is POP, 2 is Remove, 3. is Clear

A.remove('1')
print("Data removed from the list : ",A) # remove function use only data to remove the data from the list.
A.pop(-1)
print("Data Extended from the list : ",A) # pop function use only index to pop the data from the list.

A.clear()
print("Entire Data clear from the list : ",A) # clear function is clear the entire data from the list.

# Sorting we can sort the list based on numeric, or char wise into ascending order, or descending order.
B.sort() #---> By default this sort function will sort in ascending order.
print("List sorted in Ascending order : ", B)

B.sort(reverse=True) #---> By default this sort function will sort in ascending order, if we guve reverse=true it will sort into a descending order.
print("List sorted in Descending order : ", B)

B.reverse()
print("Reversed List: ", B)









