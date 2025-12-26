# levelup.gitconnected.com/working-with-data-in-python-596bbc6d6c2

fruits = [ 'apple', "banana", "cherry" ]
print(f"fruits as constructed={fruits}")

for num in -1, -3, -4, 0:
    if abs(num) > len(fruits):
        print(f"len={len(fruits)}, num={num}, too many!")
        continue
    print(f"fruit[{num}]={fruits[num]} ", end='')

fruits.append("Orange")
print(f"after 1 append=[{fruits}]")

fruits.insert(9, "mango")
print(f"off-the-scale insert={fruits}.{len(fruits)}")

print(f"pop.existing[{fruits.pop(4)}].{len(fruits)}")
print(f"{fruits}pop(-2)=[{fruits.pop(-2)}].{len(fruits)}")
# IndexError
#print(f"pop.too_large_number[{fruits.pop(9)}].{len(fruits)}")
fruits.insert(-1, "Cherry")
print(f"after insert(-1) {fruits}")
fruits.append("Orange")
fruits.append("mango")

print(f"=== slicing {fruits}.{len(fruits)}")
print(f"slice[:2] = {fruits[:2]}.{len(fruits)}")
print(f"slice[1:3] = {fruits[1:3]}.{len(fruits)}")
print(f"slice[:-2] = {fruits[:-2]}.{len(fruits)}")

## extend to add more than 1 element
fruits.extend(["kiwi", "grape"])
print(f"after extend-2-values {fruits}.{len(fruits)}")