def simple_flow_graph(): ...
def simple_no_flow_graph(): ...
def get_flowcost_from_flowdict(G, flowDict): ...
def test_infinite_demand_raise(simple_flow_graph) -> None: ...
def test_neg_infinite_demand_raise(simple_flow_graph) -> None: ...
def test_infinite_weight_raise(simple_flow_graph) -> None: ...
def test_nonzero_net_demand_raise(simple_flow_graph) -> None: ...
def test_negative_capacity_raise(simple_flow_graph) -> None: ...
def test_no_flow_satisfying_demands(simple_no_flow_graph) -> None: ...
def test_sum_demands_not_zero(simple_no_flow_graph) -> None: ...
def test_google_or_tools_example() -> None: ...
def test_google_or_tools_example2() -> None: ...
def test_large() -> None: ...
def test_simple_digraph() -> None: ...
def test_negcycle_infcap() -> None: ...
def test_transshipment() -> None: ...
def test_digraph1() -> None: ...
def test_zero_capacity_edges() -> None: ...
def test_digon() -> None: ...
def test_deadend() -> None: ...
def test_infinite_capacity_neg_digon() -> None: ...
def test_multidigraph() -> None: ...
def test_negative_selfloops() -> None: ...
def test_bone_shaped() -> None: ...
def test_graphs_type_exceptions() -> None: ...
