from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
import cv2
from threading import Lock
from detectorVocal import Camara  # Asegúrate de que la clase Camara esté correctamente implementada
import time

app = Flask(__name__)
app.config['DEBUG'] = True

# Variables globales
camara = None
camera_active = False
camara_lock = Lock()

def GenerarFrame():
    """Genera frames para enviar al cliente."""
    global camara, camera_active

    while True:
        with camara_lock:
            if not camera_active or camara is None:
                break

            ret, frame = camara.captura.read()
            if not ret:
                print("Error al leer el frame de la cámara.")
                break

            frame = cv2.flip(frame, 1)  # Efecto espejo

            # Procesar el frame
            frame, letra_detectada = camara.ProcesarFrame(frame, evaluar_dedos=True)

            # Si se detecta una letra, procesarla
            if letra_detectada:
                camara.CompararVocal(letra_detectada)
                print(f"Letra detectada: {letra_detectada}. Respuesta: {camara.respuesta_vocal}")

            # Codificar el frame para transmisión
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

        time.sleep(0.1)

# Ruta para alternar la cámara
@app.route('/toggle_camera', methods=['POST'])
def toggle_camera():
    """Activa o desactiva la cámara."""
    global camera_active, camara

    with camara_lock:
        if camera_active:
            camera_active = False
            if camara:
                camara.captura.release()
                camara = None
            print("Cámara desactivada.")
        else:
            try:
                camara = Camara()
                camera_active = True
                print("Cámara activada.")
            except Exception as e:
                print(f"Error al activar la cámara: {e}")
                return jsonify({"error": "No se pudo activar la cámara"}), 500

    return jsonify({"camera_active": camera_active})

# Ruta para apagar la cámara automáticamente al salir de la página
@app.route('/toggle_camera_off', methods=['POST'])
def toggle_camera_off():
    """Apaga la cámara al salir de la página."""
    global camera_active, camara

    with camara_lock:
        if camera_active:
            camera_active = False
            if camara:
                camara.captura.release()
                camara = None
            print("Cámara apagada automáticamente.")

    return jsonify({"camera_active": camera_active})

# Rutas para las páginas de la aplicación
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/grupo')
def pag1():
    return render_template('grupo.html')

@app.route('/jugar')
def pag2():
    return render_template('jugar.html')

@app.route('/letras')
def pag3():
    return render_template('letras.html')

@app.route('/selcNivel')
def pag4():
    return render_template('selecNivel.html')

@app.route('/redirect', methods=['POST'])
def redirect_level():
    """Redirige según el nivel seleccionado."""
    nivel = request.form.get('nivel')
    if nivel == 'principiante':
        return redirect(url_for('pag5'))
    elif nivel == 'intermedio':
        return redirect(url_for('pag6'))
    elif nivel == 'avanzado':
        return redirect(url_for('pag7'))
    else:
        return redirect(url_for('index'))

@app.route('/nivelPri')
def pag5():
    return render_template('nivelPri.html', camera_active=camera_active)

@app.route('/nivelMed')
def pag6():
    return render_template('nivelMed.html')

@app.route('/nivelAvan')
def pag7():
    return render_template('nivelAvan.html')

@app.route('/get_result')
def get_result():
    """Obtiene la letra propuesta y la respuesta actual."""
    global camara

    with camara_lock:
        if camara:
            return jsonify({
                'letra_propuesta': camara.vocal_propuesta,
                'respuesta': camara.respuesta_vocal
            })

    return jsonify({'letra_propuesta': None, 'respuesta': None})

@app.route('/nueva_letra')
def nueva_letra():
    """Genera una nueva letra propuesta."""
    global camara

    with camara_lock:
        if camara:
            camara.ElegirVocal()
            camara.respuesta_vocal = None

    return jsonify({'letra_propuesta': camara.vocal_propuesta})

@app.route('/video')
def video():
    """Envía frames del video al cliente."""
    global camera_active

    if not camera_active:
        return jsonify({"error": "La cámara no está activa"}), 503

    return Response(GenerarFrame(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/camera_status')
def camera_status():
    """Consulta el estado de la cámara."""
    return jsonify({"camera_ready": camera_active})

if __name__ == '__main__':
    app.run(debug=False)
