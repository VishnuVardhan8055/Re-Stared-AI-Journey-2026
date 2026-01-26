"""In python an Operator is a symbol used to perform a operation, it can be either arthematical or logical"""
" Type of Operations:  1. Arthematic Operation : +, -, *, %, /, **, //                                 "
"                      2. Assignment Operation : =, +=, -=, *=, %=, **=, //=, &=, /=, ^=, ~= <<=, >>=  "
"                      3. Bitwise Operation    : &, |, ^                                               "
"                      4. Logical Operation    : and, or, not                                          "
"                      5. Relational Operation : <, >, ==, <= ,>=, !=                                  "
"                      6. Identity Operation   : is, is not                                            "
"                      7. Memberhip Operation  : in, not in                                            "

print('==================================================================================================================')

"1. Arthematic Operation : +, -, *, %, /, **, //"

A, B = 2, 6
print("Addition : ",A+B)
print("Subraction : ",A-B)
print("Multiplication : ",A*B)
print("Modules Division It will print reminder : ", A%B)
print("Division It will print Quotent : ", A/B)
print("Exponential Power : ", A**B)
print("Division It will print only Int Quotent : ", A//B)

print('==================================================================================================================')


'2. Assignment Operation : =, +=, -=, *=, %=, **=, //=, &=, /=, ^=, ~= <<=, >>='

C = 5
C += C
print("C += : ",C)
C -= 2
print("C -= : ",C)
C *= C
print("C *= : ",C)
C %= C-2
print("C %= : ",C)
C **= C
print("C **= : ",C)
C &= C
print("C &= : ",C)
C |= C     # OR self  = same
print("C |= : ", C)

C <<= 2    # Left shift x2 = x4
print("C <<= : ", C)
C >>= 1    # Right shift = halve
print("C >>= : ", C)
C ^= C     # XOR self = 0
print("C ^= : ", C)

print('==================================================================================================================')

" 3. Bitwise Operation    :   &, |, ^       "

print("\n3. Bitwise Operation    : &, |, ^")

A, B = 5, 3  # 101, 011 (binary)

print("A =", A, "=", bin(A))      # A = 5 = 0b101
print("B =", B, "=", bin(B))      # B = 3 = 0b11

print("A & B =", A & B, "=", bin(A & B), "Int", int(A&B))  # 101 & 011 = 001 = 1
print("A | B =", A | B, "=", bin(A | B), "Int", int(A|B))  # 101 | 011 = 111 = 7
print("A ^ B =", A ^ B, "=", bin(A ^ B), "Int", int(A^B))  # 101 ^ 011 = 110 = 6

print('==================================================================================================================')

" 4.Logical Operation    : and, or, not  "

print("\n4. Logical Operation    : and, or, not ")

A, B = True, False

print("A =", A, "B =", B)
print("A and B =", A and B)    # True and False = False
print("A or B  =", A or B)     # True or False = True
print("not A   =", not A)      # not True = False
print("not B   =", not B)      # not False = True



print('==================================================================================================================')

" 5. Relational Operation : <, >, ==, <= ,>=, != "

print("\n5. Relational Operation : <, >, ==, <= ,>=, != ")

A, B = 10, 5

print(f"A = {A}, B = {B}")
print("A <  B  =", A < B)      # False
print("A >  B  =", A > B)      # True
print("A == B  =", A == B)     # False
print("A <= B  =", A <= B)     # False
print("A >= B  =", A >= B)     # True
print("A != B  =", A != B)     # True

print('==================================================================================================================')


print("\n6. Identity Operation   : is, is not")

A = [1, 2, 3]
B = [1, 2, 3]
C = A

print(f"A = {A}, B = {B}")
print("A is B     =", A is B)      # False (different memory addresses)
print("A is C     =", A is C)      # True (same memory address)
print("A is not B =", A is not B)  # True
print("id(A) =", hex(id(A)))
print("id(B) =", hex(id(B)))
print("id(C) =", hex(id(C)))

print('==================================================================================================================')



print("\n7. Membership Operation  : in, not in")

skills = ["Python", "SQL", "FastAPI"]
data = {"name": "Vishnu", "role": "TCS"}

print(f"skills = {skills}")
print('"Python" in skills    =', "Python" in skills)      # True
print('"Java" in skills     =', "Java" in skills)        # False
print('"Java" not in skills =', "Java" not in skills)    # True

print(f"data = {data}")
print('name' in data,       '=', 'name' in data)          # True
print('age' not in data,  '=', 'age' not in data)       # True

