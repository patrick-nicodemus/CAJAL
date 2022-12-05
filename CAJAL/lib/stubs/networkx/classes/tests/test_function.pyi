from _typeshed import Incomplete
from networkx.utils import edges_equal as edges_equal, nodes_equal as nodes_equal

class TestFunction:
    G: Incomplete
    Gdegree: Incomplete
    Gnodes: Incomplete
    Gedges: Incomplete
    DG: Incomplete
    DGin_degree: Incomplete
    DGout_degree: Incomplete
    DGnodes: Incomplete
    DGedges: Incomplete
    def setup_method(self) -> None: ...
    def test_nodes(self) -> None: ...
    def test_edges(self) -> None: ...
    def test_degree(self) -> None: ...
    def test_neighbors(self) -> None: ...
    def test_number_of_nodes(self) -> None: ...
    def test_number_of_edges(self) -> None: ...
    def test_is_directed(self) -> None: ...
    def test_add_star(self) -> None: ...
    def test_add_path(self) -> None: ...
    def test_add_cycle(self) -> None: ...
    def test_subgraph(self) -> None: ...
    def test_edge_subgraph(self) -> None: ...
    def test_create_empty_copy(self) -> None: ...
    def test_degree_histogram(self) -> None: ...
    def test_density(self) -> None: ...
    def test_density_selfloop(self) -> None: ...
    def test_freeze(self) -> None: ...
    def test_is_frozen(self) -> None: ...
    def test_info(self) -> None: ...
    def test_info_digraph(self) -> None: ...
    def test_neighbors_complete_graph(self) -> None: ...
    def test_non_neighbors(self) -> None: ...
    def test_non_edges(self) -> None: ...
    def test_is_weighted(self) -> None: ...
    def test_is_negatively_weighted(self) -> None: ...

class TestCommonNeighbors:
    @classmethod
    def setup_class(cls) -> None: ...
    def test_K5(self) -> None: ...
    def test_P3(self) -> None: ...
    def test_S4(self) -> None: ...
    def test_digraph(self) -> None: ...
    def test_nonexistent_nodes(self) -> None: ...
    def test_custom1(self) -> None: ...
    def test_custom2(self) -> None: ...

def test_set_node_attributes(graph_type) -> None: ...
def test_set_node_attributes_ignores_extra_nodes(values, name) -> None: ...
def test_set_edge_attributes(graph_type) -> None: ...
def test_set_edge_attributes_ignores_extra_edges(values, name) -> None: ...
def test_set_edge_attributes_multi(graph_type) -> None: ...
def test_set_edge_attributes_multi_ignores_extra_edges(values, name) -> None: ...
def test_get_node_attributes() -> None: ...
def test_get_edge_attributes() -> None: ...
def test_is_empty() -> None: ...
def test_selfloops(graph_type) -> None: ...
def test_selfloop_edges_attr(graph_type) -> None: ...
def test_selfloop_edges_multi_with_data_and_keys() -> None: ...
def test_selfloops_removal(graph_type) -> None: ...
def test_selfloops_removal_multi(graph_type) -> None: ...
def test_pathweight() -> None: ...
def test_ispath(G) -> None: ...
def test_restricted_view(G) -> None: ...
def test_restricted_view_multi(G) -> None: ...
