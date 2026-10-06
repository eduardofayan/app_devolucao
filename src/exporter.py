from pathlib import Path
import pandas as pd

# Função para exportar registros de devoluções de um determinado mês e ano para um arquivo Excel.
def exportar_mes(db, mes, ano, caminho):
    registros = db.buscar_mes_exportacao(
        mes,
        ano
    )
    if not registros:
        raise ValueError(
            "Nenhuma devolução encontrada "
            "para o período selecionado."
        )

    df = pd.DataFrame(
        [
            dict(row)
            for row in registros
        ]
    )

    # RENOMEAR COLUNAS
    df.rename(
        columns={
            "id": "ID",
            "conferente_abertura":
                "CONFERENTE ABERTURA",
            "numero_oc":
                "NUMERO OC",
            "placa_caminhao":
                "PLACA CAMINHAO",
            "motivo":
                "MOTIVO",
            "cliente":
                "CLIENTE",
            "valor_nf":
                "VALOR NF",
            "data_hora_inicio":
                "DATA HORA INICIO",
            "data_hora_fim":
                "DATA HORA FIM",
            "conferente_finalizacao":
                "CONFERENTE FINALIZACAO",
            "status":
                "STATUS"
        },
        inplace=True
    )

    # DURAÇÃO
    inicio = pd.to_datetime(df["DATA HORA INICIO"])
    fim = pd.to_datetime(df["DATA HORA FIM"],errors="coerce")
    duracao = fim - inicio

    df["DURACAO"] = duracao.apply(
        lambda x:
        str(x).split(".")[0]
        if pd.notna(x)
        else ""
    )

    # FORMATAR DATAS
    df["DATA HORA INICIO"] = (inicio.dt.strftime("%d/%m/%Y %H:%M:%S"))
    df["DATA HORA FIM"] = (fim.dt.strftime("%d/%m/%Y %H:%M:%S"))

    caminho = Path(caminho)
    with pd.ExcelWriter(caminho, engine="openpyxl") as writer:
        df.to_excel(writer,sheet_name="DEVOLUCOES",index=False)
        ws = writer.book["DEVOLUCOES"]

        # Cabeçalho
        for cell in ws[1:1]:
            cell.font = cell.font.copy(bold=True)

        # Formatação monetária
        coluna_valor = None

        for cell in ws[1:1]:
            if cell.value == "VALOR NF":
                coluna_valor = cell.column
                break

        if coluna_valor:
            for row in range(2,ws.max_row + 1):
                ws.cell(row=row, column=coluna_valor).number_format = ('R$ #,##0.00')

        # Autofiltro
        ws.auto_filter.ref = (ws.dimensions)

        # Congelar cabeçalho
        ws.freeze_panes = "A2"

        # Ajustar largura
        for coluna in ws.columns:
            tamanho = max(
                len(
                    str(
                        cell.value or ""
                    )
                )
                for cell in coluna
            )

            ws.column_dimensions[
                coluna[0].column_letter
            ].width = min(
                tamanho + 2,
                45
            )

    return caminho