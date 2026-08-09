import argparse

from interprete import estrai_elementi
from intelligenza import genera_prosa, MODELLO_DEFAULT
from scrittore import scrivi_writeup


def main():
    parser = argparse.ArgumentParser(
        description="Genera un writeup CTF da una sessione registrata con registratore.py."
    )
    parser.add_argument("-s", "--sessione", default="sessione.txt", help="File della sessione registrata")
    parser.add_argument("-o", "--output", default="writeup.md", help="File Markdown di destinazione")
    parser.add_argument("-m", "--modello", default=MODELLO_DEFAULT, help="Modello DeepSeek da usare")
    parser.add_argument("--nome", help="Nome della challenge (titolo del writeup)")
    parser.add_argument("--categoria", help="Categoria (web, pwn, crypto, ...)")
    parser.add_argument("--punti", help="Punti della challenge")
    parser.add_argument("--difficolta", help="Difficoltà")
    parser.add_argument("--no-stream", action="store_true", help="Disattiva lo streaming dell'output")
    parser.add_argument("--no-appendice", action="store_true", help="Non allegare l'elenco dei comandi")
    parser.add_argument("--invia-flag", action="store_true",
                        help="Invia le flag all'API (default: redatte prima dell'invio)")
    parser.add_argument("--max-output", type=int, default=2000,
                        help="Caratteri massimi per output prima del troncamento")
    args = parser.parse_args()

    elementi = estrai_elementi(args.sessione)
    print(f"Trovati {len(elementi)} elementi (comandi, note, file, screenshot)")
    if not elementi:
        print("Nessun elemento trovato. Hai registrato la sessione con 'python registratore.py'?")
        return

    metadati = {
        "nome": args.nome,
        "categoria": args.categoria,
        "punti": args.punti,
        "difficolta": args.difficolta,
    }
    metadati = {chiave: valore for chiave, valore in metadati.items() if valore}

    print("Genero il writeup con l'AI...\n")
    try:
        prosa = genera_prosa(
            elementi,
            metadati=metadati,
            modello=args.modello,
            stream=not args.no_stream,
            invia_flag=args.invia_flag,
            max_char_output=args.max_output,
        )
    except RuntimeError as e:
        print(f"\nErrore: {e}")
        return

    print(f"\n\nScrivo il writeup in '{args.output}'...")
    scrivi_writeup(
        elementi,
        prosa=prosa,
        metadati=metadati,
        nome_file=args.output,
        includi_appendice=not args.no_appendice,
    )
    print("Fatto!")


if __name__ == "__main__":
    main()
