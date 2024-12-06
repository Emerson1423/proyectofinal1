import cv2
import mediapipe as mp

# Clase de cámara con integración de Mediapipe
class Camara:
    def __init__(self, cam_id=0, max_num_hands=1, min_detection_confidence=0.9):
        # Inicializar captura de video
        self.captura = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)  # Usamos CAP_DSHOW en lugar de MSMF
        if not self.captura.isOpened():
            raise ValueError("No se pudo acceder a la cámara")

        # Inicializar Mediapipe y utilidades de dibujo
        self.mp_mano = mp.solutions.hands
        self.mano = self.mp_mano.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence
        )
        self.mp_dibujo = mp.solutions.drawing_utils

    def ProcesarFrame(self, frame):
        # Dimensiones del frame
        alto, ancho, _ = frame.shape

        # Convertir el frame a RGB para Mediapipe
        color = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultado = self.mano.process(color)

        if resultado.multi_hand_landmarks:
            for mano_landmarks in resultado.multi_hand_landmarks:
                # Obtener la coordenada central de la mano (punto 9)
                pto_i5 = mano_landmarks.landmark[9]
                cx, cy = int(pto_i5.x * ancho), int(pto_i5.y * alto)

                # Definir el área del rectángulo
                x1, y1 = max(0, cx - 100), max(0, cy - 100)
                x2, y2 = min(ancho, x1 + 200), min(alto, y1 + 200)

                # Dibujar el área de seguimiento
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

                # Dibujar solo los puntos y líneas dentro del rectángulo
                for conexion in self.mp_mano.HAND_CONNECTIONS:
                    p1, p2 = conexion
                    punto1 = mano_landmarks.landmark[p1]
                    punto2 = mano_landmarks.landmark[p2]

                    # Convertir coordenadas normalizadas a píxeles
                    px1, py1 = int(punto1.x * ancho), int(punto1.y * alto)
                    px2, py2 = int(punto2.x * ancho), int(punto2.y * alto)

                    if (x1 <= px1 <= x2 and y1 <= py1 <= y2) and (x1 <= px2 <= x2 and y1 <= py2 <= y2):
                        # Dibujar la conexión
                        cv2.line(frame, (px1, py1), (px2, py2), (255, 255, 255), 2)

                # Dibujar puntos individuales dentro del rectángulo
                for punto in mano_landmarks.landmark:
                    px, py = int(punto.x * ancho), int(punto.y * alto)
                    if x1 <= px <= x2 and y1 <= py <= y2:
                        cv2.circle(frame, (px, py), 3, (255, 0, 0), -1)
        return frame

    def FinalizarCaptura(self):
        if self.captura.isOpened():
            self.captura.release()