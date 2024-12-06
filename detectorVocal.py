import cv2
import mediapipe as mp
import random

# Clase de la cámara
class Camara:
    def __init__(self, cam_id=0, max_num_hands=1, min_detection_confidence=0.9):
        # Inicializar captura de video
        self.captura = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
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
        self.vocal_propuesta = None
        self.respuesta_vocal = None
        self.ultima_vocal = None

    def LiberarRecursos(self):
        """Liberar recursos de la cámara y cerrar ventanas."""
        if self.captura.isOpened():
            self.captura.release()
        cv2.destroyAllWindows()

    def ElegirVocal(self):
        vocales = ['A', 'E', 'I', 'O', 'U']
        self.vocal_propuesta = random.choice(vocales)
        # Asegurarse de que no sea igual a la última
        while self.vocal_propuesta == self.ultima_vocal:
            self.vocal_propuesta = random.choice(vocales)
        self.ultima_vocal = self.vocal_propuesta
        return self.vocal_propuesta
    
    def CompararVocal(self, letra_detectada):
        # Comparar la letra detectada con la vocal propuesta
        if letra_detectada == self.vocal_propuesta:
            self.respuesta_vocal = "¡correcta!"
        else:
            self.respuesta_vocal = "incorrecta :("

    def DetectarDedos(self, mano_landmarks, alto, ancho):
        # Obtener la posición de los landmarks necesarios
        nudo_pulgar = mano_landmarks.landmark[2]     # Nudillo del pulgar
        mitad_pulgar = mano_landmarks.landmark[3]    # Mitad del pulgar
        punta_pulgar = mano_landmarks.landmark[4]
        nudo2_indice = mano_landmarks.landmark[6]    # Punta del pulgar
        nudo_indice = mano_landmarks.landmark[7]     # Nudillo del índice
        punta_indice = mano_landmarks.landmark[8]    # Punta del índice
        nudo2_mayor = mano_landmarks.landmark[10]
        nudo_mayor = mano_landmarks.landmark[11]     # Nudillo del mayor
        punta_mayor = mano_landmarks.landmark[12]    # Punta del mayor
        nudo_anular = mano_landmarks.landmark[15]    # Nudillo del anular
        punta_anular = mano_landmarks.landmark[16]   # Punta del anular
        nudo2_meñique = mano_landmarks.landmark[18]
        nudo_meñique = mano_landmarks.landmark[19]   # Nudillo del meñique
        punta_meñique = mano_landmarks.landmark[20]  # Punta del meñique
        profun_indice = mano_landmarks.landmark[5]   # Base del índice
        profun_mayor = mano_landmarks.landmark[9]    # Base del mayor
        profun_anular = mano_landmarks.landmark[13]  # Base del anular
        profun_meñique = mano_landmarks.landmark[17] # Base del meñique

        # Verificar que no esté levantado
        dedo_anular = punta_anular.y < nudo_anular.y

        # Verificar que el pulgar esté hacia la izquierda
        pulgar = punta_pulgar.x < nudo_pulgar.x
        # Verificar que está haciendo puño
        a_d_indice = punta_indice.y > profun_indice.y
        a_d_mayor = punta_mayor.y > profun_mayor.y
        a_d_anular = punta_anular.y > profun_anular.y
        a_d_meñique = punta_meñique.y > profun_meñique.y
        
        # Verificar que los dedos estén medio abiertos
        e_d_pulgar = punta_pulgar.x > mitad_pulgar.x
        e_d_indice = punta_indice.y > nudo_indice.y
        e_d_mayor = punta_mayor.y > nudo_mayor.y
        e_d_anular = punta_anular.y > nudo_anular.y
        e_d_meñique = punta_meñique.y > nudo_meñique.y

        # Verificar meñique levantado
        i = punta_meñique.y < nudo2_meñique.y
        
        # Verificar que la mano está en dirección del eje z
        o = profun_indice.z > profun_mayor.z and profun_mayor.z > profun_anular.z and profun_anular.z > profun_meñique.z
        
        # Verificar índice y mayor levantado
        u = punta_indice.y < nudo2_indice.y and punta_mayor.y < nudo2_mayor.y

        # Diccionario para las condiciones de cada letra
        condiciones = {
            'A': lambda: (
                pulgar and a_d_indice and a_d_mayor and a_d_anular and a_d_meñique
                and not u and not dedo_anular and not i
            ),
            'U': lambda: (
                 u and not pulgar and not dedo_anular and not i
            ),
            'I': lambda: (
                i and e_d_pulgar and not u and not dedo_anular and e_d_indice and e_d_mayor
                and e_d_anular
            ),
            'O': lambda: (
                pulgar and o and not u and not dedo_anular and not i
            ),
            'E': lambda: (
                e_d_pulgar and not pulgar and e_d_indice and e_d_mayor and e_d_anular and e_d_meñique
            )
        }

        # Evaluar la letra en base a las condiciones de cada una
        for letra, condicion in condiciones.items():
            if condicion():
                return letra
        return 'no reconocida'
    
    def ProcesarFrame(self, frame, evaluar_dedos=False):
        # Dimensiones del frame
        alto, ancho, _ = frame.shape

        # Convertir el frame a RGB para Mediapipe
        color = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultado = self.mano.process(color)

        if self.vocal_propuesta is None:
            self.vocal_propuesta = self.ElegirVocal()

        letra_detectada = None
        if resultado.multi_hand_landmarks:
            for mano_landmarks in resultado.multi_hand_landmarks:
                # Obtener el punto central (landmark 9) para definir el rectángulo
                pto_central = mano_landmarks.landmark[9]
                cx, cy = int(pto_central.x * ancho), int(pto_central.y * alto)

                # Definir el área del rectángulo alrededor de la mano
                x1, y1 = max(0, cx - 100), max(0, cy - 100)
                x2, y2 = min(ancho, cx + 100), min(alto, cy + 100)

                # Dibujar el rectángulo de seguimiento
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

                # Dibujar puntos y conexiones dentro del rectángulo
                for conexion in self.mp_mano.HAND_CONNECTIONS:
                    p1, p2 = conexion
                    punto1 = mano_landmarks.landmark[p1]
                    punto2 = mano_landmarks.landmark[p2]

                    # Convertir coordenadas normalizadas a píxeles
                    px1, py1 = int(punto1.x * ancho), int(punto1.y * alto)
                    px2, py2 = int(punto2.x * ancho), int(punto2.y * alto)

                    if (x1 <= px1 <= x2 and y1 <= py1 <= y2) and (x1 <= px2 <= x2 and y1 <= py2 <= y2):
                        cv2.line(frame, (px1, py1), (px2, py2), (255, 255, 255), 2)

                for punto in mano_landmarks.landmark:
                    px, py = int(punto.x * ancho), int(punto.y * alto)
                    if x1 <= px <= x2 and y1 <= py <= y2:
                        cv2.circle(frame, (px, py), 3, (255, 0, 0), -1)

                # Si está habilitada la evaluación de dedos, detectar la letra
                if evaluar_dedos:
                    letra_detectada = self.DetectarDedos(mano_landmarks, alto, ancho)
        return frame, letra_detectada

# Ejecutar el programa
if __name__ == "__main__":
    camara = Camara()

    try:
        while True:
            ret, frame = camara.captura.read()
            if not ret:
                print("No se pudo leer el frame")
                break

            frame = cv2.flip(frame, 1)  # Modo espejo
            frame, letra_detectada = camara.ProcesarFrame(frame, evaluar_dedos=True)

            # Mostrar resultados en pantalla
            cv2.putText(
                frame,
                f"Letra detectada: {letra_detectada}",
                (50, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2,
            )
            cv2.putText(
                frame,
                "Presiona Enter para enviar tu respuesta",
                (50, 250),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (255, 0, 0),
                2,
            )
            cv2.imshow("Detección de signos", frame)

            if cv2.waitKey(1) == 13:  # Tecla Enter
                if letra_detectada is not None:
                    camara.CompararVocal(letra_detectada)
                    print(f"Tu respuesta fue: {letra_detectada}. Respuesta: {camara.respuesta_vocal}")
                else:
                    print("No se detectó ninguna letra")
                break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Liberar recursos
        camara.LiberarRecursos()