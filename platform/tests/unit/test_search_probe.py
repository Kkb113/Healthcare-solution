from probe_search_capability import vector


def test_precomputed_vectors_are_distinct_unit_basis_without_model_calls():
    vectors = [vector(i) for i in range(3)]
    assert all(len(v) == 768 and sum(x * x for x in v) == 1 for v in vectors)
    assert all(
        sum(a * b for a, b in zip(vectors[i], vectors[j], strict=True)) == 0
        for i, j in [(0, 1), (0, 2), (1, 2)]
    )
