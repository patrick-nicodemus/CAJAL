from networkx import is_connected as is_connected, neighbors as neighbors
from networkx.generators.internet_as_graphs import random_internet_as_graph as random_internet_as_graph

class TestInternetASTopology:
    @classmethod
    def setup_class(cls) -> None: ...
    @classmethod
    def set_customers(cls, i) -> None: ...
    @classmethod
    def set_providers(cls, i) -> None: ...
    def test_wrong_input(self) -> None: ...
    def test_node_numbers(self) -> None: ...
    def test_connectivity(self) -> None: ...
    def test_relationships(self) -> None: ...
    def test_degree_values(self) -> None: ...
