import csv
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.db.transaction import atomic
from django.utils.timezone import get_default_timezone
from pathlib import Path
from typing import Iterable, Callable

from ...models import Consumer, Consumption

ConflictResolver = Callable[[Consumption, Consumption], Decimal]


class Command(BaseCommand):
    help = "import data, the format is specified in README.md"

    def add_arguments(self, parser: CommandParser) -> None:
        default_data_dir = (Path(settings.BASE_DIR) / "../data").resolve()
        parser.add_argument("-d", "--data-dir", type=str,
                            default=str(default_data_dir))
        parser.add_argument("--resolver",
                            choices=RESOLVERS.keys(), default="sum")

    def handle(self, *args, **options):
        data_dir = Path(options["data_dir"])
        resolver = RESOLVERS[options["resolver"]]
        with atomic():
            self.import_consumption_data(data_dir, resolver)

    def import_consumption_data(self,
                                data_dir: Path, resolver: ConflictResolver):
        with (open(data_dir / "user_data.csv") as h_user_data):
            self.stderr.write(f"Loading consumers...")
            user_reader = csv.DictReader(h_user_data)
            consumers = list(map(parse_consumer, user_reader))
            Consumer.objects.bulk_create(consumers)

        for consumer in consumers:
            self.stderr.write(f"Loading data for consumer {consumer.id}...")
            with open(data_dir / f"consumption/{consumer.id}.csv") \
                    as h_consumption_data:
                consumption_reader = csv.DictReader(h_consumption_data)
                consumptions = resolve_consumption_conflicts(
                    map(lambda row: parse_consumption_row(consumer, row),
                        consumption_reader),
                    resolver)
                Consumption.objects.bulk_create(consumptions)


def parse_consumer(row: dict[str, str]) -> Consumer:
    rv = Consumer()
    rv.id = int(row["id"])
    rv.area = row["area"]
    rv.tariff = row["tariff"]
    return rv


def parse_consumption_row(consumer: Consumer,
                          row: dict[str, str]) -> Consumption:
    rv = Consumption()
    rv.consumer = consumer
    rv.datetime = datetime.strptime(
            row["datetime"], "%Y-%m-%d %H:%M:%S") \
        .replace(tzinfo=get_default_timezone())
    rv.amount = Decimal(row["consumption"])
    return rv


def resolve_consumption_conflicts(consumptions: Iterable[Consumption],
                                  resolver: ConflictResolver,
                                  ) -> list[Consumption]:
    rv = []
    processed: dict[datetime, Consumption] = dict()
    for consumption in consumptions:
        old = processed.get(consumption.datetime)
        if old is None:
            rv.append(consumption)
            processed[consumption.datetime] = consumption
        else:
            old.amount = resolver(old, consumption)
    return rv


def resolver_sum(existing: Consumption, new: Consumption) -> Decimal:
    return existing.amount + new.amount


def resolver_newer(existing: Consumption, new: Consumption) -> Decimal:
    return new.amount


def resolver_error(existing: Consumption, new: Consumption) -> Decimal:
    raise ValueError(f"Got multiple entry for same datetime {existing.datetime}"
                     f"for consumer {existing.consumer.id}")


RESOLVERS: dict[str, ConflictResolver] = {
    "sum": resolver_sum,
    "newer": resolver_newer,
    "error": resolver_error,
}
