import cv2 # type: ignore
import mediapipe as mp # type: ignore
import numpy as np
import os
from mediapipe.tasks import python # type: ignore
from mediapipe.tasks.python import vision # type: ignore
from mediapipe import solutions # type: ignore
from mediapipe.framework.formats import landmark_pb2 # type: ignore

#Parameters for drawing on the resulting image
MARGIN = 10 
FONT_SIZE = 1
FONT_THICKNESS = 1

#initial paths for models
dir_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(dir_path, 'recognizers/hand_landmarker.task')
gesture_model_path = os.path.join(dir_path, 'recognizers/gesture_recognizer.task')

#basic hand recognition
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
    running_mode=mp.tasks.vision.RunningMode.VIDEO,
)
detector = vision.HandLandmarker.create_from_options(options)

#gesture recognition
gesture_base_options = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

#printing gesture recognizer callback
def print_result(result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):
    print('gesture recognition result: {}'.format(result))

#gesture recognition parameters
gestureOptions = GestureRecognizerOptions(
    base_options=python.BaseOptions(model_asset_path=gesture_model_path),
    running_mode=VisionRunningMode.VIDEO)

#initializing gesture recognizer
gestureDetector = GestureRecognizer.create_from_options(gestureOptions)

#drawing hand landmarks on the image
def draw_landmarks_on_image(rgb_image, detection_result, mode):
    if mode == 'mm':
        HANDEDNESS_TEXT_COLOR = (255, 45, 0)
    else:
        HANDEDNESS_TEXT_COLOR = (88, 205, 54)
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    annotated_image = np.copy(rgb_image)
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
          landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
          annotated_image,
          hand_landmarks_proto,
          solutions.hands.HAND_CONNECTIONS,
          solutions.drawing_styles.get_default_hand_landmarks_style(),
          solutions.drawing_styles.get_default_hand_connections_style())
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        height, width, _ = annotated_image.shape
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN
        if mode == 'mm':
          cv2.putText(annotated_image, 
                      'MASTER MODE',
                      (text_x, text_y), 
                      cv2.FONT_HERSHEY_DUPLEX,
                      FONT_SIZE, 
                      HANDEDNESS_TEXT_COLOR, 
                      FONT_THICKNESS, 
                      cv2.LINE_AA)
        else:
             cv2.putText(annotated_image, 
                         f"{handedness[0].category_name} hand detected",
                         (text_x, text_y), 
                         cv2.FONT_HERSHEY_DUPLEX,
                         FONT_SIZE, 
                         HANDEDNESS_TEXT_COLOR, 
                         FONT_THICKNESS, 
                         cv2.LINE_AA)
    return annotated_image

# Heuristic gesture inference (optional)
# Returns 'Open_Palm', 'Pointing_Up', or None

def infer_gesture_from_landmarks(detection_result):
    try:
        if detection_result is None or not detection_result.hand_landmarks:
            return None
        lm = detection_result.hand_landmarks[0]
        # Landmark indices per MediaPipe Hands
        # Thumb: 4 (tip), 3 (ip)
        # Index: 8 (tip), 6 (pip)
        # Middle: 12, 10
        # Ring: 16, 14
        # Little: 20, 18
        def is_extended(tip_idx, pip_idx):
            tip = lm[tip_idx]
            pip = lm[pip_idx]
            return tip.y < pip.y - 0.02  # y up means smaller; small margin
        index_ext = is_extended(8, 6)
        middle_ext = is_extended(12, 10)
        ring_ext = is_extended(16, 14)
        little_ext = is_extended(20, 18)
        extended_count = sum([index_ext, middle_ext, ring_ext, little_ext])
        # Open palm: at least 3 fingers extended
        if extended_count >= 3:
            return 'Open_Palm'
        # Pointing up: only index extended
        if index_ext and not middle_ext and not ring_ext and not little_ext:
            return 'Pointing_Up'
        return None
    except Exception:
        return None

#main function for recognition to tensor

def get_annotation_from(frame, mode, timestamp_ms: int, do_gesture: bool = True):
    # Ensure RGB input for MediaPipe and convert back to BGR for OpenCV display
    if frame is None:
        return None, frame, None
    # If frame looks like BGR (typical from OpenCV), convert to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    detection_result = detector.detect_for_video(image, timestamp_ms)
    gestureResults = None
    if do_gesture:
        gestureResults = gestureDetector.recognize_for_video(image, timestamp_ms)
    annotated_rgb = draw_landmarks_on_image(rgb_frame, detection_result, mode)
    annotated_bgr = cv2.cvtColor(annotated_rgb, cv2.COLOR_RGB2BGR)
    if gestureResults and gestureResults.gestures:
        currentGesture = gestureResults.gestures[0][0].category_name
        return detection_result, annotated_bgr, currentGesture
    else:
        return detection_result, annotated_bgr, None

