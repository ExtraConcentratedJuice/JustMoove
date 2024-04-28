import cv2
import time
import pygame
import sys
import numpy as np
import scenes.title_scene
from pygame.font import Font
from media_library import MediaLibrary
from scenes.game_scene import GameScene
from scenes.scene import SceneBase
from scenes.scenes import get_scene, get_start_scene, set_scene, set_start_scene
from scenes.title_scene import TitleScene
from video_impl import CV2VideoFrames, RecordedCV2VideoFrames, VideoFramesBase
from game_state import GameVideoConfiguration, GameState
from motion_tracker import create_motion_tracker
from media_library import VideoMetadata, PosePosition

try:
    from skellytracker.trackers.mediapipe_tracker.mediapipe_holistic_tracker import(
        MediapipeHolisticTracker,
    )
except:
    print("To use mediapipe_holistic_tracker, install skellytracker[mediapipe]")
    exit()

def init_game():
    pygame.init()
    pygame.mixer.init()
    
    video_library = MediaLibrary()
    video_library.load_videos()
    state = GameState(pygame.font.Font(None, 64), pygame.display.set_mode(scenes.title_scene.TITLE_RESOLUTION), video_library)
    
    video_config = GameVideoConfiguration(30,
        RecordedCV2VideoFrames(state.videos.get_video(0)),
        CV2VideoFrames(cv2.VideoCapture("example_vids/olly.mp4")),
        create_motion_tracker()
    )

    if not video_config.camera.is_open():
        raise Exception("Could not open video device")

    set_scene("Title", TitleScene(state))
    set_scene("Game", GameScene(video_config, state))

    return video_config, state

def game_loop(video_config: GameVideoConfiguration, state: GameState):
    scene = get_start_scene()

    running = True

    while running:
        start_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            scene.handle_event(event)

        scene.update()

        scene.render(pygame.display.get_surface())

        pygame.display.flip()

        next_scene = scene.pop_next_scene()

        if next_scene:
            scene = next_scene
            scene.on_load()

        # Wait until it's time for the next frame
        elapsed = time.time() - start_time
        delay = max(1, int((video_config.frame_interval() - elapsed) * 1000))  # Calculate remaining time in ms
        pygame.time.wait(delay)

    pygame.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        set_start_scene(sys.argv[1])

    video_config, state = init_game()
    game_loop(video_config, state)