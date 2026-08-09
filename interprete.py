import re

MARCATORE = "===WRITEUP_CMD==="
PROMPT_SENTINELLA = "WUP$ "

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


def estrai_blocchi(nome_file="sessione.txt"):
    """Legge una sessione registrata e restituisce i blocchi comando+output.

    Formato prodotto da registratore.py: l'output di un comando precede il
    marcatore che lo chiude; il marcatore porta con sé il comando eseguito
    (preso da `history`, quindi pulito dagli errori di battitura).
    """
    with open(nome_file, "r", encoding="utf-8", errors="replace") as f:
        contenuto = f.read()

    righe = pulisci(contenuto).splitlines()

    blocchi = []
    buffer = []
    for riga in righe:
        if riga.startswith(MARCATORE):
            comando = riga[len(MARCATORE):].strip()
            output = _ripulisci_output(buffer)
            buffer = []
            # salta il blocco di avvio (comando vuoto) e l'uscita dalla shell
            if comando and comando != "exit":
                blocchi.append({"comando": comando, "output": output})
        else:
            buffer.append(riga)

    return blocchi
