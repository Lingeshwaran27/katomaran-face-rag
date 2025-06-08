import dlib
from PIL import Image
import numpy as np

# Load the default face detector from dlib
detector = dlib.get_frontal_face_detector()

# Load an image (replace with your image path)
image = Image.open("face-recog/test_face.jpg")  # Use an image with a face
image_np = np.array(image)

# Detect faces
faces = detector(image_np)

print(f"Detected {len(faces)} face(s)")
for i, d in enumerate(faces):
    print(f"Face {i+1}: Left: {d.left()}, Top: {d.top()}, Right: {d.right()}, Bottom: {d.bottom()}")
