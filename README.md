# CapIA.ai Backend Intern Assignment

## Overview

This project is a Python-based solution for normalizing CSV data with various delimiters and formats. The program reads CSV files, auto-detects delimiters, handles header and headerless files, and normalizes the data according to the target schema. It also includes dynamic column mapping for headerless files where the column order may vary.

## Architecture

- **Delimiter Detection:**  
  Uses Python’s `csv.Sniffer` to auto-detect the delimiter (comma, semicolon, pipe, etc.) from a sample of the file.

- **Data Normalization:**  
  - Converts headers to snake_case.
  - Normalizes the transaction date to a `datetime` object in the format `YYYY-MM-DD`.
  - Converts amount strings (handling both U.S. and European formats) to a `Decimal`.
  - Standardizes the status to lowercase.
  - Trims extra whitespace from text fields.

- **Dynamic Column Mapping (Bonus):**  
  For files without headers, the program infers column mapping dynamically by analyzing the content patterns (date, currency, status, amount, and description).

- **Error Handling:**  
  Implements error handling for mismatched columns and raises informative errors if required columns are missing.

## Results

Example output after running the code:

```
Processing file: test1.csv
{'transaction_date': '2024-01-15', 'description': 'Office Supplies', 'amount': '1234.56', 'currency': 'USD', 'status': 'completed'}
{'transaction_date': '2024-01-16', 'description': 'Software License', 'amount': '2500.00', 'currency': 'USD', 'status': 'pending'}
{'transaction_date': '2024-01-17', 'description': 'Lunch, Meeting', 'amount': '1750.50', 'currency': 'USD', 'status': 'completed'}

Processing file: test2.csv
{'transaction_date': '2024-01-15', 'description': 'Office Supplies', 'amount': '1234.56', 'currency': 'EUR', 'status': 'completed'}
{'transaction_date': '2024-01-16', 'description': 'Software License', 'amount': '2500.00', 'currency': 'EUR', 'status': 'pending'}
{'transaction_date': '2024-01-17', 'description': 'Lunch Meeting', 'amount': '1750.50', 'currency': 'EUR', 'status': 'completed'}

Processing file: test3.csv
{'transaction_date': '2024-01-15', 'description': 'Office Supplies', 'amount': '1234.56', 'currency': 'USD', 'status': 'completed'}
{'transaction_date': '2024-01-16', 'description': 'Software, License', 'amount': '2500.00', 'currency': 'USD', 'status': 'pending'}
{'transaction_date': '2024-01-17', 'description': 'Lunch Meeting', 'amount': '1750.50', 'currency': 'USD', 'status': 'completed'}

Processing file: no_header.csv
{'transaction_date': '2024-01-15', 'currency': 'USD', 'status': 'completed', 'amount': '1234.56', 'description': 'Office Supplies'}
{'transaction_date': '2024-01-16', 'currency': 'EUR', 'status': 'pending', 'amount': '2500.00', 'description': 'Software License'}
{'transaction_date': '2024-01-17', 'currency': 'USD', 'status': 'completed', 'amount': '1750.50', 'description': 'Lunch Meeting'}
```

## How to Use

1. **Place Input Files:**  
   Ensure the CSV files (`test1.csv`, `test2.csv`, `test3.csv`, and `no_header.csv`) are in the same directory as the Python script.

2. **Run the Program:**  
   Execute the Python script using:
   ```bash
   python main.py
   ```

3. **View Results:**  
   The normalized data will be printed to the console in a user-friendly format.
