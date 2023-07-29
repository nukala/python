# https://realpython.com/python-kwargs-and-args/
def concatenate(**elems):
    result = ""
    # Iterating over the Python kwargs dictionary
    for arg in elems.values():
        result += " " + str(arg)
    print(elems)
    return result

print(concatenate(a="Real", b="Python", c="Is", d="Great", e="!", f=123))
