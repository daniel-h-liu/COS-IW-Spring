count = 0
with open("shakespeare.txt") as file:
    for line in file:
        if line.strip() == "ACT I":
            count += 1

print(count / 2)
