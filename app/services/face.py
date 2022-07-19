import face_recognition
import cv2
import numpy as np


async def verify_face(img: str):
    print(img)
    target = cv2.imread(img)
    ref_image = face_recognition.load_image_file("app/resources/ref.jpeg")
    ref_face_encoding = face_recognition.face_encodings(ref_image)[0]

    known_face_encodings = [
        ref_face_encoding
    ]
    known_face_names = [
        "Senura"
    ]

    face_locations = []
    face_encodings = []
    face_names = []
    small_frame = cv2.resize(target, (0, 0), fx=0.25, fy=0.25)

    rgb_small_frame = small_frame[:, :, ::-1]

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    name = ""
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
    if name == "":
        return False
    else:
        return True
