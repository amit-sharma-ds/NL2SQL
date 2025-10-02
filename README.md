# NL2SQL CLI

![](https://blog.cogxta.com/wp-content/uploads/2025/03/nl-to-sql.png)

A Python CLI tool that uses NLP and regex to convert natural language queries into SQL-like operations on CSV datasets. Users can ask questions in plain English, such as totals, averages, filtering, and ordering, and get results instantly. It works dynamically with any CSV file, providing fast, tabular output while supporting ordinal queries like “second highest marks.”

## Features

- Natural language queries without SQL knowledge.  
- Aggregation: totals, averages, counts, min/max.  
- Filtering and conditional queries.  
- Ordering and ranking of results.  
- Works with any structured CSV file.  
- Clean tabular output.  
- Handles ordinal queries like “nth highest/lowest.”  
- Lightweight and fast using in-memory SQLite.  

## Tech Stack / Libraries

- **Python 3.x** – Core language for the CLI tool  
- **SQLite (sqlite3)** – In-memory database for SQL-like operations on CSV  
- **Regex (re)** – Parsing and interpreting natural language queries  
- **CSV module (csv)** – Reading and processing CSV files  
- **Tabulate** – Formatting output in a clean, readable table  
- **sys** – Handling command-line arguments  
- **Natural Language Processing (basic NLP techniques)** – Converting plain English queries into SQL  
- **Command-Line Interface (CLI)** – For running the tool directly in the terminal
