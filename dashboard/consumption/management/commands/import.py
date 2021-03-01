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
DUP_FILE_HEADER = ['duplicated index']


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

# comment for mode
MODE_COMMENT = 'Option for duplicated data. Select from ' \
    '{}.'.format(
        [
            '"{}": {}'.format(
                key,
                MODE_CHOICES[key]) for key in MODE_CHOICES.keys()
        ],
    )

# comment for validation
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
    """command

    Command class for data import.

    Attributes:
        valid_choice (str): choice of validation parameter
        mode_choice (str): choice of mode parameter
        dup_results (list): list[
            {
                'filename': filename of duplicated file,
                'results':  list[list[str]]:
                    list of duplicated index combination
            }
        ]
    """
    valid_choice = VALID_CHOICES_DEFAULT
    mode_choice = ''
    dup_results = []

    def get_user_data_path(self):
        """get user data file path

        Get user data file path.

        Returns:
            str: user data file path
        """
        return os.path.join(DATA_DIR, USER_DATA_FILE)

    def get_consumption_data_path_list(self):
        """get consumption data file list

        Get consumption data file list.

        Returns:
            list[str]: list of consumption data file path
        """
        data_dir = os.path.join(DATA_DIR, CONSUM_DATA_DIR)

        return [
            os.path.abspath(os.path.join(data_dir, f)) for f in listdir(
                data_dir
            ) if isfile(
                join(data_dir, f)
            )
        ]

    def get_valid_result_dir_path(self):
        """get validation result file path

        Get file path to save validation result.

        Returns:
            str: file path to save validation result
        """
        return os.path.join(
            VALIDATION_DIR,
            '{}'.format(
                datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            )
        )

    def get_dup_result_file_header(self):
        """get header for duplicated result

        Get header name of duplicated result recording file.

        Returns:
            str: header name of duplicated result recording file
        """
        return DUP_FILE_HEADER

    def get_duplicatipm_result_dirname(self):
        """get duplicatipm result direcotry name

        Get folder name for duplication result.

        Returns:
            str: folder name for duplication result
        """
        return DUP_RESULT_DIR_NAME

    def add_arguments(self, parser):
        """add command arguments

        Add custom command arguments.
        """
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
        """raead command parameters

        Read command parameters and save them to instance variable

        Args:
            valid_choice (str): option for validation
            mode_choice (str): option for mode
        """
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
        """main function

        Command from user excute this function firttly.

        Args:
            *args: default django *args
            **options: default django **options
                        (including command parameters)

        Raises:
            Exception: if importing does not executed
        """
        # read params
        self.read_params(
            valid_choice=options[VALID_DEST],
            mode_choice=options[MODE_DEST]
        )
        # get user data and consumption data
        user_file = self.get_user_data_path()
        consum_file_list = self.get_consumption_data_path_list()

        # case for skipping validation
        if self.valid_choice == VALID_CHOICE_NO:
            self.execute_import(user_file, consum_file_list)
        # case for executing validation
        else:
            result_dir = self.get_valid_result_dir_path()
            self.execute_validation(user_file, consum_file_list, result_dir)
            if self.dup_results:
                raise Exception(
                    'Importing does not executed. '
                    'See validation results in "{}"'.format(result_dir)
                )
            # if file does not have duplicate data
            else:
                self.execute_import(user_file, consum_file_list)

    def execute_validation(self, user_file, consum_file_list, result_dir):
        """execute validation

        Excecute validation process.

        Args:
            user_file (str): path to user data file
            consum_file_list (list[str]):
                list of path to consumption data files
            result_dir (str): path to save validation results
        """
        # check duplication of user data
        user_results = self.get_duplicated_index_list(data=user_file, column='id')
        if user_results:
            self.save_dup_results(
                user_results,
                os.path.splitext(os.path.basename(user_file))[0]
            )

        # check duplication of counsmption data
        for file in consum_file_list:
            consum_results = self.get_duplicated_index_list(
                data=file, column='datetime')
            if consum_results:
                self.save_dup_results(
                    consum_results,
                    os.path.splitext(os.path.basename(file))[0]
                )

        # write results
        os.makedirs(result_dir)
        self.write_dup_results_to_csv(result_dir)

    def save_dup_results(self, results, filename):
        """save duplication results

        Save duplication results to instance variable.

        Args:
            results (list[list[str]]): list of duplicated index combination
            filename (str): file name
        """
        self.dup_results.append({
            'filename': filename,
            'results': results
        })

    @transaction.atomic
    def execute_import(self, user_file, consum_file_list):
        """execute importing

        Execute importing process.
        if matching user is not found or another exceptions occures,
        print error and exceute database rollback process.
        (Even if unexpected error occures, Django will not execute queries.

        Args:
            user_file (str): path to user data file
            consum_file_list (list[str]):
                list of path to consumption data files
        """
        try:
            savepoint = transaction.savepoint()
            self.create_user(user_file)
            for file in consum_file_list:
                self.create_consumption(file)

            transaction.savepoint_commit(savepoint)
            print('Importing done safely.')

        except User.DoesNotExist as err:
            transaction.savepoint_rollback(savepoint)
            self.print_database_rollbacked()
            print(err)
        # if other error happened (e.g. Keyboard interruption)
        except BaseException as err:
            transaction.savepoint_rollback(savepoint)
            self.print_database_rollbacked()
            print(err)

    def get_duplicated_index_list(self, data, column):
        """get list of duplicated index

        Get list of duplicatd index from data with specified column

        Args:
            data(str): path to csv data
            column(str): column to check duplication

        Returns:
            list[list[str]]: list of duplicated index combination
        """
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

    def write_dup_results_to_csv(self, result_dir):
        """write duplication rsults to csv

        Write duplication results to csv in specified directory.

        Args:
            result_dir (str): directory to save results
        """
        # prepare directory for recording duplicated data
        dup_result_dirname = self.get_duplicatipm_result_dirname()
        dup_result_dir = os.path.join(result_dir, dup_result_dirname)
        os.makedirs(dup_result_dir)

        # write results
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
                writer.writerow(self.get_dup_result_file_header())
                for duplicated in data['results']:
                    writer.writerow(
                        [i for i in duplicated]
                    )

    def get_csv_rows_as_iter(self, csv_file, chk_culumn, can_sum):
        """get csv rows as iterration

        Get csv rows data as a iterration

        Args:
            csv_file (str): path to csv file to read
            chk_culumn (str): culumn for specified mode
            can_sum (bool): if duplicated data can be sum, specify true

        Yields:
            pandas.DataFrame.iterrows() : iteration of each rows

        Raises:
            Exception: if duplication found and duplicated data can not be sum
        """
        data_frame = pd.read_csv(csv_file)
        if self.mode_choice == MODE_CHOICE_FIRST:
            csv_data = data_frame.drop_duplicates([chk_culumn], keep='first')
        elif self.mode_choice == MODE_CHOICE_LAST:
            csv_data = data_frame.drop_duplicates([chk_culumn], keep='last')
        elif self.mode_choice == MODE_CHOICE_SKIP:
            csv_data = data_frame.drop_duplicates([chk_culumn], keep=False)
        elif self.mode_choice == MODE_CHOICE_SUM and can_sum:
            csv_data = data_frame.groupby([chk_culumn], as_index=False).sum()
        # need check if cannot sum data (e.g. user data)
        elif self.mode_choice == MODE_CHOICE_SUM:
            duplicated_list = self.get_duplicated_index_list(
                data=csv_file,
                column=chk_culumn
            )
            if duplicated_list:
                raise Exception(
                    'Importing failed on "{}" . '
                    'Because duplicated data '
                    'has founded in row number {}'.format(
                        csv_file, duplicated_list)
                )
            else:
                csv_data = data_frame

        return csv_data.iterrows()

    def create_user(self, user_csv_file):
        """create user

        Create user data.

        Args:
            user_csv_file (str): path to csv file of user data
        """
        csv_rows_iter = self.get_csv_rows_as_iter(
            csv_file=user_csv_file,
            chk_culumn='id',
            can_sum=False)
        self.print_importing_message(user_csv_file)
        self.import_user_data(csv_rows_iter)

    def import_user_data(self, csv_rows_iter):
        """create user

        Create user data.

        Args:
            csv_rows_iter
                (Iterator Objects([
                    index[int],
                    {
                        id (int): user id,
                        area (str): user area,
                        tariff (str): user tariff
                    }
                    ])
                )
                    : iterator which returns each row info
        """
        user_data = [
            User(
                id=row[1]['id'],
                area=row[1]['area'],
                tariff=row[1]['tariff'],
            ) for row in csv_rows_iter
        ]
        User.objects.bulk_create(user_data)

    def create_consumption(self, file):
        """create consumption

        Create consumption data.

        Args:
            file (str): path to csv file of consumption data
        """
        csv_rows_iter = self.get_csv_rows_as_iter(
            csv_file=file,
            chk_culumn='datetime',
            can_sum=True)
        self.print_importing_message(file)
        self.import_consumption_data(
            user_id=os.path.splitext(os.path.basename(file))[0],
            csv_rows_iter=csv_rows_iter
        )

    def import_consumption_data(self, user_id, csv_rows_iter):
        """create user

        Create user data.

        Args:
            csv_rows_iter
                (iter([
                    index[int],
                    {
                        datetime (str): datetime (e.g. '2016-07-15 00:00:00')
                        consumption (float): user consumption
                    }
                    ])
                )
                    : iterator returns each row info
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist as err:
            raise err
        consum_data = [
            Consumption(
                user_id=user,
                datetime=make_aware(
                    datetime.datetime.strptime(
                        row[1]['datetime'], '%Y-%m-%d %H:%M:%S'
                    )
                ),
                consumption=row[1]['consumption'],
            ) for row in csv_rows_iter
        ]
        Consumption.objects.bulk_create(consum_data)

    def print_importing_message(self, file):
        """print importing message

        Print message during importing

        Args:
            file (str): path to file of importing data
        """
        print('Importing file "{}" to database...'.format(file))

    def print_database_rollbacked(self):
        """print rollback message

        Print database rollback message
        """
        print('Database rollbacked.')
