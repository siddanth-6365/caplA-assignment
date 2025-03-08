import csv
import re
from datetime import datetime
from decimal import Decimal
import os

def snake_case(s: str) -> str:
    """
    convert a string to snake_case
    """
    parts = s.split('_')
    snake_parts = []
    for part in parts:
        new_part = re.sub(r'(?<!^)(?=[A-Z])', '_', part).lower()
        snake_parts.append(new_part)
        
    return re.sub(r'_+', '_', '_'.join(snake_parts))

def convert_amount(amount_str: str) -> Decimal:
    """
    Convert an amount string with possible thousand separators and currency symbols to a Decimal.
    
    handles two cases:
    - U.S style: "1,234.56" where comma is thousand separator and dot is decimal.
    - European style: "1.234,56" where dot is thousand separator and comma is decimal.
    """
    # remove any currency symbols like "$"
    amount_str = amount_str.replace('$', '').strip()

    # If both comma and dot exist, decide based on which appears last
    if ',' in amount_str and '.' in amount_str:
        if amount_str.rfind(',') > amount_str.rfind('.'):
            # European style
            amount_str = amount_str.replace('.', '')
            amount_str = amount_str.replace(',', '.')
        else:
            # U.S. style
            amount_str = amount_str.replace(',', '')
    elif ',' in amount_str:
        # Only comma exists
        if len(amount_str) > 3 and amount_str[-3] == ',':
            # Likely European style decimal separator
            amount_str = amount_str.replace(',', '.')
        else:
            # Otherwise, treat comma as thousand separator
            amount_str = amount_str.replace(',', '')
    # If only dot exists, assume it is the decimal separator.
    try:
        return Decimal(amount_str)
    except Exception as e:
        raise ValueError(f"Could not convert amount '{amount_str}': {e}")

def detect_delimiter(sample: str) -> str:
    """
    Using csv.Sniffer to detect the delimiter from a file
    """
    try:
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter
    except Exception:
        # Fallback to comma
        return ','

def infer_column_mapping(row: list) -> dict:
    """
    dynamically infer the mapping from column index to expected column names, based on analyzing the content
    
    Expected columns:
      - transaction_date: date in format YYYY-MM-DD
      - amount: numeric string with thousand separators (e.g., "1,234.56" or "1.234,56")
      - currency: 3-letter code (e.g, USD, EUR)
      - status: a word like "completed", "pending", "failed" or "cancelled"
      - description: free text (fallback)
    """
    mapping = {}
    used = set()
    
    # Helper checks:
    def is_date(val):
        return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', val.strip()))
    
    def is_currency(val):
        val = val.strip()
        return bool(re.match(r'^[A-Za-z]{3}$', val))
    
    def is_status(val):
        return val.strip().lower() in {"completed", "pending", "failed", "cancelled"}
    
    def is_amount(val):
        try:
            _ = convert_amount(val)
            return True
        except Exception:
            return False

    # First pass: check for clear patterns (date, currency, status)
    for i, value in enumerate(row):
        trimmed = value.strip()
        if is_date(trimmed) and 'transaction_date' not in used:
            mapping[i] = 'transaction_date'
            used.add('transaction_date')
        elif is_currency(trimmed) and 'currency' not in used:
            mapping[i] = 'currency'
            used.add('currency')
        elif is_status(trimmed) and 'status' not in used:
            mapping[i] = 'status'
            used.add('status')
    
    # Second pass: try to detect amount for remaining columns
    for i, value in enumerate(row):
        if i in mapping:
            continue
        if is_amount(value) and 'amount' not in used:
            mapping[i] = 'amount'
            used.add('amount')
    
    # Finally, assign any remaining column as description.
    for i, value in enumerate(row):
        if i not in mapping:
            if 'description' not in used:
                mapping[i] = 'description'
                used.add('description')
            else:
                # If extra unmapped columns exist, mark them as unknown.
                mapping[i] = 'unknown'
    
    # Verify that all required columns are found.
    required = {'transaction_date', 'description', 'amount', 'currency', 'status'}
    if not required.issubset(used):
        missing = required - used
        raise ValueError("Could not infer columns for: " + ", ".join(missing))
    
    return mapping

def normalize_row(row_dict: dict) -> dict:
    """
    Normalize a row dictionary using the defined rules:
      - Convert transaction_date to a datetime object.
      - Convert amount to Decimal.
      - Standardize status to lowercase.
      - Trim whitespace for other fields.
    """
    normalized = {}
    for key, value in row_dict.items():
        value = value.strip()
        if key == "transaction_date":
            try:
                normalized[key] = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                normalized[key] = datetime.fromisoformat(value)
        elif key == "amount":
            normalized[key] = convert_amount(value)
        elif key == "status":
            normalized[key] = value.lower()
        else:
            normalized[key] = value
    return normalized

def process_csv(file_path: str, has_header: bool = True, column_mapping: dict = None) -> list:
    """
    Process and normalize CSV files

    For files : 
    - with headers: the headers are normalized to snake_case
    - headerless files: the column mapping is inferred dynamically
    
    Returns:
      A list of normalized row dictionaries.
    """
    normalized_data = []
    with open(file_path, newline='', encoding='utf-8') as f:
        sample = f.read(1024)
        f.seek(0)
        delimiter = detect_delimiter(sample)
        reader = csv.reader(f, delimiter=delimiter)
        
        if has_header:
            headers = next(reader)
            headers = [snake_case(header) for header in headers]
        else:
            # Read the first row and infer column mapping if not provided.
            first_row = next(reader)
            if column_mapping is None:
                mapping = infer_column_mapping(first_row)
            else:
                mapping = column_mapping
            # Create headers preserving original order.
            headers = [mapping[i] for i in range(len(first_row))]
            # Process the first row as data.
            normalized_data.append(normalize_row(dict(zip(headers, first_row))))
        
        for row in reader:
            if not row:  # Skip empty rows
                continue
            if len(row) != len(headers):
                print(f"Warning: Mismatched number of columns in row: {row}")
                continue
            row_dict = dict(zip(headers, row))
            normalized_data.append(normalize_row(row_dict))
    return normalized_data

def print_normalized_data(data: list):
    """
    Helper function to print normalized data in a readable format.
    """
    for row in data:
        print(row)


def print_readable_data(data: list):
    """
    Print normalized data in a user-friendly format.
    """
    for row in data:
        formatted_row = row.copy()
        if isinstance(formatted_row.get("transaction_date"), datetime):
            formatted_row["transaction_date"] = formatted_row["transaction_date"].strftime('%Y-%m-%d')
        if isinstance(formatted_row.get("amount"), Decimal):
            formatted_row["amount"] = f"{formatted_row['amount']:.2f}"
        print(formatted_row)


if __name__ == "__main__":
    test_files = [
        {"file": "test1.csv", "has_header": True},
        {"file": "test2.csv", "has_header": True},
        {"file": "test3.csv", "has_header": True},
        {"file": "no_header.csv", "has_header": False}
    ]
    
    for test in test_files:
        file_name = test["file"]
        has_header = test["has_header"]
        if not os.path.exists(file_name):
            print(f"File '{file_name}' not found. Skipping...")
            continue
        print(f"\nProcessing file: {file_name}")
        try:
            # for headerless files, dynamically detect the mapping
            data = process_csv(file_name, has_header=has_header)
            print_readable_data(data)
        except Exception as e:
            print(f"An error occurred while processing {file_name}: {e}")
