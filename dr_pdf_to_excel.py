#!/usr/bin/env python3
"""
dr_pdf_to_excel.py
Robust PDF -> Excel extractor for TAFE Delivery Requests.

Usage:
  python dr_pdf_to_excel.py input_pdf output_xlsx

Notes:
- Tries: 1) pdfplumber table extraction, 2) pdfplumber text + regex, 3) OCR (pytesseract)
- Produces Excel with columns:
  DR No, Order No, Part No, Part Name, Qty, Unit Size, Box Type, Branch, Buyer Order No, Vehicle No, Kanban, Crate Details
"""

import sys, re
import pdfplumber
import pandas as pd
from PIL import Image
import numpy as np
import cv2
import pytesseract

def try_tables(pdf_path):
    """Extract table data from PDF and return parsed items"""
    rows = []
    header_info = {}
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                if not tables:
                    continue
                
                main_table = tables[0] if tables else []
                
                if not main_table:
                    continue
                
                # Extract header info from the table metadata rows
                for row in main_table[:7]:
                    row_text = " ".join([str(c) for c in (row or []) if c])
                    
                    # Extract DR No
                    m = re.search(r"Delivery\s*Request\s*No\.?\s*[:\-]?\s*(\d{5,12})", row_text, re.I)
                    if m:
                        header_info['DR No'] = m.group(1).strip()
                    
                    # Extract Branch/Request - now supports Operations, Plant, Pl patterns
                    m = re.search(r"Request\s*[:\-]?\s*([A-Za-z\-\s]+(?:Operations|Plant|Pl)[A-Za-z0-9\s\-]*)", row_text, re.I)
                    if m:
                        header_info['Branch'] = m.group(1).strip()
                
                # Data rows start after the header row
                header_row_idx = -1
                for i, row in enumerate(main_table):
                    row_text = " ".join([str(c) for c in (row or []) if c]).upper()
                    if "ORDER NO" in row_text and "PART NO" in row_text:
                        header_row_idx = i
                        break
                
                # Parse data rows
                if header_row_idx >= 0:
                    for row in main_table[header_row_idx+1:]:
                        if not row or all(not cell for cell in row):
                            continue
                        
                        row_str = " ".join([str(c) for c in (row or []) if c]).strip()
                        if not row_str or len(row_str) < 10:
                            continue
                        
                        if any(skip in row_str.lower() for skip in ['note:', 'delivery', '......']):
                            continue
                        
                        try:
                            order_no = str(row[0]).strip() if row[0] else ""
                            part_no = str(row[1]).strip() if row[1] else ""
                            # Clean up part names - remove newlines
                            part_name = str(row[2]).strip().replace('\n', ' ').replace('\r', '') if row[2] else ""
                            box_type = str(row[3]).strip() if row[3] else ""
                            qty_request = str(row[4]).strip() if row[4] else ""
                            unit_size = str(row[9]).strip() if len(row) > 9 and row[9] else ""
                            kanban = str(row[4]).strip() if row[4] else ""
                            
                            if order_no and part_no:
                                rows.append({
                                    "Order No": order_no,
                                    "Part No": part_no,
                                    "Part Name": part_name,
                                    "Box Type": box_type,
                                    "Qty": qty_request,
                                    "Unit Size": unit_size,
                                    "Kanban": kanban
                                })
                        except (IndexError, ValueError):
                            continue
    
    except Exception as e:
        print(f"Table extraction error: {e}")
    
    return header_info, rows

def text_from_pdf(pdf_path):
    txt = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text() or ""
                txt += "\n" + t
    except Exception as e:
        txt = ""
    return txt

def ocr_pdf(pdf_path):
    txt = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                img = page.to_image(resolution=300).original.convert("RGB")
                arr = np.array(img)
                gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
                blur = cv2.medianBlur(gray, 3)
                _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                pil = Image.fromarray(th)
                page_text = pytesseract.image_to_string(pil, lang='eng')
                txt += "\n" + page_text
    except Exception as e:
        txt = ""
    return txt

def parse_from_text(full_text):
    header = {}
    items = []

    text = full_text.replace('\r','\n')

    # DR No
    m = re.search(r"Delivery\s*Request\s*No\.?\s*[:\-]?\s*(\d{5,12})", text, re.I)
    if m:
        header['DR No'] = m.group(1).strip()

    # Branch / Request - now supports Operations, Plant, Pl patterns
    m = re.search(r"Request\s*[:\-]?\s*([A-Za-z\-\s]+(?:Operations|Plant|Pl)[A-Za-z0-9\s\-]*)", text, re.I)
    if m:
        header['Branch'] = m.group(1).strip()
    else:
        header['Branch'] = ""

    lines = text.splitlines()
    
    table_start_idx = -1
    for i, ln in enumerate(lines):
        if re.search(r"Order\s*No|Part\s*No", ln, re.I):
            table_start_idx = i
            break
    
    if table_start_idx >= 0:
        for ln in lines[table_start_idx+1:]:
            ln = ln.strip()
            if not ln or len(ln) < 5:
                continue
            
            if any(skip in ln.lower() for skip in ['note:', 'delivery', 'request', 'bin', 'unit', 'supplier', 'shipping', 'departure']):
                continue
            if re.search(r'^\.+$', ln):
                continue
            
            order_match = re.search(r'\b(\d{10})\b', ln)
            part_match = re.search(r'\b([A-Z0-9]{4,20}M\d{1,3})\b', ln)
            
            if order_match and part_match:
                order_no = order_match.group(1)
                part_no = part_match.group(1)
                
                part_name_match = re.search(part_no + r'\s+([A-Z0-9\.\s\-/&()]+?)\s+(PP BOX|CHEP BOX|BOX|BIN|[A-Z]+\s+BOX)', ln, re.I)
                part_name = part_name_match.group(1).strip().replace('\n', ' ') if part_name_match else ""
                
                box_match = re.search(r'(PP BOX|CHEP BOX|BOX|BIN|[A-Z]+\s+BOX)', ln, re.I)
                box_type = box_match.group(1).strip() if box_match else ""
                
                numbers = re.findall(r'\b(\d+)\b', ln)
                
                qty = ""
                unit_size = ""
                kanban = ""
                
                if len(numbers) >= 5:
                    qty = numbers[2] if len(numbers) > 2 else ""
                    unit_size = numbers[-2] if len(numbers) >= 2 else ""
                    kanban = numbers[-1] if len(numbers) >= 1 else ""
                
                item = {
                    "Order No": order_no,
                    "Part No": part_no,
                    "Part Name": part_name,
                    "Box Type": box_type,
                    "Qty": qty,
                    "Unit Size": unit_size,
                    "Kanban": kanban
                }
                items.append(item)
    
    if not items:
        pattern = re.compile(r"(\d{10})\s+([A-Z0-9\-]{5,20})\s+([A-Z0-9\.\- /&()]+?)\s+(PP BOX|CHEP BOX|BOX|BIN)\s+(\d+)", re.I)
        for m in pattern.finditer(text):
            items.append({
                "Order No": m.group(1).strip(),
                "Part No": m.group(2).strip(),
                "Part Name": m.group(3).strip().replace('\n', ' '),
                "Box Type": m.group(4).strip(),
                "Qty": m.group(5).strip(),
                "Unit Size": "",
                "Kanban": ""
            })

    header.setdefault('Buyer Order No', items[0].get('Order No', '') if items else '')
    header.setdefault('Vehicle No', '')
    header.setdefault('Crate Details', '')

    return header, items

def make_dataframe(header, items):
    rows = []
    if items:
        for it in items:
            row = {
                "DR No": header.get("DR No",""),
                "Order No": it.get("Order No",""),
                "Part No": it.get("Part No",""),
                "Part Name": it.get("Part Name",""),
                "Qty": it.get("Qty",""),
                "Unit Size": it.get("Unit Size",""),
                "Box Type": it.get("Box Type",""),
                "Branch": header.get("Branch",""),
                "Buyer Order No": header.get("Buyer Order No",""),
                "Vehicle No": header.get("Vehicle No",""),
                "Kanban": it.get("Kanban",""),
                "Crate Details": header.get("Crate Details","")
            }
            rows.append(row)
    else:
        rows.append({
            "DR No": header.get("DR No",""),
            "Order No": header.get("Buyer Order No",""),
            "Part No": "",
            "Part Name": "",
            "Qty": "",
            "Unit Size": "",
            "Box Type": "",
            "Branch": header.get("Branch",""),
            "Buyer Order No": header.get("Buyer Order No",""),
            "Vehicle No": header.get("Vehicle No",""),
            "Kanban": "",
            "Crate Details": header.get("Crate Details","")
        })
    df = pd.DataFrame(rows, columns=[
        "DR No","Order No","Part No","Part Name","Qty","Unit Size","Box Type",
        "Branch","Buyer Order No","Vehicle No","Kanban","Crate Details"
    ])
    return df

def main(pdf_path, out_xlsx):
    print("Attempting table extraction...")
    header_info, table_rows = try_tables(pdf_path)
    
    if table_rows:
        header = {
            'DR No': header_info.get('DR No', ''),
            'Branch': header_info.get('Branch', ''),
            'Buyer Order No': table_rows[0].get('Order No', '') if table_rows else '',
            'Vehicle No': '',
            'Crate Details': ''
        }
        df = make_dataframe(header, table_rows)
        try:
            df.to_excel(out_xlsx, index=False, engine='openpyxl')
            print(f"Saved {len(df)} rows from table extraction to {out_xlsx}")
        except PermissionError:
            print(f"ERROR: Cannot write to {out_xlsx}. File may be open in Excel. Please close it and try again.")
            sys.exit(1)
        return

    print("No useful tables found — trying text extraction...")
    t = text_from_pdf(pdf_path)
    if len(t.strip()) < 100:
        print("Text extraction returned little text — falling back to OCR...")
        t = ocr_pdf(pdf_path)

    if len(t.strip()) < 50:
        print("ERROR: Could not extract readable text from PDF. Please try a scanned-high-res PDF or enable better scan quality.")
        df = pd.DataFrame([{
            "DR No":"", "Order No":"", "Part No":"", "Part Name":"", "Qty":"", "Unit Size":"",
            "Box Type":"", "Branch":"", "Buyer Order No":"", "Vehicle No":"", "Kanban":"", "Crate Details":""
        }])
        try:
            df.to_excel(out_xlsx, index=False, engine='openpyxl')
            print("Saved blank template to help manual fill:", out_xlsx)
        except PermissionError:
            print(f"ERROR: Cannot write to {out_xlsx}. File may be open in Excel. Please close it and try again.")
            sys.exit(1)
        return

    header, items = parse_from_text(t)
    df = make_dataframe(header, items)
    try:
        df.to_excel(out_xlsx, index=False, engine='openpyxl')
        print(f"Saved {len(df)} rows to {out_xlsx}")
    except PermissionError:
        print(f"ERROR: Cannot write to {out_xlsx}. File may be open in Excel. Please close it and try again.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python dr_pdf_to_excel.py input.pdf output.xlsx")
        sys.exit(1)
    pdf_path = sys.argv[1]
    out_xlsx = sys.argv[2]
    main(pdf_path, out_xlsx)
