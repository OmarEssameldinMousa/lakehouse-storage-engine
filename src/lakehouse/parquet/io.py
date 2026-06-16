import pyarrow as pa
import pyarrow.parquet as pq
from lakehouse.storage.base import StorageBackend

def write_parquet(table: pa.Table, backend: StorageBackend, path: str) -> int:
    """Write `table` as a single Parquet file via `backend`. Return byte size.
    One row group is fine for M1. Do NOT compute stats here by iterating rows.
    """
    # creat an empty buffer to write the parquet file into
    sink = pa.BufferOutputStream()
    # write the table to the buffer as a parquet file
    
    pq.write_table(table, sink)
    
    # get the buffer contents as bytes
    
    parquet_bytes = sink.getvalue().to_pybytes()

    # write the bytes to the backend at the specified path
    backend.put(path, parquet_bytes)
    
    # parquet_size is the length of the bytes
    
    parquet_size = len(parquet_bytes)
    
    return parquet_size


def read_footer_stats(backend: StorageBackend, path: str) -> dict:
    """Open ONLY the Parquet footer metadata and return:
        {"numRecords": int,
         "minValues": {col: val, ...},
         "maxValues": {col: val, ...},
         "nullCount": {col: int, ...}}
    Aggregate across row groups (min of mins, max of maxes, sum of nulls).
    If you call .to_pandas() or read any data page here, you've failed the task.
    """
    # read the parquet file metadata from the backend
    parquet_bytes = backend.get(path)
    
    # create a buffer reader from the parquet bytes
    buffer_reader = pa.BufferReader(parquet_bytes)
    
    # read the parquet file metadata using pyarrow
    parquet_file = pq.ParquetFile(buffer_reader)
    metadata = parquet_file.metadata
    
    # initialize the stats dictionary
    stats = {
        "numRecords": 0,
        "minValues": {},
        "maxValues": {},
        "nullCount": {}
    }
    
    # iterate over each row group in the parquet file metadata
    for i in range(metadata.num_row_groups):
        row_group_metadata = metadata.row_group(i)
        
        # update the total number of records
        stats["numRecords"] += row_group_metadata.num_rows
        
        # iterate over each column in the row group metadata
        for j in range(row_group_metadata.num_columns):
            column_metadata = row_group_metadata.column(j)
            column_name = column_metadata.path_in_schema
            col_stats = column_metadata.statistics
            if col_stats is not None:
                
                if col_stats.has_min_max:
                    current_min = col_stats.min
                    current_max = col_stats.max
                    if column_name in stats["minValues"]:
                        stats["minValues"][column_name] = min(stats["minValues"][column_name], current_min)
                    else:
                        stats["minValues"][column_name] = current_min

                    if column_name in stats["maxValues"]:
                        stats["maxValues"][column_name] = max(stats["maxValues"][column_name], current_max)
                    else:
                        stats["maxValues"][column_name] = current_max 
                    
    
                if col_stats.null_count is not None:
                    if column_name in stats["nullCount"]:
                        stats["nullCount"][column_name] += col_stats.null_count
                    else:
                        stats["nullCount"][column_name] = col_stats.null_count

    return stats
            
            
