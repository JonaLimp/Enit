import os
from django.core.management.base import BaseCommand
import pandas as pd
from environmental_data.models import (
    HistoricalEnvironmentalRecord,
    Country,
    Sector,
    Substance,
)


class Command(BaseCommand):
    help = "Import emissions data from a CSV file."

    def handle(self, *args, **kwargs):
        file_path = os.getcwd() + "/data/datasets/IEA_EDGAR_CO2_1970_2023_cleaned.csv"
        df = pd.read_csv(file_path)
        records_to_create = []

        for _, row in df.iterrows():
            country, _ = Country.objects.get_or_create(
                code=row["country_code"], defaults={"name": row["country_name"]}
            )

            substance, _ = Substance.objects.get_or_create(name="CO2")
            sector, _ = Sector.objects.get_or_create(name=row["sector"])

            for year in range(1970, 2023):
                column_name = str(year)
                emission_value = row[column_name]

                if not pd.isna(emission_value):
                    records_to_create.append(
                        HistoricalEnvironmentalRecord(
                            country=country,
                            substance=substance,
                            sector=sector,
                            value=emission_value,
                            year=year,
                        )
                    )

        if records_to_create:
            HistoricalEnvironmentalRecord.objects.bulk_create(records_to_create)

        self.stdout.write(self.style.SUCCESS("Emissions data imported successfully."))
