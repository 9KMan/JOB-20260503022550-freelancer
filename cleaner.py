"""AI Data Cleaning Automation Tool.

A CLI tool for cleaning mixed text + numerical datasets.
"""
import argparse
import sys
from pathlib import Path

from src.utils import load_data, save_data, get_column_types, generate_report
from src.cleaners.text import clean_text
from src.cleaners.numeric import clean_numeric
from src.cleaners.dedup import remove_duplicates


def parse_args():
    parser = argparse.ArgumentParser(
        description='AI Data Cleaning Automation Tool'
    )
    parser.add_argument('--input', '-i', required=True, help='Input file path')
    parser.add_argument('--output', '-o', required=True, help='Output directory')
    parser.add_argument('--format', '-f', choices=['csv', 'json', 'xlsx'],
                        help='Output format (default: same as input)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be changed without making changes')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('--no-dedup', action='store_true',
                        help='Skip deduplication')
    parser.add_argument('--no-cap-outliers', action='store_true',
                        help='Do not cap outliers')
    parser.add_argument('--text-columns', nargs='+',
                        help='Columns to treat as text')
    parser.add_argument('--numeric-columns', nargs='+',
                        help='Columns to treat as numeric')
    return parser.parse_args()


def main():
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.verbose:
        print(f"Loading data from: {input_path}")

    df = load_data(input_path)

    if args.verbose:
        print(f"Loaded {len(df)} rows, {len(df.columns)} columns")

    report = []
    original_df = df.copy() if args.dry_run else None

    df = clean_text(df, text_columns=args.text_columns, report=report)

    df = clean_numeric(
        df,
        numeric_columns=args.numeric_columns,
        cap_outliers_flag=not args.no_cap_outliers,
        report=report
    )

    if not args.no_dedup:
        df = remove_duplicates(df, report=report)

    if args.dry_run:
        print("DRY RUN - Changes that would be made:")
        for change in report:
            print(f"  - {change['description']}")
        return

    base_name = input_path.stem
    output_format = args.format or input_path.suffix.lstrip('.')

    output_file = output_dir / f"{base_name}_clean.{output_format}"
    save_data(df, output_file)

    report_file = output_dir / "cleaning_report.txt"
    generate_report(report, report_file)

    if args.verbose:
        print(f"Cleaned data saved to: {output_file}")
        print(f"Report saved to: {report_file}")
        print(f"Total changes: {len(report)}")


if __name__ == '__main__':
    main()
