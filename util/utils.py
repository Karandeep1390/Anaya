import logging
import pandas as pd
from typing import Dict, Any, Optional, List
from config.config import LOG_FILE_PATH, CUSTOMER_DATA_PATH
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def load_customer_data(customer_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Load customer data from CSV file with proper validation and cleaning.

    Args:
        customer_id: Optional customer ID to filter data

    Returns:
        Dict containing cleaned customer data

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If customer_id is not found or data is invalid
        Exception: For other data loading errors
    """
    try:
        # Check if file exists
        if not os.path.exists(CUSTOMER_DATA_PATH):
            raise FileNotFoundError(f"Customer data file not found at {CUSTOMER_DATA_PATH}")

        # Read CSV file with error handling
        try:
            df = pd.read_csv(CUSTOMER_DATA_PATH, encoding='utf-8')
            logger.info(f"Successfully loaded CSV file with {len(df)} rows")
        except pd.errors.EmptyDataError:
            raise ValueError("Customer data file is empty")
        except UnicodeDecodeError:
            # Try with different encoding if UTF-8 fails
            try:
                df = pd.read_csv(CUSTOMER_DATA_PATH, encoding='latin-1')
                logger.info(f"Successfully loaded CSV file with latin-1 encoding, {len(df)} rows")
            except Exception as e:
                raise ValueError(f"Error reading CSV file with multiple encodings: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")

        # Validate dataframe
        if df.empty:
            raise ValueError("Customer data file contains no data")

        # Clean column names (remove extra spaces, convert to lowercase)
        df.columns = df.columns.str.strip().str.lower()

        # Log column information for debugging
        logger.info(f"Available columns: {list(df.columns)}")

        # Check if customer_id column exists
        if 'customer_id' not in df.columns:
            raise ValueError("'customer_id' column not found in the data file")

        if customer_id:
            # Convert customer_id to string for consistent comparison
            customer_id = str(customer_id).strip()
            df['customer_id'] = df['customer_id'].astype(str).str.strip()

            customer_data = df[df['customer_id'] == customer_id]
            if customer_data.empty:
                available_ids = df['customer_id'].unique()[:5]
                raise ValueError(
                    f"Customer ID '{customer_id}' not found. "
                    f"Available IDs (first 5): {list(available_ids)}"
                )

            result = customer_data.iloc[0].to_dict()
            cleaned_result = _clean_customer_data(result)
            logger.info(f"Successfully loaded data for customer: {cleaned_result}")
            return cleaned_result

        # For demo purposes, return first customer
        result = df.iloc[0].to_dict()
        cleaned_result = _clean_customer_data(result)
        logger.info("Successfully loaded default customer data")
        return cleaned_result

    except FileNotFoundError:
        logger.error(f"Customer data file not found at {CUSTOMER_DATA_PATH}")
        raise
    except ValueError as e:
        logger.error(f"Data validation error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading customer data: {str(e)}")
        raise Exception(f"Failed to load customer data: {str(e)}")


def _clean_customer_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean customer data by handling NaN values and ensuring proper data types.

    Args:
        data: Raw customer data dictionary

    Returns:
        Cleaned customer data dictionary
    """
    cleaned_data = {}

    # Define expected data types and defaults
    numeric_fields = {
        'loan_offer': 0.0,
        'emi_amount': 0.0,
        'processing_fee': 0.0,
        'foreclosure_charges': 0.0,
        'interest_rate': 0.0,
        'minimumTenure': 0,
        'maximumTenure': 0,
        'apr': 0.0
    }

    string_fields = {
        'name': '',
        'customer_id': '',
        'offer_expiry': '',
        'purpose': '',
        'application_link': ''
    }

    for key, value in data.items():
        # Handle pandas NaN values
        if pd.isna(value) or value is None:
            if key in numeric_fields:
                cleaned_data[key] = numeric_fields[key]
            elif key in string_fields:
                cleaned_data[key] = string_fields[key]
            else:
                cleaned_data[key] = ''
        else:
            # Convert numpy types to native Python types
            if hasattr(value, 'item'):  # numpy scalar
                cleaned_data[key] = value.item()
            elif key in numeric_fields:
                # Ensure numeric fields are properly typed
                try:
                    if key == 'tenure':
                        cleaned_data[key] = int(float(value))
                    else:
                        cleaned_data[key] = float(value)
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert {key}={value} to number, using default")
                    cleaned_data[key] = numeric_fields[key]
            elif key in string_fields:
                # Ensure string fields are properly typed
                cleaned_data[key] = str(value).strip()
            else:
                cleaned_data[key] = value

    # Log the cleaned data for debugging
    logger.info(f"Cleaned customer data: {cleaned_data}")
    return cleaned_data


def format_currency(amount: float) -> str:
    """
    Format amount as Indian currency with proper error handling.

    Args:
        amount: Numeric amount to format

    Returns:
        Formatted currency string
    """
    try:
        # Handle None or NaN values
        if pd.isna(amount) or amount is None:
            return "₹0.00"

        # Convert to float if it's not already
        amount = float(amount)

        # Format with Indian currency symbol
        return f"₹{amount:,.2f}"

    except (ValueError, TypeError) as e:
        logger.warning(f"Error formatting currency for amount {amount}: {e}")
        return "₹0.00"


def format_percentage(value: float) -> str:
    """
    Format value as percentage with proper error handling.

    Args:
        value: Numeric value to format as percentage

    Returns:
        Formatted percentage string
    """
    try:
        # Handle None or NaN values
        if pd.isna(value) or value is None:
            return "0.0%"

        # Convert to float if it's not already
        value = float(value)

        # Format as percentage
        return f"{value:.1f}%"

    except (ValueError, TypeError) as e:
        logger.warning(f"Error formatting percentage for value {value}: {e}")
        return "0.0%"


def get_all_customer_ids() -> List[str]:
    """
    Get list of all available customer IDs.

    Returns:
        List of customer IDs

    Raises:
        Exception: If unable to load customer data
    """
    try:
        if not os.path.exists(CUSTOMER_DATA_PATH):
            raise FileNotFoundError(f"Customer data file not found at {CUSTOMER_DATA_PATH}")

        df = pd.read_csv(CUSTOMER_DATA_PATH, encoding='utf-8')

        # Clean column names
        df.columns = df.columns.str.strip().str.lower()

        if 'customer_id' not in df.columns:
            raise ValueError("'customer_id' column not found in the data file")

        customer_ids = df['customer_id'].astype(str).str.strip().unique().tolist()
        logger.info(f"Found {len(customer_ids)} unique customer IDs")
        return customer_ids

    except UnicodeDecodeError:
        # Try with different encoding
        try:
            df = pd.read_csv(CUSTOMER_DATA_PATH, encoding='latin-1')
            df.columns = df.columns.str.strip().str.lower()
            customer_ids = df['customer_id'].astype(str).str.strip().unique().tolist()
            logger.info(f"Found {len(customer_ids)} unique customer IDs (latin-1 encoding)")
            return customer_ids
        except Exception as e:
            logger.error(f"Error getting customer IDs with multiple encodings: {str(e)}")
            raise
    except Exception as e:
        logger.error(f"Error getting customer IDs: {str(e)}")
        raise


def validate_customer_exists(customer_id: str) -> bool:
    """
    Check if a customer ID exists in the data.

    Args:
        customer_id: Customer ID to validate

    Returns:
        True if customer exists, False otherwise
    """
    try:
        if not os.path.exists(CUSTOMER_DATA_PATH):
            return False

        df = pd.read_csv(CUSTOMER_DATA_PATH, encoding='utf-8')

        # Clean column names
        df.columns = df.columns.str.strip().str.lower()

        if 'customer_id' not in df.columns:
            return False

        customer_id = str(customer_id).strip()
        df['customer_id'] = df['customer_id'].astype(str).str.strip()

        exists = customer_id in df['customer_id'].values
        logger.debug(f"Customer {customer_id} exists: {exists}")
        return exists

    except UnicodeDecodeError:
        # Try with different encoding
        try:
            df = pd.read_csv(CUSTOMER_DATA_PATH, encoding='latin-1')
            df.columns = df.columns.str.strip().str.lower()
            customer_id = str(customer_id).strip()
            df['customer_id'] = df['customer_id'].astype(str).str.strip()
            exists = customer_id in df['customer_id'].values
            logger.debug(f"Customer {customer_id} exists: {exists} (latin-1 encoding)")
            return exists
        except Exception as e:
            logger.error(f"Error validating customer {customer_id} with multiple encodings: {str(e)}")
            return False
    except Exception as e:
        logger.error(f"Error validating customer {customer_id}: {str(e)}")
        return False


def validate_csv_structure(file_path: str = None) -> Dict[str, Any]:
    """
    Validate the structure of the CSV file and return information about it.

    Args:
        file_path: Path to CSV file (defaults to CUSTOMER_DATA_PATH)

    Returns:
        Dictionary with validation results
    """
    if file_path is None:
        file_path = CUSTOMER_DATA_PATH

    validation_result = {
        'valid': False,
        'errors': [],
        'warnings': [],
        'info': {}
    }

    try:
        if not os.path.exists(file_path):
            validation_result['errors'].append(f"File not found: {file_path}")
            return validation_result

        # Try to read with UTF-8 first
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin-1')
            validation_result['warnings'].append("File read with latin-1 encoding instead of UTF-8")

        # Clean column names
        df.columns = df.columns.str.strip().str.lower()

        # Basic info
        validation_result['info']['total_rows'] = len(df)
        validation_result['info']['total_columns'] = len(df.columns)
        validation_result['info']['columns'] = list(df.columns)

        # Check for required columns
        required_columns = ['customer_id', 'name', 'loan_offer', 'interest_rate']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            validation_result['errors'].append(f"Missing required columns: {missing_columns}")

        # Check for empty data
        if df.empty:
            validation_result['errors'].append("CSV file is empty")

        # Check for duplicate customer IDs
        if 'customer_id' in df.columns:
            duplicates = df['customer_id'].duplicated().sum()
            if duplicates > 0:
                validation_result['warnings'].append(f"Found {duplicates} duplicate customer IDs")

        # Check for missing values in critical columns
        for col in ['customer_id', 'name']:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                if missing_count > 0:
                    validation_result['warnings'].append(f"Column '{col}' has {missing_count} missing values")

        # Check for inconsistent data types in numeric columns
        numeric_columns = ['loan_offer', 'interest_rate', 'tenure', 'emi_amount', 'processing_fee',
                           'foreclosure_charges']
        for col in numeric_columns:
            if col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='coerce')
                except Exception:
                    validation_result['warnings'].append(f"Column '{col}' contains non-numeric values")

        validation_result['valid'] = len(validation_result['errors']) == 0

    except Exception as e:
        validation_result['errors'].append(f"Error reading CSV file: {str(e)}")

    return validation_result


def create_sample_csv(file_path: str = "sample_customer_data.csv") -> None:
    """
    Create a sample CSV file with customer data.

    Args:
        file_path: Path where the sample CSV file will be created
    """
    sample_data = [
        {
            'customer_id': 'CUST001',
            'name': 'John Doe',
            'loan_offer': 500000,
            'interest_rate': 10.5,
            'tenure': 24,
            'emi_amount': 23000,
            'processing_fee': 2500,
            'foreclosure_charges': 1000,
            'offer_expiry': '2024-12-31',
            'purpose': 'Home Renovation',
            'application_link': 'https://example.com/apply/CUST001'
        },
        {
            'customer_id': 'CUST002',
            'name': 'Jane Smith',
            'loan_offer': 750000,
            'interest_rate': 9.8,
            'tenure': 36,
            'emi_amount': 24500,
            'processing_fee': 3750,
            'foreclosure_charges': 1500,
            'offer_expiry': '2024-11-30',
            'purpose': 'Business Expansion',
            'application_link': 'https://example.com/apply/CUST002'
        },
        {
            'customer_id': 'CUST003',
            'name': 'Rajesh Kumar',
            'loan_offer': 1000000,
            'interest_rate': 11.2,
            'tenure': 48,
            'emi_amount': 26800,
            'processing_fee': 5000,
            'foreclosure_charges': 2000,
            'offer_expiry': '2025-01-15',
            'purpose': 'Education',
            'application_link': 'https://example.com/apply/CUST003'
        },
        {
            'customer_id': 'CUST004',
            'name': 'Priya Sharma',
            'loan_offer': 300000,
            'interest_rate': 12.5,
            'tenure': 18,
            'emi_amount': 18500,
            'processing_fee': 1500,
            'foreclosure_charges': 750,
            'offer_expiry': '2024-10-31',
            'purpose': 'Personal',
            'application_link': 'https://example.com/apply/CUST004'
        },
        {
            'customer_id': 'CUST005',
            'name': 'Mohammed Ali',
            'loan_offer': 850000,
            'interest_rate': 10.0,
            'tenure': 30,
            'emi_amount': 31200,
            'processing_fee': 4250,
            'foreclosure_charges': 1700,
            'offer_expiry': '2025-02-28',
            'purpose': 'Vehicle Purchase',
            'application_link': 'https://example.com/apply/CUST005'
        }
    ]

    try:
        df = pd.DataFrame(sample_data)
        df.to_csv(file_path, index=False, encoding='utf-8')
        print(f"Sample CSV file created successfully at: {file_path}")
        print(f"File contains {len(sample_data)} sample customer records")

        # Display the sample data
        print("\nSample data preview:")
        print(df.to_string(index=False))

    except Exception as e:
        print(f"Error creating sample CSV file: {str(e)}")


# Example usage and testing