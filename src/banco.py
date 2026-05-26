"""
Módulo de banco de dados — SQLite
==================================
Responsável por criar a estrutura do banco e inserir os dados do CSV.

SQLite é um banco de dados embutido no Python (sem precisar instalar nada).
É perfeito para projetos menores ou para aprender SQL.
"""

import sqlite3
import csv


def criar_banco(caminho_db: str) -> sqlite3.Connection:
    """
    Cria o banco de dados e a tabela de vendas.

    sqlite3.connect() cria o arquivo .db se ele não existir.
    Retorna uma conexão que usaremos para executar queries.
    """
    # connect() abre ou cria o arquivo de banco
    conn = sqlite3.connect(caminho_db)

    # cursor é o objeto que executa os comandos SQL
    cursor = conn.cursor()

    # CREATE TABLE IF NOT EXISTS: cria a tabela só se ela ainda não existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            data        TEXT NOT NULL,
            produto     TEXT NOT NULL,
            categoria   TEXT NOT NULL,
            quantidade  INTEGER NOT NULL,
            preco       REAL NOT NULL,
            total       REAL GENERATED ALWAYS AS (quantidade * preco) STORED,
            vendedor    TEXT NOT NULL,
            regiao      TEXT NOT NULL
        )
    """)

    # Confirma as alterações no banco
    conn.commit()

    return conn


def inserir_vendas(conn: sqlite3.Connection, caminho_csv: str) -> int:
    """
    Lê o arquivo CSV e insere os dados na tabela vendas.

    Retorna o número de registros inseridos.
    """
    cursor = conn.cursor()

    # Limpa os dados existentes antes de reimportar
    cursor.execute("DELETE FROM vendas")

    total_inserido = 0

    # 'with open' garante que o arquivo será fechado mesmo se der erro
    # encoding='utf-8' para suportar acentos
    with open(caminho_csv, newline='', encoding='utf-8') as arquivo:
        # DictReader lê cada linha como um dicionário {coluna: valor}
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            cursor.execute("""
                INSERT INTO vendas (data, produto, categoria, quantidade, preco, vendedor, regiao)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                linha['data'],
                linha['produto'],
                linha['categoria'],
                int(linha['quantidade']),
                float(linha['preco']),
                linha['vendedor'],
                linha['regiao'],
            ))
            total_inserido += 1

    conn.commit()
    return total_inserido
