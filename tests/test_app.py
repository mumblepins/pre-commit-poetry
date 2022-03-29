# -*- coding: utf-8 -*-
import pytest
from pre_commit_poetry.app import main


def test_main(monkeypatch):
    monkeypatch.setattr("sys.argv", ["pre-commit-poetry", "-h"])

    with pytest.raises(SystemExit):
        main()
