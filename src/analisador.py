"""
Módulo de análise e geração de relatório
==========================================
Executa queries SQL para calcular estatísticas e salva o relatório em arquivo.
"""

import json
import sqlite3
from datetime import datetime

MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def formatar_moeda(valor: float) -> str:
    """
    Formata no padrão brasileiro: 1234.5 → 'R$ 1.234,50'.

    O Python formata com vírgula para milhar e ponto para decimal (padrão
    americano), então trocamos os dois separadores.
    """
    texto = f"{valor:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {texto}"


def _titulo(texto: str) -> str:
    """Formata um título de seção."""
    linha = "-" * 55
    return f"\n{linha}\n  {texto}\n{linha}"


def calcular_estatisticas(conn: sqlite3.Connection) -> dict:
    """
    Executa todas as consultas e devolve os resultados em um dicionário.

    Separar o cálculo da formatação permite testar os números e
    exportar o mesmo resultado em texto ou JSON.
    """
    cursor = conn.cursor()

    # -------------------------------------------------------
    # 1. Resumo geral
    # -------------------------------------------------------
    cursor.execute("""
        SELECT
            COUNT(*)                    AS total_vendas,
            COALESCE(SUM(total), 0)     AS receita_total,
            COALESCE(AVG(total), 0)     AS ticket_medio,
            COALESCE(MAX(total), 0)     AS maior_venda,
            COALESCE(MIN(total), 0)     AS menor_venda,
            MIN(data)                   AS primeira_venda,
            MAX(data)                   AS ultima_venda
        FROM vendas
    """)
    colunas = [c[0] for c in cursor.description]
    resumo = dict(zip(colunas, cursor.fetchone()))

    # -------------------------------------------------------
    # 2. Vendas por categoria (GROUP BY + ORDER BY)
    # -------------------------------------------------------
    cursor.execute("""
        SELECT
            categoria,
            COUNT(*)        AS vendas,
            SUM(total)      AS receita,
            AVG(preco)      AS preco_medio
        FROM vendas
        GROUP BY categoria
        ORDER BY receita DESC
    """)
    categorias = [dict(zip(("categoria", "vendas", "receita", "preco_medio"), r)) for r in cursor.fetchall()]

    # -------------------------------------------------------
    # 3. Top 5 produtos mais vendidos
    # -------------------------------------------------------
    cursor.execute("""
        SELECT
            produto,
            SUM(quantidade) AS unidades,
            SUM(total)      AS receita
        FROM vendas
        GROUP BY produto
        ORDER BY unidades DESC, receita DESC
        LIMIT 5
    """)
    produtos = [dict(zip(("produto", "unidades", "receita"), r)) for r in cursor.fetchall()]

    # -------------------------------------------------------
    # 4. Desempenho por vendedor, com participação na receita
    #    (subquery para calcular o percentual)
    # -------------------------------------------------------
    cursor.execute("""
        SELECT
            vendedor,
            COUNT(*)        AS vendas,
            SUM(total)      AS receita,
            100.0 * SUM(total) / (SELECT SUM(total) FROM vendas) AS participacao
        FROM vendas
        GROUP BY vendedor
        ORDER BY receita DESC
    """)
    vendedores = [dict(zip(("vendedor", "vendas", "receita", "participacao"), r)) for r in cursor.fetchall()]

    # -------------------------------------------------------
    # 5. Vendas por região
    # -------------------------------------------------------
    cursor.execute("""
        SELECT regiao, COUNT(*) AS vendas, SUM(total) AS receita
        FROM vendas
        GROUP BY regiao
        ORDER BY receita DESC
    """)
    regioes = [dict(zip(("regiao", "vendas", "receita"), r)) for r in cursor.fetchall()]

    # -------------------------------------------------------
    # 6. Evolução mensal (strftime extrai ano-mês da data)
    # -------------------------------------------------------
    cursor.execute("""
        SELECT strftime('%Y-%m', data) AS mes, COUNT(*) AS vendas, SUM(total) AS receita
        FROM vendas
        GROUP BY mes
        ORDER BY mes
    """)
    meses = [dict(zip(("mes", "vendas", "receita"), r)) for r in cursor.fetchall()]

    return {
        "resumo": resumo,
        "categorias": categorias,
        "top_produtos": produtos,
        "vendedores": vendedores,
        "regioes": regioes,
        "mensal": meses,
    }


def _nome_mes(ano_mes: str) -> str:
    """'2024-03' → 'Mar/2024'"""
    ano, mes = ano_mes.split("-")
    return f"{MESES[int(mes) - 1]}/{ano}"


def formatar_relatorio(estatisticas: dict) -> str:
    """Transforma o dicionário de estatísticas em um relatório de texto."""
    linhas = []

    # Cabeçalho
    linhas.append("=" * 55)
    linhas.append("  RELATÓRIO DE VENDAS")
    linhas.append(f"  Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    linhas.append("=" * 55)

    resumo = estatisticas["resumo"]
    if resumo["total_vendas"] == 0:
        linhas.append("\n  Nenhuma venda encontrada no arquivo.")
        linhas.append("\n" + "=" * 55)
        return "\n".join(linhas)

    linhas.append(_titulo("RESUMO GERAL"))
    linhas.append(f"  Período:            {resumo['primeira_venda']} a {resumo['ultima_venda']}")
    linhas.append(f"  Total de vendas:    {resumo['total_vendas']}")
    linhas.append(f"  Receita total:      {formatar_moeda(resumo['receita_total'])}")
    linhas.append(f"  Ticket médio:       {formatar_moeda(resumo['ticket_medio'])}")
    linhas.append(f"  Maior venda:        {formatar_moeda(resumo['maior_venda'])}")
    linhas.append(f"  Menor venda:        {formatar_moeda(resumo['menor_venda'])}")

    linhas.append(_titulo("VENDAS POR CATEGORIA"))
    linhas.append(f"  {'Categoria':<15} {'Vendas':>7} {'Receita':>16} {'Preço Médio':>14}")
    linhas.append("  " + "-" * 53)
    for c in estatisticas["categorias"]:
        linhas.append(f"  {c['categoria']:<15} {c['vendas']:>7} {formatar_moeda(c['receita']):>16} "
                      f"{formatar_moeda(c['preco_medio']):>14}")

    linhas.append(_titulo("TOP 5 PRODUTOS (por unidades)"))
    for i, p in enumerate(estatisticas["top_produtos"], start=1):
        linhas.append(f"  {i}. {p['produto']:<26} {p['unidades']:>4} un. — {formatar_moeda(p['receita'])}")

    linhas.append(_titulo("RANKING DE VENDEDORES"))
    linhas.append(f"  {'Vendedor':<15} {'Vendas':>7} {'Receita':>16} {'Part.':>7}")
    linhas.append("  " + "-" * 48)
    for v in estatisticas["vendedores"]:
        participacao = f"{v['participacao']:.1f}%".replace(".", ",")
        linhas.append(f"  {v['vendedor']:<15} {v['vendas']:>7} {formatar_moeda(v['receita']):>16} "
                      f"{participacao:>7}")

    linhas.append(_titulo("VENDAS POR REGIÃO"))
    for r in estatisticas["regioes"]:
        linhas.append(f"  {r['regiao']:<15} {formatar_moeda(r['receita']):>16}  ({r['vendas']} vendas)")

    linhas.append(_titulo("EVOLUÇÃO MENSAL"))
    maior = max(m["receita"] for m in estatisticas["mensal"])
    for m in estatisticas["mensal"]:
        # Barra proporcional à receita do melhor mês (gráfico em texto)
        barra = "█" * round(20 * m["receita"] / maior) if maior else ""
        linhas.append(f"  {_nome_mes(m['mes']):<9} {formatar_moeda(m['receita']):>16}  {barra}")

    linhas.append("\n" + "=" * 55)
    return "\n".join(linhas)


def gerar_relatorio(conn: sqlite3.Connection, caminho_saida: str, caminho_json: str | None = None) -> dict:
    """
    Calcula as estatísticas, salva o relatório em texto (e opcionalmente
    em JSON) e o exibe no terminal. Retorna as estatísticas calculadas.
    """
    estatisticas = calcular_estatisticas(conn)
    conteudo = formatar_relatorio(estatisticas)

    with open(caminho_saida, 'w', encoding='utf-8') as f:
        f.write(conteudo)

    if caminho_json:
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(estatisticas, f, ensure_ascii=False, indent=2)

    # Também exibe no terminal
    print(conteudo)
    return estatisticas
