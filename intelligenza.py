import os
import sys
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

from sicurezza import redigi

MODELLO_DEFAULT = "deepseek-v4-flash"


def _costruisci_riassunto(blocchi, max_char_output=2000):
    """Serializza i blocchi in testo, troncando gli output troppo lunghi."""
    parti = []
    for b in blocchi:
        output = "\n".join(b["output"])
        if len(output) > max_char_output:
            tagliati = len(output) - max_char_output
            output = output[:max_char_output] + f"\n...[{tagliati} caratteri troncati]..."
        parti.append(f"Comando: {b['comando']}\nOutput:\n{output}")
    return "\n\n".join(parti)


def genera_prosa(blocchi, metadati=None, modello=MODELLO_DEFAULT, stream=True,
                 invia_flag=False, on_chunk=None, max_char_output=2000):
    """Trasforma i blocchi comando+output in prosa da writeup, usando DeepSeek.

    - redige i segreti prima dell'invio (flag comprese, se invia_flag=False);
    - tronca gli output enormi per non gonfiare il prompt;
    - usa lo streaming per far comparire il testo man mano;
    - disattiva il reasoning nascosto (altrimenti lentissimo).
    """
    riassunto = _costruisci_riassunto(blocchi, max_char_output)
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
        "Non inventare passaggi o dettagli non presenti negli output forniti. "
        "Non includere un titolo H1 (# ...): il titolo viene aggiunto a parte, "
        "inizia direttamente dalle sezioni (## ...)."
    )
    utente = intestazione + "Ecco i comandi e gli output della challenge:\n\n" + riassunto

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
