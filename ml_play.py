"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    ball_Xprev = 0
    ball_Yprev = 0
    ball_Xdiff = 0
    ball_Ydiff = 0
    prid_X = 0
    
    
    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()
        
        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False
            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue
        
        # 3.3. Put the code here to handle the scene information
        ball_Xdiff = scene_info.ball[0] - ball_Xprev
        ball_Ydiff = scene_info.ball[1] - ball_Yprev
        ball_Xprev = scene_info.ball[0]
        ball_Yprev = scene_info.ball[1]
        #print("Xmove:", ball_Xdiff, "Ymove", ball_Ydiff, "X", scene_info.platform[0], "Y", scene_info.platform[1])
        brick_list = scene_info.bricks
        #print(type(brick_list), len(brick_list), brick_list[0])

        # 3.4. ball_YprevSend the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            #當球上升時
            if ball_Ydiff < 0:
                if scene_info.platform[0] > 80:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                elif scene_info.platform[0] == 80:
                    comm.send_instruction(scene_info.frame, PlatformAction.NONE)
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            #當球下降時
            else:
                #predict ball's x when y==400
                if ball_Xdiff > 0:
                    prid_X = scene_info.ball[0] + (400 - scene_info.ball[1])
                    if prid_X > 200:
                        prid_X = prid_X - 2*(prid_X - 200)
                else:
                    prid_X = scene_info.ball[0] - (400 - scene_info.ball[1])
                    if prid_X < 0:
                        prid_X = prid_X + 2*(-prid_X)
                #print("prid_x", prid_X)
                
                #move platform to the predict x of ball
                if prid_X < scene_info.platform[0]:
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                elif prid_X > (scene_info.platform[0] + 40):
                    comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                else:
                    comm.send_instruction(scene_info.frame, PlatformAction.NONE)
