import os
import sqlite3
from pathlib import Path
from datetime import datetime

# Classe para gerenciar o banco de dados de devoluções.
class DevolucaoDatabase:

    def __init__(self):

        # Cria a pasta onde o banco de dados será armazenado, caso não exista.
        pasta_dados = Path(r"\\Jaguar.corp\dados\Global\Inbound\Recebimento\SISTEMA_APP_DEVOLUCAO\DATABASE")

        # Cria a pasta, caso não exista.
        pasta_dados.mkdir(parents=True,exist_ok=True)

        # Define o caminho completo para o banco de dados.
        self.db_path = (pasta_dados / "devolucoes.db")

        self.criar_tabela()

    # Função para conectar ao banco de dados.
    def conectar(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # Função para criar a tabela de devoluções, caso não exista.
    def criar_tabela(self):
        with self.conectar() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS devolucoes
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conferente_abertura TEXT NOT NULL,
                    numero_oc TEXT NOT NULL,
                    placa_caminhao TEXT NOT NULL,
                    motivo TEXT NOT NULL,
                    clientes TEXT NOT NULL,
                    valor_nf REAL NOT NULL,
                    destino TEXT,
                    data_hora_inicio TEXT NOT NULL,
                    data_hora_fim TEXT,
                    conferente_finalizacao TEXT,
                    status TEXT NOT NULL
                        DEFAULT 'ABERTA'
                )
                """
            )

            # Cria a tabela de OCs relacionadas às devoluções, caso não exista.
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS ocs_devolucao
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    devolucao_id INTEGER NOT NULL,
                    numero_oc TEXT NOT NULL,
                    cliente TEXT NOT NULL,
                    valor_nf REAL NOT NULL,
                    FOREIGN KEY (devolucao_id)
                    REFERENCES devolucoes(id)
                    ON DELETE CASCADE,

                    UNIQUE (
                        devolucao_id,
                        numero_oc
                    )
                )
                """
            )

            try:

                conn.execute(
                    """
                    ALTER TABLE devolucoes
                    ADD COLUMN destino TEXT
                    """
                )

            except sqlite3.OperationalError:
                # Coluna já existe
                pass

            # Índices para melhorar as buscas
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_devolucoes_status
                ON devolucoes(status)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_devolucoes_inicio
                ON devolucoes(data_hora_inicio)
                """
            )

            conn.commit()

    # Função para criar uma nova devolução.
    def criar_devolucao(self, conferente, lista_ocs, placa, motivo):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        valor_total = sum(
            item["valor_nf"]
            for item in lista_ocs
        )

        with self.conectar() as conn:
            clientes = ", ".join(
                sorted(
                    {
                        item["cliente"]
                        for item in lista_ocs
                    }
                )
            )

            cursor = conn.execute(
                """
                INSERT INTO devolucoes
                (
                    conferente_abertura,
                    numero_oc,
                    placa_caminhao,
                    motivo,
                    clientes,
                    valor_nf,
                    data_hora_inicio,
                    status
                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    conferente,

                    ", ".join(
                        item["numero_oc"]
                        for item in lista_ocs
                    ),

                    placa.upper(),

                    motivo,

                    clientes,

                    valor_total,

                    agora,

                    "ABERTA"
                )
            )

            devolucao_id = cursor.lastrowid

            for item in lista_ocs:

                conn.execute(
                    """
                    INSERT INTO ocs_devolucao
                    (
                        devolucao_id,
                        numero_oc,
                        cliente,
                        valor_nf
                    )

                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        devolucao_id,
                        item["numero_oc"],
                        item["cliente"],
                        item["valor_nf"]
                    )
                )

            conn.commit()
            return devolucao_id

    # Função para listar todas as devoluções abertas.
    def listar_abertas(self):
        with self.conectar() as conn:
            registros = conn.execute(
                """
                SELECT *
                FROM devolucoes
                WHERE status = 'ABERTA'
                ORDER BY data_hora_inicio ASC
                """
            ).fetchall()

        return registros

    # Função para finalizar uma devolução.
    def finalizar_devolucao(self, devolucao_id, conferente, destino):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Atualiza a devolução para finalizada com a data e hora atual.
        with self.conectar() as conn:
            cursor = conn.execute(
                """
                UPDATE devolucoes

                SET

                    data_hora_fim = ?,
                    conferente_finalizacao = ?,
                    destino = ?,
                    status = 'FINALIZADA'

                WHERE id = ?
                AND status = 'ABERTA'
                """,
                (
                    agora,
                    conferente,
                    destino,
                    devolucao_id
                )
            )

            conn.commit()

            return cursor.rowcount > 0

    # Função para buscar devoluções por mês.
    def buscar_mes(self,mes,ano):
        mes = str(mes).zfill(2)
        ano = str(ano)
        prefixo = f"{ano}-{mes}"

        with self.conectar() as conn:
            registros = conn.execute(
                """
                SELECT *
                FROM devolucoes
                WHERE
                    substr(
                        data_hora_inicio,
                        1,
                        7
                    ) = ?
                ORDER BY
                    data_hora_inicio ASC
                """,
                (prefixo,)
            ).fetchall()
        return registros

    # Função específica para exportação. Retorna uma linha para cada OC da devolução.
    def buscar_mes_exportacao(self, mes, ano):

        mes = str(mes).zfill(2)
        ano = str(ano)

        prefixo = f"{ano}-{mes}"

        with self.conectar() as conn:

            registros = conn.execute(
                """
                SELECT
                    d.id,
                    d.conferente_abertura,
                    o.numero_oc,
                    o.cliente,
                    d.placa_caminhao,
                    d.motivo,
                    o.valor_nf,
                    d.data_hora_inicio,
                    d.data_hora_fim,
                    d.conferente_finalizacao,
                    d.status

                FROM devolucoes d

                INNER JOIN ocs_devolucao o
                    ON o.devolucao_id = d.id

                WHERE
                    substr(
                        d.data_hora_inicio,
                        1,
                        7
                    ) = ?

                ORDER BY
                    d.data_hora_inicio ASC,
                    d.id ASC,
                    o.id ASC
                """,
                (prefixo,)
            ).fetchall()

        return registros