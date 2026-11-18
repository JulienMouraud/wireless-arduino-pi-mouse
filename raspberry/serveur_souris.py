from flask import Flask, jsonify
from gpiozero import Button
import serial
import threading
import time

app = Flask(__name__)

btn_clic_gauche = Button(17, pull_up=True)
btn_clic_droit = Button(27, pull_up=True)

PORT_SERIE = '/dev/ttyACM0' 
BAUD_RATE = 115200

x_brut = 0
y_brut = 0
pot_brut = 0

def lire_arduino():
    global x_brut, y_brut, pot_brut
    try:
        arduino = serial.Serial(PORT_SERIE, BAUD_RATE, timeout=1)
        print("Connecté à l'Arduino sur le Pi !")
        while True:
            if arduino.in_waiting > 0:
                ligne = arduino.readline().decode('utf-8', errors='ignore').strip()
                if ligne:
                    donnees = ligne.split(',')
                    if len(donnees) == 3:
                        x_brut = int(donnees[0])
                        y_brut = int(donnees[1])
                        pot_brut = int(donnees[2])
            time.sleep(0.01)
    except Exception as e:
        print(f"Erreur série sur le Pi : {e}")

# Lancer la lecture de l'Arduino en arrière-plan sur le Pi
t_serie = threading.Thread(target=lire_arduino)
t_serie.daemon = True
t_serie.start()

@app.route('/donnees_souris', methods=['GET'])
def get_donnees():
    return jsonify({
        "x": x_brut,
        "y": y_brut,
        "pot": pot_brut,
        "clic_gauche": btn_clic_gauche.is_pressed,
        "clic_droit": btn_clic_droit.is_pressed
    })

if __name__ == '__main__':
    print("Serveur central Raspberry Pi démarré...")
    app.run(host='0.0.0.0', port=5000)