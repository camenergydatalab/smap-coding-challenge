from importlib import import_module
from operator import attrgetter
from unittest import mock

from django.core.management import call_command, CommandError
from django.db import IntegrityError
from django.test import TransactionTestCase

from consumption.models import UserData, ConsumptionData

import_command = import_module("consumption.management.commands.import")


class CommandsTest(TransactionTestCase):
    @staticmethod
    def command(*args, **kwargs):
        return call_command("import", *args, **kwargs)

    def test_no_option(self):
        self.command()
        self.assertEqual(0, UserData.objects.count())
        self.assertEqual(0, ConsumptionData.objects.count())

    @mock.patch.object(import_command, "store_user_data")
    @mock.patch.object(import_command, "data_from_csv_file")
    def test_user_import_no_csv_path_short_command(
        self, mock_store_user_data, mock_data_from_csv_file
    ):
        """ユーザデータ読み込みコマンドテスト ショートコマンドテスト"""

        mock_data_from_csv_file.return_value = []
        with self.subTest("csv pathが指定されていない場合にエラーが出ること"):
            with self.assertRaises(CommandError):
                self.command("-u")

        with self.subTest("csvが指定されている場合にstore_user_dataが呼び出されること"):
            self.command("-u", "test_data")
            self.assertTrue(mock_store_user_data.called)

    @mock.patch.object(import_command, "store_user_data")
    @mock.patch.object(import_command, "data_from_csv_file")
    def test_user_import_no_csv_path(
        self, mock_store_user_data, mock_data_from_csv_file
    ):
        """ユーザデータ読み込みコマンドテスト"""

        mock_data_from_csv_file.return_value = []
        with self.subTest("pathが指定されていない場合にエラーが出ること"):
            with self.assertRaises(CommandError):
                self.command("--user")

        with self.subTest("csvが指定されている場合にstore_user_dataが呼び出されること"):
            self.command("--user", "test_data")
            self.assertTrue(mock_store_user_data.called)

    @mock.patch.object(import_command, "store_consumption_data")
    @mock.patch.object(import_command, "data_from_csv_file")
    @mock.patch.object(import_command, "get_csv_file_paths")
    def test_consumption_import_no_csv_path_short(
        self,
        mock_store_consumption_data,
        mock_data_from_csv_file,
        mock_get_csv_file_paths,
    ):
        """消費量データ読み込みコマンドテスト ショートコマンドテスト"""

        mock_data_from_csv_file.return_value = []
        mock_get_csv_file_paths.return_value = ["1000.csv"]

        with self.subTest("pathが指定されていない場合にエラーが出ること"):
            with self.assertRaises(CommandError):
                self.command("-c")

        with self.subTest("csvが指定されている場合にstore_consumption_dataが呼び出されること"):
            self.command("-c", "test_data")
            mock_store_consumption_data.called_with(1000, [])

    @mock.patch.object(import_command, "store_consumption_data")
    @mock.patch.object(import_command, "data_from_csv_file")
    @mock.patch.object(import_command, "get_csv_file_paths")
    def test_consumption_import_no_csv(
        self,
        mock_store_consumption_data,
        mock_data_from_csv_file,
        mock_get_csv_file_paths,
    ):
        """消費量データ読み込みコマンドテスト"""

        mock_data_from_csv_file.return_value = []
        mock_get_csv_file_paths.return_value = ["1000.csv"]

        with self.subTest("pathが指定されていない場合にエラーが出ること"):
            with self.assertRaises(CommandError):
                self.command("--consumption")

        with self.subTest("csvが指定されている場合にstore_consumption_dataが呼び出されること"):
            self.command("--consumption", "test_data")
            mock_store_consumption_data.called_with(1000, [])


class CommandFunctionTest(TransactionTestCase):
    def test_store_consumption_data_no_user(self):
        """存在しないユーザIDの場合にエラーが出ること"""
        with self.assertRaisesMessage(IntegrityError, "FOREIGN KEY constraint failed"):
            import_command.store_consumption_data(
                "999", [{"datetime": "2023-01-01 00:00:00", "consumption": 100.0}]
            )

    def test_store_consumption_data(self):
        """データが登録できること"""
        UserData.objects.create(id="1000", area="a1", tariff="t1")
        import_command.store_consumption_data(
            "1000", [{"datetime": "2023-01-01 00:00:00", "consumption": 100.0}]
        )

        self.assertQuerysetEqual(
            ConsumptionData.objects.all().order_by("pk"),
            [(1000, 100.0)],
            attrgetter("user_id", "consumption"),
        )

    def test_store_user_data(self):
        """ユーザを登録するできること"""
        import_command.store_user_data(
            [
                {"id": "1000", "area": "a1", "tariff": "t1"},
                {"id": "1001", "area": "a2", "tariff": "t2"},
                {"id": "1002", "area": "a3", "tariff": "t3"},
            ]
        )

        self.assertQuerysetEqual(
            UserData.objects.all().order_by("pk"),
            [
                (1000, "a1", "t1"),
                (1001, "a2", "t2"),
                (1002, "a3", "t3"),
            ],
            attrgetter("id", "area", "tariff"),
        )

    def test_store_user_data_error_same_id(self):
        """同じユーザIDを登録する場合にエラーが出ること"""
        with self.assertRaisesMessage(IntegrityError, "UNIQUE constraint failed"):
            import_command.store_user_data(
                [
                    {"id": "1000", "area": "a1", "tariff": "t1"},
                    {"id": "1000", "area": "a2", "tariff": "t2"},
                ]
            )
