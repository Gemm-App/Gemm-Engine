"""Dogfood the contract harness against the bundled MockAdapter.

If MockAdapter breaks the contract, these tests catch it. Also proves the
AdapterContractTests base class works as a reusable testing utility.
"""

import pytest

from gemm.adapters import MockAdapter
from gemm.testing import AdapterContractTests


class TestMockAdapterContract(AdapterContractTests):
    @pytest.fixture
    def adapter(self) -> MockAdapter:
        return MockAdapter(name="contract-probe")
