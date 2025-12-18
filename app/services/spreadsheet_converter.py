import pandas as pd
import openpyxl
from openpyxl.workbook import Workbook
import csv
import json

def convert_spreadsheet(input_path, output_path, target_format):
    """Convert between spreadsheet formats (CSV, XLSX, XLS, JSON)"""
    try:
        # Determine input format
        input_ext = input_path.lower().split('.')[-1]
        
        # Read the file based on input format
        if input_ext == 'csv':
            df = pd.read_csv(input_path)
        elif input_ext in ['xlsx', 'xls']:
            df = pd.read_excel(input_path)
        elif input_ext == 'json':
            df = pd.read_json(input_path)
        else:
            raise ValueError(f"Unsupported input format: {input_ext}")
        
        # Convert to target format
        target_format = target_format.lower()
        
        if target_format == 'csv':
            df.to_csv(output_path, index=False)
        elif target_format == 'xlsx':
            df.to_excel(output_path, index=False, engine='openpyxl')
        elif target_format == 'xls':
            df.to_excel(output_path, index=False, engine='xlsxwriter')
        elif target_format == 'json':
            df.to_json(output_path, orient='records', indent=2)
        elif target_format == 'html':
            df.to_html(output_path, index=False)
        else:
            raise ValueError(f"Unsupported target format: {target_format}")
            
    except Exception as e:
        raise Exception(f"Spreadsheet conversion failed: {str(e)}")

def csv_to_excel(input_path, output_path):
    """Convert CSV to Excel with formatting"""
    try:
        df = pd.read_csv(input_path)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Data']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
                
    except Exception as e:
        raise Exception(f"CSV to Excel conversion failed: {str(e)}")

def excel_to_csv(input_path, output_path, sheet_name=None):
    """Convert Excel to CSV"""
    try:
        if sheet_name:
            df = pd.read_excel(input_path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(input_path)
        
        df.to_csv(output_path, index=False)
        
    except Exception as e:
        raise Exception(f"Excel to CSV conversion failed: {str(e)}")