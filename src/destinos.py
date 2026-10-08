from pathlib import Path


PASTA_EMAILS = Path(
    r"\\Jaguar.corp\dados\Global\Inbound\Recebimento\SISTEMA_APP_DEVOLUCAO\EMAILS"
)


def obter_destinatarios(
    destino
):

    if destino == "SEM_EMAIL":

        return []

    arquivo = (
        PASTA_EMAILS /
        f"{destino}.txt"
    )

    if not arquivo.exists():

        raise FileNotFoundError(
            f"Arquivo de e-mails não encontrado:\n"
            f"{arquivo}"
        )

    with open(
        arquivo,
        encoding="utf-8"
    ) as f:

        return [
            linha.strip()
            for linha in f.readlines()
            if linha.strip()
        ]