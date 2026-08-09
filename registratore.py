import pty
import os

from interprete import (
    MARCATORE, PROMPT_SENTINELLA,
    M_NOTA, M_FILE_INIZIO, M_FILE_FINE, M_IMG,
)


def _config_bash():
    """Contenuto della rcfile: prompt, marcatore dei comandi e primitive manuali."""
    return (
        f"export PS1='{PROMPT_SENTINELLA}'\n"
        "export HISTCONTROL=\n"
        f"export PROMPT_COMMAND='echo \"{MARCATORE}$(history 1 | sed \"s/^ *[0-9]*  *//\")\"'\n"
        # primitive per agganciare cose che NON passano dal terminale:
        f"wnote() {{ echo \"{M_NOTA}$*\"; }}\n"
        f"wfile() {{ echo \"{M_FILE_INIZIO}$1\"; cat \"$1\"; echo; echo \"{M_FILE_FINE}\"; }}\n"
        f"wshot() {{ echo \"{M_IMG}$1\"; }}\n"
    )


def registra(file_sessione="sessione.txt", file_rc=".writeup_bashrc"):
    """Apre una bash interattiva registrando comandi e output in un file.

    Oltre ai comandi normali, dentro la sessione hai a disposizione:
      wnote "testo"   -> annota un'osservazione (es. analisi in Ghidra)
      wfile solve.py  -> incorpora il contenuto di un file (script, decompilato)
      wshot img.png   -> allega uno screenshot (Ghidra, Burp, browser)
    """
    with open(file_rc, "w") as f:
        f.write(_config_bash())

    print(f"Registro la sessione in '{file_sessione}'.")
    print("Comandi extra: wnote \"testo\" | wfile <file> | wshot <img>")
    print("Esegui la challenge, poi digita 'exit' per terminare.\n")

    with open(file_sessione, "wb") as log:
        def leggi_output(fd):
            dati = os.read(fd, 1024)
            log.write(dati)
            return dati

        pty.spawn(["/bin/bash", "--rcfile", file_rc, "-i"], leggi_output)

    print(f"\nSessione salvata in '{file_sessione}'.")


if __name__ == "__main__":
    registra()
