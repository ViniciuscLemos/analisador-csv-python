# Sales CSV Analyzer

![Tests](https://github.com/ViniciuscLemos/csv-analyzer-python/actions/workflows/tests.yml/badge.svg)

A Python program that reads a sales CSV, loads the data into a SQLite database and generates a report with the queries written in SQL.

You don't need to install anything besides Python (3.10+).

## Running

```bash
python main.py
```

If there's no CSV at `data/sales.csv`, it generates one with 200 made-up sales. The report goes to `output/report.txt` and also shows up in the terminal.

The report has:
- total revenue and average ticket
- sales by category and by region
- the best-selling products
- the seller ranking
- a simple text chart with the revenue for each month

Options:

```bash
python main.py --csv my_sales.csv          # use another file
python main.py --generate 1000 --seed 42   # generate a new CSV
python main.py --json                      # also save it as JSON
```

## What the report looks like

A piece of the report with 50 generated sales (`python main.py --generate 50 --seed 1`):

```
-------------------------------------------------------
  OVERVIEW
-------------------------------------------------------
  Period:             2024-01-08 to 2024-12-22
  Total sales:        50
  Total revenue:      $142,855.02
  Average ticket:     $2,857.10
  Biggest sale:       $23,651.90
  Smallest sale:      $28.16

-------------------------------------------------------
  SELLER RANKING
-------------------------------------------------------
  Seller            Sales          Revenue   Share
  ------------------------------------------------
  Elisa Ramos          11       $38,172.04   26.7%
  Diego Costa          14       $37,728.42   26.4%
  Ana Lima             11       $24,965.37   17.5%
  Bruno Silva           6       $22,797.23   16.0%
  Carla Souza           8       $19,191.96   13.4%

-------------------------------------------------------
  MONTHLY TREND
-------------------------------------------------------
  Jan/2024        $20,512.20  ██████████████
  Feb/2024        $25,897.73  █████████████████
  Mar/2024         $2,235.17  ██
  Apr/2024        $19,930.72  █████████████
  May/2024        $29,631.84  ████████████████████
  Jun/2024           $617.17  █
  Jul/2024        $19,101.35  █████████████
  Aug/2024         $1,793.67  █
  Sep/2024         $2,231.26  ██
  Oct/2024        $16,277.86  ███████████
  Nov/2024         $2,675.37  ██
  Dec/2024         $1,950.68  █
```

The full report also has sales by category, by region and the top 5 products.

## CSV format

```
date,product,category,quantity,price,seller,region
2024-03-10,Laptop,Electronics,1,2500.00,Ana Lima,Southeast
```

The date has to be in the `YYYY-MM-DD` format, and the price can be written with a dot or a comma. The separator can be a comma or a semicolon, which is how Excel saves the file in some languages. If a row is wrong, the program skips it and tells you which one and why.

## Tests

```bash
python -m unittest discover -s tests
```

## Files

```
main.py
src/database.py        creates the database and imports the CSV
src/analyzer.py        queries and building the report
src/csv_generator.py   generates the sample data
```
