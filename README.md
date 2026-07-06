# Game Bloxorz Solver

Bloxorz Solver là một game giải đố được viết bằng Python. Người chơi điều khiển một khối chữ nhật kích thước 1 x 1 x 2 lăn trên bản đồ để đưa khối đến đúng lỗ đích.

Game có giao diện desktop bằng Pygame, hỗ trợ chơi thủ công và các thuật toán tìm đường tự động như BFS, DFS/IDS, UCS và A*.

---

## Cách chơi

Người chơi cần di chuyển khối trên các ô sàn để đưa khối đến lỗ đích.

Khối có 3 trạng thái:

* Đứng thẳng: chiếm 1 ô.
* Nằm ngang: chiếm 2 ô theo chiều trái - phải.
* Nằm dọc: chiếm 2 ô theo chiều trên - dưới.

Người chơi thắng khi khối **đứng thẳng đúng trên lỗ đích**. Nếu khối chỉ nằm ngang hoặc nằm dọc qua lỗ đích thì chưa thắng.

Nếu khối lăn ra ngoài bản đồ hoặc rơi vào ô trống, lượt đi đó không hợp lệ và level sẽ được reset.

---

## Điều khiển

| Phím / Nút           | Chức năng                     |
| -------------------- | ----------------------------- |
| W hoặc mũi tên lên   | Di chuyển lên                 |
| S hoặc mũi tên xuống | Di chuyển xuống               |
| A hoặc mũi tên trái  | Di chuyển trái                |
| D hoặc mũi tên phải  | Di chuyển phải                |
| R                    | Chơi lại level hiện tại       |
| N                    | Chuyển sang level tiếp theo   |
| P                    | Quay lại level trước          |
| ESC                  | Thoát game                    |
| Restart              | Chơi lại level                |
| Previous Level       | Quay lại level trước          |
| Next Level           | Chuyển sang level tiếp theo   |
| Solve BFS            | Giải bằng BFS                 |
| Solve DFS            | Giải bằng DFS hoặc IDS        |
| Solve UCS            | Giải bằng Uniform-Cost Search |
| Solve A*             | Giải bằng A* Search           |
| Quit                 | Thoát game                    |

---

## Một số tính năng chính

* Giao diện desktop bằng Pygame.
* Bản đồ dạng pseudo-3D/isometric.
* Khối có đủ 3 trạng thái: đứng, nằm ngang, nằm dọc.
* Kiểm tra nước đi hợp lệ và không hợp lệ.
* Hiệu ứng rơi khi khối đi ra ngoài bản đồ.
* Tự động reset level sau khi khối rơi.
* Đếm số bước di chuyển hợp lệ.
* Hỗ trợ nhiều level với độ khó tăng dần.
* Hỗ trợ các thuật toán tìm kiếm:

  * Breadth-First Search
  * Depth-First Search hoặc Iterative Deepening Search
  * Uniform-Cost Search
  * A* Search
* Hỗ trợ các loại ô nâng cao như fragile tile, bridge, switch và split block.

---

## Cài đặt và chạy game

### 1. Clone project

```bash
git clone https://github.com/TVinhQuang/Game_Bloxorz.git
cd Game_Bloxorz
```

### 2. Tạo môi trường ảo

Trên Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

Trên macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Cài thư viện cần thiết

```bash
pip install -r requirements.txt
```

### 4. Chạy game

```bash
python main.py
```

---

## Debug và kiểm tra lỗi

### Chạy test core mechanics

```bash
python -m tests.test_core_mechanics
```

Nếu chạy đúng, chương trình sẽ in:

```text
All core mechanics tests passed.
```

### Lỗi thiếu pygame

Nếu gặp lỗi:

```text
ModuleNotFoundError: No module named 'pygame'
```

chạy lại:

```bash
pip install -r requirements.txt
```

### Lỗi không tìm thấy level

Nếu gặp lỗi không tìm thấy file level, kiểm tra thư mục:

```text
levels/
```

Trong thư mục này cần có các file dạng:

```text
level_01_core_intro.json
level_02_core_turning.json
...
```

### Game không nhận phím

Hãy click chuột vào cửa sổ game trước, sau đó thử bấm lại các phím di chuyển.

### Muốn kiểm tra nhanh một level

Mở file JSON trong thư mục `levels/` và kiểm tra các ký hiệu:

| Ký hiệu | Ý nghĩa        |
| ------- | -------------- |
| `#`     | Ô trống / void |
| `.`     | Ô sàn          |
| `S`     | Vị trí bắt đầu |
| `G`     | Lỗ đích        |
| `F`     | Fragile tile   |
| `B`     | Bridge         |
| `O`     | Soft switch    |
| `X`     | Heavy switch   |
| `P`     | Split switch   |

---

## Cấu trúc chính

```text
bloxorz/
├── core/        # Logic chính của game
├── gui/         # Giao diện Pygame
├── solvers/     # BFS, DFS/IDS, UCS, A*
├── advanced/    # Fragile, bridge, switch, split block
└── experiments/ # Chạy thí nghiệm và đo hiệu năng

levels/          # Các màn chơi
tests/           # Kiểm thử
tools/
└── write_core_levels.py        # Tạo/đặt lại 10 levels
```

---

## Ghi chú

Các thuật toán tìm kiếm sử dụng chung logic game trong `bloxorz/core/`, không viết lại luật di chuyển riêng. Điều này giúp kết quả giữa game thủ công và solver luôn thống nhất.
