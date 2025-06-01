import heapq
from math import sqrt

def get_next_move(grid, ghost_pos, target_pos):
    rows, cols = len(grid), len(grid[0])
    directions = {
        (-1, 0): "up",
        (1, 0): "down",
        (0, -1): "left",
        (0, 1): "right"
    }

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    # Đặt giá trị f = g + h, trong đó g là khoảng cách từ ghost đến node hiện tại và h là khoảng cách từ node hiện tại đến target
    # g = 0 ban đầu vì ghost bắt đầu tại ghost_pos
    # path là danh sách các node đã đi qua
    # open_set chứa các tuple (f, g, current_node, path) và nhờ heapq sẽ tự động sắp xếp theo giá trị f theo thứ tự tăng dần
    # f = h(ghost_pos, target_pos) + g(ghost_pos, ghost_pos)

    heapq.heappush(open_set, (heuristic(ghost_pos, target_pos), 0, []))
    visited = set()

    while open_set:
        f, g, path = heapq.heappop(open_set)
        current = path[-1] if path else ghost_pos  # Lấy node hiện tại từ path, nếu path rỗng thì dùng ghost_pos
        
        if current == target_pos:
            # Khi tìm ra được đường đi đến target, lấy hướng đi tiếp theo bằng cách lấy node đầu tiên trong path - vị trí hiện tại của ghost
            if path:
                move = (path[0][0] - ghost_pos[0], path[0][1] - ghost_pos[1])
                print("Path found:", path)
                return directions.get(move, None)
            else:
                return None  # Ngay từ đầu đã ở target

        if current in visited:
            continue # Nhảy qua vòng lặp nếu đã thăm node này
        visited.add(current)

        for d in directions:
            nx, ny = current[0] + d[0], current[1] + d[1]
            if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == 0:
                next_node = (nx, ny)
                if next_node not in visited:
                    heapq.heappush(open_set, (
                        g + 1 + heuristic(next_node, target_pos),
                        g + 1,
                        path + [next_node]
                    ))

    return None  # Không tìm được đường

grid = [
    [0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0],
    [1, 0, 1, 0, 0],
    [0, 0, 0, 0, 0]
]

ghost_pos = (3, 0)  # In giá trị tại vị trí ghost
target_pos = (1, 3)

direction = get_next_move(grid, ghost_pos, target_pos)
print("Ghost nên đi:", direction)