from _typeshed import Incomplete

np: Incomplete

class TestLayout:
    @classmethod
    def setup_class(cls) -> None: ...
    def test_spring_fixed_without_pos(self) -> None: ...
    def test_spring_init_pos(self) -> None: ...
    def test_smoke_empty_graph(self) -> None: ...
    def test_smoke_int(self) -> None: ...
    def test_smoke_string(self) -> None: ...
    def check_scale_and_center(self, pos, scale, center) -> None: ...
    def test_scale_and_center_arg(self) -> None: ...
    def test_planar_layout_non_planar_input(self) -> None: ...
    def test_smoke_planar_layout_embedding_input(self) -> None: ...
    def test_default_scale_and_center(self) -> None: ...
    def test_circular_planar_and_shell_dim_error(self) -> None: ...
    def test_adjacency_interface_numpy(self) -> None: ...
    def test_adjacency_interface_scipy(self) -> None: ...
    def test_single_nodes(self) -> None: ...
    def test_smoke_initial_pos_fruchterman_reingold(self) -> None: ...
    def test_fixed_node_fruchterman_reingold(self) -> None: ...
    def test_center_parameter(self) -> None: ...
    def test_center_wrong_dimensions(self) -> None: ...
    def test_empty_graph(self) -> None: ...
    def test_bipartite_layout(self) -> None: ...
    def test_multipartite_layout(self) -> None: ...
    def test_kamada_kawai_costfn_1d(self) -> None: ...
    def check_kamada_kawai_costfn(self, pos, invdist, meanwt, dim) -> None: ...
    def test_kamada_kawai_costfn(self) -> None: ...
    def test_spiral_layout(self) -> None: ...
    def test_spiral_layout_equidistant(self) -> None: ...
    def test_rescale_layout_dict(self) -> None: ...

def test_multipartite_layout_nonnumeric_partition_labels() -> None: ...
def test_multipartite_layout_layer_order() -> None: ...
