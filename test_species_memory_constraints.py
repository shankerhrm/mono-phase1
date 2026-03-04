#!/usr/bin/env python3
"""Adversarial sanity tests for SpeciesMemory forbidden-knowledge constraints.

These tests are intentionally lightweight (no pytest dependency) and should fail fast
if SpeciesMemory is allowed to store non-scalar or non-whitelisted state.
"""

import sys
sys.path.append('.')

from species_memory import SpeciesMemory
from reproduction.spawn import divide


def assert_raises(exc_type, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc_type:
        return
    except Exception as e:
        raise AssertionError(f"Expected {exc_type.__name__}, got {type(e).__name__}: {e}") from e
    raise AssertionError(f"Expected {exc_type.__name__} to be raised")


def test_init_rejects_non_scalar_ms_values():
    sm = SpeciesMemory()
    sm.Ms['gamma'] = {'not': 'scalar'}
    assert_raises(TypeError, sm._validate_memory_state)


def test_init_rejects_forbidden_ms_keys():
    sm = SpeciesMemory()
    sm.Ms['policy'] = 1.0
    assert_raises(ValueError, sm._validate_memory_state)


def test_update_rejects_non_scalar_phi_outputs():
    sm = SpeciesMemory()

    def bad_compress(_):
        return {'gamma': {'not': 'scalar'}}

    sm.compress_phi = bad_compress
    organism_data = [(1.0, 1.0, 0.5, {'module_count': 3}, 1.0, 1)]
    assert_raises(TypeError, sm.update, organism_data)


def test_update_rejects_forbidden_expected_keys():
    sm = SpeciesMemory()

    def bad_compress(_):
        return {'gamma': 0.5, 'policy': 1.0}

    sm.compress_phi = bad_compress
    organism_data = [(1.0, 1.0, 0.5, {'module_count': 3}, 1.0, 1)]
    assert_raises(ValueError, sm.update, organism_data)


def test_divide_rejects_species_memory_object():
    sm = SpeciesMemory()
    assert_raises(TypeError, divide, None, sm)


def main():
    tests = [
        test_init_rejects_non_scalar_ms_values,
        test_init_rejects_forbidden_ms_keys,
        test_update_rejects_non_scalar_phi_outputs,
        test_update_rejects_forbidden_expected_keys,
        test_divide_rejects_species_memory_object,
    ]

    for t in tests:
        t()
        print(f"PASS: {t.__name__}")


if __name__ == '__main__':
    main()
