import os

# estensione -> linguaggio per l'evidenziazione nei blocchi di codice
_LINGUAGGI = {
    ".py": "python", ".c": "c", ".cpp": "cpp", ".h": "c",
    ".sh": "bash", ".js": "javascript", ".rb": "ruby",
    ".php": "php", ".go": "go", ".rs": "rust", ".java": "java",
}


def _linguaggio(nome):
    return _LINGUAGGI.get(os.path.splitext(nome)[1].lower(), "")


def scrivi_writeup(elementi, prosa=None, metadati=None, nome_file="writeup.md",
                   includi_appendice=True):
    """Scrive il writeup finale: prosa generata dall'AI + appendice del materiale.

    L'appendice usa gli elementi ORIGINALI (non redatti): la flag resta nel tuo
    file locale anche se non è stata inviata all'API.
    """
    metadati = metadati or {}
    with open(nome_file, "w", encoding="utf-8") as out:
        titolo = metadati.get("nome") or "Writeup"
        out.write(f"# {titolo}\n\n")

        righe_meta = [
            f"- **{chiave.capitalize()}:** {valore}"
            for chiave, valore in metadati.items()
            if valore and chiave != "nome"
        ]
        if righe_meta:
            out.write("\n".join(righe_meta) + "\n\n")

        if prosa:
            out.write(prosa.rstrip() + "\n\n")

        if includi_appendice:
            out.write("---\n\n## Appendice\n\n")
            for e in elementi:
                tipo = e["tipo"]
                if tipo == "comando":
                    out.write("**Comando:**\n\n```bash\n" + e["comando"] + "\n```\n\n")
                    if e["output"]:
                        out.write("**Output:**\n\n```\n" + "\n".join(e["output"]) + "\n```\n\n")
                elif tipo == "nota":
                    out.write("> " + e["testo"] + "\n\n")
                elif tipo == "file":
                    out.write(f"**File `{e['nome']}`:**\n\n")
                    out.write(f"```{_linguaggio(e['nome'])}\n" + e["contenuto"] + "\n```\n\n")
                elif tipo == "immagine":
                    out.write(f"![{os.path.basename(e['percorso'])}]({e['percorso']})\n\n")
