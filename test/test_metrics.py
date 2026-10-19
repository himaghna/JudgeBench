"""Synthetic two-game inputs; decisions use each game's displayed ordering."""

from copy import deepcopy

import pytest

from utils.metrics import compute_final_audit_metrics, compute_final_metrics

@pytest.fixture
def generic_pairs():
    """Three complete pairs with valid strict decisions."""
    return [
        {
            'pair_id': 'pair-1',
            'source': 'source-a',
            'label': 'A>B',
            'judgments': [{'decision': 'A>B'}, {'decision': 'B>A'}],
        },
        {
            'pair_id': 'pair-2',
            'source': 'source-a',
            'label': 'B>A',
            'judgments': [{'decision': 'A>B'}, {'decision': 'B>A'}],
        },
        {
            'pair_id': 'pair-3',
            'source': 'source-b',
            'label': 'A>B',
            'judgments': [{'decision': 'A>B'}, {'decision': 'A>B'}],
        },
    ]


@pytest.fixture
def pairs_with_invalid_decisions(generic_pairs):
    """Four complete pairs, including unsupported string and numeric decisions."""
    pairs = deepcopy(generic_pairs)
    pairs[1]['judgments'][0]['decision'] = 'unsure'
    pairs.append({
        'pair_id': 'pair-4',
        'source': 'source-b',
        'label': 'B>A',
        'judgments': [{'decision': 42}, {'decision': 'A>B'}],
    })
    return pairs


@pytest.fixture
def pairs_with_missing_decisions(generic_pairs):
    """Three pairs adding three missing forms."""
    pairs = deepcopy(generic_pairs)
    pairs[0]['judgments'][0] = None
    pairs[2]['judgments'][0] = {'decision': None}
    pairs[2]['judgments'][1] = {}
    return pairs


@pytest.fixture
def empty_pairs():
    return []


@pytest.fixture
def all_tied_pairs(pairs_with_missing_decisions):
    """Four pairs with every judgment replaced by an explicit tie."""
    pairs = deepcopy(pairs_with_missing_decisions)
    for pair in pairs:
        pair['judgments'] = [{'decision': 'A=B'}, {'decision': 'A=B'}]
    return pairs


@pytest.fixture
def some_tied_pairs(all_tied_pairs):
    """Four complete pairs mixing explicit ties and valid strict decisions."""
    pairs = deepcopy(all_tied_pairs)
    pairs[0]['judgments'] = [{'decision': 'A>B'}, {'decision': 'B>A'}]
    pairs[1]['judgments'][0] = {'decision': 'B>A'}
    return pairs


def test_num_pairs(empty_pairs, generic_pairs):
    generic_results = compute_final_audit_metrics(generic_pairs)
    assert generic_results['summary_metrics']['num_pairs'] == 3

    empty_results = compute_final_audit_metrics(empty_pairs)
    assert empty_results['summary_metrics']['num_pairs'] == 0

def test_tied_pairs(all_tied_pairs, some_tied_pairs, generic_pairs):
    all_tied_result = compute_final_audit_metrics(all_tied_pairs)
    assert all_tied_result['sample_metrics']['tied'] == 6

    some_tied_result = compute_final_audit_metrics(some_tied_pairs)
    assert some_tied_result['sample_metrics']['tied'] == 3

    generic_results = compute_final_audit_metrics(generic_pairs)
    assert generic_results['sample_metrics']['tied'] == 0



def test_missing_pairs(generic_pairs, pairs_with_missing_decisions):
    missing_result = compute_final_audit_metrics(pairs_with_missing_decisions)
    assert missing_result['sample_metrics']['missing'] == 3

    generic_results = compute_final_audit_metrics(generic_pairs)
    assert generic_results['sample_metrics']['missing'] == 0

def test_invalid_pairs(pairs_with_invalid_decisions, generic_pairs):
    invalid_results = compute_final_audit_metrics(pairs_with_invalid_decisions)
    assert invalid_results['sample_metrics']['invalid'] == 2

    generic_results = compute_final_audit_metrics(generic_pairs)
    assert generic_results['sample_metrics']['invalid'] == 0

def test_consistent_accuracy(generic_pairs, pairs_with_invalid_decisions, pairs_with_missing_decisions, all_tied_pairs, some_tied_pairs):
    generic_results = compute_final_audit_metrics(generic_pairs)
    assert generic_results['summary_metrics']['accuracy'] == compute_final_metrics(generic_pairs, True)
    
    invalid_results = compute_final_audit_metrics(pairs_with_invalid_decisions)
    assert invalid_results['summary_metrics']['accuracy'] == compute_final_metrics(pairs_with_invalid_decisions, True)

    # this raises an error when 'decision' is missing as a key in the legacy code
    # missing_result = compute_final_audit_metrics(pairs_with_missing_decisions)
    # assert missing_result['summary_metrics']['accuracy'] == compute_final_metrics(pairs_with_missing_decisions, True)

    all_tied_result = compute_final_audit_metrics(all_tied_pairs)
    assert all_tied_result['summary_metrics']['accuracy'] == compute_final_metrics(all_tied_pairs, True)
    
    some_tied_result = compute_final_audit_metrics(some_tied_pairs)
    assert some_tied_result['summary_metrics']['accuracy'] == compute_final_metrics(some_tied_pairs, True)

def test_inconsistency(generic_pairs, all_tied_pairs):
    generic_results = compute_final_audit_metrics(generic_pairs)
    assert generic_results['summary_metrics']['inconsistent_pairs'] == 1

    all_tied_result = compute_final_audit_metrics(all_tied_pairs)
    assert all_tied_result['summary_metrics']['inconsistent_pairs'] == 0







