
# **T-SQL to PL/SQL Automated Conversion: Project Charter and Implementation Plan**

## **Executive Summary**

This document outlines a strategic initiative to automate the migration of database logic from Microsoft SQL Server (T-SQL) to Oracle Database 19c (PL/SQL). The core problem is the significant manual effort, cost, and risk of error associated with translating thousands of scripts between these two syntactically and functionally different platforms.

After thorough exploratory research into available resources like the HammerDB benchmarking tool and SQLines documentation, we have designed a forward-thinking solution. Instead of relying on brittle, rule-based tools or costly manual conversion, we will build a custom, AI-driven conversion engine.

The proposed solution involves fine-tuning an open-source Large Language Model (LLM) like Code Llama on a curated dataset of paired T-SQL and PL/SQL scripts. This engine will be hosted locally to ensure data security and will be integrated into an automated pipeline for efficient, overnight batch processing. A rigorous validation and feedback loop will ensure the engine's accuracy improves over time, transforming it into a valuable, long-term asset.

This approach was chosen for its superior scalability, cost-effectiveness, security, and its ability to be customized to our specific needs. The go-forward plan is detailed in this document, beginning with the immediate task of constructing the foundational training dataset.

## **1. Project Motivation and Objective**

The primary objective of this project is to create an efficient, scalable, and secure system to **automate the conversion of T-SQL scripts to functionally equivalent PL/SQL scripts compatible with Oracle 19c.**

This initiative aims to:
*   **Drastically Reduce Manual Effort:** Eliminate the time-consuming and error-prone task of manually rewriting thousands of stored procedures, functions, and triggers.
*   **Increase Migration Velocity:** Enable the rapid migration of large-scale database applications from SQL Server to Oracle.
*   **Ensure Functional Equivalence:** Maintain the integrity and logic of the original database code in the new Oracle environment.
*   **Enhance Security:** Process all database scripts, which may contain sensitive business logic, in a secure, on-premises environment without reliance on third-party cloud services.
*   **Create a Cost-Effective Solution:** Leverage open-source technology to avoid expensive commercial migration tools and licensing fees.

## **2. Background and Problem Statement**

Migrating from SQL Server to Oracle involves more than just moving data; it requires a complete translation of the procedural code that defines business logic. T-SQL (for SQL Server) and PL/SQL (for Oracle) are both procedural extensions to SQL, but they have fundamental differences that make direct conversion impossible.

Key differences include:

| Feature | Microsoft SQL Server (T-SQL) | Oracle Database 19c (PL/SQL) |
| :--- | :--- | :--- |
| **Variable Declaration** | `DECLARE @varname datatype;` | `varname datatype;` (in a DECLARE block) |
| **Variable Assignment**| `SET @varname = 'value';` | `varname := 'value';` |
| **String Concatenation**| `+` operator | `||` operator |
| **System Date/Time** | `GETDATE()` | `SYSDATE` or `SYSTIMESTAMP` |
| **Error Handling** | `BEGIN TRY...END TRY BEGIN CATCH...END CATCH` | `BEGIN...EXCEPTION WHEN...THEN...END;` |
| **Output to Console**| `PRINT 'message';` | `DBMS_OUTPUT.PUT_LINE('message');` |
| **Returning Result Sets**| A simple `SELECT` statement in a procedure. | Requires an `OUT SYS_REFCURSOR` parameter. |
| **Script Delimiter** | `GO` | `/` |

These differences necessitate a sophisticated translation mechanism that understands the context and intent of the code, rather than performing a simple find-and-replace.

## **3. Exploratory Research and Key Findings**

To build a robust training dataset for our AI model, we investigated several open-source and public resources. This research confirmed the feasibility of creating a high-quality dataset.

*   **Source 1: HammerDB (TPC-H Benchmark)**
    *   **What it is:** An open-source database load testing and benchmarking tool.
    *   **Finding:** HammerDB contains scripts for the TPC-H benchmark queries, pre-written for multiple database dialects, including T-SQL and Oracle. This provides a foundational set of **22 complex, functionally equivalent query pairs.** These are ideal for teaching the AI model the core differences in SQL syntax for data retrieval operations (joins, subqueries, aggregations).

*   **Source 2: SQLines Documentation**
    *   **What it is:** An open-source database migration tool and documentation resource.
    *   **Finding:** The SQLines SQL Server to Oracle migration guide contains extensive examples of one-to-one syntax mappings for procedural logic, data types, and built-in functions. These examples are perfect for creating a set of **small, targeted training snippets** to teach the model fundamental grammatical rules that are absent in the TPC-H queries.

*   **Source 3: AdventureWorks Sample Database**
    *   **What it is:** Microsoft's well-known sample database for SQL Server, which has also been ported to Oracle by the community.
    *   **Finding:** The T-SQL version of AdventureWorks contains hundreds of real-world stored procedures. While the Oracle port primarily focuses on schema and data, the T-SQL procedures serve as excellent source material. By **manually converting a select few of these complex procedures to PL/SQL**, we can create high-value training examples that show the model how to assemble syntax and query logic into complete, functional programs.

**Conclusion of Research:** By combining these three sources, we can construct a powerful, multi-layered dataset that covers a wide spectrum of conversion challenges, from basic syntax to complex procedural logic.

## **4. The Proposed Solution: An AI-Driven Conversion Engine**

We will build an intelligent conversion system based on four pillars: an Engine, Fuel, a Factory, and Quality Control.

#### **Pillar 1: The Engine (The AI Converter)**
This is a locally-hosted, fine-tuned Large Language Model (LLM).
*   **Core Technology:** An open-source code model such as **Code Llama (13B or 34B parameter version)**.
*   **Execution Platform:** **Ollama**, a tool that simplifies running LLMs on local hardware and provides a ready-to-use API.
*   **Key Process:** We will perform **fine-tuning** using a framework like Axolotl. This adapts the general-purpose model, making it a specialist in T-SQL to PL/SQL translation, significantly improving its accuracy over a base model.

#### **Pillar 2: The Fuel (The Curated Training Dataset)**
This is the `tsql_plsql_dataset.jsonl` file we will construct. It will contain hundreds of high-quality T-SQL/PL/SQL pairs, structured as follows:
1.  **Complex Queries:** From HammerDB TPC-H.
2.  **Syntax Snippets:** Manually created based on SQLines documentation to teach procedural fundamentals.
3.  **Full Procedures:** Manually converted from AdventureWorks to demonstrate real-world structure and patterns like returning result sets via `SYS_REFCURSOR`.

#### **Pillar 3: The Factory (The Automation Pipeline)**
This is a Python script that orchestrates the entire batch conversion process:
1.  **Input:** Scans a directory for T-SQL (`.sql`) files.
2.  **Process:** For each file, it constructs a detailed prompt, sends it to the fine-tuned model's local API, and receives the PL/SQL output.
3.  **Output:** Saves the generated PL/SQL code to a separate directory.
4.  **Logging:** Records the success or failure of each conversion for later review.
This pipeline is designed to run non-interactively, such as in an overnight cron job.

#### **Pillar 4: The Quality Control (Validation & Feedback Loop)**
This ensures the output is reliable and the system improves over time.
1.  **Syntax Validation:** An automated script will attempt to compile every generated PL/SQL file against a test Oracle 19c database, immediately flagging any syntax errors.
2.  **Functional Validation:** For a key subset of scripts, manual tests will be run to confirm the business logic is preserved.
3.  **Feedback Loop:** This is the self-improvement mechanism. When a systemic error is found, we will:
    *   Create a new, perfect T-SQL/PL/SQL pair demonstrating the correct conversion.
    *   Add this pair to our dataset.
    *   Re-run the fine-tuning process to create a smarter version of the model.

## **5. Justification for the Proposed Solution**

This AI-driven approach was chosen over alternatives like manual conversion or off-the-shelf commercial tools for several strategic reasons:

*   **Security & Confidentiality:** By hosting the model and processing all scripts locally, we ensure that sensitive business logic never leaves our on-premises environment.
*   **Cost-Effectiveness:** The solution is built entirely on open-source software, eliminating licensing costs associated with commercial migration suites. The primary investment is in development time and local hardware.
*   **Scalability & Efficiency:** The automated pipeline can process hundreds or thousands of scripts in a single batch run, a task that would take months of manual labor.
*   **Customizability & Future-Proofing:** The fine-tuning process allows us to tailor the engine to our specific coding standards and T-SQL patterns. The resulting model is a strategic asset that can be further improved and reused for future projects. It is not a "black box" solution; we have full control over its behavior.

## **6. Actionable Go-Forward Plan**

The project will be executed in four distinct phases.

#### **Phase 1: Foundation & Dataset Curation**
*   **Task 1:** Set up the project workspace, including directories and cloning required Git repositories (HammerDB, AdventureWorks, etc.).
*   **Task 2:** Execute scripts to automatically pair and extract the 22 TPC-H queries from HammerDB.
*   **Task 3:** Manually create 15-20 targeted syntax snippets for loops, error handling, cursors, and variables.
*   **Task 4:** Manually convert 3-5 representative stored procedures from AdventureWorks to high-quality PL/SQL.
*   **Task 5:** Run the formatting script to consolidate all pairs into the final `tsql_plsql_dataset.jsonl` file.
*   **Deliverable:** A complete, formatted dataset ready for fine-tuning.

#### **Phase 2: Engine Fine-Tuning & Pipeline Development**
*   **Task 1:** Set up the technical environment (Python, CUDA, Ollama, Axolotl).
*   **Task 2:** Perform the fine-tuning process on the dataset to create our specialized model.
*   **Task 3:** Develop and test the Python-based automation pipeline script.
*   **Deliverable:** A fine-tuned AI model and a functional batch processing script.

#### **Phase 3: Validation, Iteration, and Refinement**
*   **Task 1:** Develop the automated syntax validation script using SQL*Plus.
*   **Task 2:** Run the entire pipeline on a large batch of T-SQL scripts and analyze the results.
*   **Task 3:** Identify patterns of failure, update the dataset with corrective examples, and re-tune the model (the feedback loop).
*   **Deliverable:** A validation report and a v1.1 refined model with a documented accuracy score.

#### **Phase 4: Deployment and Operationalization**
*   **Task 1:** Deploy the finalized pipeline and model to a production server.
*   **Task 2:** Schedule the script to run as a nightly batch process.
*   **Task 3:** Finalize documentation for running the system and handling manual reviews for failed scripts.
*   **Deliverable:** A fully operational, automated T-SQL to PL/SQL conversion system.


*   **Usability:** The system requires minimal manual intervention, with clear logging for any scripts that fail conversion and require manual review.
*   **Functional Equivalence:** For a tested subset of 20 critical procedures, the converted PL/SQL code produces functionally identical results to the original T-SQL.
