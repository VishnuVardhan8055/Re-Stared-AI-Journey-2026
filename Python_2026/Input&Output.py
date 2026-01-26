" Here We are Learning about Input and Output "

# 1 --> We are taking input using input function input(), for to get Output we use Output function print().

A = input("Taking input and Assing the input into a variable name A : ") #---> inside input() func we kept comments for a user understanding porpouse
print("Your Input is Assined to Variable to A. Here is the Output: ---> "+A)

# 2 --> We are a Strict while taking a Input on int, float, Str, Char et...

#----> Here we are taking Strict Int type as a input, for this we use int function. Note int(input())
B = int(input("Taking only Int as Input : "))
print(B)


#----> Here we are taking Strict FLoat type as a input, for this we use int function. Note float(input())
C = float(input("Taking only Float as Input : "))
print(C)

#----> Here we are taking Strict bool type as a input, for this we use int function. Note bool(input()) D= bool(input()) it will print always true. So we use the condtional Input here.
D = input("Taking only bool as Input : ").strip()in"1,True,Yes,y"
#It will print True only when If input is 1, Ture, Yes, y else it will print False.
print(D)

" ========================================================  =====================  ======================================================"


# 3. Here we are learning about Formate-Strings for Output strictly.

name = "Vishnu"
age = 23
height = 5.750
"Here we use f for make it formated. "
"{name:conditon} Aligns left, integer, float[web:50]"
print(f"Hello, {name:<2}! Age: {age:d}, Pi: {height:.2f}")

'''' ==================================================    =======================   ================================================= '''

# 4. Here we are using ternary functionallity to print the strict output.
num = int(input("Enter integer: "))
print(f"Output: {num}" if num < 50 else "")


 #4.1 we can use Short circut method.

num = int(input("Enter integer: "))
(num < 50) and print(f"Output: {num}")


'''' ==================================================    =======================   ================================================= '''

# here we are using  functions max, min. for to take input from range 0 to 120
age = max(0, min(120, int(input("Age: "))))  # Clamps 0-120
print(age)




