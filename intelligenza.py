import os
import sys
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

from sicurezza import redigi

MODELLO_DEFAULT = "deepseek-v4-flash"


def _tronca(testo, massimo):
    if len(testo) > massimo:
        return testo[:massimo] + f"\n...[{len(testo) - massimo} caratteri troncati]..."
    return testo


def _serializza(elementi, max_char_output=2000):
    """Serializza gli elementi tipizzati in testo per il prompt."""
    parti = []
    for e in elementi:
        tipo = e["tipo"]
        if tipo == "comando":
            output = _tronca("\n".join(e["output"]), max_char_output)
            parti.append(f"Comando: {e['comando']}\nOutput:\n{output}")
        elif tipo == "nota":
            parti.append(f"Nota dell'autore: {e['testo']}")
        elif tipo == "file":
            parti.append(f"File allegato '{e['nome']}':\n{_tronca(e['contenuto'], max_char_output)}")
        elif tipo == "immagine":
            parti.append(f"Screenshot allegato: {e['percorso']}")
    return "\n\n".join(parti)


def genera_prosa(elementi, metadati=None, modello=MODELLO_DEFAULT, stream=True,
                 invia_flag=False, on_chunk=None, max_char_output=2000):
    """Trasforma gli elementi (comandi, note, file, screenshot) in prosa da writeup.

    - redige i segreti prima dell'invio (flag comprese, se invia_flag=False);
    - tronca gli output enormi per non gonfiare il prompt;
    - usa lo streaming per far comparire il testo man mano;
    - disattiva il reasoning nascosto (altrimenti lentissimo).
    """
    riassunto = _serializza(elementi, max_char_output)
    riassunto, redazioni = redigi(riassunto, redigi_flag=not invia_flag)
    if redazioni:
        print(f"[sicurezza] redatti prima dell'invio: {redazioni}", file=sys.stderr)

    intestazione = ""
    if metadati:
        campi = [f"- {chiave}: {valore}" for chiave, valore in metadati.items() if valore]
        if campi:
            intestazione = "Dettagli della challenge:\n" + "\n".join(campi) + "\n\n"

    sistema = (
        "Sei un esperto di CTF. Scrivi un writeup chiaro e ben strutturato in italiano, "
        "in formato Markdown, spiegando cosa fa ogni passo e la logica della soluzione. "
        "Il materiale può contenere comandi con output, note dell'autore, file di codice "
        "(es. exploit) e riferimenti a screenshot: integrali nel racconto in modo coerente. "
        "Non inventare passaggi o dettagli non presenti nel materiale fornito. "
        "Non includere un titolo H1 (# ...): il titolo viene aggiunto a parte, "
        "inizia direttamente dalle sezioni (## ...)."
    )
    utente = intestazione + "Ecco il materiale della challenge:\n\n" + riassunto

    try:
        api_key = os.environ["DEEPSEEK_API_KEY"]
    except KeyError:
        raise RuntimeError("DEEPSEEK_API_KEY non impostata: controlla il file .env")

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com", timeout=120.0)
    messaggi = [
        {"role": "system", "content": sistema},
        {"role": "user", "content": utente},
    ]
    kwargs = dict(model=modello, reasoning_effort="none", messages=messaggi)

    try:
        if stream:
            pezzi = []
            emetti = on_chunk or (lambda t: print(t, end="", flush=True))
            risposta = client.chat.completions.create(stream=True, **kwargs)
            for chunk in risposta:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta.content
                if delta:
                    pezzi.append(delta)
                    emetti(delta)
            if on_chunk is None:
                print()
            return "".join(pezzi)

        risposta = client.chat.completions.create(**kwargs)
        return risposta.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Errore durante la chiamata a DeepSeek: {e}")
