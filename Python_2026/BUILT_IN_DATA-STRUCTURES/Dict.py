" Dictionaire "
" Python Dictionaries - mutable, unordered key-value collections using curly braces {}. "

"| Method   | Syntax                 | Example                           | Result                              |"
"| -------- | ---------------------- | --------------------------------- | ----------------------------------- |"
"| get()    | dict.get(key, default) | config.get('port', 80)            | 8080                                |"
"| keys()   | dict.keys()            | config.keys()                     | dict_keys(['host', 'port'])         |"
"| values() | dict.values()          | config.values()                   | dict_values(['localhost', 8080])    |"
"| items()  | dict.items()           | config.items()                    | dict_items([('host', 'localhost')]) |"
"| pop()    | dict.pop(key)          | config.pop('debug')               | True, key removed                   |"
"| update() | dict.update(other)     | config.update({'user': 'vishnu'}) | Adds/updates keys                   |"
"| clear()  | dict.clear()           | config.clear()                    | {}                                  |"
"| copy()   | dict.copy()            | backup = config.copy()            | Independent copy                    |"

# Empty Dictionary
A = {}

print("Enter key1: ")
k1 = input().strip()
print("Enter value1: ")
v1 = input().strip()
A[k1] = v1

print("Enter key2: ")
k2 = input().strip()
print("Enter value2: ")
v2 = input().strip()
A[k2] = v2

print("Original:", A)

# UPDATE TIME!
print("Enter key to UPDATE/ADD: ")
update_key = input().strip()
print("Enter new value: ")
update_value = input().strip()

# Method 1: Direct assignment (SINGLE key)
A[update_key] = update_value

# Method 2: update() for MULTIPLE keys
extra_updates = {"timestamp": "2026-01-27", "status": "completed"}
A.update(extra_updates)

print("FINAL Dictionary:", A)
print("All keys:", list(A.keys()))


A = {"name": "Vishnu", "job": "ETL"}

print("Original dictionary:", A)

# POP example
popped_value = A.pop("name")
print("Popped value:", popped_value)  # Vishnu
print("After pop:", A)                # {'job': 'ETL'}

# Add back for demo
A["name"] = "Vishnu"

# CLEAR example
A.clear()
print("After clear:", A)              # {}

# COPY example
original = {"host": "localhost", "port": 8080}
B = original.copy()
original["debug"] = True
print("Original:", original)          # Has debug
print("Copy B:", B)                   # No debug

