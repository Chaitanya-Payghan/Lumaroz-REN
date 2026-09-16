from ren.app.bootstrap import run


def test_bootstrap_imports() -> None:
    assert callable(run)
