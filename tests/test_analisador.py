import csv
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.analisador import calcular_estatisticas, formatar_moeda, formatar_relatorio  # noqa: E402
from src.banco import CSVInvalidoError, criar_banco, inserir_vendas  # noqa: E402
from src.gerador_csv import gerar_csv_exemplo  # noqa: E402
import main  # noqa: E402

CABECALHO = ["data", "produto", "categoria", "quantidade", "preco", "vendedor", "regiao"]


class BaseComPasta(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.csv = os.path.join(self.pasta.name, "vendas.csv")

    def tearDown(self):
        self.pasta.cleanup()

    def escrever_csv(self, linhas, cabecalho=CABECALHO):
        with open(self.csv, "w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f)
            escritor.writerow(cabecalho)
            escritor.writerows(linhas)


class TestFormatarMoeda(unittest.TestCase):
    def test_padrao_brasileiro(self):
        self.assertEqual(formatar_moeda(1234.5), "R$ 1.234,50")
        self.assertEqual(formatar_moeda(0), "R$ 0,00")
        self.assertEqual(formatar_moeda(1_000_000), "R$ 1.000.000,00")


class TestImportacao(BaseComPasta):
    def test_importa_linhas_validas(self):
        self.escrever_csv([
            ["2024-01-10", "Café", "Alimentos", "2", "10.50", "Ana", "Sul"],
            ["2024-02-01", "Mel", "Alimentos", "1", "20,00", "Bruno", "Norte"],
        ])
        conn = criar_banco(":memory:")
        resultado = inserir_vendas(conn, self.csv)
        self.assertEqual(resultado.inseridos, 2)
        self.assertEqual(resultado.rejeitados, [])
        total = conn.execute("SELECT SUM(total) FROM vendas").fetchone()[0]
        self.assertAlmostEqual(total, 41.0)

    def test_rejeita_linhas_invalidas_sem_parar(self):
        self.escrever_csv([
            ["2024-01-10", "Café", "Alimentos", "2", "10", "Ana", "Sul"],
            ["10/01/2024", "Café", "Alimentos", "2", "10", "Ana", "Sul"],   # data errada
            ["2024-01-10", "Café", "Alimentos", "dois", "10", "Ana", "Sul"],  # quantidade
            ["2024-01-10", "Café", "Alimentos", "0", "10", "Ana", "Sul"],   # quantidade zero
            ["2024-01-10", "", "Alimentos", "1", "10", "Ana", "Sul"],       # produto vazio
        ])
        conn = criar_banco(":memory:")
        resultado = inserir_vendas(conn, self.csv)
        self.assertEqual(resultado.inseridos, 1)
        self.assertEqual([n for n, _ in resultado.rejeitados], [3, 4, 5, 6])

    def test_csv_com_ponto_e_virgula(self):
        with open(self.csv, "w", newline="", encoding="utf-8-sig") as f:
            f.write(";".join(CABECALHO) + "\n")
            f.write("2024-01-10;Café;Alimentos;2;10,50;Ana;Sul\n")
        conn = criar_banco(":memory:")
        resultado = inserir_vendas(conn, self.csv)
        self.assertEqual(resultado.inseridos, 1)
        total = conn.execute("SELECT SUM(total) FROM vendas").fetchone()[0]
        self.assertAlmostEqual(total, 21.0)

    def test_colunas_ausentes(self):
        self.escrever_csv([["2024-01-10", "Café"]], cabecalho=["data", "produto"])
        conn = criar_banco(":memory:")
        with self.assertRaises(CSVInvalidoError):
            inserir_vendas(conn, self.csv)

    def test_reimportar_substitui_dados(self):
        self.escrever_csv([["2024-01-10", "Café", "Alimentos", "1", "10", "Ana", "Sul"]])
        conn = criar_banco(":memory:")
        inserir_vendas(conn, self.csv)
        inserir_vendas(conn, self.csv)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM vendas").fetchone()[0], 1)


class TestEstatisticas(BaseComPasta):
    def setUp(self):
        super().setUp()
        self.escrever_csv([
            ["2024-01-10", "Café", "Alimentos", "2", "10", "Ana", "Sul"],     # 20
            ["2024-01-20", "Livro", "Livros", "1", "50", "Ana", "Norte"],     # 50
            ["2024-02-05", "Café", "Alimentos", "3", "10", "Bruno", "Sul"],   # 30
        ])
        self.conn = criar_banco(":memory:")
        inserir_vendas(self.conn, self.csv)

    def test_resumo(self):
        resumo = calcular_estatisticas(self.conn)["resumo"]
        self.assertEqual(resumo["total_vendas"], 3)
        self.assertAlmostEqual(resumo["receita_total"], 100)
        self.assertAlmostEqual(resumo["maior_venda"], 50)
        self.assertEqual(resumo["primeira_venda"], "2024-01-10")

    def test_agrupamentos(self):
        est = calcular_estatisticas(self.conn)
        self.assertEqual(est["top_produtos"][0]["produto"], "Café")
        self.assertEqual(est["top_produtos"][0]["unidades"], 5)
        ana = next(v for v in est["vendedores"] if v["vendedor"] == "Ana")
        self.assertAlmostEqual(ana["participacao"], 70.0)
        self.assertEqual([m["mes"] for m in est["mensal"]], ["2024-01", "2024-02"])

    def test_relatorio_texto(self):
        texto = formatar_relatorio(calcular_estatisticas(self.conn))
        self.assertIn("R$ 100,00", texto)
        self.assertIn("EVOLUÇÃO MENSAL", texto)
        self.assertIn("Jan/2024", texto)

    def test_mes_com_pouca_venda_aparece_no_grafico(self):
        self.escrever_csv([
            ["2024-01-10", "Notebook", "Eletrônicos", "1", "5000", "Ana", "Sul"],
            ["2024-02-10", "Caneta", "Papelaria", "1", "2", "Ana", "Sul"],
        ])
        conn = criar_banco(":memory:")
        inserir_vendas(conn, self.csv)
        texto = formatar_relatorio(calcular_estatisticas(conn))
        linha_fev = next(l for l in texto.splitlines() if l.strip().startswith("Fev/2024"))
        self.assertTrue(linha_fev.endswith("█"))

    def test_banco_vazio_nao_quebra(self):
        conn = criar_banco(":memory:")
        texto = formatar_relatorio(calcular_estatisticas(conn))
        self.assertIn("Nenhuma venda", texto)


class TestGerador(BaseComPasta):
    def test_seed_reproduz_mesmo_arquivo(self):
        outro = os.path.join(self.pasta.name, "outro.csv")
        gerar_csv_exemplo(self.csv, 30, seed=7)
        gerar_csv_exemplo(outro, 30, seed=7)
        with open(self.csv, encoding="utf-8") as a, open(outro, encoding="utf-8") as b:
            self.assertEqual(a.read(), b.read())


class TestMain(BaseComPasta):
    def test_fluxo_completo(self):
        saida = os.path.join(self.pasta.name, "out")
        with redirect_stdout(StringIO()):
            codigo = main.main(["--csv", self.csv, "--saida", saida, "--gerar", "50", "--seed", "1", "--json"])
        self.assertEqual(codigo, 0)
        self.assertTrue(os.path.exists(os.path.join(saida, "relatorio.txt")))
        with open(os.path.join(saida, "relatorio.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["resumo"]["total_vendas"], 50)

    def test_csv_invalido_retorna_erro(self):
        self.escrever_csv([["x"]], cabecalho=["coluna_errada"])
        with redirect_stdout(StringIO()):
            codigo = main.main(["--csv", self.csv, "--saida", self.pasta.name])
        self.assertEqual(codigo, 1)


if __name__ == "__main__":
    unittest.main()
