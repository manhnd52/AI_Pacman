@echo off
set OUTPUT=results.txt
echo === Bắt đầu chạy test lúc %date% %time% > %OUTPUT%

:: Danh sách Pacman Agents
set agents=ReflexAgent MinimaxAgent AlphaBetaAgent ExpectimaxAgent

:: Nhóm 1: RandomGhost
for %%P in (%agents%) do (
    echo ==== RandomGhost vs %%P ==== >> %OUTPUT%
    python pacman.py -g RandomGhost -p %%P -n 100 -q >> %OUTPUT%
)

:: Nhóm 2: DirectionalGhost
for %%P in (%agents%) do (
    echo ==== DirectionalGhost vs %%P ==== >> %OUTPUT%
    python pacman.py -g DirectionalGhost -p %%P -n 100 -q >> %OUTPUT%
)

:: Nhóm 3: AStarGhost + BlockGhost
for %%P in (%agents%) do (
    echo ==== AStarGhost + BlockGhost vs %%P ==== >> %OUTPUT%
    python pacman.py -g AStarGhost,BlockGhost -p %%P -n 100 -q >> %OUTPUT%
)

@REM :: Nhóm 4: MinimaxGhost + BlockGhost
@REM for %%P in (%agents%) do (
@REM     echo ==== MinimaxGhost + BlockGhost vs %%P ==== >> %OUTPUT%
@REM     python pacman.py -g MinimaxGhost -g BlockGhost -k 2 -p %%P -n 100 -q >> %OUTPUT%
@REM )

echo === Kết thúc test lúc %date% %time% >> %OUTPUT%
pause
