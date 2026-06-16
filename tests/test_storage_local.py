import pytest
from lakehouse.errors import FileAlreadyExists
def test_put_if_absent_rejects_second_write(backend):
    # put_if_absent once → ok. Same key again → must raise FileAlreadyExists.
    # This single test is the foundation of your entire concurrency story.
    backend.put_if_absent("foo", b"bar")
    with pytest.raises(FileAlreadyExists):
        backend.put_if_absent("foo", b"baz")
    

def test_get_returns_what_put_wrote(backend):
    # put → get → assert equality. This is the foundation of your entire
    # correctness story.
    backend.put("foo", b"bar")
    data = backend.get("foo")
    assert data == b"bar"