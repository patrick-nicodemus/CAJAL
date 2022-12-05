from _typeshed import Incomplete

def test_simple() -> None: ...
def test_weightkey() -> None: ...

class TestNodeMatch_Graph:
    g1: Incomplete
    g2: Incomplete
    def setup_method(self) -> None: ...
    nm: Incomplete
    em: Incomplete
    def build(self) -> None: ...
    def test_noweight_nocolor(self) -> None: ...
    def test_color1(self) -> None: ...
    def test_color2(self) -> None: ...
    def test_weight1(self) -> None: ...
    def test_weight2(self) -> None: ...
    def test_colorsandweights1(self) -> None: ...
    def test_colorsandweights2(self) -> None: ...
    def test_colorsandweights3(self) -> None: ...

class TestEdgeMatch_MultiGraph:
    g1: Incomplete
    g2: Incomplete
    GM: Incomplete
    def setup_method(self) -> None: ...
    em: Incomplete
    emc: Incomplete
    emcm: Incomplete
    emg1: Incomplete
    emg2: Incomplete
    def build(self) -> None: ...
    def test_weights_only(self) -> None: ...
    def test_colors_only(self) -> None: ...
    def test_colorsandweights(self) -> None: ...
    def test_generic1(self) -> None: ...
    def test_generic2(self) -> None: ...

class TestEdgeMatch_DiGraph(TestNodeMatch_Graph):
    g1: Incomplete
    g2: Incomplete
    def setup_method(self) -> None: ...

class TestEdgeMatch_MultiDiGraph(TestEdgeMatch_MultiGraph):
    g1: Incomplete
    g2: Incomplete
    GM: Incomplete
    def setup_method(self) -> None: ...
