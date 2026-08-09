# writeupctf

Genera automaticamente writeup per challenge CTF partendo da una sessione di
terminale registrata. Registri i comandi che usi per risolvere la challenge,
e un modello DeepSeek li trasforma in un writeup in italiano.

## Come funziona

Pipeline in quattro passi:

1. **`registratore.py`** — apre una bash interattiva e registra comandi + output
   in `sessione.txt`. Il comando viene letto da `history` (non dai tasti premuti),
   quindi resta pulito anche se correggi mentre digiti.
2. **`interprete.py`** — ripulisce l'output dal "rumore" del terminale (sequenze
   ANSI, prompt) e lo divide in blocchi comando+output.
3. **`intelligenza.py`** — manda i blocchi a DeepSeek e genera la prosa del writeup.
4. **`scrittore.py`** — salva il writeup finale (prosa AI + appendice dei comandi).

## Requisiti

- Python ≥ 3.13
- Una API key DeepSeek in un file `.env`:

  ```
  DEEPSEEK_API_KEY=sk-...
  ```

Installazione dipendenze (con [uv](https://github.com/astral-sh/uv)):

```bash
uv sync
```

## Uso

**1. Registra la sessione** mentre risolvi la challenge:

```bash
python registratore.py
# ... esegui i comandi ...
exit
```

**2. Genera il writeup:**

```bash
python main.py --nome "Nome Challenge" --categoria web --punti 200 --difficolta media
```

Il writeup viene scritto in `writeup.md`.

### Opzioni principali

| Opzione | Descrizione |
|---|---|
| `-s, --sessione` | File della sessione (default `sessione.txt`) |
| `-o, --output` | File di destinazione (default `writeup.md`) |
| `-m, --modello` | Modello DeepSeek (default `deepseek-v4-flash`) |
| `--nome / --categoria / --punti / --difficolta` | Metadati della challenge |
| `--no-stream` | Disattiva lo streaming a schermo |
| `--no-appendice` | Non allegare l'elenco dei comandi |
| `--invia-flag` | Invia le flag all'API (default: **redatte** prima dell'invio) |
| `--max-output N` | Tronca gli output più lunghi di N caratteri |

## Sicurezza / privacy

La sessione viene inviata a un servizio esterno (DeepSeek). Prima dell'invio,
`sicurezza.py` **redige** flag, chiavi private, JWT, API key e assegnazioni tipo
`password=...`. Le flag sono redatte per default: usa `--invia-flag` se vuoi che
l'AI ne parli nel testo. In ogni caso, l'**appendice dei comandi nel writeup
locale conserva i valori originali** (la flag resta nel tuo file, non viene mai
persa).

## Limiti noti

- La cattura è pensata per bash; comandi multi-riga (heredoc, cicli `for` su più
  righe) possono finire spezzati.
- La redazione è basata su pattern: controlla sempre il writeup prima di pubblicarlo.
