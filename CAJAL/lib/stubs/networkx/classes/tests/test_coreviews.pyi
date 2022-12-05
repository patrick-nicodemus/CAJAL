from _typeshed import Incomplete

class TestAtlasView:
    d: Incomplete
    av: Incomplete
    def setup(self) -> None: ...
    def test_pickle(self) -> None: ...
    def test_len(self) -> None: ...
    def test_iter(self) -> None: ...
    def test_getitem(self) -> None: ...
    def test_copy(self) -> None: ...
    def test_items(self) -> None: ...
    def test_str(self) -> None: ...
    def test_repr(self) -> None: ...

class TestAdjacencyView:
    nd: Incomplete
    adj: Incomplete
    adjview: Incomplete
    def setup(self) -> None: ...
    def test_pickle(self) -> None: ...
    def test_len(self) -> None: ...
    def test_iter(self) -> None: ...
    def test_getitem(self) -> None: ...
    def test_copy(self) -> None: ...
    def test_items(self) -> None: ...
    def test_str(self) -> None: ...
    def test_repr(self) -> None: ...

class TestMultiAdjacencyView(TestAdjacencyView):
    kd: Incomplete
    nd: Incomplete
    adj: Incomplete
    adjview: Incomplete
    def setup(self) -> None: ...
    def test_getitem(self) -> None: ...
    def test_copy(self) -> None: ...

class TestUnionAtlas:
    s: Incomplete
    p: Incomplete
    av: Incomplete
    def setup(self) -> None: ...
    def test_pickle(self) -> None: ...
    def test_len(self) -> None: ...
    def test_iter(self) -> None: ...
    def test_getitem(self) -> None: ...
    def test_copy(self) -> None: ...
    def test_items(self) -> None: ...
    def test_str(self) -> None: ...
    def test_repr(self) -> None: ...

class TestUnionAdjacency:
    nd: Incomplete
    s: Incomplete
    p: Incomplete
    adjview: Incomplete
    def setup(self) -> None: ...
    def test_pickle(self) -> None: ...
    def test_len(self) -> None: ...
    def test_iter(self) -> None: ...
    def test_getitem(self) -> None: ...
    def test_copy(self) -> None: ...
    def test_str(self) -> None: ...
    def test_repr(self) -> None: ...

class TestUnionMultiInner(TestUnionAdjacency):
    kd: Incomplete
    s: Incomplete
    p: Incomplete
    adjview: Incomplete
    def setup(self) -> None: ...
    def test_len(self) -> None: ...
    def test_getitem(self) -> None: ...
    def test_copy(self) -> None: ...

class TestUnionMultiAdjacency(TestUnionAdjacency):
    kd: Incomplete
    nd: Incomplete
    s: Incomplete
    p: Incomplete
    adjview: Incomplete
    def setup(self) -> None: ...
    def test_getitem(self) -> None: ...
    def test_copy(self) -> None: ...

class TestFilteredGraphs:
    Graphs: Incomplete
    def setup(self) -> None: ...
    def test_hide_show_nodes(self) -> None: ...
    def test_str_repr(self) -> None: ...
    def test_copy(self) -> None: ...
    def test_filtered_copy(self) -> None: ...
