import requests
import pyautogui
import threading
import time

# --- CONFIGURATION ---
URL_RASPBERRY = "http://172.20.10.2:5000/api/donnees_souris"

SENSIBILITE_X = 0.1
SENSIBILITE_Y = 0.1
ZONE_MORTE = 50
SENSIBILITE_MOLETTE = 1
SEUIL_MOLETTE = 1

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0

valeur_pot_precedente = None
x_lisse = 0
y_lisse = 0
programme_en_cours = True

etat_gauche_prec = False
etat_droit_prec = False

print("Connexion au Raspberry Pi en cours...")

try:
    while programme_en_cours:
        try:
            # On interroge le Raspberry Pi pour tout récupérer d'un coup
            reponse = requests.get(URL_RASPBERRY, timeout=0.05)
            data = reponse.json()
            
            x_brut = data["x"]
            y_brut = data["y"]
            pot_brut = data["pot"]
            clic_gauche = data["clic_gauche"]
            clic_droit = data["clic_droit"]
            
            # --- CORRECTION 12 BITS ---
            if x_brut > 2047:
                x_brut -= 4096
            if y_brut > 2047:
                y_brut -= 4096

            # Inversion des axes si besoin
            x_brut, y_brut = y_brut, x_brut

            # --- LISSAGE ---
            x_lisse = (x_brut * 0.2) + (x_lisse * 0.8)
            y_lisse = (y_brut * 0.2) + (y_lisse * 0.8)

            # --- MOUVEMENT CURSEUR ---
            deplacement_x = 0
            deplacement_y = 0
            
            if abs(x_lisse) > ZONE_MORTE:
                deplacement_x = int(x_lisse * SENSIBILITE_X)
            if abs(y_lisse) > ZONE_MORTE:
                deplacement_y = int(y_lisse * SENSIBILITE_Y)
                
            if deplacement_x != 0 or deplacement_y != 0:
                pyautogui.move(deplacement_x, deplacement_y)
                
            # --- MOLETTE ---
            if valeur_pot_precedente is None:
                valeur_pot_precedente = pot_brut
                
            delta_pot = pot_brut - valeur_pot_precedente
            if abs(delta_pot) > SEUIL_MOLETTE:
                pyautogui.scroll(int(delta_pot * SENSIBILITE_MOLETTE))
                valeur_pot_precedente = pot_brut

            # --- CLIC GAUCHE : MAINTIEN ---
            if clic_gauche and not etat_gauche_prec:
                pyautogui.mouseDown(button='left')

            elif not clic_gauche and etat_gauche_prec:
                pyautogui.mouseUp(button='left')

            # --- CLIC DROIT : CLIC SIMPLE ---
            if clic_droit and not etat_droit_prec:
                pyautogui.click(button='right')

            # Mise à jour des états précédents
            etat_gauche_prec = clic_gauche
            etat_droit_prec = clic_droit
            
        except requests.exceptions.RequestException:
            # Petite pause si le réseau tousse un coup
            time.sleep(0.01)
            
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nArrêt du programme PC.")