import sqlite3
import json
from datetime import datetime
import os
import logging

class Database:
    def __init__(self):
        db_path = os.getenv("DATABASE_PATH", "nfce.db")
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        with open("schema.sql", "r") as schema_file:
            schema = schema_file.read()
        self.conn.executescript(schema)
        self.conn.commit()

    def add_user(self, user_id, primeiro_nome, ultimo_nome, nome_usuario):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO usuarios (id, primeiro_nome, ultimo_nome, nome_usuario)
            VALUES (?, ?, ?, ?)
        """,
            (user_id, primeiro_nome, ultimo_nome, nome_usuario),
        )
        self.conn.commit()

    def save_invoice(self, user_id, data):
        cursor = self.conn.cursor()

        # Log the parsed JSON
        log_dir = "logs/json"
        os.makedirs(log_dir, exist_ok=True)
        log_file = f"{log_dir}/invoice_{data['informacoes']['chave_acesso']}.json"
        with open(log_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

        # Insert or update empresa
        cursor.execute(
            """
            INSERT OR REPLACE INTO empresas (cnpj, razao_social)
            VALUES (?, ?)
        """,
            (data["empresa"]["cnpj"], data["empresa"]["razao_social"]),
        )
        empresa_id = cursor.lastrowid

        # Check if nota fiscal already exists
        cursor.execute(
            """
            SELECT id FROM notas_fiscais WHERE chave_acesso = ?
        """,
            (data["informacoes"]["chave_acesso"],),
        )
        existing_nota = cursor.fetchone()

        if existing_nota:
            nota_fiscal_id = existing_nota["id"]
            # Update existing nota fiscal
            cursor.execute(
                """
                UPDATE notas_fiscais SET
                id_empresa = ?, id_usuario = ?, numero = ?, serie = ?,
                protocolo_autorizacao = ?, data_autorizacao = ?, data_emissao = ?,
                tributacao_federal = ?, tributacao_estadual = ?, tributacao_municipal = ?
                WHERE id = ?
            """,
                (
                    empresa_id,
                    user_id,
                    data["informacoes"]["numero"],
                    data["informacoes"]["serie"],
                    data["informacoes"]["protocolo_autorizacao"],
                    data["informacoes"]["data_autorizacao"],
                    data["informacoes"]["data_emissao"],
                    data["tributos"]["federal"],
                    data["tributos"]["estadual"],
                    data["tributos"]["municipal"],
                    nota_fiscal_id,
                ),
            )
        else:
            # Insert new nota fiscal
            cursor.execute(
                """
                INSERT INTO notas_fiscais (id_empresa, id_usuario, chave_acesso, numero, serie,
                                           protocolo_autorizacao, data_autorizacao, data_emissao,
                                           tributacao_federal, tributacao_estadual, tributacao_municipal)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    empresa_id,
                    user_id,
                    data["informacoes"]["chave_acesso"],
                    data["informacoes"]["numero"],
                    data["informacoes"]["serie"],
                    data["informacoes"]["protocolo_autorizacao"],
                    data["informacoes"]["data_autorizacao"],
                    data["informacoes"]["data_emissao"],
                    data["tributos"]["federal"],
                    data["tributos"]["estadual"],
                    data["tributos"]["municipal"],
                ),
            )
            nota_fiscal_id = cursor.lastrowid

        # Insert or update items
        for item in data["itens"].values():
            cursor.execute(
                """
                INSERT OR REPLACE INTO produtos (codigo, descricao)
                VALUES (?, ?)
            """,
                (item["codigo_produto"], item["descricao_produto"]),
            )
            produto_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT OR REPLACE INTO itens_nota (id_produto, id_nota_fiscal, quantidade,
                                                   preco_unitario, unidade_medida)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    produto_id,
                    nota_fiscal_id,
                    item["quantidade"],
                    item["preco_unitario"],
                    item["unidade_medida"],
                ),
            )

        self.conn.commit()

    def close(self):
        self.conn.close()
