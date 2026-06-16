import pyarrow as pa
import pyarrow.parquet as pq
import json
from lakehouse.protocol.actions import AddFile, CommitInfo, Metadata, Format, Protocol
from lakehouse.protocol.log import write_commit, read_commit 
from lakehouse.parquet.io import read_footer_stats, write_parquet
def test_round_trip_via_log_not_listing(backend):
    # write_parquet → build [protocol, metaData, add, commitInfo] →
    # write_commit(version=0) → read_commit(0) → follow the add.path →
    # load that parquet → assert rows equal the original.
    # HARD RULE: read the data by following the add action, never by
    # backend.list("data/"). If your test lists the data dir, it's wrong.
    table = pa.Table.from_arrays([
        pa.array([1, 2, None], type=pa.int64())
    ], names=["col1"])
    parquet_file_path = "data/test.parquet"
    write_parquet(table, backend, parquet_file_path)

    actions = [
        Protocol(min_reader_version=1, min_writer_version=2),
        Metadata(
            id="test_table",
            schema_string=json.dumps({
                "type": "struct",
                "fields": [
                    {
                        "name": field.name,
                        "type": str(field.type),
                        "nullable": field.nullable,
                        "metadata": field.metadata or {}
                    }
                    for field in table.schema
                ]
            }),
            format=Format(provider="parquet"),
            partition_columns=[]
        ),
        AddFile(
            path=parquet_file_path,
            size=len(backend.get(parquet_file_path)),
            modification_time= 16,
            data_change=True,
            stats=json.dumps(read_footer_stats(backend=backend, path=parquet_file_path)),
            partition_values={}
        ),
        CommitInfo(
            timestamp= 16,
            operation="test_commit_zero",
            operation_parameters={}
        ),
    ]

    write_commit(backend, version=0, actions=actions)

    read_actions = read_commit(backend, version=0)    
    assert read_actions is not None
    add_file_action = next((a for a in read_actions if isinstance(a, AddFile)), None)
    assert add_file_action is not None

    file_bytes = backend.get(add_file_action.path)
    read_table = pq.read_table(pa.BufferReader(file_bytes))

    assert read_table.equals(table)

    # check if the format will survive 
    format_action = next((a for a in read_actions if isinstance(a, Metadata)), None)
    assert format_action is not None
    assert format_action.format.provider == "parquet"