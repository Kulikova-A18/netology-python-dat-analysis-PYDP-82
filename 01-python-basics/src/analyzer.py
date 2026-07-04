import os
import csv
import pandas as pd
import logging
from datetime import datetime
import config


class OrderAnalyzer:
    """
    Класс для пакетного анализа данных о заказах интернет-магазина.
    """

    def __init__(self, data_dir, reports_dir, logs_dir):
        """
        Инициализация анализатора заказов.

        Args:
            data_dir (str): Путь к директории с входными CSV-файлами заказов
            reports_dir (str): Путь к директории для сохранения отчетов
            logs_dir (str): Путь к директории для сохранения логов ошибок
        """
        self.data_dir = data_dir
        self.reports_dir = reports_dir
        self.logs_dir = logs_dir

        self._ensure_directories()

        self.logger = self._setup_logger()
        self.detailed_logger = self._setup_detailed_logger()

        self.processed_files = 0
        self.error_files = 0
        self.results = []

    def _ensure_directories(self):
        """Создаёт служебные папки, если их ещё нет."""
        for directory in [self.data_dir, self.reports_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)

    def _setup_logger(self):
        """
        Настраивает логгер для ошибок в папке logs/.

        Returns:
            logging.Logger: Настроенный логгер для записи ошибок
        """
        logger = logging.getLogger('error_logger')
        logger.setLevel(logging.ERROR)

        if not logger.handlers:
            log_path = os.path.join(self.logs_dir, config.ERROR_LOG_FILENAME)
            file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
            formatter = logging.Formatter(
                '%(asctime)s - ERROR - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def _setup_detailed_logger(self):
        """
        Настраивает логгер для вывода в консоль.

        Returns:
            logging.Logger: Настроенный логгер для консольного вывода
        """
        logger = logging.getLogger('console_logger')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

    def load_data(self, filepath):
        """
        Загружает данные из CSV-файла с проверкой формата.

        Args:
            filepath (str): Путь к CSV-файлу для загрузки

        Returns:
            pandas.DataFrame: Загруженные данные в виде DataFrame

        Raises:
            ValueError: если файл пуст или не содержит ожидаемых колонок.
            Exception: при проблемах чтения файла.
        """
        if os.path.getsize(filepath) == 0:
            raise ValueError("Файл пуст")

        try:
            df = pd.read_csv(filepath)
        except pd.errors.EmptyDataError:
            raise ValueError("Файл не содержит данных")
        except pd.errors.ParserError as e:
            raise ValueError(f"Ошибка парсинга CSV: {e}")

        required_columns = [
            config.STATUS_COLUMN,
            config.AMOUNT_COLUMN,
            config.ORDER_ID_COLUMN
        ]

        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"В файле отсутствуют обязательные колонки: {missing}")

        return df

    def filter_delivered(self, df):
        """
        Фильтрует DataFrame, оставляя только доставленные заказы.

        Args:
            df (pandas.DataFrame): Исходный DataFrame с заказами

        Returns:
            pandas.DataFrame: Отфильтрованный DataFrame только с доставленными заказами
        """
        mask = df[config.STATUS_COLUMN] == config.TARGET_STATUS
        filtered = df[mask].copy()

        if filtered.empty:
            self.detailed_logger.info(
                f"  В файле нет заказов со статусом '{config.TARGET_STATUS}'"
            )

        return filtered

    def calculate_metrics(self, df):
        """
        Рассчитывает три ключевые метрики по отфильтрованным данным.

        Args:
            df (pandas.DataFrame): DataFrame с отфильтрованными доставленными заказами

        Returns:
            dict: Словарь с рассчитанными метриками:
                - total_revenue (float): Общая выручка
                - average_order_value (float): Средняя стоимость заказа
                - order_count (int): Количество заказов
        """
        if df.empty:
            return {
                'total_revenue': 0.0,
                'average_order_value': 0.0,
                'order_count': 0
            }

        total_revenue = df[config.AMOUNT_COLUMN].sum()
        average_order_value = df[config.AMOUNT_COLUMN].mean()
        order_count = len(df)

        return {
            'total_revenue': round(total_revenue, 2),
            'average_order_value': round(average_order_value, 2),
            'order_count': int(order_count)
        }

    def process_single_file(self, filepath):
        """
        Полный цикл обработки одного файла: загрузка, фильтрация, расчёт.

        Args:
            filepath (str): Путь к CSV-файлу для обработки

        Returns:
            dict or None: Словарь с результатами обработки или None при ошибке
        """
        filename = os.path.basename(filepath)

        try:
            df = self.load_data(filepath)
        except Exception as e:
            self.logger.error(f"Файл '{filename}': {e}")
            self.detailed_logger.info(f"  Файл пропущен (ошибка: {e})")
            return None

        delivered_df = self.filter_delivered(df)
        metrics = self.calculate_metrics(delivered_df)
        metrics['filename'] = filename

        self.detailed_logger.info(
            f"Обработан: заказов={metrics['order_count']}, "
            f"выручка={metrics['total_revenue']}"
        )
        return metrics

    def process_all_files(self):
        """Обрабатывает все CSV-файлы в папке data/."""
        self.detailed_logger.info("=" * 60)
        self.detailed_logger.info("Запуск пакетного анализа заказов")
        self.detailed_logger.info(f"Папка с данными: {self.data_dir}")
        self.detailed_logger.info("=" * 60)

        csv_files = [
            os.path.join(self.data_dir, f)
            for f in os.listdir(self.data_dir)
            if f.endswith('.csv')
        ]

        if not csv_files:
            self.detailed_logger.info("В папке data/ не найдено CSV-файлов.")
            return

        for filepath in csv_files:
            filename = os.path.basename(filepath)
            self.detailed_logger.info(f"\nОбработка файла: {filename}")

            result = self.process_single_file(filepath)

            if result is not None:
                self.results.append(result)
                self.processed_files += 1
            else:
                self.error_files += 1

        self.save_report()

        self.detailed_logger.info("\n" + "=" * 60)
        self.detailed_logger.info(
            f"Обработано файлов: {self.processed_files}"
        )
        self.detailed_logger.info(
            f"Файлов с ошибками: {self.error_files}"
        )
        self.detailed_logger.info("=" * 60)

    def save_report(self):
        """Сохраняет итоговый отчёт в CSV."""
        if not self.results:
            self.detailed_logger.info("\nНет данных для сохранения отчёта.")
            return

        output_path = os.path.join(self.reports_dir, config.OUTPUT_FILENAME)
        df_report = pd.DataFrame(self.results)
        df_report = df_report[config.OUTPUT_COLUMNS]

        df_report.to_csv(output_path, index=False, encoding='utf-8')

        self.detailed_logger.info(
            f"\nОтчёт сохранён: {output_path}"
        )