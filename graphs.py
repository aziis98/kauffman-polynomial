from typing import Callable, TypeVar, Iterable


T = TypeVar('T')


# Graph = dict[tuple[int, ...], set[tuple[int, ...]]]

# generic graph over T vertices
Graph = dict[T, set[T]]


def connected_components(
    get_vertices: Callable[[], Iterable[T]],
    get_neighbors: Callable[[T], Iterable[T]]
) -> list[list[T]]:
    """
    Find the connected components of a graph represented by functions to obtain 
    vertices and their neighbors.

    Args:
        get_vertices: A function that returns a list of vertices.
        get_neighbors: A function that takes a vertex and returns a list of its neighbors.

    Returns:
        A list of lists, where each list contains the vertices in a connected component.
    """
    visited: set[T] = set()
    components: list[list[T]] = []

    queue: list[T] = []
    for vertex in get_vertices():
        if vertex not in visited:
            component: set[T] = set()
            queue.append(vertex)

            list()

            while queue:
                current = queue.pop(0)
                if current not in visited:
                    visited.add(current)
                    component.add(current)
                    queue.extend(get_neighbors(current))

            components.append(list(component))

    return components


def collapse_loops(g: Graph[T]) -> Graph[tuple[T, ...]]:
    """
    Collapse loops in a graph.

    Args:
        g: The input graph represented as a dictionary.

    Returns:
        A new graph with loops collapsed.
    """
    new_graph: Graph[tuple[T, ...]] = {}

    def find_cycle(g: Graph[T], start: T) -> list[T] | None:
        """
        Find a cycle in the graph starting from a given vertex.

        Args:
            g: The input graph.
            start: The starting vertex.

        Returns:
            A list of vertices in the cycle or None if no cycle is found.
        """
        visited = set()
        stack = [(start, [start])]

        while stack:
            current, path = stack.pop()
            visited.add(current)

            for neighbor in g[current]:
                if neighbor == start and len(path) > 1:
                    return path
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))

        return None

    visited = set()

    # create all vertices
    for vertex in g:
        if vertex in visited:
            continue

        visited.add(vertex)

        cycle = find_cycle(g, vertex)
        if cycle:
            visited.update(cycle)
            cycle_vertex = tuple(cycle)
            new_graph[cycle_vertex] = set()
            # for v in cycle:
            #     new_graph[cycle_vertex].update(g[v])
        else:
            new_graph[(vertex,)] = set()

    v_to_group = {
        v: cycle_vertex
        for cycle_vertex in new_graph
        for v in cycle_vertex
    }

    # add missing edges
    for vertex_group in new_graph:
        for v in vertex_group:
            for neighbor in g[v]:
                if neighbor not in vertex_group:
                    new_graph[vertex_group].add(v_to_group[neighbor])

    return new_graph


# def find_disjoint_loops(g: Graph[T]) -> list[list[T]]:
#     """
#     Find disjoint loops in a graph.

#     Args:
#         g: The input graph represented as a dictionary.

#     Returns:
#         A list of lists, where each list contains the vertices in a loop.
#     """
#     visited = set()
#     loops = []

#     def dfs(vertex: T, path: list[T]):
#         if vertex in visited:
#             return
#         visited.add(vertex)
#         path.append(vertex)

#         for neighbor in g[vertex]:
#             if neighbor not in visited:
#                 dfs(neighbor, path)
#             elif neighbor in path and len(path) > 1:
#                 loops.append(path[path.index(neighbor):])

#         path.pop()

#     for vertex in g:
#         if vertex not in visited:
#             dfs(vertex, [])

#     return loops

def find_roots(g: Graph[T]) -> list[T]:
    """
    Find the roots of a graph.

    Args:
        g: The input graph represented as a dictionary.

    Returns:
        A list of vertices that are roots of the graph.
    """
    in_degree = {v: 0 for v in g}

    for neighbors in g.values():
        for neighbor in neighbors:
            in_degree[neighbor] += 1

    return [v for v, deg in in_degree.items() if deg == 0]
