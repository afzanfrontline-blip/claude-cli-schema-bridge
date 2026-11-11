from schema_bridge import compress

def test_comp():
    assert len(compress('x'*9000)) <= 8000
