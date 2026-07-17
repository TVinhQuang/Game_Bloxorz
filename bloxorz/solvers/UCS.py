import time
import tracemalloc
import heapq # Thư viện hỗ trợ Hàng đợi ưu tiên (Min-Heap)

from bloxorz.solvers.base import SolverResult
from bloxorz.core.game import BloxorzCoreGame

def canonicalize(state):
    cube1, cube2, bridge_status, active_cube = state
    sorted_cubes = sorted([cube1, cube2])
    return (tuple(sorted_cubes[0]), tuple(sorted_cubes[1]), bridge_status, active_cube)

def solve_ucs(game: BloxorzCoreGame) -> SolverResult:
    start_time = time.time()
    tracemalloc.start()
    
    expanded_nodes = 0
    
    # Biến 'counter' trong heapq ở Python.
    # Khi 2 phần tử có cùng chi phí g_cost, heapq sẽ so sánh đến phần tử tiếp theo trong tuple.
    # Nếu không có counter, nó sẽ so sánh 'state', mà tuple chứa Set/Frozenset có thể lỗi. 
    # Counter giúp đảm bảo trạng thái nào sinh ra trước sẽ được ưu tiên bốc ra trước nếu trùng chi phí.
    counter = 0 
    
    initial_state = game.get_initial_state()
    goal_pos = game.get_goal_position()

    # Cấu trúc của 1 item trong Hàng đợi ưu tiên là:
    # (Tổng chi phí tới hiện tại, Biến đếm thứ tự, Trạng thái, Lịch sử bước đi)
    heap = [(0, counter, initial_state, [])]
    heapq.heapify(heap) # Chuyển list thường thành Min-Heap
    
    # Từ điển (Dictionary) 'g_scores' lưu trữ CHỈ SỐ CHI PHÍ NHỎ NHẤT ĐÃ BIẾT để đi đến một trạng thái.
    # Khác với BFS (đến trước thì luôn tối ưu), trong UCS ta có thể tìm ra đường khác tới cùng 1 điểm nhưng giá rẻ hơn, 
    # nên ta dùng dict thay vì dùng set 'visited'.
    g_scores = {canonicalize(initial_state): 0}
    
    success = False
    solution = []

    # Lặp cho đến khi hàng đợi ưu tiên trống
    while heap:
        # Lấy phần tử có 'g_cost' THẤP NHẤT hiện tại ra khỏi heap
        g_cost, _, curr_state, path = heapq.heappop(heap)
        norm_state = canonicalize(curr_state)
        
        # BƯỚC LOẠI TRỪ:
        # Vì ta có thể push cùng 1 trạng thái nhiều lần vào heap (do tìm được đường khác rẻ hơn),
        # nên khi rút 1 state ra, nếu chi phí g_cost hiện tại lớn hơn chi phí tốt nhất ta đang lưu trong g_scores,
        # nghĩa là ta đang lấy ra 1 đường đi cũ, kém tối ưu -> Bỏ qua nhánh này không xét tiếp.
        if g_cost > g_scores.get(norm_state, float('inf')):
            continue
            
        expanded_nodes += 1

        # Goal Test
        cube1, cube2 = curr_state[0], curr_state[1]
        if cube1 == cube2 and cube1 == goal_pos:
            success = True
            solution = path
            break

        # Generate Successors
        for next_state, action in game.get_successors(curr_state):
            norm_next = canonicalize(next_state)
            
            # Chi phí cho 1 bước đi. 
            # (Ở game Bloxorz bình thường, chi phí này luôn = 1, nên kết quả UCS chạy y hệt BFS. 
            # Nhưng nếu game có "nền gạch dính" lăn mất 2 chi phí thì UCS mới phát huy sức mạnh)
            step_cost = 1
            new_g = g_cost + step_cost  # Tính tổng chi phí từ đầu đến next_state
            
            # NẾU TÌM ĐƯỢC ĐƯỜNG MỚI RẺ HƠN (hoặc chưa từng đi qua) ĐỂ ĐẾN next_state
            if new_g < g_scores.get(norm_next, float('inf')):
                # 1. Cập nhật lại kỷ lục chi phí rẻ nhất vào từ điển g_scores
                g_scores[norm_next] = new_g
                counter += 1
                
                # 2. Đẩy trạng thái này vào Hàng đợi ưu tiên cùng chi phí mới
                heapq.heappush(heap, (new_g, counter, next_state, path + [action]))

    search_time = time.time() - start_time
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return SolverResult(
        algorithm="UCS",
        success=success,
        solution=solution,
        search_time=search_time,
        memory_usage=peak_memory,
        expanded_nodes=expanded_nodes,
        solution_length=len(solution),
        message="UCS found a solution!" if success else "UCS failed to find a solution."
    )