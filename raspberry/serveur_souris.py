from flask import Flask, jsonify, render_template_string
from gpiozero import Button
import serial
import threading
import time

app = Flask(__name__)

# --- CONFIGURATION BOUTONS ---
btn_clic_gauche = Button(17, pull_up=True)
btn_clic_droit = Button(27, pull_up=True)

# --- CONFIGURATION ARDUINO ---
PORT_SERIE = '/dev/ttyACM0'
BAUD_RATE = 115200

x_brut = 0
y_brut = 0
pot_brut = 0


# --- LECTURE ARDUINO ---
def lire_arduino():
    global x_brut, y_brut, pot_brut

    try:
        arduino = serial.Serial(PORT_SERIE, BAUD_RATE, timeout=1)
        print("Connecté à l'Arduino sur le Pi !")

        while True:
            if arduino.in_waiting > 0:
                ligne = arduino.readline().decode(
                    'utf-8', errors='ignore'
                ).strip()

                if ligne:
                    donnees = ligne.split(',')

                    if len(donnees) == 3:
                        try:
                            x_brut = int(donnees[0])
                            y_brut = int(donnees[1])
                            pot_brut = int(donnees[2])
                        except ValueError:
                            pass

            time.sleep(0.01)

    except Exception as e:
        print(f"Erreur série sur le Pi : {e}")


# --- INTERFACE WEB ---
HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Mouse Controller | Raspberry Pi</title>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    background: #0b1120;
    color: #e2e8f0;
    min-height: 100vh;
    padding: 35px 20px;
}

.container {
    max-width: 950px;
    margin: auto;
}

header {
    text-align: center;
    margin-bottom: 40px;
}

.logo {
    font-size: 36px;
    margin-bottom: 12px;
}

h1 {
    font-size: 28px;
    color: white;
    margin-bottom: 10px;
}

.subtitle {
    color: #94a3b8;
    font-size: 14px;
}

.status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-top: 20px;
    padding: 9px 16px;
    background: #142d28;
    border: 1px solid #22543d;
    border-radius: 30px;
    color: #4ade80;
    font-size: 13px;
}

.dot {
    width: 8px;
    height: 8px;
    background: #4ade80;
    border-radius: 50%;
}

.section-title {
    font-size: 16px;
    color: #94a3b8;
    margin-bottom: 16px;
    font-weight: normal;
}

.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 35px;
}

.card {
    background: #151f32;
    border: 1px solid #263449;
    border-radius: 16px;
    padding: 25px;
    min-height: 150px;
}

.card-label {
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 20px;
}

.card-value {
    font-size: 34px;
    font-weight: bold;
    color: white;
    font-variant-numeric: tabular-nums;
}

.unit {
    font-size: 14px;
    color: #64748b;
    margin-left: 5px;
}

.buttons {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
}

.button-card {
    background: #151f32;
    border: 1px solid #263449;
    border-radius: 16px;
    padding: 25px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: 0.2s;
}

.button-name {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 7px;
}

.button-description {
    font-size: 12px;
    color: #64748b;
}

.badge {
    padding: 9px 15px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: bold;
    min-width: 90px;
    text-align: center;
}

.released {
    background: #263449;
    color: #94a3b8;
}

.pressed {
    background: #14532d;
    color: #4ade80;
    border: 1px solid #22c55e;
}

footer {
    margin-top: 40px;
    text-align: center;
    color: #64748b;
    font-size: 12px;
}

@media(max-width: 650px) {
    .grid {
        grid-template-columns: repeat(2, 1fr);
    }

    .buttons {
        grid-template-columns: 1fr;
    }

    .card-value {
        font-size: 28px;
    }
}
</style>
</head>

<body>

<div class="container">

    <header>
        <div class="logo">🖱️</div>
        <h1>Mouse Controller</h1>
        <p class="subtitle">Raspberry Pi · Real-time monitoring</p>

        <div class="status" id="connection">
            <span class="dot"></span>
            Connexion active
        </div>
    </header>

    <h2 class="section-title">Données des capteurs</h2>

    <div class="grid">

        <div class="card">
            <div class="card-label">Axe X</div>
            <div class="card-value" id="x">0</div>
        </div>

        <div class="card">
            <div class="card-label">Axe Y</div>
            <div class="card-value" id="y">0</div>
        </div>

        <div class="card">
            <div class="card-label">Potentiomètre</div>
            <div class="card-value" id="pot">0</div>
        </div>

    </div>

    <h2 class="section-title">État des boutons</h2>

    <div class="buttons">

        <div class="button-card">
            <div>
                <div class="button-name">🖱️ Clic gauche</div>
                <div class="button-description">GPIO 17</div>
            </div>
            <div class="badge released" id="gauche">
                RELÂCHÉ
            </div>
        </div>

        <div class="button-card">
            <div>
                <div class="button-name">🖱️ Clic droit</div>
                <div class="button-description">GPIO 27</div>
            </div>
            <div class="badge released" id="droit">
                RELÂCHÉ
            </div>
        </div>

    </div>

    <footer>
        Raspberry Pi Mouse Controller · Actualisation automatique
        <br><br>
        Dernière mise à jour : <span id="update">--:--:--</span>
    </footer>

</div>

<script>
async function actualiserDonnees() {

    const connection = document.getElementById("connection");

    try {
        const response = await fetch("/api/donnees_souris");

        if (!response.ok) {
            throw new Error("Erreur serveur");
        }

        const data = await response.json();

        document.getElementById("x").textContent = data.x;
        document.getElementById("y").textContent = data.y;
        document.getElementById("pot").textContent = data.pot;

        afficherBouton("gauche", data.clic_gauche);
        afficherBouton("droit", data.clic_droit);

        connection.innerHTML =
            '<span class="dot"></span> Connexion active';

        connection.style.color = "#4ade80";
        connection.style.background = "#142d28";

        document.getElementById("update").textContent =
            new Date().toLocaleTimeString("fr-FR");

    } catch (error) {

        connection.innerHTML =
            '<span class="dot"></span> Connexion perdue';

        connection.style.color = "#f87171";
        connection.style.background = "#451a1a";
    }
}

function afficherBouton(id, appuye) {

    const element = document.getElementById(id);

    if (appuye) {
        element.textContent = "APPUYÉ";
        element.className = "badge pressed";
    } else {
        element.textContent = "RELÂCHÉ";
        element.className = "badge released";
    }
}

actualiserDonnees();
setInterval(actualiserDonnees, 150);
</script>

</body>
</html>
"""


# --- API JSON POUR LE PROGRAMME PC ---
@app.route('/api/donnees_souris', methods=['GET'])
def get_api_donnees():

    return jsonify({
        "x": x_brut,
        "y": y_brut,
        "pot": pot_brut,
        "clic_gauche": btn_clic_gauche.is_pressed,
        "clic_droit": btn_clic_droit.is_pressed
    })


# --- PAGE WEB ---
@app.route('/donnees_souris', methods=['GET'])
def page_donnees():

    return render_template_string(HTML)


# --- DEMARRAGE ---
if __name__ == '__main__':

    t_serie = threading.Thread(target=lire_arduino)
    t_serie.daemon = True
    t_serie.start()

    print("Serveur Raspberry Pi démarré !")
    print("Interface : http://172.20.10.2:5000/donnees_souris")

    app.run(host='0.0.0.0', port=5000)
