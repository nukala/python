student_scores = [150, 142, 185, 120, 171, 184, 149, 24, 59, 68, 199, 78, 65, 89, 86, 55, 91, 64, 89]
print(range(1, 10))

print(f"sum={sum(student_scores)}, max={max(student_scores)}")

total = 0
largest = -1
for s in student_scores:
    total += s
    if s > largest:
        largest = s

print(f"total={total}, largest={largest}")
