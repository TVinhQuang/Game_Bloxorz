import time
import tracemalloc
from collections import deque

from bloxorz.solvers.base import SolverResult
from bloxorz.core.game import BloxorzCoreGame

def canonicalize(state):
    """
    Hàm chuẩn hóa trạng thái: Vì khối Bloxorz không phân biệt đầu đuôi (viên 1 và viên 2 giống nhau),
    nếu ta không sắp xếp lại tọa độ, máy tính sẽ hiểu (A, B) và (B, A) là 2 trạng thái khác nhau.
    Hàm này giúp đưa tọa độ về 1 chuẩn duy nhất để so sánh và lưu vào tập 'visited'.
    """
    cube1, cube2, bridge_status, active_cube = state
    sorted_cubes = sorted([cube1, cube2])
    return (tuple(sorted_cubes[0]), tuple(sorted_cubes[1]), bridge_status, active_cube)

def solve_bfs(game: BloxorzCoreGame) -> SolverResult:
    # Bắt đầu tính giờ và bật bộ đo RAM của Python
    start_time = time.time()
    tracemalloc.start()
    
    expanded_nodes = 0 
    
    # Lấy trạng thái bắt đầu và vị trí đích từ game
    initial_state = game.get_initial_state()
    goal_pos = game.get_goal_position()

    # Khởi tạo queue. Dùng deque của 'collections' để popleft() tốn O(1) thời gian
    # Mỗi phần tử trong queue là 1 tuple chứa: (Trạng thái hiện tại, Lịch sử bước đi để tới đây)
    queue = deque([(initial_state, [])])
    
    # Tập hợp (set) 'visited' dùng để ghi nhớ những trạng thái đã đi qua nhằm tránh lặp vòng.
    visited = {canonicalize(initial_state)}

    success = False
    solution = []

    # Vòng lặp chính: Cứ tiếp tục tìm kiếm chừng nào hàng đợi chưa rỗng
    while queue:
        # Lấy phần tử ở đầu hàng đợi ra
        curr_state, path = queue.popleft()
        expanded_nodes += 1

        # KIỂM TRA ĐÍCH
        # Khối Bloxorz rơi xuống lỗ đích khi 2 tọa độ cube1 và cube2 trùng nhau
        cube1, cube2 = curr_state[0], curr_state[1]
        if cube1 == cube2 and cube1 == goal_pos:
            success = True
            solution = path
            break # Dừng thuật toán vì đã tìm thấy đường đi

        # SINH CÁC TRẠNG THÁI KẾ TIẾP
        # xem từ trạng thái hiện tại, khối có thể lăn đi những hướng nào hợp lệ
        for next_state, action in game.get_successors(curr_state):
            # Chuẩn hóa trạng thái mới sinh ra
            norm_next = canonicalize(next_state)
            
            # Nếu trạng thái này chưa được sinh ra trước đây
            if norm_next not in visited:
                visited.add(norm_next)
                
                # Đẩy trạng thái mới vào cuối hàng đợi, kèm theo lịch sử bước đi cộng thêm hành động vừa làm
                queue.append((next_state, path + [action]))

    # Tính toán thời gian và đo lượng RAM lớn nhất đã tiêu thụ
    search_time = time.time() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Đóng gói và trả về object cấu trúc chuẩn theo yêu cầu của dự án
    return SolverResult(
        algorithm="BFS",
        success=success,
        solution=solution,
        search_time=search_time,
        memory_usage=peak_memory,
        expanded_nodes=expanded_nodes,
        solution_length=len(solution),
        message="BFS found a solution!" if success else "BFS failed to find a solution."
    )

