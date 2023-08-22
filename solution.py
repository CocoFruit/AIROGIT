
# Step 1: Read the number of test cases
t = int(input())

# Step 2: Repeat the following steps t times
for _ in range(t):
    # Step 3: Read the values of a, b, and c
    a, b, c = map(int, input().split())

    # Step 4: Calculate the maximum number of turns
    max_turns = a + b

    # Step 5: Check if c is greater than or equal to the maximum number of turns
    if c >= max_turns:
        print("First")
    else:
        # Step 6: Check if a is smaller than or equal to b
        if a <= b:
            print("First")
        else:
            # Step 7: If a is greater than b
            print("Second")
