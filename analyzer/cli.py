import argparse
from analyzer.reports.handlers import HandlersReport
from analyzer.utils import validate_files


class ReportCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Analyze Django application logs and generate reports'
        )
        self._setup_arguments()

    def _setup_arguments(self):
        self.parser.add_argument(
            'files',
            nargs='+',
            help='Paths to log files'
        )
        self.parser.add_argument(
            '--report',
            required=True,
            choices=['handlers'],
            help='Report type to generate'
        )

    def parse_args(self):
        args = self.parser.parse_args()
        validate_files(args.files)
        return args


def main():
    cli = ReportCLI()
    args = cli.parse_args()

    if args.report == 'handlers':
        report = HandlersReport()

    print(report.execute(args.files))


if __name__ == '__main__':
    main()
