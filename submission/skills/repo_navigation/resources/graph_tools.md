# Graph tool cheat sheet

## Symbol ids

Nodes use fully qualified Python paths, for example:

- `fastapi.routing.APIRouter.add_api_route`
- `rich.console.Console.print`

Use the exact id strings returned by `search_similar_code` or graph JSON in the dataset.

## `get_code_neighbors`

- **node** — qualified symbol id.
- **edge_type** — optional filter (e.g. `calls`); omit to see all edge types.
- **max_neighbors** — cap fan-out (default 50). Increase only when necessary.

Strategy: expand 1–2 hops from the top semantic hit, not the entire graph.

## `get_code_subgraph`

Provide a **small** list of nodes (3–12) that form a suspected call chain or module cluster.
The returned induced subgraph helps you see how a bug propagates.

## `search_similar_code`

Craft queries from the issue title, exception type, API names, and error strings.
Run multiple queries with different phrasing before giving up on retrieval.
