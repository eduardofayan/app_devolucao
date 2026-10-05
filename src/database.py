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
                    cliente TEXT NOT NULL,
                    valor_nf REAL NOT NULL,
                    data_hora_inicio TEXT NOT NULL,
                    data_hora_fim TEXT,
                    conferente_finalizacao TEXT,
                    status TEXT NOT NULL
                        DEFAULT 'ABERTA'
                )
                """
            )

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
    def criar_devolucao(self, conferente, numero_oc, placa, motivo, cliente, valor_nf):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with self.conectar() as conn:
            cursor = conn.execute(
                """
                INSERT INTO devolucoes
                (
                    conferente_abertura,
                    numero_oc,
                    placa_caminhao,
                    motivo,
                    cliente,
                    valor_nf,
                    data_hora_inicio,
                    status
                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    conferente,
                    numero_oc,
                    placa.upper(),
                    motivo,
                    cliente,
                    valor_nf,
                    agora,
                    "ABERTA"
                )
            )

            conn.commit()
            return cursor.lastrowid

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
    def finalizar_devolucao(self, devolucao_id, conferente):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Atualiza a devolução para finalizada com a data e hora atual.
        with self.conectar() as conn:
            cursor = conn.execute(
                """
                UPDATE devolucoes

                SET
                    data_hora_fim = ?,
                    conferente_finalizacao = ?,
                    status = 'FINALIZADA'

                WHERE id = ?
                AND status = 'ABERTA'
                """,
                (
                    agora,
                    conferente,
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