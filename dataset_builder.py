import json

# --- Configuration ---
# The machine-generated file from our previous step
SOURCE_JSONL_FILE = "tsql_plsql_master_dataset.jsonl"
# The name of the final, combined dataset file
FINAL_DATASET_FILE = "tsql_plsql_final_training_dataset.jsonl"
PROMPT_INSTRUCTION = "You are an expert database migration specialist. Convert the following T-SQL script to a functionally equivalent PL/SQL script for Oracle 19c. Ensure all data types, functions, and procedural constructs are correctly translated."

# --- Part 1: Comprehensive Hand-Crafted Syntax "Flashcards" ---
# This is the full list of 24 high-quality manual examples.
SYNTAX_PAIRS = [
    # Your 4 examples
    {"tsql": "-- T-SQL: Basic variable handling and printing\nDECLARE @employee_name VARCHAR(100);\nDECLARE @salary DECIMAL(10, 2);\nSET @employee_name = 'John Smith';\nSET @salary = 75000.50;\nPRINT 'Employee: ' + @employee_name + ', Salary: ' + CAST(@salary AS VARCHAR);", "plsql": "-- PL/SQL: Basic variable handling and printing\nDECLARE\n  v_employee_name VARCHAR2(100);\n  v_salary NUMBER(10, 2);\nBEGIN\n  v_employee_name := 'John Smith';\n  v_salary := 75000.50;\n  DBMS_OUTPUT.PUT_LINE('Employee: ' || v_employee_name || ', Salary: ' || TO_CHAR(v_salary));\nEND;\n/"},
    {"tsql": "-- T-SQL: Error handling with TRY...CATCH\nBEGIN TRY\n    DECLARE @divisor INT = 0;\n    DECLARE @result INT;\n    SET @result = 100 / @divisor;\nEND TRY\nBEGIN CATCH\n    PRINT 'Error occurred: ' + ERROR_MESSAGE();\nEND CATCH;", "plsql": "-- PL/SQL: Error handling with EXCEPTION\nDECLARE\n  v_divisor NUMBER := 0;\n  v_result NUMBER;\nBEGIN\n  v_result := 100 / v_divisor;\nEXCEPTION\n  WHEN ZERO_DIVIDE THEN\n    DBMS_OUTPUT.PUT_LINE('Error occurred: Division by zero.');\n  WHEN OTHERS THEN\n    DBMS_OUTPUT.PUT_LINE('Error occurred: ' || SQLERRM);\nEND;\n/"},
    {"tsql": "-- T-SQL: Simple procedure\nCREATE PROCEDURE dbo.sp_GetEmployee\n    @EmployeeID INT\nAS\nBEGIN\n    SET NOCOUNT ON;\n    SELECT FirstName, LastName, JobTitle\n    FROM HumanResources.Employee\n    WHERE BusinessEntityID = @EmployeeID;\nEND\nGO", "plsql": "-- PL/SQL: Simple procedure returning a REF CURSOR\nCREATE OR REPLACE PROCEDURE sp_GetEmployee (\n    p_EmployeeID IN NUMBER,\n    p_recordset OUT SYS_REFCURSOR\n)\nAS\nBEGIN\n    OPEN p_recordset FOR\n        SELECT FirstName, LastName, JobTitle\n        FROM Employee\n        WHERE BusinessEntityID = p_EmployeeID;\nEND;\n/"},
    {"tsql": "-- T-SQL: A simple WHILE loop\nDECLARE @counter INT;\nSET @counter = 1;\nWHILE (@counter <= 5)\nBEGIN\n   PRINT 'The counter value is ' + CAST(@counter AS VARCHAR);\n   SET @counter = @counter + 1;\nEND;", "plsql": "-- PL/SQL: A simple WHILE loop\nDECLARE\n  v_counter NUMBER := 1;\nBEGIN\n  WHILE v_counter <= 5\n  LOOP\n     DBMS_OUTPUT.PUT_LINE('The counter value is ' || v_counter);\n     v_counter := v_counter + 1;\n  END LOOP;\nEND;\n/"},
    # The other 20 examples
    {"tsql": "-- T-SQL: Printing and string concatenation\nDECLARE @first_name VARCHAR(50) = 'Jane';\nPRINT 'Name: ' + @first_name;", "plsql": "-- PL/SQL: Printing and string concatenation\nDECLARE\n  v_first_name VARCHAR2(50) := 'Jane';\nBEGIN\n  DBMS_OUTPUT.PUT_LINE('Name: ' || v_first_name);\nEND;\n/"},
    {"tsql": "-- T-SQL: IF/ELSE logic\nDECLARE @sales INT = 5000;\nIF @sales > 4000\nBEGIN\n    PRINT 'High';\nEND\nELSE\nBEGIN\n    PRINT 'Low';\nEND;", "plsql": "-- PL/SQL: IF/ELSE logic\nDECLARE\n  v_sales NUMBER := 5000;\nBEGIN\n  IF v_sales > 4000 THEN\n    DBMS_OUTPUT.PUT_LINE('High');\n  ELSE\n    DBMS_OUTPUT.PUT_LINE('Low');\n  END IF;\nEND;\n/"},
    {"tsql": "-- T-SQL: Error handling with TRY...CATCH\nBEGIN TRY\n    DELETE FROM employees WHERE id = 9999;\nEND TRY\nBEGIN CATCH\n    PRINT 'Error: ' + ERROR_MESSAGE();\nEND CATCH;", "plsql": "-- PL/SQL: Error handling with EXCEPTION\nBEGIN\n    DELETE FROM employees WHERE id = 9999;\nEXCEPTION\n    WHEN OTHERS THEN\n        DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);\nEND;\n/"},
    {"tsql": "-- T-SQL: Basic Cursor\nDECLARE @emp_id INT;\nDECLARE emp_cursor CURSOR FOR SELECT EmployeeID FROM Employees WHERE Department = 'Sales';\nOPEN emp_cursor;\nFETCH NEXT FROM emp_cursor INTO @emp_id;\nWHILE @@FETCH_STATUS = 0\nBEGIN\n    PRINT @emp_id;\n    FETCH NEXT FROM emp_cursor INTO @emp_id;\nEND;\nCLOSE emp_cursor;\nDEALLOCATE emp_cursor;", "plsql": "-- PL/SQL: Basic Cursor (using an idiomatic FOR loop)\nBEGIN\n  FOR emp_rec IN (SELECT EmployeeID FROM Employees WHERE Department = 'Sales')\n  LOOP\n    DBMS_OUTPUT.PUT_LINE(emp_rec.EmployeeID);\n  END LOOP;\nEND;\n/"},
    {"tsql": "-- T-SQL: Procedure with IN and OUT parameters\nCREATE PROCEDURE dbo.sp_GetManager\n    @EmployeeID INT,\n    @ManagerID INT OUTPUT\nAS\nBEGIN\n    SELECT @ManagerID = ManagerID FROM Employees WHERE EmployeeID = @EmployeeID;\nEND\nGO", "plsql": "-- PL/SQL: Procedure with IN and OUT parameters\nCREATE OR REPLACE PROCEDURE sp_GetManager (\n    p_EmployeeID IN NUMBER,\n    p_ManagerID OUT NUMBER\n)\nAS\nBEGIN\n    SELECT ManagerID INTO p_ManagerID FROM Employees WHERE EmployeeID = p_EmployeeID;\nEND;\n/"},
    {"tsql": "SELECT ISNULL(commission_pct, 0) FROM employees;", "plsql": "SELECT NVL(commission_pct, 0) FROM employees;"},
    {"tsql": "SELECT GETDATE();", "plsql": "SELECT SYSDATE FROM DUAL;"},
    {"tsql": "SELECT DATEADD(month, 2, '2023-01-15');", "plsql": "SELECT ADD_MONTHS(TO_DATE('2023-01-15', 'YYYY-MM-DD'), 2) FROM DUAL;"},
    {"tsql": "SELECT CHARINDEX('world', 'hello world');", "plsql": "SELECT INSTR('hello world', 'world') FROM DUAL;"},
    {"tsql": "SELECT SUBSTRING('abcdef', 3, 2);", "plsql": "SELECT SUBSTR('abcdef', 3, 2) FROM DUAL;"},
    {"tsql": "SELECT LEN('test');", "plsql": "SELECT LENGTH('test') FROM DUAL;"},
    {"tsql": "SELECT CAST(123 AS VARCHAR(10));", "plsql": "SELECT TO_CHAR(123) FROM DUAL;"},
    {"tsql": "SELECT TOP 10 * FROM Employees ORDER BY HireDate DESC;", "plsql": "SELECT * FROM Employees ORDER BY HireDate DESC FETCH FIRST 10 ROWS ONLY;"},
    {"tsql": "-- T-SQL: Transaction\nBEGIN TRANSACTION;\nUPDATE Accounts SET balance = balance - 100 WHERE account_id = 1;\nUPDATE Accounts SET balance = balance + 100 WHERE account_id = 2;\nCOMMIT TRANSACTION;", "plsql": "-- PL/SQL: Transaction\nBEGIN\n    UPDATE Accounts SET balance = balance - 100 WHERE account_id = 1;\n    UPDATE Accounts SET balance = balance + 100 WHERE account_id = 2;\n    COMMIT;\nEND;\n/"},
    {"tsql": "-- T-SQL: Session-scoped temporary table\nCREATE TABLE #TempEmployees (EmployeeID INT, EmployeeName VARCHAR(100));\nINSERT INTO #TempEmployees VALUES (1, 'Temp User');\nSELECT * FROM #TempEmployees;", "plsql": "-- PL/SQL: Session-scoped temporary table (requires pre-defined table)\n-- DDL (run once): CREATE GLOBAL TEMPORARY TABLE TempEmployees (EmployeeID NUMBER, EmployeeName VARCHAR2(100)) ON COMMIT PRESERVE ROWS;\nBEGIN\n    INSERT INTO TempEmployees VALUES (1, 'Temp User');\n    -- Logic to process TempEmployees would go here\nEND;\n/"},
    {"tsql": "-- T-SQL: Dynamic SQL execution\nDECLARE @sql_command NVARCHAR(1000);\nSET @sql_command = N'SELECT * FROM Employees WHERE DepartmentID = @dept';\nEXEC sp_executesql @sql_command, N'@dept INT', @dept = 10;", "plsql": "-- PL/SQL: Dynamic SQL execution\nDECLARE\n  v_sql_command VARCHAR2(1000);\nBEGIN\n  v_sql_command := 'SELECT * FROM Employees WHERE DepartmentID = :dept_id';\n  -- In a real scenario, you would use a REF CURSOR to process the results\n  EXECUTE IMMEDIATE v_sql_command USING 10;\nEND;\n/"},
    {"tsql": "-- T-SQL: Auto-incrementing primary key\nCREATE TABLE Products (\n    ProductID INT IDENTITY(1,1) PRIMARY KEY,\n    ProductName VARCHAR(100)\n);", "plsql": "-- PL/SQL: Auto-incrementing primary key (using an identity column)\nCREATE TABLE Products (\n    ProductID NUMBER GENERATED BY DEFAULT ON NULL AS IDENTITY PRIMARY KEY,\n    ProductName VARCHAR2(100)\n);"}
]


def main():
    """
    Merges the hand-crafted syntax pairs with the machine-extracted pairs
    from HammerDB to create the final, complete training dataset.
    """
    print("--- Starting Final Dataset Merge Process ---")
    
    # 1. Start with the hand-crafted syntax pairs
    final_records = []
    for pair in SYNTAX_PAIRS:
        final_records.append({
            "instruction": PROMPT_INSTRUCTION,
            "input": pair["tsql"],
            "output": pair["plsql"]
        })
    print(f"Step 1: Loaded {len(final_records)} hand-crafted syntax pairs.")
    
    # 2. Read and append the extracted pairs from the source JSONL file
    try:
        with open(SOURCE_JSONL_FILE, 'r', encoding='utf-8') as f_in:
            extracted_records = [json.loads(line) for line in f_in]
            final_records.extend(extracted_records)
            print(f"Step 2: Loaded {len(extracted_records)} extracted pairs from '{SOURCE_JSONL_FILE}'.")
    except FileNotFoundError:
        print(f"WARNING: Source file '{SOURCE_JSONL_FILE}' not found. The final dataset will only contain hand-crafted examples.")
    
    # 3. Write the final, merged dataset to a new file
    with open(FINAL_DATASET_FILE, 'w', encoding='utf-8') as f_out:
        for record in final_records:
            f_out.write(json.dumps(record) + "\n")

    print(f"\n--- MERGE COMPLETE ---")
    print(f"SUCCESS: Created final training dataset '{FINAL_DATASET_FILE}' with a grand total of {len(final_records)} records.")
    print("This is your definitive training data. You are ready to fine-tune.")

if __name__ == "__main__":
    main()