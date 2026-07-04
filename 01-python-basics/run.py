import config
from src.analyzer import OrderAnalyzer


def main():
    analyzer = OrderAnalyzer(
        data_dir=config.DATA_DIR,
        reports_dir=config.REPORTS_DIR,
        logs_dir=config.LOGS_DIR
    )
    analyzer.process_all_files()


if __name__ == '__main__':
    main()