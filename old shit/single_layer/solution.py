To solve this problem, we need to count the number of operations Alphen will perform to sort the array. 

We can do this by iterating through the array and comparing each element with its previous element. If the current element is smaller than the previous element, we need to perform an operation to make it equal or greater than the previous element. 

Here is the step-by-step approach to solve this problem:

1. Read the number of test cases, t.

2. Repeat the following steps for each test case:
   a. Read the length of the array, n.
   b. Read the elements of the array, a.

3. For each test case, initialize the operations count to 0.

4. Iterate through the array from index 1 to n-1.
   a. If the current element is smaller than the previous element, update the current element to be equal to the previous element and increment the operations count by 1.

5. Print the operations count for each test case.

Let's implement this algorithm in code.