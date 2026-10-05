import sqlite3
import csv
from dataclasses import dataclass, field
from datetime import datetime

COLUNAS_OBRIGATORIAS = ("data", "produto", "categoria", "quantidade", "preco", "vendedor", "regiao")


class CSVInvalidoError(ValueError):
    """CSV sem as colunas esperadas."""


@dataclass
class ResultadoImportacao:
    inseridos: int = 0
    rejeitados: list[tuple[int, str]] = field(default_factory=list)  # (linha, motivo)


def criar_banco(caminho_db: str) -> sqlite3.Connection:
    conn = sqlite3.connect(caminho_db)
    conn.execute("""
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
    conn.commit()
    return conn


def _validar_linha(linha: dict) -> tuple:
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
        preco = float(linha["preco"].replace(",", "."))  # aceita 10.5 e 10,5
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
    """Importa o CSV. Linhas com problema são puladas e ficam em `rejeitados`."""
    resultado = ResultadoImportacao()
    validas = []

    # utf-8-sig por causa do BOM que o Excel coloca no começo do arquivo
    with open(caminho_csv, newline='', encoding='utf-8-sig') as arquivo:
        leitor = csv.DictReader(arquivo)

        colunas = {c.strip() for c in (leitor.fieldnames or [])}
        faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in colunas]
        if faltando:
            raise CSVInvalidoError(f"Colunas ausentes no CSV: {', '.join(faltando)}")

        for numero, linha in enumerate(leitor, start=2):  # linha 1 é o cabeçalho
            linha = {(k or "").strip(): v for k, v in linha.items()}
            try:
                validas.append(_validar_linha(linha))
            except ValueError as erro:
                resultado.rejeitados.append((numero, str(erro)))

    with conn:
        conn.execute("DELETE FROM vendas")
        conn.executemany("""
            INSERT INTO vendas (data, produto, categoria, quantidade, preco, vendedor, regiao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, validas)

    resultado.inseridos = len(validas)
    return resultado
