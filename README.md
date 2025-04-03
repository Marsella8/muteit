Library for custom program mutation.

Write a custom DSL and a starting program. The engine will:
- Turn it into a computation graph.
- Find all available substitutions which are type compatible.
- Select a substitution and apply it.

Different substitution engines are available, such as random and mcts style mutation
