"""
Analisador de Dados CSV — Python + SQLite
==========================================
Este projeto lê arquivos CSV, armazena os dados em um banco SQLite
e gera relatórios com estatísticas e análises.

Conceitos que você vai aprender:
- Leitura e manipulação de arquivos CSV com a biblioteca csv
- Banco de dados SQLite com o módulo sqlite3 (nativo do Python)
- Argumentos de linha de comando com argparse
- Funções e módulos em Python
- Formatação de dados e geração de relatórios
- Context managers (with statement)
"""

import argparse
import os
import sys

from src.banco import criar_banco, inserir_vendas, CSVInvalidoError
from src.analisador import gerar_relatorio
from src.gerador_csv import gerar_csv_exemplo

# Pasta do projeto: os caminhos padrão funcionam de qualquer diretório
PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))


def ler_argumentos(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Importa um CSV de vendas para o SQLite e gera um relatório.",
    )
    parser.add_argument("--csv", default=os.path.join(PASTA_PROJETO, "data", "vendas.csv"),
                        help="arquivo CSV de entrada (padrão: data/vendas.csv)")
    parser.add_argument("--saida", default=os.path.join(PASTA_PROJETO, "output"),
                        help="pasta onde o relatório é salvo (padrão: output/)")
    parser.add_argument("--json", action="store_true",
                        help="também salva as estatísticas em output/relatorio.json")
    parser.add_argument("--gerar", type=int, metavar="N",
                        help="gera (ou regera) um CSV de exemplo com N vendas antes de analisar")
    parser.add_argument("--seed", type=int,
                        help="semente para o CSV de exemplo (mesmo valor = mesmos dados)")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    """Ponto de entrada principal do programa. Retorna o código de saída."""
    args = ler_argumentos(argv)

    print("=" * 55)
    print("  ANALISADOR DE DADOS DE VENDAS")
    print("=" * 55)

    arquivo_csv = args.csv
    pasta_csv = os.path.dirname(os.path.abspath(arquivo_csv))
    arquivo_db = os.path.join(pasta_csv, "vendas.db")

    # Cria as pastas se não existirem
    os.makedirs(pasta_csv, exist_ok=True)
    os.makedirs(args.saida, exist_ok=True)

    # Passo 1: Gera um CSV de exemplo se pedido ou se não existir
    if args.gerar or not os.path.exists(arquivo_csv):
        quantidade = args.gerar or 200
        print(f"\n[1/4] Gerando CSV de exemplo com {quantidade} vendas...")
        gerar_csv_exemplo(arquivo_csv, quantidade, seed=args.seed)
        print(f"      CSV criado em: {arquivo_csv}")
    else:
        print(f"\n[1/4] Usando CSV existente: {arquivo_csv}")

    # Passo 2: Cria o banco de dados SQLite
    print("\n[2/4] Criando banco de dados SQLite...")
    conn = criar_banco(arquivo_db)
    print(f"      Banco criado em: {arquivo_db}")

    try:
        # Passo 3: Lê o CSV e insere no banco
        print("\n[3/4] Importando dados do CSV para o banco...")
        try:
            resultado = inserir_vendas(conn, arquivo_csv)
        except CSVInvalidoError as erro:
            print(f"      Erro: {erro}")
            print("      Colunas esperadas: data, produto, categoria, quantidade, preco, vendedor, regiao")
            return 1

        print(f"      {resultado.inseridos} registros importados com sucesso!")
        if resultado.rejeitados:
            print(f"      {len(resultado.rejeitados)} linha(s) ignorada(s):")
            for numero, motivo in resultado.rejeitados[:10]:
                print(f"        linha {numero}: {motivo}")
            if len(resultado.rejeitados) > 10:
                print(f"        ... e mais {len(resultado.rejeitados) - 10}")

        # Passo 4: Gera o relatório
        print("\n[4/4] Gerando relatório de análise...")
        arquivo_relatorio = os.path.join(args.saida, "relatorio.txt")
        arquivo_json = os.path.join(args.saida, "relatorio.json") if args.json else None
        gerar_relatorio(conn, arquivo_relatorio, arquivo_json)
        print(f"      Relatório salvo em: {arquivo_relatorio}")
        if arquivo_json:
            print(f"      Estatísticas em JSON: {arquivo_json}")
    finally:
        conn.close()

    print("\n" + "=" * 55)
    print("  Análise concluída!")
    print("=" * 55)
    return 0


if __name__ == "__main__":
    # Este bloco só executa se rodarmos este arquivo diretamente
    # (não quando importado como módulo)
    sys.exit(main())
