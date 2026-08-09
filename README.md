# writeupctf

Genera automaticamente writeup per challenge CTF partendo da una sessione di
terminale registrata. Registri i comandi (e, se vuoi, note, script e screenshot)
che usi per risolvere la challenge, e un modello DeepSeek li trasforma in un
writeup in italiano.

## Come funziona

Pipeline in quattro passi:

1. **`registratore.py`** — apre una bash interattiva e registra la sessione in
   `sessione.txt`. Il comando viene letto da `history` (non dai tasti premuti),
   quindi resta pulito anche se correggi mentre digiti. Mette anche a disposizione
   le primitive `wnote` / `wfile` / `wshot` (vedi sotto).
2. **`interprete.py`** — ripulisce l'output dal "rumore" del terminale (sequenze
   ANSI, prompt) e lo divide in **elementi tipizzati**: comando, nota, file, immagine.
3. **`intelligenza.py`** — manda gli elementi a DeepSeek e genera la prosa del writeup.
4. **`scrittore.py`** — salva il writeup finale (prosa AI + appendice del materiale).

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

## Oltre la riga di comando

Nei CTF non si usa solo la shell. Ci sono due casi:

- **Strumenti che girano nel terminale** (Python REPL, `gdb`/`pwndbg`, `pwntools`,
  `radare2`, `nc`...) → sono **già catturati** automaticamente: girano dentro la
  bash registrata, quindi il loro I/O finisce nell'output.
- **Strumenti GUI** (Ghidra, Burp, browser) e **script scritti in un editor** →
  non passano dal terminale, quindi li agganci con tre comandi disponibili durante
  la registrazione:

  | Comando | Cosa fa | Esempio |
  |---|---|---|
  | `wnote "testo"` | annota un'osservazione | `wnote "Ghidra: check() fa XOR 0x42"` |
  | `wfile <file>` | incorpora il contenuto di un file | `wfile solve.py` |
  | `wshot <img>` | allega uno screenshot | `wshot ghidra_main.png` |

  Per Ghidra: esporta il decompilato (`File → Export`) e fai `wfile decompiled.c`,
  oppure fai uno screenshot e `wshot`, aggiungendo `wnote` per il ragionamento.

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

## Changelog

### 1.1.0
- Supporto a tutto ciò che non è pura riga di comando: le primitive `wnote`
  (annotazioni), `wfile` (incorpora uno script o il decompilato) e `wshot`
  (allega uno screenshot).
- Gli strumenti che girano nel terminale (`gdb`, `pwntools`, Python REPL,
  `radare2`...) restano catturati automaticamente.
- Modello dati a elementi tipizzati (comando / nota / file / immagine), integrati
  nel prompt e resi nel writeup. Aggiornamento retrocompatibile nell'uso.

### 1.0.0
- Prima release stabile: registrazione della sessione, parsing in blocchi
  comando+output con pulizia ANSI, generazione della prosa con DeepSeek (streaming,
  reasoning disattivato), redazione di flag/chiavi/token prima dell'invio, CLI con
  metadati e writeup finale in Markdown con appendice dei comandi.
