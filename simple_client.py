import socket
import threading
import time
import struct

class Client(threading.Thread):
    """
    Classe Client qui permet de gérer la réception de message en provenance du serveur
    et en parallèle de nos propres envois de messages
    """
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket

    def recv_all(self, sock, n):
        """
        Lit exactement n octets depuis le socket
        """
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None  # Connexion coupée
            data += packet
        return data

    def run(self):
        """
        Méthode lancée automatiquement à la création du thread
        et qui permet d'écouter les messages
        """
        while True:
            try:
                # Lire la taille du message sur 4 octets
                raw_len = self.recv_all(self.socket, 4)
                if not raw_len:
                    break  # Fin de la connexion
                message_len = struct.unpack('>I', raw_len)[0]

                # Lire le message complet en fonction de la taille lue précédemment
                raw_msg = self.recv_all(self.socket, message_len)
                if not raw_msg:
                    break
                
                # Affichage du message reçu
                print("Message reçu :", raw_msg)

            except Exception as e:
                # Si quelque chose s'est mal passé, on l'affiche
                print(f"Erreur lors de la réception : {e}")
                break
      

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Création de la socket
soc.connect(("localhost", 1664)) # Connexion vers localhost sur le port 1664

client = Client(soc) # Instanciation de la classe Client pour gérer la réception des messages
client.start() # Puis exécution en parallèle

def send(soc, message):
    """
    Fonction send() permettant d'envoyer un message sur la socket
    Formattage : 4 premiers octets utilisés pour la taille du message puis message inséré après ces 4 premiers octets
    """
    taille = struct.pack('>I', len(message))  # '>I' = entier non signé, 4 octets, big endian
    soc.sendall(taille + message)

# Envoi de "test" sur la socket (vers le serveur) toutes les secondes
while True:
    message = "test"
    send(soc, message.encode())
    time.sleep(1)
