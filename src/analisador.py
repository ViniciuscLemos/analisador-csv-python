"""
Módulo de análise e geração de relatório
==========================================
Executa queries SQL para calcular estatísticas e salva o relatório em arquivo.
"""

import sqlite3
from datetime import datetime


def _titulo(texto: str) -> str:
    """Formata um título de seção."""
    linha = "-" * 45
    return f"\n{linha}\n  {texto}\n{linha}"


def gerar_relatorio(conn: sqlite3.Connection, caminho_saida: str) -> None:
    """
    Executa consultas SQL no banco e salva um relatório em texto.

    Cada bloco de análise usa uma query SQL diferente.
    """
    cursor = conn.cursor()
    linhas = []  # Lista que acumula todas as linhas do relatório

    # Cabeçalho
    linhas.append("=" * 45)
    linhas.append("  RELATÓRIO DE VENDAS")
    linhas.append(f"  Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    linhas.append("=" * 45)

    # -------------------------------------------------------
    # 1. Resumo geral
    # -------------------------------------------------------
    linhas.append(_titulo("RESUMO GERAL"))

    cursor.execute("""
        SELECT
            COUNT(*)                    AS total_vendas,
            SUM(total)                  AS receita_total,
            AVG(total)                  AS ticket_medio,
            MAX(total)                  AS maior_venda,
            MIN(total)                  AS menor_venda
        FROM vendas
    """)
    row = cursor.fetchone()
    linhas.append(f"  Total de vendas:    {row[0]}")
    linhas.append(f"  Receita total:      R$ {row[1]:,.2f}")
    linhas.append(f"  Ticket médio:       R$ {row[2]:,.2f}")
    linhas.append(f"  Maior venda:        R$ {row[3]:,.2f}")
    linhas.append(f"  Menor venda:        R$ {row[4]:,.2f}")

    # -------------------------------------------------------
    # 2. Vendas por categoria (GROUP BY + ORDER BY)
    # -------------------------------------------------------
    linhas.append(_titulo("VENDAS POR CATEGORIA"))

    cursor.execute("""
        SELECT
            categoria,
            COUNT(*)        AS qtd_vendas,
            SUM(total)      AS receita,
            AVG(preco)      AS preco_medio
        FROM vendas
        GROUP BY categoria
        ORDER BY receita DESC
    """)
    linhas.append(f"  {'Categoria':<15} {'Vendas':>8} {'Receita':>14} {'Preço Médio':>12}")
    linhas.append("  " + "-" * 52)
    for row in cursor.fetchall():
        linhas.append(f"  {row[0]:<15} {row[1]:>8} R$ {row[2]:>10,.2f} R$ {row[3]:>8,.2f}")

    # -------------------------------------------------------
    # 3. Top 5 produtos mais vendidos
    # -------------------------------------------------------
    linhas.append(_titulo("TOP 5 PRODUTOS"))

    cursor.execute("""
        SELECT
            produto,
            SUM(quantidade) AS unidades,
            SUM(total)      AS receita
        FROM vendas
        GROUP BY produto
        ORDER BY unidades DESC
        LIMIT 5
    """)
    for i, row in enumerate(cursor.fetchall(), start=1):
        linhas.append(f"  {i}. {row[0]:<20} {row[1]} unidades — R$ {row[2]:,.2f}")

    # -------------------------------------------------------
    # 4. Desempenho por vendedor (HAVING para filtrar grupos)
    # -------------------------------------------------------
    linhas.append(_titulo("RANKING DE VENDEDORES"))

    cursor.execute("""
        SELECT
            vendedor,
            COUNT(*)        AS vendas,
            SUM(total)      AS receita
        FROM vendas
        GROUP BY vendedor
        HAVING COUNT(*) >= 1
        ORDER BY receita DESC
    """)
    linhas.append(f"  {'Vendedor':<15} {'Vendas':>8} {'Receita':>14}")
    linhas.append("  " + "-" * 40)
    for row in cursor.fetchall():
        linhas.append(f"  {row[0]:<15} {row[1]:>8} R$ {row[2]:>10,.2f}")

    # -------------------------------------------------------
    # 5. Vendas por região
    # -------------------------------------------------------
    linhas.append(_titulo("VENDAS POR REGIÃO"))

    cursor.execute("""
        SELECT regiao, SUM(total) AS receita, COUNT(*) AS vendas
        FROM vendas
        GROUP BY regiao
        ORDER BY receita DESC
    """)
    for row in cursor.fetchall():
        linhas.append(f"  {row[0]:<15} R$ {row[1]:>10,.2f}  ({row[2]} vendas)")

    linhas.append("\n" + "=" * 45)

    # Salva o relatório em arquivo
    conteudo = "\n".join(linhas)

    with open(caminho_saida, 'w', encoding='utf-8') as f:
        f.write(conteudo)

    # Também exibe no terminal
    print(conteudo)
