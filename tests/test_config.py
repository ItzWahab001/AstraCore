def test_env_example_exists():
    from pathlib import Path
    assert (Path(__file__).parents[1]/'.env.example').exists()
