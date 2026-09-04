import csv
from dataclasses import asdict

from domain.csv_model import CSVModel


def generate_csv(header: list[str], csv_data: list[CSVModel]) -> None:

    with open("result.csv", "w", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=header)

        writer.writeheader()

        for data in csv_data:
            writer.writerow(asdict(data))
