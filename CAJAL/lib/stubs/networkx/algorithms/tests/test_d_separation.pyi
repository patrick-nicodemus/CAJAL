def path_graph(): ...
def fork_graph(): ...
def collider_graph(): ...
def naive_bayes_graph(): ...
def asia_graph(): ...
def path_graph_fixture(): ...
def fork_graph_fixture(): ...
def collider_graph_fixture(): ...
def naive_bayes_graph_fixture(): ...
def asia_graph_fixture(): ...
def test_markov_condition(graph) -> None: ...
def test_path_graph_dsep(path_graph) -> None: ...
def test_fork_graph_dsep(fork_graph) -> None: ...
def test_collider_graph_dsep(collider_graph) -> None: ...
def test_naive_bayes_dsep(naive_bayes_graph) -> None: ...
def test_asia_graph_dsep(asia_graph) -> None: ...
def test_undirected_graphs_are_not_supported() -> None: ...
def test_cyclic_graphs_raise_error() -> None: ...
def test_invalid_nodes_raise_error(asia_graph) -> None: ...
