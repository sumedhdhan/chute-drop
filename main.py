import sys, time, random, pygame
from collections import deque
import cv2 as cv, mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)


def main():
    with mp_hands.Hands(
     max_num_hands=1,
     model_complexity = 0,
     min_detection_confidence = 0.5,
     min_tracking_confidence = 0.5) as hands:
        pygame.init() 
        VID_CAP = cv.VideoCapture(0)
        window_size = (VID_CAP.get(cv.CAP_PROP_FRAME_WIDTH), VID_CAP.get(cv.CAP_PROP_FRAME_HEIGHT)) # width by height
        screen = pygame.display.set_mode(window_size)

        ret, frame = VID_CAP.read()
   
        screen.fill((125, 220, 232))

        # Init hand landmarker
        frame.flags.writeable = False
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = hands.process(frame)
        frame.flags.writeable = True
       
        if results.multi_hand_landmarks and len(results.multi_hand_landmarks) > 0:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
           
        # Mirror frame, swap axes because opencv != pygame
        frame = cv.flip(frame, 1).swapaxes(1, 0)
        pygame.surfarray.blit_array(screen, frame)
        pygame.display.flip()

        while True:
        
            # MAIN MENU

            ret, frame = VID_CAP.read()
            if not ret:
                        print("Empty frame, continuing...")
                        continue
            screen.fill((125, 220, 232))

            frame.flags.writeable = False
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            results = hands.process(frame)
            frame.flags.writeable = True

            # Init hand landmarker again 
            if results.multi_hand_landmarks and len(results.multi_hand_landmarks) > 0:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
            
            frame = cv.flip(frame, 1).swapaxes(1, 0)
            pygame.surfarray.blit_array(screen, frame)

            text = pygame.font.SysFont("modernno20", 50).render(f'Chute Drop', True, (255, 215, 255))
            tr = text.get_rect()
            tr.center = (320, 120)
            screen.blit(text, tr)
            text = pygame.font.SysFont("modernno20", 50).render(f'Press 1 to play', True, (205, 255, 255))
            tr = text.get_rect()
            tr.center = (320, 250)
            screen.blit(text, tr)
            text = pygame.font.SysFont("modernno20", 50).render(f'Press 2 to quit', True, (205, 255, 255))
            tr = text.get_rect()
            tr.center = (320, 350)
            screen.blit(text, tr)
            # Check if user quit window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cv.destroyAllWindows()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        playGame()
                    if event.key == pygame.K_2:
                        cv.destroyAllWindows()
                        pygame.quit()
                        sys.exit()
            pygame.display.flip()
        
                        
def playGame():
    
    # GAME LOOP
    # Open camera and window
    VID_CAP = cv.VideoCapture(0)
    window_size = (VID_CAP.get(cv.CAP_PROP_FRAME_WIDTH), VID_CAP.get(cv.CAP_PROP_FRAME_HEIGHT)) # width by height
    screen = pygame.display.set_mode(window_size)
    print(window_size)

    # Load in assets
    present_img = pygame.image.load("present.png")
    present_img = pygame.transform.scale(present_img, (present_img.get_width() / 3, present_img.get_height() / 3))
    present_frame = present_img.get_rect()
    present_frame.center = (window_size[0] // 6, window_size[1] // 2)
    cloud_frames = deque()
    cloud_img = pygame.image.load("cloud2.png")
    cloud_img = pygame.transform.rotate(cloud_img, 90)

    cloud_starting_template = cloud_img.get_rect()
    space_between_clouds = 250

    # Start game
    game_clock = time.time()
    stage = 1
    cloudSpawnTimer = 0
    time_between_cloud_spawn = 40
    dist_between_clouds = 500
    cloud_velocity = lambda: (dist_between_clouds / time_between_cloud_spawn) / 2
    level = 0
    score = 0
    didUpdateScore = False
    game_is_running = True

    with mp_hands.Hands(
    max_num_hands=1,
    model_complexity = 0,
    min_detection_confidence = 0.5,
    min_tracking_confidence = 0.5) as hands:
        
      
        ret, frame = VID_CAP.read()

        screen.fill((125, 220, 232))
        # Init hand landmarker
        frame.flags.writeable = False
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        results = hands.process(frame)
        frame.flags.writeable = True
        # Draw hand
        if results.multi_hand_landmarks and len(results.multi_hand_landmarks) > 0:
            # Landmark 8 = Tip of index finger
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
            marker = results.multi_hand_landmarks[0].landmark[8].x
            present_frame.centerx = (0.5 - marker) * 1.5 * window_size[0] + window_size[0]/2
            if present_frame.left < 0: present_frame.x = 0
            if present_frame.right > window_size[0]: present_frame.x = window_size[0] - present_frame.width
        
        # Mirror frame, swap axes because opencv != pygame
        frame = cv.flip(frame, 1).swapaxes(1, 0)
        pygame.surfarray.blit_array(screen, frame)
        pygame.display.flip()
        
        while True:

                # When game is over
                if not game_is_running:
                    text = pygame.font.SysFont("modernno20", 64).render('Game over!', True, (255, 205, 255))
                    tr = text.get_rect()
                    tr.center = (window_size[0]/2, window_size[1]/2)
                    screen.blit(text, tr)
                    pygame.display.update()
                    pygame.time.wait(2000)
                    VID_CAP.release()
                    main()
                    
                # Check if user has quit
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        VID_CAP.release()
                        cv.destroyAllWindows()
                        pygame.quit()
                        sys.exit()

             
                ret, frame = VID_CAP.read()
                if not ret:
                    print("Empty frame, continuing...")
                    continue
                # Clear screen
                screen.fill((125, 220, 232))

                # Hand landmarker
                frame.flags.writeable = False
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                results = hands.process(frame)
                frame.flags.writeable = True
                # Draw mesh
                if results.multi_hand_landmarks and len(results.multi_hand_landmarks) > 0:
                    # 8 = Tip of index finger
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
                    marker = results.multi_hand_landmarks[0].landmark[8].x
                    present_frame.centerx = (0.5 - marker) * 1.5 * window_size[0] + window_size[0]/2
                    if present_frame.left < 0: present_frame.x = 0
                    if present_frame.right > window_size[0]: present_frame.x = window_size[0] - present_frame.width
                
                # Mirror frame, swap axes because opencv != pygame
                frame = cv.flip(frame, 1).swapaxes(1, 0)
        
                # Update cloud positions
                for pf in cloud_frames:
                    pf[0].y -= cloud_velocity()
                    pf[1].y -= cloud_velocity()
                if len(cloud_frames) > 0 and cloud_frames[0][0].bottom < 0:
                    cloud_frames.popleft()
                # Update screen
                pygame.surfarray.blit_array(screen, frame)
                screen.blit(present_img, present_frame)
                checker = True
                for pf in cloud_frames:
                    # Check if present went through the clouds to update score
                    if pf[0].top <= present_frame.y <= pf[0].bottom:
                        checker = False
                        if not didUpdateScore:
                            score += 1
                            didUpdateScore = True
                    # Update screen
                    screen.blit(cloud_img, pf[1])
                    screen.blit(pygame.transform.flip(cloud_img, 0, 1), pf[0])
                if checker: didUpdateScore = False
                # Stage, score text
                text = pygame.font.SysFont("modernno20", 30).render(f'Stage {stage}', True, (205, 255, 255))
                tr = text.get_rect()
                tr.center = (100, 50)
                screen.blit(text, tr)
                text = pygame.font.SysFont("modernno20", 30).render(f'Score: {score}', True, (205, 255, 255))
                tr = text.get_rect()
                tr.center = (100, 100)
                screen.blit(text, tr)
                # Update screen
                pygame.display.flip()
                # Check if present is touching a cloud
                if any([present_frame.colliderect(pf[0]) or present_frame.colliderect(pf[1]) for pf in cloud_frames]):
                    game_is_running = False
                # Add new cloud
                if cloudSpawnTimer == 0:
                    left = cloud_starting_template.copy()
                    left.x, left.y = random.randint(120 - 1000, window_size[0] - 120 - space_between_clouds - 900), window_size[1]
                    right = cloud_starting_template.copy()
                    right.x, right.y = left.x + 1000 + space_between_clouds, window_size[1], 
                    cloud_frames.append([left, right])
                # Update cloud spawn timer 
                cloudSpawnTimer += 0.7
                if cloudSpawnTimer >= time_between_cloud_spawn: cloudSpawnTimer = 0
                # Make the game harder
                if time.time() - game_clock >= 10:
                    time_between_cloud_spawn *= 4 / 6
                    stage += 1
                    game_clock = time.time()

main()