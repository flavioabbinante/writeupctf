def scrivi_writeup(blocchi, prosa=None, metadati=None, nome_file="writeup.md",
                   includi_appendice=True):
    """Scrive il writeup finale: prosa generata dall'AI + appendice dei comandi.

    L'appendice usa i blocchi ORIGINALI (non redatti), quindi la flag resta nel
    tuo file locale anche se non è stata inviata all'API.
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
            out.write("---\n\n## Appendice: comandi eseguiti\n\n")
            for blocco in blocchi:
                out.write("**Comando:**\n\n")
                out.write("```bash\n" + blocco["comando"] + "\n```\n\n")
                if blocco["output"]:
                    out.write("**Output:**\n\n")
                    out.write("```\n" + "\n".join(blocco["output"]) + "\n```\n\n")
