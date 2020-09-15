from datetime import datetime, timedelta
import pytest
from ...examples.qt_search import Searches


@pytest.fixture(scope="function")
def make_test_searches(qtbot, request):
    searchess = []

    def actual_factory(*model_args, **model_kwargs):
        model_kwargs["show"] = model_kwargs.pop(
            "show", request.config.getoption("--show-window")
        )
        searches = Searches(*model_args, **model_kwargs)
        searchess.append(searches)
        return searches

    yield actual_factory

    for searches in searchess:
        searches.close()


def test_searches(make_test_searches):
    "An integration test"
    searches = make_test_searches()
    searches[0].input.since = datetime(1980, 2, 2)
    searches[0].input.since = datetime(1985, 11, 15)
    searches[0].input.since = timedelta(days=-1)
