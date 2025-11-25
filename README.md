# DR to Invoice Generator - Complete Guide

## 📋 System Overview

The **DR to Invoice Generator** is a complete end-to-end automation system that converts Delivery Request (DR) PDFs into Excel files, Tally XML, and invoices with an interactive prompt interface.

### Workflow:
```
Upload DR PDF → Extract Data → Edit Prompt → Generate Excel → Generate Tally XML → Create Invoice
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Windows/Mac/Linux
- Modern web browser (Chrome, Firefox, Edge)

### Installation & Setup

#### Step 1: Install Python Dependencies
```bash
pip install flask pandas openpyxl pdfplumber werkzeug
```

#### Step 2: Start the Application

**Option A: Using PowerShell (Recommended)**
```powershell
cd "C:\Users\abhin\OneDrive\Documents\Final_year"
python app.py
```

**Option B: Using Batch File**
```bash
start.bat
```

#### Step 3: Access the Web Interface
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📊 Step-by-Step Usage Guide

### **Step 1: Upload Delivery Request PDF**

1. **Click the Upload Area**
   - Click anywhere in the upload box or drag-drop your PDF
   - Supported format: `.pdf` only
   - Maximum file size: 50MB

2. **File Information**
   - The selected filename will appear below the upload box
   - Status message: "✅ PDF uploaded successfully!"

3. **Auto-Extraction**
   - The system automatically extracts:
     - DR Number
     - Part Number & Name
     - Order Number
     - Quantity
     - Box Type
     - Unit Size
     - Branch Information
     - Buyer Order Number

---

### **Step 2: Verify Extracted Details**

The system displays all extracted information in read-only fields:

**DR Information Section:**
- DR Number (e.g., 11559032)
- Today's Date (auto-filled)

**Part Details Section:**
- Part Name (e.g., ASSY. SUCTION PIPE - STEERING PUMP)
- Part Number (e.g., 1816A1810169)
- Order Number (e.g., 1210000691)
- Box Type (e.g., CHEP BOX)
- Unit Size (e.g., 10)

**Order Information Section:**
- Buyer's Order Number
- Quantity (e.g., 1)

**Action:** Review the details. Click "Next →" to proceed.

---

### **Step 3: Edit Prompt Details**

Edit the fields as per your requirements:

#### **Basic Information**
- **Vehicle Number** (Default: `TN13AH0050`)
  - Edit if the vehicle delivering this part is different
  - Format: License plate number

- **Party Code** (Auto-filled based on branch)
  - `TAFEMDU` = Madurai Operations
  - `TAFEDBR` = Bangalore / Doddaballapur
  - Read-only field

#### **Kanban Details**
- **No. of Pieces**
  - Number of individual items (default: same as Quantity)
  
- **No. of Packages**
  - Number of packages/containers (default: 1)
  
- **Total Nos**
  - Total count (default: 20)
  
- **Total Kgs**
  - Total weight - edit as needed

#### **Crate Details**
- **For Crate**
  - Format: `14403 - 1 NOS`
  - Crate part number and quantity
  
- **Lid**
  - Format: `13054 - 1 NOS`
  - Lid part number and quantity
  
- **DR Reference** (Auto-filled)
  - Example: `DR 11559032`
  - Read-only field

**Action:** Edit all required fields. Click "Next →" to save and proceed.

---

### **Step 4: Generate Output Files**

Three file generation options available:

#### **Option 1: Generate Excel File**
```
Button: 📊 Generate Excel File
```
- Creates an Excel spreadsheet with 16 columns
- Columns: DR No, Date, Buyers Order Number, Quantity, Vehicle Number, Party Name, Part No, Part Name, Order No, Box Type, Unit Size, No of Pieces, No of Packages, Total Nos, Total Kgs, Crate Details
- Auto-downloads to your computer
- Filename format: `DR_11559032_Invoice.xlsx`

#### **Option 2: Generate Tally XML**
```
Button: 📋 Generate Tally XML
```
- Creates XML file compatible with Tally accounting software
- Includes all voucher details
- XML structure contains:
  - Company information
  - Voucher type and dates
  - Party details
  - Item/ledger entries
  - Additional vehicle/crate details
- XML preview displayed in the interface
- Auto-downloads to your computer
- Filename format: `DR_11559032_Tally.xml`

#### **Option 3: Generate Invoice**
```
Button: 🧾 Generate Invoice
```
- Generates final invoice data
- Displays invoice summary with:
  - Invoice Number (e.g., `INV-11559032`)
  - DR Number
  - Date
  - Party Code
  - Vehicle
  - Part Details
  - Quantity
  - Status: Generated ✅

---

### **Step 5: Process Complete**

After generating the invoice:
- Success message displays
- Invoice summary shows all details
- **Option to Process Another DR**
  - Click "🔄 Process Another DR" to start over
  - All fields reset
  - Ready for next delivery request

---

## 🔧 Backend API Reference

### **POST /upload-dr**
Upload and extract DR PDF

**Request:**
```
Method: POST
Body: FormData with 'file' (PDF)
```

**Response:**
```json
{
  "success": true,
  "details": {
    "DR No": "11559032",
    "Buyer Order No": "1210000691",
    "Quantity": "1",
    "Branch": "Madurai Operations- K Patti Pl - 1000",
    "Part Name": "ASSY. SUCTION PIPE - STEERING PUMP",
    "Order No": "1210000691",
    "Part No": "1816A1810169",
    "Box Type": "CHEP BOX",
    "Unit Size": "10"
  }
}
```

### **GET /generate-prompt**
Generate prompt interface data

**Response:**
```json
{
  "success": true,
  "prompt": {
    "dr_no": "11559032",
    "today_date": "25-01-2025",
    "buyers_order_number": "1210000691",
    "quantity": "1",
    "vehicle_number": "TN13AH0050",
    "kanban": {
      "no_of_pieces": "1",
      "no_of_packages": "1",
      "total_nos": "20",
      "total_kgs": ""
    },
    "bill_details": {
      "party_name": "TAFEMDU"
    }
  }
}
```

### **POST /verify-prompt**
Save edited prompt data

**Request:**
```json
{
  "data": {
    "vehicle_number": "TN13AH0050",
    "kanban": {
      "total_kgs": "25.5"
    }
  }
}
```

### **POST /generate-excel**
Generate Excel file

**Response:** Excel file download

### **POST /generate-xml**
Generate Tally XML

**Response:** XML file download

### **POST /generate-invoice**
Generate invoice

**Response:**
```json
{
  "success": true,
  "invoice": {
    "invoice_number": "INV-11559032",
    "status": "Generated"
  }
}
```

---

## 📁 Project File Structure

```
Final_year/
├── app.py                    # Main Flask application
├── dr_pdf_to_excel.py        # PDF extraction utility
├── start.bat                 # Windows batch launcher
├── start.ps1                 # PowerShell launcher
├── templates/
│   └── index.html            # Web interface
├── uploads/                  # Temporary PDF uploads (auto-created)
└── README.md                 # This file
```

---

## 🔌 Tally Integration Guide

### Importing XML to Tally

#### **Method 1: Automatic Import**
1. Open Tally
2. Go to: **Gateway → Import → Data Import**
3. Select the generated XML file
4. Choose options and import
5. Verify invoice created

#### **Method 2: Manual Entry**
1. Open Tally
2. Create a new Voucher (Sales Order)
3. Enter details from the XML preview
4. Save

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "PDF uploaded but no data extracted" | Ensure PDF has proper table structure with columns: Order No, Part No, Part Name, Box Type, Qty, etc. |
| "Permission denied" error | Close Excel if file is open. The system cannot overwrite locked files. |
| "Branch not recognized" | System supports: Madurai, Bangalore, Doddaballapur. Check PDF for exact branch name. |
| "Port 5000 already in use" | Change port in app.py: `app.run(port=5001)` then access `http://127.0.0.1:5001` |
| Parts/Quantity not extracted | PDF structure may vary. Manually edit values in Step 3 if needed. |

---

## 📊 Data Mapping Reference

### **Branch to Party Code Mapping**
| Branch | Party Code | Full Name |
|--------|-----------|-----------|
| Madurai Operations | TAFEMDU | TAFE Madurai |
| Bangalore | TAFEDBR | TAFE Bangalore |
| Doddaballapur | TAFEDBR | TAFE Bangalore |

### **Default Values**
| Field | Default Value |
|-------|----------------|
| Vehicle Number | TN13AH0050 |
| No. of Packages | 1 |
| Total Nos | 20 |
| For Crate | 14403 - 1 NOS |
| Lid | 13054 - 1 NOS |

---

## ✅ Testing Checklist

- [ ] Application starts at `http://127.0.0.1:5000`
- [ ] Upload PDF from test folder
- [ ] All details extract correctly
- [ ] Can edit prompt fields
- [ ] Excel file downloads
- [ ] XML file downloads
- [ ] Invoice summary displays
- [ ] Process Another DR button resets form
- [ ] All branch types extract correctly
- [ ] Part names with newlines display correctly

---

## 🔐 Security Notes

- **File Upload:** Max 50MB
- **Temporary Files:** Auto-deleted after processing
- **Session Data:** Stored in server memory
- **No Database:** All data is session-based

---

**Created:** January 2025
**Status:** Production Ready
**License:** Internal Use Only
