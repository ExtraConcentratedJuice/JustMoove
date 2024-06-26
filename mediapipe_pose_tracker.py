import cv2
import mediapipe as mp
import numpy as np
from typing import Dict

from skellytracker.trackers.base_tracker.base_tracker import BaseTracker
from skellytracker.trackers.base_tracker.tracked_object import TrackedObject
from skellytracker.trackers.mediapipe_tracker.mediapipe_holistic_recorder import (
    MediapipeHolisticRecorder,
)
from skellytracker.trackers.mediapipe_tracker.mediapipe_model_info import (
    MediapipeModelInfo,
)


class MediapipePoseTracker(BaseTracker):
    def __init__(
        self,
        model_complexity=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        static_image_mode=False,
        smooth_landmarks=True,
    ):
        super().__init__(
            tracked_object_names=MediapipeModelInfo.mediapipe_tracked_object_names,
            recorder=MediapipeHolisticRecorder(),
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose
        self.holistic = self.mp_pose.Pose(
            model_complexity=model_complexity,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            static_image_mode=static_image_mode,
            smooth_landmarks=smooth_landmarks,
        )

    def process_image(self, image: np.ndarray, **kwargs) -> Dict[str, TrackedObject]:
        # Convert the image to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image
        results = self.holistic.process(rgb_image)

        # Update the tracking data
        self.tracked_objects["pose_landmarks"].extra[
            "landmarks"
        ] = results.pose_landmarks

        self.raw_image = image.copy()

        self.annotated_image = self.annotate_image(
            image=image, tracked_objects=self.tracked_objects
        )

        return self.tracked_objects

    def annotate_image(
        self, image: np.ndarray, tracked_objects: Dict[str, TrackedObject], **kwargs
    ) -> np.ndarray:
        # Draw the pose, face, and hand landmarks on the image
        self.mp_drawing.draw_landmarks(
            image,
            tracked_objects["pose_landmarks"].extra["landmarks"],
            self.mp_pose.POSE_CONNECTIONS,
        )

        return image
