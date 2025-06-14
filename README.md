# AI Pacman 

### Dự án gốc:

Bài tập **Project 2 - Introduction to AI** của Đại học Berkeley.
🔗 [Link gốc dự án](https://inst.eecs.berkeley.edu/~cs188/fa24/projects/proj2/)

Dự án này là bản mở rộng có chỉnh sửa của nhóm, tập trung vào:

* Cài đặt các thuật toán tự chơi cho Pacman.
* Phát triển và thử nghiệm các chiến lược thông minh hơn cho Ghost.


## 1. Cài đặt

### Clone dự án

```bash
git clone https://github.com/manhnd52/AI_Pacman
cd AI_Pacman
cd multiagent
```

###  Thử nghiệm trò chơi

#### Người chơi đấu với bot:

* Chạy mặc định:

```bash
python pacman.py -n <số lượt chơi>
```

#### Tùy chọn Ghost Agent:

```bash
python pacman.py -g <TênGhost>
```

* `RandomGhost`: ma di chuyển ngẫu nhiên
* `DirectionalGhost`: ma đuổi theo Pacman với xác suất 0.8
* `AStarGhost`: ma đuổi theo Pacman bằng thuật toán A\*
* `AStarGhost,BlockingGhost`: kết hợp giữa ma đuổi và ma chặn đường


## 2. Đánh giá các thuật toán với Pacman tự chơi

### Các câu lệnh thử nghiệm:

```bash
python pacman.py -p AlphaBetaAgent -g DirectionalGhost -n 50
python pacman.py -p AlphaBetaAgent -g AStarGhost,BlockingGhost -n 50
python pacman.py -p AlphaBetaAgent -g MinimaxGhost,BlockingGhost -n 50
python pacman.py -p ReflexAgent -g MinimaxGhost,BlockingGhost -n 50
```

> **Phương pháp đánh giá**:
> Chạy nhiều ván game, sau đó nhận xét tỉ lệ thắng của Pacman dựa trên kết quả.

### Kết quả:

| Ghost Agent                  | ReflexAgent | AlphaBetaAgent |
| ---------------------------- | ----------- | -------------- |
| DirectionalGhost             | 0.3         | 0.58           |
| AStarGhost + BlockingGhost   | 0           | 0.08           |
| MinimaxGhost + BlockingGhost | Thua/Hòa    | 1.0            |

**Lưu ý**:
"Thua/Hòa" là trạng thái ghost không bắt được Pacman, nhưng liên tục di chuyển qua lại ở food, khiến Pacman không thể ăn hết thức ăn và trò chơi không thể kết thúc.



## 3.  Demo

* AlphaBetaAgent vs DirectionalGhost
* AlphaBetaAgent vs AStarGhost + BlockingGhost

