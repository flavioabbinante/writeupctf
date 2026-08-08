import pty
import sys
import os


# il file dove salviamo tutto quello che passa nel terminale
file_log = open("sessione.txt", "wb")

# questa funzione viene chiamata ogni volta che la shell
# stampa qualcosa (output). "dati" sono i byte che escono.
def leggi_output(fd):
    dati = os.read(fd, 1024)
    file_log.write(dati)   # li salviamo nel file
    return dati            # e li restituiamo così li vedi anche a schermo

# lancia una shell (bash) e la registra usando la nostra funzione
pty.spawn("/bin/bash", leggi_output)

file_log.close()
print("Sessione salvata in sessione.txt")