"""
Analisador de Dados CSV — Python + SQLite
==========================================
Este projeto lê arquivos CSV, armazena os dados em um banco SQLite
e gera relatórios com estatísticas e análises.

Conceitos que você vai aprender:
- Leitura e manipulação de arquivos CSV com a biblioteca csv
- Banco de dados SQLite com o módulo sqlite3 (nativo do Python)
- Funções e módulos em Python
- Formatação de dados e geração de relatórios
- Context managers (with statement)
"""

import csv
import sqlite3
import os
from datetime import datetime
from src.banco import criar_banco, inserir_vendas
from src.analisador import gerar_relatorio
from src.gerador_csv import gerar_csv_exemplo


def main():
    """Ponto de entrada principal do programa."""

    print("=" * 50)
    print("  ANALISADOR DE DADOS DE VENDAS")
    print("=" * 50)

    # Caminhos dos arquivos
    pasta_data = "data"
    pasta_output = "output"
    arquivo_csv = os.path.join(pasta_data, "vendas.csv")
    arquivo_db = os.path.join(pasta_data, "vendas.db")

    # Cria as pastas se não existirem
    os.makedirs(pasta_data, exist_ok=True)
    os.makedirs(pasta_output, exist_ok=True)

    # Passo 1: Gera um CSV de exemplo se não existir
    if not os.path.exists(arquivo_csv):
        print("\n[1/4] Gerando arquivo CSV de exemplo...")
        gerar_csv_exemplo(arquivo_csv)
        print(f"      CSV criado em: {arquivo_csv}")
    else:
        print(f"\n[1/4] Usando CSV existente: {arquivo_csv}")

    # Passo 2: Cria o banco de dados SQLite
    print("\n[2/4] Criando banco de dados SQLite...")
    conn = criar_banco(arquivo_db)
    print(f"      Banco criado em: {arquivo_db}")

    # Passo 3: Lê o CSV e insere no banco
    print("\n[3/4] Importando dados do CSV para o banco...")
    total = inserir_vendas(conn, arquivo_csv)
    print(f"      {total} registros importados com sucesso!")

    # Passo 4: Gera o relatório
    print("\n[4/4] Gerando relatório de análise...")
    arquivo_relatorio = os.path.join(pasta_output, "relatorio.txt")
    gerar_relatorio(conn, arquivo_relatorio)
    print(f"      Relatório salvo em: {arquivo_relatorio}")

    conn.close()

    print("\n" + "=" * 50)
    print("  Análise concluída! Verifique a pasta output/")
    print("=" * 50)


if __name__ == "__main__":
    # Este bloco só executa se rodarmos este arquivo diretamente
    # (não quando importado como módulo)
    main()
