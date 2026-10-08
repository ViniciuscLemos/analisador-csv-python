"""Lê um CSV de vendas, importa pro SQLite e gera o relatório."""

import argparse
import os
import sys

from src.banco import criar_banco, inserir_vendas, CSVInvalidoError
from src.analisador import gerar_relatorio
from src.gerador_csv import gerar_csv_exemplo

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
                        help="gera um CSV de exemplo com N vendas antes de analisar")
    parser.add_argument("--seed", type=int,
                        help="semente pro CSV de exemplo (mesmo valor = mesmos dados)")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    # No Windows, com a saída redirecionada pra arquivo (python main.py > log.txt),
    # o Python usa cp1252 e quebra no █ do gráfico
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = ler_argumentos(argv)

    print("=" * 55)
    print("  ANALISADOR DE DADOS DE VENDAS")
    print("=" * 55)

    arquivo_csv = args.csv
    pasta_csv = os.path.dirname(os.path.abspath(arquivo_csv))
    arquivo_db = os.path.join(pasta_csv, "vendas.db")

    os.makedirs(pasta_csv, exist_ok=True)
    os.makedirs(args.saida, exist_ok=True)

    if args.gerar or not os.path.exists(arquivo_csv):
        quantidade = args.gerar or 200
        print(f"\n[1/4] Gerando CSV de exemplo com {quantidade} vendas...")
        gerar_csv_exemplo(arquivo_csv, quantidade, seed=args.seed)
        print(f"      CSV criado em: {arquivo_csv}")
    else:
        print(f"\n[1/4] Usando CSV existente: {arquivo_csv}")

    print("\n[2/4] Criando banco de dados SQLite...")
    conn = criar_banco(arquivo_db)
    print(f"      Banco criado em: {arquivo_db}")

    try:
        print("\n[3/4] Importando dados do CSV para o banco...")
        try:
            resultado = inserir_vendas(conn, arquivo_csv)
        except CSVInvalidoError as erro:
            print(f"      Erro: {erro}")
            print("      Colunas esperadas: data, produto, categoria, quantidade, preco, vendedor, regiao")
            return 1

        print(f"      {resultado.inseridos} registros importados.")
        if resultado.rejeitados:
            print(f"      {len(resultado.rejeitados)} linha(s) ignorada(s):")
            for numero, motivo in resultado.rejeitados[:10]:
                print(f"        linha {numero}: {motivo}")
            if len(resultado.rejeitados) > 10:
                print(f"        ... e mais {len(resultado.rejeitados) - 10}")

        print("\n[4/4] Gerando relatório...")
        arquivo_relatorio = os.path.join(args.saida, "relatorio.txt")
        arquivo_json = os.path.join(args.saida, "relatorio.json") if args.json else None
        gerar_relatorio(conn, arquivo_relatorio, arquivo_json)
        print(f"      Relatório salvo em: {arquivo_relatorio}")
        if arquivo_json:
            print(f"      JSON salvo em: {arquivo_json}")
    finally:
        conn.close()

    print("\n" + "=" * 55)
    print("  Pronto!")
    print("=" * 55)
    return 0


if __name__ == "__main__":
    sys.exit(main())
