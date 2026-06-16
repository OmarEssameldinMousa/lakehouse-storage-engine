import pyarrow as pa
from lakehouse.parquet.io import read_footer_stats, write_parquet

def test_footer_stats_match_known_data(backend):
    # Build a pa.Table with a KNOWN min, max, and exactly one null in a column.
    table = pa.Table.from_arrays([
        pa.array([1, 2, None], type=pa.int64())
    ], names=["col1"])
    # write_parquet → read_footer_stats → assert numRecords, minValues,
    parquet_file_path = "test.parquet"
    write_parquet(table, backend, parquet_file_path)
    footer_stats = read_footer_stats(backend, path=parquet_file_path)
    # maxValues, nullCount[col] == your hand-computed truth.
    assert footer_stats["numRecords"] == 3
    assert footer_stats["minValues"]["col1"] == 1
    assert footer_stats["maxValues"]["col1"] == 2
    assert footer_stats["nullCount"]["col1"] == 1

def test_all_null_column_does_not_corrupt_bounds(backend):
    # The all-null row group case from the io.py review. Decide the contract
    # and pin it: what SHOULD min/max be for a column with no real values?
    table = pa.Table.from_arrays([
        pa.array([None, None, None], type=pa.int64())
    ], names=["col1"])
    parquet_file_path = "test_all_null.parquet"
    write_parquet(table, backend, parquet_file_path)
    footer_stats = read_footer_stats(backend, path=parquet_file_path)
    assert footer_stats["numRecords"] == 3
    assert "col1" not in footer_stats["minValues"]
    assert "col1" not in footer_stats["maxValues"]
    assert footer_stats["nullCount"]["col1"] == 3

    # answer to the contract question: for an all-null column, minValues and maxValues
    # should simply not have that column as a key. The nullCount should still be correctly reported as 3. 
    # This way, we avoid any confusion about what the min and max values 
    # should be when there are no real values to compute them from.
