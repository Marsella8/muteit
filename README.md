Fun toy project for working with computation graph non-semantically equivalent mutations.

How it works:
- Define a DSL
- Build a program using the DSL
The engine will convert your program to a computation graph and apply intermediate mutations (changing inputs, changing operators, adding new operators), while still making sure it type-checks.