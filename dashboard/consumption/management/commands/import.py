import csv
import datetime
import os
from os import listdir
from os.path import isfile, join

import pandas as pd
from consumption.models import Consumption, User
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import make_aware


BASE_DIR = getattr(settings, "BASE_DIR", None)
DATA_DIR = os.path.join(BASE_DIR, '../data')
USER_DATA_FILE = 'user_data.csv'
CONSUM_DATA_DIR = 'consumption'
VALIDATION_DIR = os.path.join(DATA_DIR, 'validation_results')
DUP_RESULT_DIR_NAME = 'duplicated'


MODE_ARG = '--mode'
MODE_DEST = 'mode'
MODE_CHOICE_SKIP = "skip"
MODE_CHOICE_FIRST = "first"
MODE_CHOICE_LAST = "last"
MODE_CHOICE_SUM = "sum"
MODE_CHOICES = {
    MODE_CHOICE_SKIP: "...Skip duplicated data.",
    MODE_CHOICE_FIRST: "...Select first one.",
    MODE_CHOICE_LAST: "...Select last one.",
    MODE_CHOICE_SUM: "...Sum duplicated data if type is Number.",
}

VALID_ARG = '--validation'
VALID_DEST = 'validation'
VALID_CHOICE_YES = "yes"
VALID_CHOICE_NO = "no"
VALID_CHOICES_DEFAULT = VALID_CHOICE_YES
VALID_CHOICES = {
    VALID_CHOICES_DEFAULT: "...Execute validation. "
    "If duplicated data found, Importing does not be executed.",
    VALID_CHOICE_NO: "...Does Not Execute validation.",
}

# commend for mode
MODE_COMMENT = 'Option for duplicated data. Select from ' \
    '{}.'.format(
        [
            '"{}": {}'.format(
                key,
                MODE_CHOICES[key]) for key in MODE_CHOICES.keys()
        ],
    )

# commend for validation
VALID_COMMENT = 'Check If data has duplication before importing. ' \
    'If duplication found, importing will not be executed. Select from'\
    '{}, default is "{}".'.format(
        [
            '"{}": {}'.format(
                key,
                VALID_CHOICES[key]) for key in VALID_CHOICES.keys()
        ],
        VALID_CHOICES_DEFAULT
    )


class Command(BaseCommand):
    valid_choice = VALID_CHOICES_DEFAULT
    mode_choice = None
    dup_results = []

    def add_arguments(self, parser):
        parser.add_argument(
            MODE_ARG,
            help=MODE_COMMENT,
            type=str,
            dest=MODE_DEST,
            default=None,
            choices=[key for key in MODE_CHOICES.keys()],
        )
        parser.add_argument(
            VALID_ARG,
            help=VALID_COMMENT,
            type=str,
            choices=[key for key in VALID_CHOICES.keys()],
            dest=VALID_DEST,
            default=VALID_CHOICES_DEFAULT
        )

    def read_params(self, valid_choice, mode_choice):
        # if "--mode" is param is None, raise an Error
        # ( if other choice is selected, Django automatically raise Error. )
        if mode_choice is None:
            raise Exception(
                'Please specify param "{}" . That is {}'.format(
                    MODE_ARG,
                    MODE_COMMENT)
            )

        self.valid_choice = valid_choice
        self.mode_choice = mode_choice

    def handle(self, *args, **options):
        # read param
        self.read_params(
            valid_choice=options[VALID_DEST],
            mode_choice=options[MODE_DEST]
        )
        # get user data and consumption data
        user_file = self.get_user_data()
        consum_file_list = self.get_consumption_data_list()

        # case for skipping validation
        if self.valid_choice == VALID_CHOICE_NO:
            self.execute_import(user_file, consum_file_list)
        # case for executing validation
        else:
            result_dir = self.get_valid_result_dir()
            self.execute_validation(user_file, consum_file_list, result_dir)
            if self.dup_results:
                raise Exception(
                    'Importing does not executed. '
                    'See results in {}'.format(result_dir)
                )
            # if file does not have duplicate data
            else:
                self.execute_import(user_file, consum_file_list)

    def execute_validation(self, user_file, consum_file_list, result_dir):
        # check duplication of user data
        result = self.check_duplication(data=user_file, column='id')
        if result:
            self.append_dup_results(
                result,
                os.path.splitext(os.path.basename(user_file))[0]
            )

        # check duplication of counsmption data
        for file in consum_file_list:
            result = self.check_duplication(data=file, column='datetime')
            if result:
                self.append_dup_results(
                    result,
                    os.path.splitext(os.path.basename(file))[0]
                )

        # write results
        os.makedirs(result_dir)
        self.save_dup_results_to_csv(result_dir)

    def append_dup_results(self, result, filename):
        self.dup_results.append({
            'filename': filename,
            'results': result
        })

    @transaction.atomic
    def execute_import(self, user_file, consum_file_list):
        try:
            savepoint = transaction.savepoint()
            self.create_user(user_file)
            for file in consum_file_list:
                self.create_consumption(file)

            transaction.savepoint_commit(savepoint)
            print('Importing done safely.')

        except User.DoesNotExist:
            transaction.savepoint_rollback(savepoint)
            self.print_database_rollbacked()
            raise User.DoesNotExist
        except Exception as err:
            transaction.savepoint_rollback(savepoint)
            self.print_database_rollbacked()
            raise err
        # if other error happened (e.g. Keyboard interruption)
        except: # noqa
            transaction.savepoint_rollback(savepoint)
            self.print_database_rollbacked()
            print('Importing failed due to Unexpected error.')

    def check_duplication(self, data, column):
        # get pandas data frame object
        data_frame = pd.read_csv(data)
        # get pandas series object
        pd_series = data_frame[column]

        duplicated_list = []
        # iterate duplicated keys and append duplicated row number
        for data in pd_series[pd_series.duplicated()].keys():
            duplicated = data_frame[pd_series.isin([pd_series[data]])].index
            duplicated_list.append(
                [dup for dup in duplicated]
            )

        return duplicated_list

    def save_dup_results_to_csv(self, result_dir):
        # prepare directory for recording duplicated data
        dup_result_dirname = self.get_duplicatipm_result_dirname()
        dup_result_dir = os.path.join(result_dir, dup_result_dirname)
        os.makedirs(dup_result_dir)

        for data in self.dup_results:
            filename = '{}.csv'.format(data['filename'])
            filepath = os.path.join(dup_result_dir, filename)
            with open(filepath, mode='w') as file:
                writer = csv.writer(
                    file,
                    delimiter=',',
                    quotechar='"',
                    quoting=csv.QUOTE_MINIMAL
                )
                for duplicated in data['results']:
                    writer.writerow(
                        [i for i in duplicated]
                    )

    def get_user_data(self):
        return os.path.join(DATA_DIR, USER_DATA_FILE)

    def get_consumption_data_list(self):
        data_dir = os.path.join(DATA_DIR, CONSUM_DATA_DIR)

        return [
            os.path.abspath(os.path.join(data_dir, f)) for f in listdir(
                data_dir
            ) if isfile(
                join(data_dir, f)
            )
        ]

    def get_valid_result_dir(self):
        return os.path.join(
            VALIDATION_DIR,
            '{}'.format(
                datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            )
        )

    def get_duplicatipm_result_dirname(self):
        return DUP_RESULT_DIR_NAME

    def get_csv_rows(self, data_file, chk_culumn, can_sum):
        data_frame = pd.read_csv(data_file)
        if self.mode_choice == MODE_CHOICE_FIRST:
            csv_data = data_frame.drop_duplicates([chk_culumn], keep='first')
        elif self.mode_choice == MODE_CHOICE_LAST:
            csv_data = data_frame.drop_duplicates([chk_culumn], keep='last')
        elif self.mode_choice == MODE_CHOICE_SKIP:
            csv_data = data_frame.drop_duplicates([chk_culumn], keep=False)
        elif self.mode_choice == MODE_CHOICE_SUM and can_sum:
            csv_data = data_frame.groupby([chk_culumn], as_index=False).sum()
        elif self.mode_choice == MODE_CHOICE_SUM:  # if cannot sum data
            duplicated_list = self.check_duplication(
                data=data_file,
                column=chk_culumn
            )
            if duplicated_list:
                raise Exception(
                    'Importing failed on "{}" . '
                    'Because duplicated data '
                    'has founded in row number {}'.format(
                        data_file, duplicated_list)
                )
            else:
                csv_data = data_frame

        return csv_data.iterrows()

    def create_user(self, user_data_file):
        csv_rows = self.get_csv_rows(user_data_file, 'id', False)
        self.print_importing_message(user_data_file)
        self.import_user_data(csv_rows)

    def import_user_data(self, csv_rows):
        user_data = [
            User(
                id=row[1].id,
                area=row[1].area,
                tariff=row[1].tariff,
            ) for row in csv_rows
        ]
        User.objects.bulk_create(user_data)

    def create_consumption(self, file):
        csv_rows = self.get_csv_rows(file, 'datetime', True)
        self.print_importing_message(file)
        self.import_consumption_data(
            user_id=os.path.splitext(os.path.basename(file))[0],
            csv_rows=csv_rows
        )

    def import_consumption_data(self, user_id, csv_rows):
        user = User.objects.get(id=user_id)
        consum_data = [
            Consumption(
                user_id=user,
                datetime=make_aware(
                    datetime.datetime.strptime(
                        row[1].datetime, '%Y-%m-%d %H:%M:%S'
                    )
                ),
                consumption=row[1].consumption,
            ) for row in csv_rows
        ]
        Consumption.objects.bulk_create(consum_data)

    def print_importing_message(self, file):
        print('Importing file "{}" to database...'.format(file))

    def print_database_rollbacked(self):
        print('Database rollbacked.')
