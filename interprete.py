import re

MARCATORE = "===WRITEUP_CMD==="
PROMPT_SENTINELLA = "WUP$ "

# marcatori delle primitive manuali (funzioni wnote/wfile/wshot nella shell)
M_NOTA = "===WRITEUP_NOTE==="
M_FILE_INIZIO = "===WRITEUP_FILE_BEGIN==="
M_FILE_FINE = "===WRITEUP_FILE_END==="
M_IMG = "===WRITEUP_IMG==="

# nomi delle funzioni helper: i loro comandi non vanno trattati come passi normali
HELPER = ("wnote", "wfile", "wshot")

# --- pulizia del testo del terminale --------------------------------------

_OSC = re.compile(r'\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)')   # sequenze OSC (titoli finestra, ecc.)
_CSI = re.compile(r'\x1b\[[0-9;?]*[ -/]*[@-~]')           # sequenze CSI (colori, [?1034h, [K, ...)
_ESC = re.compile(r'\x1b[@-Z\\-_]')                       # altri escape a due byte
_CTRL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')       # residui di controllo (tranne \n e \t)


def pulisci(testo):
    """Rimuove sequenze ANSI/di controllo dal testo grezzo del terminale."""
    testo = testo.replace("\r\n", "\n").replace("\r", "")
    testo = _OSC.sub("", testo)
    testo = _CSI.sub("", testo)
    testo = _ESC.sub("", testo)
    testo = _CTRL.sub("", testo)
    return testo


def _ripulisci_output(righe):
    """Toglie le righe di prompt (l'eco del comando digitato) e gli spazi ai bordi."""
    out = [r for r in righe if not r.startswith(PROMPT_SENTINELLA)]
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return out


def estrai_elementi(nome_file="sessione.txt"):
    """Legge una sessione registrata e restituisce una lista di elementi tipizzati.

    Ogni elemento è un dict con chiave "tipo":
      - {"tipo": "comando",  "comando": str, "output": [str]}
      - {"tipo": "nota",     "testo": str}
      - {"tipo": "file",     "nome": str, "contenuto": str}
      - {"tipo": "immagine", "percorso": str}

    I comandi normali vengono chiusi dal marcatore che ne porta il testo (da
    history). Le primitive manuali (wnote/wfile/wshot) emettono marcatori
    dedicati e non compaiono come passi a sé.
    """
    with open(nome_file, "r", encoding="utf-8", errors="replace") as f:
        righe = pulisci(f.read()).splitlines()

    elementi = []
    buffer = []
    file_nome = None
    file_righe = None

    for riga in righe:
        # dentro un blocco file: accumula finché non arriva la fine
        if file_nome is not None:
            if riga.startswith(M_FILE_FINE):
                elementi.append({
                    "tipo": "file",
                    "nome": file_nome,
                    "contenuto": "\n".join(file_righe).strip("\n"),
                })
                file_nome = None
                file_righe = None
            else:
                file_righe.append(riga)
            continue

        if riga.startswith(M_FILE_INIZIO):
            file_nome = riga[len(M_FILE_INIZIO):].strip() or "file"
            file_righe = []
        elif riga.startswith(M_NOTA):
            testo = riga[len(M_NOTA):].strip()
            if testo:
                elementi.append({"tipo": "nota", "testo": testo})
        elif riga.startswith(M_IMG):
            percorso = riga[len(M_IMG):].strip()
            if percorso:
                elementi.append({"tipo": "immagine", "percorso": percorso})
        elif riga.startswith(MARCATORE):
            comando = riga[len(MARCATORE):].strip()
            output = _ripulisci_output(buffer)
            buffer = []
            prima_parola = comando.split(" ", 1)[0] if comando else ""
            # salta avvio (vuoto), uscita shell e le funzioni helper
            if comando and comando != "exit" and prima_parola not in HELPER:
                elementi.append({"tipo": "comando", "comando": comando, "output": output})
        else:
            buffer.append(riga)

    return elementi
