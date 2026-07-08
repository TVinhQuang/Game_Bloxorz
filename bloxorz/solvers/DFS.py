#Chuẩn hóa trạng thái để tọa độ của cube1 và cube2 không bị lộn xộn thứ tự vì khối không phân biệt đầu đuôi
def canonicalize(state):
    """
    state dạng: (cube1, cube2, bridge_status, active_cube)
    cube1: (r1, c1), cube2: (r2, c2)
    bridge_status: có thể là tuple hoặc frozenset lưu trạng thái các cầu (để băm được)
    """
    cube1, cube2, bridge_status, active_cube = state
    # Sắp xếp tọa độ của 2 ô nhỏ theo quy tắc cố định (ví dụ: ưu tiên hàng nhỏ, cột nhỏ trước)
    sorted_cubes = sorted([cube1, cube2])
    
    # Trả về một tuple mới đã được chuẩn hóa để làm Key cho set/dict
    return (tuple(sorted_cubes[0]), tuple(sorted_cubes[1]), bridge_status, active_cube)



#---------------------DFS---------------------
import time
import psutil
import os

def solve_dfs(initial_state, goal_pos, game_engine):
    start_time = time.time()
    expanded_nodes = 0
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    peak_memory = initial_memory

    # Stack lưu trữ: (trạng thái_hiện_tại, danh_sách_bước_đi)
    stack = [(initial_state, [])]
    visited = set()  # Lưu các trạng thái đã chuẩn hóa để chặn vòng lặp 

    while stack:
        curr_state, path = stack.pop()  # Lấy phần tử cuối cùng ra (LIFO)

        # 1. Chuẩn hóa trạng thái và kiểm tra trùng lặp
        norm_state = canonicalize(curr_state)
        if norm_state in visited:
            continue
        
        # Ghi nhận đã mở rộng nút 
        visited.add(norm_state)
        expanded_nodes += 1

        # Đo bộ nhớ đỉnh (Peak Memory) liên tục trong quá trình chạy
        current_mem = process.memory_info().rss
        if current_mem > peak_memory:
            peak_memory = current_mem

        # 2. Kiểm tra điều kiện đích (Goal Test) 
        # Điều kiện thắng: cả 2 ô nhỏ trùng nhau (đứng thẳng) và trùng với goal_pos
        cube1, cube2 = curr_state[0], curr_state[1]
        if cube1 == cube2 and cube1 == goal_pos:
            search_time = time.time() - start_time
            mem_used_kb = (peak_memory - initial_memory) / 1024  # Tính lượng ram tăng thêm (KB)
            return {
                "status": "Success",
                "path": path,
                "search_time": search_time,
                "memory": mem_used_kb,
                "expanded_nodes": expanded_nodes,
                "solution_length": len(path)
            }

        # 3. Gọi hàm sinh trạng thái kế tiếp từ Engine của bạn 
        # Lấy danh sách các bước đi hợp lệ từ vị trí hiện tại
        successors = game_engine.get_successors(curr_state) 
        
        for next_state, action in successors:
            # Nếu trạng thái kế tiếp sau khi chuẩn hóa chưa từng được duyệt, đẩy vào Stack
            if canonicalize(next_state) not in visited:
                stack.append((next_state, path + [action]))

    # Nếu duyệt hết không gian trạng thái mà không tìm thấy đường đi
    return {"status": "Fail", "search_time": time.time() - start_time, "expanded_nodes": expanded_nodes}



#---------------------A*---------------------
import math

def calculate_heuristic(state, goal_pos):
    cube1, cube2 = state[0], state[1]
    r_g, c_g = goal_pos
    
    # Khoảng cách Manhattan từ từng ô đến đích
    d1 = abs(cube1[0] - r_g) + abs(cube1[1] - c_g)
    d2 = abs(cube2[0] - r_g) + abs(cube2[1] - c_g)
    
    # Lấy khoảng cách ngắn nhất chia 2 (vì 1 bước lật block có thể đi 2 ô)
    h_base = math.ceil(min(d1, d2) / 2)
    
    # Điểm phạt định hướng: Nếu block đang nằm (cube1 != cube2), 
    # chắc chắn mất thêm ít nhất 1 hoặc 2 bước lật để dựng đứng nó lên đích
    penalty = 0 if cube1 == cube2 else 1
    
    return h_base + penalty

import heapq

def solve_astar(initial_state, goal_pos, game_engine):
    start_time = time.time()
    expanded_nodes = 0
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    peak_memory = initial_memory
    
    counter = 0  # Biến phụ tăng dần để tránh lỗi so sánh tuple trong heapq khi f bằng nhau và h bằng nhau
    
    # Khởi tạo giá trị ban đầu
    h_init = calculate_heuristic(initial_state, goal_pos)
    # Cấu trúc phần tử trong Heap: (f_value, h_value, unique_counter, current_state, path_moved)
    heap = [(0 + h_init, h_init, counter, initial_state, [])]
    heapq.heapify(heap)
    
    # Bảng lưu trữ chi phí đường đi thực tế g(n) tốt nhất từng ghi nhận 
    g_scores = {canonicalize(initial_state): 0}
    
    while heap:
        f, h, _, curr_state, path = heapq.heappop(heap)
        norm_state = canonicalize(curr_state)
        
        # Nếu chi phí đường đi hiện tại dài hơn chi phí tối ưu đã từng tìm thấy cho trạng thái này -> bỏ qua
        if len(path) > g_scores.get(norm_state, float('inf')):
            continue
            
        expanded_nodes += 1
        
        # Theo dõi bộ nhớ đỉnh
        current_mem = process.memory_info().rss
        if current_mem > peak_memory:
            peak_memory = current_mem

        # Kiểm tra Đích
        cube1, cube2 = curr_state[0], curr_state[1]
        if cube1 == cube2 and cube1 == goal_pos:
            search_time = time.time() - start_time
            mem_used_kb = (peak_memory - initial_memory) / 1024
            return {
                "status": "Success",
                "path": path,
                "search_time": search_time,
                "memory": mem_used_kb,
                "expanded_nodes": expanded_nodes,
                "solution_length": len(path)
            }

        # Khám phá các trạng thái lân cận từ Engine 
        successors = game_engine.get_successors(curr_state)
        
        for next_state, action in successors:
            norm_next = canonicalize(next_state)
            new_g = len(path) + 1  # Giả định chi phí mỗi bước đi cố định bằng 1
            
            # Nếu tìm thấy một đường đi mới tới trạng thái này với chi phí thấp hơn trước đây
            if new_g < g_scores.get(norm_next, float('inf')):
                g_scores[norm_next] = new_g
                new_h = calculate_heuristic(next_state, goal_pos)
                new_f = new_g + new_h
                
                counter += 1
                # Đẩy trạng thái mới vào hàng đợi ưu tiên
                heapq.heappush(heap, (new_f, new_h, counter, next_state, path + [action]))
                
    return {"status": "Fail", "search_time": time.time() - start_time, "expanded_nodes": expanded_nodes}