import re

# Regole di redazione: (nome, pattern, sostituto).
# Servono a NON mandare segreti a un servizio esterno (DeepSeek) quando si
# genera la prosa del writeup. La flag è trattata a parte: spesso la vuoi nel
# tuo writeup locale, ma non necessariamente inviata all'API.

_REGOLE = [
    ("flag",        re.compile(r'(?i)\b(?:flag|ctf|htb|thm|picoCTF)\{[^}\n]*\}'), "[FLAG-REDATTA]"),
    ("chiave_privata", re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----', re.S), "[CHIAVE-PRIVATA-REDATTA]"),
    ("jwt",         re.compile(r'\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+'), "[JWT-REDATTO]"),
    ("aws_key",     re.compile(r'\bAKIA[0-9A-Z]{16}\b'), "[AWS-KEY-REDATTA]"),
    ("sk_key",      re.compile(r'\bsk-[A-Za-z0-9]{16,}\b'), "[API-KEY-REDATTA]"),
    ("bearer",      re.compile(r'(?i)\bbearer\s+[A-Za-z0-9._\-]{8,}'), "Bearer [TOKEN-REDATTO]"),
    ("assegnazione_segreta", re.compile(r'(?i)\b(password|passwd|pwd|secret|token|api[_-]?key)\b(\s*[=:]\s*)\S+'), r"\1\2[REDATTO]"),
]


def redigi(testo, redigi_flag=True):
    """Redige segreti dal testo. Restituisce (testo_redatto, conteggio).

    Se `redigi_flag` è False, le flag vengono lasciate in chiaro (utile se vuoi
    che l'AI ne parli esplicitamente nel writeup).
    """
    conteggio = {}
    for nome, pattern, sostituto in _REGOLE:
        if nome == "flag" and not redigi_flag:
            continue
        testo, n = pattern.subn(sostituto, testo)
        if n:
            conteggio[nome] = n
    return testo, conteggio
