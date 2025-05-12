# utils/graph.py

import heapq

def dijkstra(start_id, end_id, edges_qs):
    """
    start_id, end_id: primary keys của Address
    edges_qs: queryset hoặc list các Edge instances
    Trả về list các Address.id theo đường đi ngắn nhất, hoặc None nếu không có đường.
    """
    # 1. Xây dựng adjacency list
    graph = {}
    for edge in edges_qs:
        u, v, w = edge.start_id, edge.end_id, edge.distance
        graph.setdefault(u, []).append((v, w))
        graph.setdefault(v, []).append((u, w))  # nếu đường 2 chiều

    # 2. Khởi tạo
    dist = {node: float('inf') for node in graph}
    prev = {}
    dist[start_id] = 0
    heap = [(0, start_id)]

    # 3. Thực thi Dijkstra
    while heap:
        cur_d, u = heapq.heappop(heap)
        if u == end_id:
            break
        if cur_d > dist[u]:
            continue
        for v, w in graph.get(u, []):
            nd = cur_d + w
            if nd < dist.get(v, float('inf')):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))

    # 4. Reconstruct path
    if dist.get(end_id, float('inf')) == float('inf'):
        return None  # không nối được
    path = []
    u = end_id
    while u != start_id:
        path.append(u)
        u = prev[u]
    path.append(start_id)
    return path[::-1]

