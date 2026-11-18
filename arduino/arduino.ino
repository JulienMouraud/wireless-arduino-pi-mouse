#include <Wire.h>

byte adresse_capteur = 0; 
const int pinPotentiometre = A0;

void setup() {
  Wire.begin();       // Initialisation du bus I2C
  Serial.begin(115200); // Initialisation du moniteur série
  
  // Recherche et récupération de l'adresse I2C
  for(byte i = 1; i < 127; i++) {
    Wire.beginTransmission(i);
    if (Wire.endTransmission() == 0) {
      adresse_capteur = i;
      break;
    }
  }

  // Initialisation du BMA400 (Mode normal)
  if (adresse_capteur != 0) {
    Wire.beginTransmission(adresse_capteur);
    Wire.write(0x19);
    Wire.write(0x02);
    Wire.endTransmission();
    delay(100);
  }
}

void loop() {
  if (adresse_capteur != 0) {
    // Lecture de l'accéléromètre                       // On place le pointeur de lecture sur le premier registre de données (Axe X LSB)
    Wire.beginTransmission(adresse_capteur);
    Wire.write(0x04);                                   // 0x04 est le registre de départ (X_LSB)
    Wire.endTransmission(false);                        // false pour maintenir la connexion active
    Wire.requestFrom((int)adresse_capteur, 6);

    if (Wire.available() == 6) {                        // On demande la lecture de 6 octets consécutifs (X_LSB, X_MSB, Y_LSB, Y_MSB, Z_LSB, Z_MSB)
      int16_t x = Wire.read() | (Wire.read() << 8);
      int16_t y = Wire.read() | (Wire.read() << 8);
      int16_t z = Wire.read() | (Wire.read() << 8); // Z lu mais pas forcément utilisé

      // Lecture du potentiomètre (valeur de 0 à 1023)
      int valeurPot = analogRead(pinPotentiometre);

      // Envoi des données formatées : X,Y,Potentiometre
      Serial.print(x);
      Serial.print(",");
      Serial.print(y);
      Serial.print(",");
      Serial.println(valeurPot);
    }
  }
  delay(10);
}