from features import FEATURE_COUNT, FEATURES

def test_feature_count():
    assert FEATURE_COUNT >= 500
    assert len(FEATURES) == FEATURE_COUNT
    assert all(callable(fn) for fn in FEATURES.values())

def test_toolkit_behaviour():
    assert FEATURES['normalize_name_moderation'](' Hello World ') == 'hello-world'
    assert FEATURES['clamp_value_music'](99, 0, 50) == 50
    assert FEATURES['paginate_items_tickets']([1,2,3,4], 2, 2) == [3,4]
