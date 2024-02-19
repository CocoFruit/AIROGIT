f = lambda x: [[y for j, y in enumerate(set(x)) if (i >> j) & 1] for i in range(2**len(set(x)))]

print(f([1,2,3]))

# bit shift 
# 0x1 