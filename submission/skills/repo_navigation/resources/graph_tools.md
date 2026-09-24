# Graph tools are fallible sensors

## Symbol ids

Nodes use fully qualified Python paths, for example:

- `fastapi.routing.APIRouter.add_api_route`
- `rich.console.Console.print`

Use exact ids returned by a graph call. Do not infer ids from natural-language
descriptions.

## `search_similar_code`

Despite its name, the harness first resolves `query` against a stored graph
symbol and uses that symbol's precomputed vector. Use a function, class, or
module name such as `HTTPAdapter`, never an issue sentence.

An empty result means the query did not resolve or graph data is unavailable;
it does not prove that relevant code is absent. Unrelated or repetitive results
are low-trust evidence. Switch to lexical search instead of paraphrasing.

## `get_code_neighbors`

- **node** — qualified symbol id.
- **edge_type** — optional filter (e.g. `calls`); omit to see all edge types.
- **max_neighbors** — cap fan-out (default 50). Increase only when necessary.

Expand only an exact node, one hop at a time. Verify at least one returned
symbol against source before trusting the path.

## `get_code_subgraph`

Provide a **small** list of nodes (3–12) that form a suspected call chain or module cluster.
The returned induced subgraph shows relationships among known nodes; it is not
a discovery tool.

## Reliability downgrade signals

- exact symbol does not resolve;
- relevant code is `async` but absent from graph results;
- output conflicts with exact grep hits;
- repeated calls return unrelated nodes;
- similarities or rankings appear indistinguishable.

On any two signals, set graph trust to low and continue with `grep` plus
`read_file`. Do not conclude that the issue has no implementation.
