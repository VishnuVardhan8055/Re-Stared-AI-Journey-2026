# BINARY WATCH PROBLEM
""" """
" The question is Binary Watch asking about the bit count of the given turnedon value. "

def Binarywatch(turnedon :int) -> list[str]:

    if turnedon > 8: return []
    ans = []
    for hour in range(12):
        for minute in range(60):
            if hour.bit_count() + minute.bit_count() == turnedon.bit_count():
                ans.append(f"{hour}:{minute:02d}")

    return ans
turnedon = int(input("Eneter the value for Binary watch : "))
Binary = Binarywatch(turnedon)
print(Binary)

# ====================================*============================================================================





