import argparse

from utils import file_operations, metrics


def print_report_row(source, result):
    """Format one result returned by compute_final_audit_metrics."""
    summary = result['summary_metrics']
    samples = result['sample_metrics']
    accuracy = summary['accuracy']
    accuracy_text = 'N/A' if accuracy is None else f'{accuracy:.2f}%'
    pair_count = summary['num_pairs']
    inconsistent = summary['inconsistent_pairs']
    print(
        f"{source:<36} "
        f"{str(pair_count) if pair_count is not None else 'N/A':>7} "
        f"{accuracy_text:>10} "
        f"{samples['tied']:>10} "
        f"{samples['missing']:>10} "
        f"{samples['invalid']:>10} "
        f"{str(inconsistent) if inconsistent is not None else 'N/A':>13}"
    )


def main(args: argparse.Namespace):
    pairs = file_operations.read_jsonl(args.input)
    print(
        f"{'Source':<36} {'Pairs':>7} {'Accuracy':>10} "
        f"{'Ties':>10} {'Missing':>10} {'Invalid':>10} {'Inconsistent':>13}"
    )
    print('-' * 112)
    print_report_row('Overall', metrics.compute_final_audit_metrics(pairs))
    for source in sorted({pair['source'] for pair in pairs}):
        result = metrics.compute_final_audit_metrics(
            pairs, include_fn=lambda pair, source=source: pair['source'] == source
        )
        print_report_row(source, result)
    print('\nAccuracy denominator: all pairs in the row; values are percentages.')
    print('Ties, Missing, Invalid: individual judgment counts.')
    print('Inconsistent: pair count after normalizing answer ordering.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Report metrics for saved judge results.')
    parser.add_argument(
        '-i', '--input', type=str, required=True,
        help='Filepath of the input file containing judge annotations, e.g. outputs/x.jsonl',
    )
    args = parser.parse_args()
    main(args)
