# data_processing.py
import pandas as pd
import io
import base64

def process_file(file_path, file_type):
    """
    Processes the uploaded file based on its type.
    """
    try:
        df = pd.read_excel(file_path, skiprows=5)

        if file_type == "file1":
            df = df.rename(columns={})
            df = df.drop(columns=['Sl.no', 'Clear Time'], errors='ignore')
            # additional data cleaning code...
        elif file_type == "file2":
            # Clean file2 specific data
            pass
        else:
            raise ValueError("Invalid file type specified.")
        return df
    except Exception as e:
        print(f"Error processing file: {e}")
        return pd.DataFrame()

def decode_file(contents):
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        return io.BytesIO(decoded)
    except Exception as e:
        raise ValueError(f"Error decoding file: {e}")
