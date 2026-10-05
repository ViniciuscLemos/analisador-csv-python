"""
Módulo de banco de dados — SQLite
==================================
Responsável por criar a estrutura do banco e inserir os dados do CSV.

SQLite é um banco de dados embutido no Python (sem precisar instalar nada).
É perfeito para projetos menores ou para aprender SQL.
"""

import sqlite3
import csv
from dataclasses import dataclass, field
from datetime import datetime

# Colunas que o CSV precisa ter (a ordem não importa)
COLUNAS_OBRIGATORIAS = ("data", "produto", "categoria", "quantidade", "preco", "vendedor", "regiao")


class CSVInvalidoError(ValueError):
    """Lançada quando o CSV não tem o formato esperado."""


@dataclass
class ResultadoImportacao:
    """Resumo do que aconteceu na importação."""
    inseridos: int = 0
    # Lista de (número da linha no arquivo, motivo)
    rejeitados: list[tuple[int, str]] = field(default_factory=list)


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
    # CHECK garante no próprio banco que quantidade e preço são positivos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            data        TEXT NOT NULL,
            produto     TEXT NOT NULL,
            categoria   TEXT NOT NULL,
            quantidade  INTEGER NOT NULL CHECK (quantidade > 0),
            preco       REAL NOT NULL CHECK (preco >= 0),
            total       REAL GENERATED ALWAYS AS (quantidade * preco) STORED,
            vendedor    TEXT NOT NULL,
            regiao      TEXT NOT NULL
        )
    """)

    # Confirma as alterações no banco
    conn.commit()

    return conn


def _validar_linha(linha: dict) -> tuple:
    """
    Converte uma linha do CSV para a tupla que vai para o banco.
    Lança ValueError com uma mensagem clara se algum campo for inválido.
    """
    for coluna in COLUNAS_OBRIGATORIAS:
        if not (linha.get(coluna) or "").strip():
            raise ValueError(f"campo '{coluna}' vazio")

    data = linha["data"].strip()
    try:
        datetime.strptime(data, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"data '{data}' não está no formato AAAA-MM-DD") from None

    try:
        quantidade = int(linha["quantidade"])
    except ValueError:
        raise ValueError(f"quantidade '{linha['quantidade']}' não é um número inteiro") from None
    if quantidade <= 0:
        raise ValueError("quantidade deve ser maior que zero")

    try:
        # Aceita tanto 10.5 quanto 10,5
        preco = float(linha["preco"].replace(",", "."))
    except ValueError:
        raise ValueError(f"preço '{linha['preco']}' não é um número") from None
    if preco < 0:
        raise ValueError("preço não pode ser negativo")

    return (
        data,
        linha["produto"].strip(),
        linha["categoria"].strip(),
        quantidade,
        preco,
        linha["vendedor"].strip(),
        linha["regiao"].strip(),
    )


def inserir_vendas(conn: sqlite3.Connection, caminho_csv: str) -> ResultadoImportacao:
    """
    Lê o arquivo CSV e insere os dados na tabela vendas.

    Linhas com problema não interrompem a importação: são puladas e
    registradas em ResultadoImportacao.rejeitados.
    """
    resultado = ResultadoImportacao()
    validas = []

    # 'with open' garante que o arquivo será fechado mesmo se der erro
    # encoding='utf-8-sig' suporta acentos e ignora o BOM que o Excel coloca
    with open(caminho_csv, newline='', encoding='utf-8-sig') as arquivo:
        # DictReader lê cada linha como um dicionário {coluna: valor}
        leitor = csv.DictReader(arquivo)

        colunas = {c.strip() for c in (leitor.fieldnames or [])}
        faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in colunas]
        if faltando:
            raise CSVInvalidoError(f"Colunas ausentes no CSV: {', '.join(faltando)}")

        # A linha 1 é o cabeçalho, então os dados começam na linha 2
        for numero, linha in enumerate(leitor, start=2):
            linha = {(k or "").strip(): v for k, v in linha.items()}
            try:
                validas.append(_validar_linha(linha))
            except ValueError as erro:
                resultado.rejeitados.append((numero, str(erro)))

    # 'with conn' abre uma transação: se algo falhar, nada é gravado pela metade
    with conn:
        # Limpa os dados existentes antes de reimportar
        conn.execute("DELETE FROM vendas")
        # executemany insere todas as linhas de uma vez (bem mais rápido que um loop)
        conn.executemany("""
            INSERT INTO vendas (data, produto, categoria, quantidade, preco, vendedor, regiao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, validas)

    resultado.inseridos = len(validas)
    return resultado
