import pty
import os

from interprete import MARCATORE, PROMPT_SENTINELLA


def registra(file_sessione="sessione.txt", file_rc=".writeup_bashrc"):
    """Apre una bash interattiva registrando comandi e output in un file.

    Usa un PROMPT_COMMAND che, dopo ogni comando, stampa il marcatore seguito
    dal comando realmente eseguito (letto da `history`, non dai tasti premuti).
    Così il parser ottiene il comando pulito anche se durante la digitazione
    hai corretto o cancellato dei caratteri.
    """
    config = (
        f"export PS1='{PROMPT_SENTINELLA}'\n"
        "export HISTCONTROL=\n"
        f"export PROMPT_COMMAND='echo \"{MARCATORE}$(history 1 | sed \"s/^ *[0-9]*  *//\")\"'\n"
    )
    with open(file_rc, "w") as f:
        f.write(config)

    print(f"Registro la sessione in '{file_sessione}'.")
    print("Esegui i comandi della challenge, poi digita 'exit' per terminare.\n")

    with open(file_sessione, "wb") as log:
        def leggi_output(fd):
            dati = os.read(fd, 1024)
            log.write(dati)
            return dati

        pty.spawn(["/bin/bash", "--rcfile", file_rc, "-i"], leggi_output)

    print(f"\nSessione salvata in '{file_sessione}'.")


if __name__ == "__main__":
    registra()
