from dataclasses import dataclass


@dataclass(frozen=True)
class QRData:
    codigo: str
    grade: str
    op: str
    seq_apon: str
    quantidade: int


class QRParser:

    @staticmethod
    def parse(leitura: str) -> QRData:

        leitura = leitura.strip()

        if not leitura:
            raise ValueError("QR vazio.")

        partes = leitura.split("-")

        if len(partes) < 6:
            raise ValueError("QR inválido.")

        try:
            quantidade = int(partes[4])
        except ValueError:
            raise ValueError(
                f"Quantidade inválida no QR: {partes[4]}"
            )

        return QRData(
            codigo=partes[0].strip(),
            grade=partes[1].strip(),
            op=partes[2].strip(),
            seq_apon=partes[3].strip(),
            quantidade=quantidade
        )