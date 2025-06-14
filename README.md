1.Cài đặt 

Dự án gốc: project 2 bài tập Introduction to AI đại học berkeley 

Link dự án: https://inst.eecs.berkeley.edu/~cs188/fa24/projects/proj2/ 

Dự án của nhóm, với cài đặt thuật toán các thuật toán tự chơi cho pacman và các thuật toán cải tiến của ghost. 

Clone dự án:  

git clone https://github.com/manhnd52/AI_Pacman 

cd AI_Pacman  

cd multiagent  

Thử nghiệm trò chơi 

Người chơi đấu với bot: 

Mặc định: python pacman.py -n <số lượt chơi> 

Tùy chọn ghost: python pacman.py -g <ghostAgent> 

<ghostAgent>: RandomGhost: ma di chuyển random 

<ghostAgent>: DirectionalGhost: ma đuổi theo pacman với tỷ lệ 0.8 

<ghostAgent>: AStarGhost: ma đuổi theo với thuật toán A* 

<ghostAgent>:AStarGhost,BlockingGhost: kết hợp ma đuổi theo và ma block pacman 

2.Đánh giá thuật toán với pacman tự chơi: 

Các câu lệnh: 

python pacman.py -p AlphaBetaAgent -g DirectionalGhost –n 50 

python pacman.py -p AlphaBetaAgent -g AStarGhost,BlockingGhost –n 50 

python pacman.py -p AlphaBetaAgent -g MinimaxGhost,BlockingGhost –n 50 

python pacman.py -p ReflexAgent -g MinimaxGhost,BlockingGhost –n 50 

Phương pháp đánh giá: Chạy nhiều ván game bằng câu lệnh hỗ trợ của Base Project → nhận xét tỉ lệ thắng của PACMAN 

Kết quả: 

| Ghost Agent                        | ReflexAgent | AlphaBetaAgent |
|-----------------------------------|-------------|----------------|
| DirectionalGhost                  | 0.3         | 0.58           |
| AstarGhost<sup>+</sup> + BlockingGhost     | 0           | 0.08           |
| MinimaxGhost<sup>+</sup> + BlockingGhost  | Thua/Hòa     | 1              |

 

Thua/Hòa là trạng thái mà ghost không thể tìm bắt được pacman, nhưng luôn di chuyển qua lại ở vị trí food, khiến cho pacman không thể kết thúc trò chơi. 

3.Demo:

[alphabeta VS directional](demo/demo1.mp4)

[alphabeta VS blocking+A_star](demo/demo2.mp4)


