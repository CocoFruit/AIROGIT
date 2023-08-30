
def solve_sorting(t, test_cases):
    for _ in range(t):
        n = test_cases[_]["n"]
        a = test_cases[_]["a"]
        
        operations = 0
        sorted_array = False
        
        while not sorted_array:
            sorted_array = True
            
            for i in range(1, n):
                if a[i] < a[i-1]:
                    a[i] = max(0, a[i-1])
                    operations += 1
                    sorted_array = False
        
        print(operations)

t = int(input())
test_cases = []

for _ in range(t):
    n = int(input())
    a = list(map(int, input().split()))
    
    test_case = {
        "n": n,
        "a": a
    }
    
    test_cases.append(test_case)

solve_sorting(t, test_cases)

