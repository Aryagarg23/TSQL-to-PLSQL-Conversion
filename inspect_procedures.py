import os
import re

# --- Configuration ---
HAMMERDB_DIR = "HammerDB"

# List of all benchmark pairs to inspect
BENCHMARK_PAIRS = {
    "olap": {
        "tsql": os.path.join(HAMMERDB_DIR, "src", "mssqlserver", "mssqlsolap.tcl"),
        "plsql": os.path.join(HAMMERDB_DIR, "src", "oracle", "oraolap.tcl")
    },
    "oltp": {
        "tsql": os.path.join(HAMMERDB_DIR, "src", "mssqlserver", "mssqlsoltp.tcl"),
        "plsql": os.path.join(HAMMERDB_DIR, "src", "oracle", "oraoltp.tcl")
    }
    # You can add more here if you want to inspect them
}

def get_proc_names(filepath):
    """Finds all procedure names in a given TCL file."""
    proc_names = set()
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except FileNotFoundError:
        return None

    proc_pattern = re.compile(r"proc (\w+)")
    matches = proc_pattern.finditer(content)
    for match in matches:
        proc_names.add(match.group(1))
    return proc_names

def inspect_common_procedures():
    """Compares two files and prints the names of common procedures."""
    print("--- Inspecting for Common Procedures ---")
    
    for benchmark_name, files in BENCHMARK_PAIRS.items():
        print(f"\n--- Benchmark: {benchmark_name.upper()} ---")
        tsql_procs = get_proc_names(files["tsql"])
        plsql_procs = get_proc_names(files["plsql"])

        if tsql_procs is None or plsql_procs is None:
            print(" -> One or more files not found. Skipping.")
            continue
            
        common_procs = sorted(list(tsql_procs & plsql_procs))
        
        if common_procs:
            print(f" -> SUCCESS: Found {len(common_procs)} common procedure(s):")
            for proc in common_procs:
                print(f"    - {proc}")
        else:
            print(" -> INFO: Found 0 common procedures.")
            
if __name__ == "__main__":
    inspect_common_procedures()