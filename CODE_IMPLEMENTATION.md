# CODE IMPLEMENTATION GUIDE

## 📝 Complete Source Code Breakdown

### **File 1: app.py (Flask Backend)**

**Purpose:** Main Flask application serving the web interface and handling all API endpoints

**Key Sections:**

#### **Imports & Setup (Lines 1-15)**
```python
from flask import Flask, render_template, request, send_file, jsonify, session
import os, re, pdfplumber, pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename
from io import BytesIO, StringIO
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

app = Flask(__name__)
app.secret_key = 'dr_invoice_app_secret_2025'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
os.makedirs('uploads', exist_ok=True)
```

**What it does:**
- Imports Flask web framework components
- Imports PDF, Excel, XML processing libraries
- Sets up Flask app with security token
- Creates uploads folder for temporary PDFs

#### **Configuration (Lines 16-30)**
```python
BRANCH_MAPPING = {
    'Madurai': {'code': 'TAFEMDU', 'name': 'TAFE Madurai'},
    'Doddaballapur': {'code': 'TAFEDBR', 'name': 'TAFE Bangalore'},
    'Bangalore': {'code': 'TAFEDBR', 'name': 'TAFE Bangalore'}
}

CRATE_DETAILS_TEMPLATE = {
    'FOR CRATE': '14403',
    'FOR CRATE_NOS': '1',
    'LID': '13054',
    'LID_NOS': '1'
}
```

**What it does:**
- Maps branch names to party codes for Tally
- Defines default crate template values

#### **PDF Extraction Function (Lines 31-90)**
```python
def extract_dr_details(pdf_path):
    """Extract DR details from PDF"""
    details = {
        'DR No': '',
        'Buyer Order No': '',
        'Quantity': '',
        'Branch': '',
        'Part Name': '',
        'Order No': '',
        'Part No': '',
        'Box Type': '',
        'Unit Size': ''
    }
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]
            tables = page.extract_tables()
            
            # Extract header info (DR Number, Branch)
            for row in main_table[:7]:
                row_text = " ".join([str(c) for c in (row or []) if c])
                
                # Extract DR Number
                m = re.search(r"Delivery\s*Request\s*No\.?\s*[:\-]?\s*(\d{5,12})", row_text, re.I)
                if m:
                    details['DR No'] = m.group(1).strip()
                
                # Extract Branch (supports multiple formats)
                m = re.search(r"Request\s*[:\-]?\s*([A-Za-z\-\s]+(?:Operations|Plant|Pl)[A-Za-z0-9\s\-]*)", row_text, re.I)
                if m:
                    details['Branch'] = m.group(1).strip()
            
            # Extract table data (Order No, Part No, etc.)
            header_row_idx = -1
            for i, row in enumerate(main_table):
                row_text = " ".join([str(c) for c in (row or []) if c]).upper()
                if "ORDER NO" in row_text and "PART NO" in row_text:
                    header_row_idx = i
                    break
            
            if header_row_idx >= 0:
                row = main_table[header_row_idx + 1]
                if row:
                    # Map columns to fields
                    details['Order No'] = str(row[0]).strip() if row[0] else ""
                    details['Buyer Order No'] = details['Order No']
                    details['Part No'] = str(row[1]).strip() if row[1] else ""
                    # Remove newlines from part names
                    details['Part Name'] = str(row[2]).strip().replace('\n', ' ') if row[2] else ""
                    details['Box Type'] = str(row[3]).strip() if row[3] else ""
                    details['Quantity'] = str(row[4]).strip() if row[4] else ""
                    details['Unit Size'] = str(row[9]).strip() if len(row) > 9 and row[9] else ""
        
        return details
    
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None
```

**What it does:**
- Opens PDF using pdfplumber
- Extracts DR number using regex
- Finds and extracts branch name (handles Madurai, Bangalore, Doddaballapur)
- Locates table with part details
- Maps table columns to field names
- Cleans data (removes newlines, strips whitespace)
- Returns dictionary with all extracted fields

**Key Features:**
- Flexible regex for branch extraction
- Automatic newline cleanup for part names
- Error handling with try-except

#### **POST /upload-dr Endpoint (Lines 92-130)**
```python
@app.route('/upload-dr', methods=['POST'])
def upload_dr():
    """Upload DR PDF and extract details"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Please upload a PDF file'}), 400
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract DR details
        details = extract_dr_details(filepath)
        
        if not details:
            os.remove(filepath)
            return jsonify({'error': 'Could not extract DR data from PDF'}), 400
        
        # Store in session for later use
        session['dr_details'] = details
        session['pdf_filename'] = filename
        
        # Delete temporary file
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'details': details
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**What it does:**
- Receives PDF file upload from browser
- Validates file is PDF
- Saves to temporary folder
- Extracts details using extract_dr_details()
- Stores details in Flask session
- Deletes temporary file
- Returns JSON with extracted data to browser

**Security:** Uses secure_filename() to prevent path traversal attacks

#### **GET /generate-prompt Endpoint (Lines 132-178)**
```python
@app.route('/generate-prompt', methods=['GET'])
def generate_prompt():
    """Generate the prompt interface data"""
    try:
        # Get extracted DR details from session
        dr_details = session.get('dr_details', {})
        
        if not dr_details:
            return jsonify({'error': 'No DR details found'}), 400
        
        # Determine party code from branch
        branch = dr_details.get('Branch', '')
        branch_code = 'TAFEMDU'  # Default
        
        for branch_name, mapping in BRANCH_MAPPING.items():
            if branch_name.lower() in branch.lower():
                branch_code = mapping['code']
                break
        
        # Get quantity for kanban
        quantity = dr_details.get('Quantity', '')
        
        # Build prompt data with defaults
        prompt_data = {
            'dr_no': dr_details.get('DR No', ''),
            'today_date': datetime.now().strftime('%d-%m-%Y'),
            'buyers_order_number': dr_details.get('Buyer Order No', ''),
            'quantity': quantity,
            'vehicle_number': 'TN13AH0050',  # Default vehicle
            'kanban': {
                'no_of_pieces': quantity,
                'no_of_packages': '1',
                'total_nos': '20',
                'total_kgs': ''  # User will edit
            },
            'bill_details': {
                'party_name': branch_code
            },
            'crate_details': {
                'for_crate': f"{CRATE_DETAILS_TEMPLATE['FOR CRATE']} - {CRATE_DETAILS_TEMPLATE['FOR CRATE_NOS']} NOS",
                'lid': f"{CRATE_DETAILS_TEMPLATE['LID']} - {CRATE_DETAILS_TEMPLATE['LID_NOS']} NOS",
                'dr_reference': f"DR {dr_details.get('DR No', '')}"
            },
            'part_details': {
                'part_no': dr_details.get('Part No', ''),
                'part_name': dr_details.get('Part Name', ''),
                'order_no': dr_details.get('Order No', ''),
                'box_type': dr_details.get('Box Type', ''),
                'unit_size': dr_details.get('Unit Size', '')
            }
        }
        
        # Store in session for later use
        session['prompt_data'] = prompt_data
        
        return jsonify({
            'success': True,
            'prompt': prompt_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**What it does:**
- Retrieves DR details from session
- Maps branch to party code (TAFEMDU or TAFEDBR)
- Creates prompt_data dictionary with:
  - Extracted fields
  - Default values (vehicle, kanban, crate)
  - Today's date
- Stores in session
- Returns JSON to browser for display in form

#### **POST /generate-excel Endpoint (Lines 297-333)**
```python
@app.route('/generate-excel', methods=['POST'])
def generate_excel():
    """Generate Excel from verified prompt data"""
    try:
        prompt_data = session.get('prompt_data')
        dr_details = session.get('dr_details')
        
        if not prompt_data or not dr_details:
            return jsonify({'error': 'No data found'}), 400
        
        # Create dictionary for Excel rows
        data = {
            'DR No': [prompt_data['dr_no']],
            'Date': [prompt_data['today_date']],
            'Buyers Order Number': [prompt_data['buyers_order_number']],
            'Quantity': [prompt_data['quantity']],
            'Vehicle Number': [prompt_data['vehicle_number']],
            'Party Name': [prompt_data['bill_details']['party_name']],
            'Part No': [dr_details.get('Part No', '')],
            'Part Name': [dr_details.get('Part Name', '')],
            'Order No': [dr_details.get('Order No', '')],
            'Box Type': [dr_details.get('Box Type', '')],
            'Unit Size': [dr_details.get('Unit Size', '')],
            'No of Pieces': [prompt_data['kanban']['no_of_pieces']],
            'No of Packages': [prompt_data['kanban']['no_of_packages']],
            'Total Nos': [prompt_data['kanban']['total_nos']],
            'Total Kgs': [prompt_data['kanban']['total_kgs']],
            'Crate Details': [f"{prompt_data['crate_details']['for_crate']}; {prompt_data['crate_details']['lid']}"]
        }
        
        # Create DataFrame and export to Excel
        df = pd.DataFrame(data)
        
        output = BytesIO()
        df.to_excel(output, index=False, sheet_name='DR Invoice', engine='openpyxl')
        output.seek(0)
        
        # Store for later reference
        session['excel_data'] = data
        
        # Return Excel file for download
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"DR_{prompt_data['dr_no']}_Invoice.xlsx"
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**What it does:**
- Gets prompt_data and dr_details from session
- Creates dictionary with 16 columns
- Converts to pandas DataFrame
- Exports DataFrame to Excel using openpyxl
- Returns Excel file as downloadable attachment
- Filename: DR_XXXXX_Invoice.xlsx

#### **POST /generate-xml Endpoint (Lines 335-387)**
```python
@app.route('/generate-xml', methods=['POST'])
def generate_xml():
    """Generate Tally XML from prompt data"""
    try:
        prompt_data = session.get('prompt_data')
        dr_details = session.get('dr_details')
        
        if not prompt_data or not dr_details:
            return jsonify({'error': 'No data found'}), 400
        
        # Create XML structure
        root = ET.Element('ENVELOPE')
        root.set('xmlns:UDF', 'TallyUDF')
        
        # Company info
        company = ET.SubElement(root, 'COMPANY')
        ET.SubElement(company, 'NAME').text = 'TAFE Motors'
        ET.SubElement(company, 'MNAME').text = 'TAFE Motors'
        
        # Voucher details
        voucher = ET.SubElement(root, 'VOUCHER')
        ET.SubElement(voucher, 'VOUCHERNUMBER').text = f"INV-{prompt_data['dr_no']}"
        ET.SubElement(voucher, 'VOUCHERTYPE').text = 'Sales'
        ET.SubElement(voucher, 'DATE').text = datetime.now().strftime('%d-%m-%Y')
        ET.SubElement(voucher, 'REFERENCENUMBER').text = f"DR-{prompt_data['dr_no']}"
        
        # Party details
        party = ET.SubElement(voucher, 'PARTYDETAILS')
        ET.SubElement(party, 'PARTYNAME').text = prompt_data['bill_details']['party_name']
        ET.SubElement(party, 'BUYERORDERNUMBER').text = prompt_data['buyers_order_number']
        
        # Line items
        ledgers = ET.SubElement(voucher, 'LEDGERENTRIES')
        item = ET.SubElement(ledgers, 'ITEM')
        ET.SubElement(item, 'ITEMNAME').text = dr_details.get('Part Name', '')
        ET.SubElement(item, 'ITEMNO').text = dr_details.get('Part No', '')
        ET.SubElement(item, 'QUANTITY').text = str(prompt_data['quantity'])
        ET.SubElement(item, 'RATE').text = prompt_data['kanban'].get('total_kgs', '0')
        ET.SubElement(item, 'AMOUNT').text = '0'
        
        # Additional details (vehicle, crate, kanban)
        additional = ET.SubElement(voucher, 'ADDITIONALDETAILS')
        ET.SubElement(additional, 'VEHICLENUMBER').text = prompt_data['vehicle_number']
        ET.SubElement(additional, 'CRATEDETAILS').text = prompt_data['crate_details']['dr_reference']
        ET.SubElement(additional, 'NOOFPIECES').text = str(prompt_data['kanban']['no_of_pieces'])
        ET.SubElement(additional, 'NOOFPACKAGES').text = str(prompt_data['kanban']['no_of_packages'])
        
        # Pretty print XML
        xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent='  ')
        xml_string = '\n'.join([line for line in xml_string.split('\n') if line.strip()])
        
        # Store and return
        session['xml_data'] = xml_string
        
        output = BytesIO(xml_string.encode('utf-8'))
        
        return send_file(
            output,
            mimetype='application/xml',
            as_attachment=True,
            download_name=f"DR_{prompt_data['dr_no']}_Tally.xml"
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

**What it does:**
- Creates XML ElementTree structure
- Builds ENVELOPE → COMPANY → VOUCHER hierarchy
- Adds party details, items, additional fields
- Pretty-prints XML for readability
- Returns XML file for download

---

### **File 2: templates/index.html (Frontend UI)**

**Purpose:** Interactive 5-step web interface with form inputs and file downloads

**Key Sections:**

#### **Step 1: Upload PDF**
- Drag-drop upload area
- File input with validation
- Progress messages

#### **Step 2: Verify Extracted Data**
- Read-only fields displaying extracted values
- DR number, part details, order info
- No editing allowed

#### **Step 3: Edit Prompt**
- Editable fields for vehicle, kanban, crate details
- Auto-populated defaults
- Real-time validation

#### **Step 4: Generate Files**
- Three buttons: Excel, XML, Invoice
- XML preview display
- Download management

#### **Step 5: Complete**
- Success summary
- Invoice details
- Process another DR option

**JavaScript Functions:**

```javascript
// Upload handling
uploadPDF() → Sends PDF to /upload-dr
generatePrompt() → Calls /generate-prompt
savePrompt() → Calls /verify-prompt
generateExcel() → Calls /generate-excel
generateXML() → Calls /generate-xml
generateInvoice() → Calls /generate-invoice

// Navigation
nextStep() → Move to next step with validation
previousStep() → Go back one step
updateUI() → Refresh display
resetForm() → Clear all and restart
```

---

## 🔄 DATA FLOW DIAGRAM

```
┌──────────────────┐
│  User Browser    │
│  index.html      │
└────────┬─────────┘
         │
         ├─→ [Upload PDF File]
         │    ↓ (FormData)
         │    
         ├─→ POST /upload-dr
         │    └─→ extract_dr_details(pdf)
         │        └─→ Returns: dr_details dict
         │    └─→ Store in session['dr_details']
         │    └─→ Return JSON to browser
         │
         ├─→ [Step 2: Display extracted data]
         │
         ├─→ GET /generate-prompt
         │    └─→ Build prompt_data with defaults
         │    └─→ Store in session['prompt_data']
         │    └─→ Return JSON to browser
         │
         ├─→ [Step 3: User edits fields]
         │
         ├─→ POST /verify-prompt
         │    └─→ Update session['prompt_data']
         │
         ├─→ [Step 4: Choose output format]
         │
         ├─→ POST /generate-excel
         │    ├─→ Create pandas DataFrame
         │    ├─→ Export to XLSX
         │    └─→ Download: DR_XXXXX_Invoice.xlsx
         │
         ├─→ POST /generate-xml
         │    ├─→ Create ElementTree XML
         │    ├─→ Build Tally structure
         │    ├─→ Display preview
         │    └─→ Download: DR_XXXXX_Tally.xml
         │
         ├─→ POST /generate-invoice
         │    ├─→ Create invoice data object
         │    └─→ Return JSON summary
         │
         └─→ [Step 5: Complete + Download]
```

---

## 🔧 CONFIGURATION GUIDE

### **Customize Branch Mapping**
Edit `app.py` around line 25:
```python
BRANCH_MAPPING = {
    'Madurai': {'code': 'TAFEMDU', 'name': 'TAFE Madurai'},
    'YourBranch': {'code': 'YOUR_CODE', 'name': 'Branch Name'},
}
```

### **Change Default Vehicle**
Edit `app.py` line ~155:
```python
'vehicle_number': 'TN13AH0050'  # Change this
```

### **Change Port**
Edit `app.py` last line:
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # Change 5000 to 5001
```

### **Change Crate Defaults**
Edit `app.py` around line 33:
```python
CRATE_DETAILS_TEMPLATE = {
    'FOR CRATE': '14403',  # Change this
    'LID': '13054',        # Change this
}
```

### **Add New Extract Fields**
Edit `extract_dr_details()` function in `app.py`:
```python
details['NEW_FIELD'] = str(row[10]).strip() if row[10] else ""
```

---

## 📊 API CONTRACTS

### **POST /upload-dr**
```
Request: FormData { file: PDF }
Response: {
  "success": true,
  "details": {
    "DR No": "11559032",
    "Part Name": "...",
    ...
  }
}
```

### **GET /generate-prompt**
```
Request: None (uses session)
Response: {
  "success": true,
  "prompt": {
    "dr_no": "11559032",
    "vehicle_number": "TN13AH0050",
    ...
  }
}
```

### **POST /verify-prompt**
```
Request: JSON { data: {...} }
Response: {
  "success": true,
  "message": "Prompt data verified..."
}
```

### **POST /generate-excel**
```
Request: None (uses session)
Response: Binary XLSX file
```

---

## 🐛 DEBUGGING TIPS

### **Enable Debug Logging**
Add to `app.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In functions:
logger.debug(f"Extracted: {details}")
```

### **Check Session Data**
Add route:
```python
@app.route('/debug/session')
def debug_session():
    return jsonify(dict(session))
```

### **Test PDF Extraction**
Create `test_pdf.py`:
```python
from app import extract_dr_details
result = extract_dr_details('test.pdf')
print(result)
```

---

## ✅ CODE QUALITY CHECKLIST

- [x] Error handling in all functions
- [x] Input validation for file uploads
- [x] Session storage for data persistence
- [x] Proper MIME types for downloads
- [x] Security: secure_filename() used
- [x] Resource cleanup: temp files deleted
- [x] Clear function documentation
- [x] Consistent naming conventions
- [x] Try-except blocks for robustness

---

**Code Version:** 1.0 | **Updated:** January 2025 | **Status:** Production Ready
