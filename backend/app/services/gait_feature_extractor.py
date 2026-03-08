import cv2
import mediapipe as mp
import numpy as np
import torch

SEQUENCE_LENGTH = 150
FEATURE_SIZE = 272  # expected by gait CNN

mp_pose = mp.solutions.pose


def extract_gait_features(video_path):

    cap = cv2.VideoCapture(video_path)

    pose = mp_pose.Pose(static_image_mode=False)

    frames = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        keypoints = []

        if results.pose_landmarks:

            for lm in results.pose_landmarks.landmark:
                keypoints.append(lm.x)
                keypoints.append(lm.y)

        else:
            keypoints = [0] * 66  # 33 landmarks × (x,y)

        # convert to expected size
        if len(keypoints) < FEATURE_SIZE:
            keypoints += [0] * (FEATURE_SIZE - len(keypoints))

        frames.append(keypoints[:FEATURE_SIZE])

    cap.release()

    sequence = np.array(frames)

    if len(sequence) > SEQUENCE_LENGTH:
        indices = np.linspace(0, len(sequence)-1, SEQUENCE_LENGTH).astype(int)
        sequence = sequence[indices]

    else:
        padding = np.zeros((SEQUENCE_LENGTH - len(sequence), FEATURE_SIZE))
        sequence = np.vstack((sequence, padding))

    sequence = torch.tensor(sequence, dtype=torch.float32)
    sequence = sequence.unsqueeze(0)

    return sequence