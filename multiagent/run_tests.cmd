@echo off
set OUTPUT=results.txt
echo === Bắt đầu chạy test lúc %date% %time% > %OUTPUT%

:: Danh sách Pacman Agents
set agents=ReflexAgent AlphaBetaAgent


:: Nhóm 1: DirectionalGhost
for %%P in (%agents%) do (
    echo ==== DirectionalGhost vs %%P ==== >> %OUTPUT%
    python pacman.py -g DirectionalGhost -p %%P -n 100 -q >> %OUTPUT%
)

:: Nhóm 2: AStarGhost + BlockGhost
for %%P in (%agents%) do (
    echo ==== AStarGhost + BlockGhost vs %%P ==== >> %OUTPUT%
    python pacman.py -g AStarGhost,BlockingGhost -p %%P -n 100 -q >> %OUTPUT%
)

:: Nhóm 3: MinimaxGhost + BlockGhost
for %%P in (%agents%) do (
    echo ==== MinimaxGhost + BlockGhost vs %%P ==== >> %OUTPUT%
    python pacman.py -g MinimaxGhost,BlockingGhost -p %%P -n 100 -q >> %OUTPUT%
)

echo === Kết thúc test lúc %date% %time% >> %OUTPUT%
pause
