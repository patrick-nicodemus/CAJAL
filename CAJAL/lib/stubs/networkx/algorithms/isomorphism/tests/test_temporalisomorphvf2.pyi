def provide_g1_edgelist(): ...
def put_same_time(G, att_name): ...
def put_same_datetime(G, att_name): ...
def put_sequence_time(G, att_name): ...
def put_time_config_0(G, att_name): ...
def put_time_config_1(G, att_name): ...
def put_time_config_2(G, att_name): ...

class TestTimeRespectingGraphMatcher:
    def provide_g1_topology(self): ...
    def provide_g2_path_3edges(self): ...
    def test_timdelta_zero_timeRespecting_returnsTrue(self) -> None: ...
    def test_timdelta_zero_datetime_timeRespecting_returnsTrue(self) -> None: ...
    def test_attNameStrange_timdelta_zero_timeRespecting_returnsTrue(self) -> None: ...
    def test_notTimeRespecting_returnsFalse(self) -> None: ...
    def test_timdelta_one_config0_returns_no_embeddings(self) -> None: ...
    def test_timdelta_one_config1_returns_four_embedding(self) -> None: ...
    def test_timdelta_one_config2_returns_ten_embeddings(self) -> None: ...

class TestDiTimeRespectingGraphMatcher:
    def provide_g1_topology(self): ...
    def provide_g2_path_3edges(self): ...
    def test_timdelta_zero_same_dates_returns_true(self) -> None: ...
    def test_attNameStrange_timdelta_zero_same_dates_returns_true(self) -> None: ...
    def test_timdelta_one_config0_returns_no_embeddings(self) -> None: ...
    def test_timdelta_one_config1_returns_one_embedding(self) -> None: ...
    def test_timdelta_one_config2_returns_two_embeddings(self) -> None: ...
