"""Fixtures shared by portable validation tests."""
import pytest

from tests.runtime_review_real import install_reviewer_host


@pytest.fixture(scope="session")
def reviewer_host(tmp_path_factory):
    """One installed host with every shipped Reviewer registered, for real_run tests."""
    return install_reviewer_host(tmp_path_factory.mktemp("reviewer_host") / "host")
