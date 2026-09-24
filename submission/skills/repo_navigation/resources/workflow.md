# Navigation workflow

1. Read the issue once; extract nouns (classes, functions, flags, error messages).
2. `search_similar_code` with each high-signal phrase (k=8–15).
3. Pick 2–4 nodes; `get_code_subgraph` to see relationships.
4. `read_file` definitions implicated by the subgraph.
5. `run_command` a minimal repro or targeted `pytest` node id.
6. Hand off a short plan to the root agent (or continue if you are root).

Avoid reading entire packages linearly — use the graph to steer.
