import pytest


@pytest.fixture
def test_season():
    # The season in which Samsung Lions won their last KBO championship
    return 2014


@pytest.fixture
def test_date():
    # Date of Korean Series Game 6, where Samsung Lions defeated Nexen Heroes 4-2
    return "20141111"


@pytest.fixture
def test_game_id():
    # Game ID for Korean Series Game 6, where Samsung Lions defeated Nexen Heroes 4-2
    return "20141111SSWO0"
