import networkx as nx
from .test_multigraph import BaseMultiGraphTester as BaseMultiGraphTester, TestEdgeSubgraph as _TestMultiGraphEdgeSubgraph, TestMultiGraph as _TestMultiGraph
from _typeshed import Incomplete
from collections import UserDict
from networkx.utils import edges_equal as edges_equal

class BaseMultiDiGraphTester(BaseMultiGraphTester):
    def test_edges(self) -> None: ...
    def test_edges_data(self) -> None: ...
    def test_edges_multi(self) -> None: ...
    def test_out_edges(self) -> None: ...
    def test_out_edges_multi(self) -> None: ...
    def test_out_edges_data(self) -> None: ...
    def test_in_edges(self) -> None: ...
    def test_in_edges_no_keys(self) -> None: ...
    def test_in_edges_data(self) -> None: ...
    def is_shallow(self, H, G) -> None: ...
    def is_deep(self, H, G) -> None: ...
    def test_to_undirected(self) -> None: ...
    def test_has_successor(self) -> None: ...
    def test_successors(self) -> None: ...
    def test_has_predecessor(self) -> None: ...
    def test_predecessors(self) -> None: ...
    def test_degree(self) -> None: ...
    def test_in_degree(self) -> None: ...
    def test_out_degree(self) -> None: ...
    def test_size(self) -> None: ...
    def test_to_undirected_reciprocal(self) -> None: ...
    def test_reverse_copy(self) -> None: ...
    def test_reverse_nocopy(self) -> None: ...
    def test_di_attributes_cached(self) -> None: ...

class TestMultiDiGraph(BaseMultiDiGraphTester, _TestMultiGraph):
    Graph: Incomplete
    k3edges: Incomplete
    k3nodes: Incomplete
    K3: Incomplete
    def setup_method(self) -> None: ...
    def test_add_edge(self) -> None: ...
    def test_add_edges_from(self) -> None: ...
    def test_remove_edge(self) -> None: ...
    def test_remove_multiedge(self) -> None: ...
    def test_remove_edges_from(self) -> None: ...

class TestEdgeSubgraph(_TestMultiGraphEdgeSubgraph):
    G: Incomplete
    H: Incomplete
    def setup_method(self) -> None: ...

class CustomDictClass(UserDict): ...

class MultiDiGraphSubClass(nx.MultiDiGraph):
    node_dict_factory: Incomplete
    node_attr_dict_factory: Incomplete
    adjlist_outer_dict_factory: Incomplete
    adjlist_inner_dict_factory: Incomplete
    edge_key_dict_factory: Incomplete
    edge_attr_dict_factory: Incomplete
    graph_attr_dict_factory: Incomplete

class TestMultiDiGraphSubclass(TestMultiDiGraph):
    Graph: Incomplete
    k3edges: Incomplete
    k3nodes: Incomplete
    K3: Incomplete
    def setup_method(self) -> None: ...
