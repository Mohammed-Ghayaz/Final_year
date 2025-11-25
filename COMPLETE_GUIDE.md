# COMPLETE STEP-BY-STEP GUIDE: DR to Invoice Generator

## 🎯 Overall System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           WEB BROWSER (http://127.0.0.1:5000)              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Step 1: Upload PDF  →  Step 2: Verify  →  Step 3: Edit │  │
│  │                                                           │  │
│  │  Step 4: Generate Files  →  Step 5: Complete            │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────┐
│              FLASK APPLICATION SERVER (app.py)              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  /upload-dr         - Extract PDF data               │  │
│  │  /generate-prompt   - Prepare editable interface     │  │
│  │  /verify-prompt     - Save edited data               │  │
│  │  /generate-excel    - Create Excel file              │  │
│  │  /generate-xml      - Create Tally XML               │  │
│  │  /generate-invoice  - Final invoice data             │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────┐
│           PDF PROCESSING LAYER (pdfplumber)                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  - Extract tables from PDF                            │  │
│  │  - Parse DR number, branch, part details             │  │
│  │  - Clean and format extracted data                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────────┐
│         OUTPUT GENERATION LAYER                             │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │  Excel Gen.  │  XML Gen.    │  Invoice JSON Gen.       │ │
│  │  (openpyxl)  │  (ElementTree)│  (Session Storage)      │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 DETAILED STEP-BY-STEP PROCEDURE

### **STEP 1: START THE APPLICATION**

#### **1.1 Prerequisites Check**
```bash
# Verify Python is installed
python --version
# Expected output: Python 3.8.x or higher

# Verify required packages
pip list | findstr "Flask pandas openpyxl pdfplumber"
# Expected: All packages listed
```

#### **1.2 Start Server - Method A (PowerShell)**
```powershell
cd "C:\Users\abhin\OneDrive\Documents\Final_year"
python app.py
```

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

#### **1.3 Start Server - Method B (Batch File)**
```cmd
Double-click: start.bat
```

#### **1.4 Start Server - Method C (PowerShell Script)**
```powershell
Right-click start.ps1 → Run with PowerShell
```

---

### **STEP 2: OPEN WEB INTERFACE**

#### **2.1 Access Application**
1. **Open Web Browser** (Chrome, Firefox, Edge)
2. **Navigate to:** `http://127.0.0.1:5000`
3. **You should see:** DR to Invoice Generator interface

#### **2.2 Verify UI Elements**
- ✓ Header: "📦 DR to Invoice Generator"
- ✓ Subtitle: "Delivery Request → Excel → XML → Tally → Invoice"
- ✓ Step Indicator: Shows 5 steps (1 through 5)
- ✓ Progress Bar: Shows progress (0% at start)
- ✓ Upload Area: Large dashed box for PDF

---

### **STEP 3: UPLOAD DELIVERY REQUEST PDF**

#### **3.1 Prepare PDF File**
- **Required format:** `.pdf` (PDF document)
- **Expected content:** Delivery Request with:
  - DR Number
  - Part details table
  - Order information
  - Branch/Location info
- **File size:** Must be < 50MB
- **Example filename:** `DeliveryRequest_11559032.pdf`

#### **3.2 Upload Methods**

**Method A: Click Upload Area**
1. **Click** on the dashed upload box
2. **File browser opens**
3. **Select** your PDF file
4. **Click "Open"**

**Method B: Drag & Drop**
1. **Select** PDF file from Windows Explorer
2. **Drag** it to the upload area
3. **Drop** the file on the dashed box

#### **3.3 Verify Upload**
- Filename appears: "File Selected: DeliveryRequest_11559032.pdf"
- Status message: "✅ PDF uploaded successfully!"
- Progress moves to Step 2
- Screen automatically advances

---

### **STEP 4: VERIFY EXTRACTED DETAILS (Step 2)**

#### **4.1 Review DR Information**
| Field | Example | Read-only? |
|-------|---------|-----------|
| DR Number | 11559032 | ✓ Yes |
| Date | 25-01-2025 | ✓ Yes |

#### **4.2 Review Part Details**
| Field | Example | Read-only? |
|-------|---------|-----------|
| Part Name | ASSY. SUCTION PIPE - STEERING PUMP | ✓ Yes |
| Part Number | 1816A1810169 | ✓ Yes |
| Order Number | 1210000691 | ✓ Yes |
| Box Type | CHEP BOX | ✓ Yes |
| Unit Size | 10 | ✓ Yes |

#### **4.3 Review Order Information**
| Field | Example | Read-only? |
|-------|---------|-----------|
| Buyer's Order Number | 1210000691 | ✓ Yes |
| Quantity | 1 | ✓ Yes |

#### **4.4 Verify All Data**
- [ ] DR Number extracted correctly
- [ ] Part Name displayed without errors
- [ ] All quantities populated
- [ ] Branch information recognized

#### **4.5 Proceed to Next Step**
- **Click:** "Next →" button at bottom
- **Action:** System generates prompt interface with defaults
- **Progress:** Advances to Step 3

---

### **STEP 5: EDIT PROMPT DETAILS (Step 3)**

#### **5.1 Basic Information Section**

**Vehicle Number**
- **Current Value:** TN13AH0050 (default)
- **Edit if:** Different vehicle is delivering
- **Format:** License plate (e.g., TN13AH0050)
- **Action:** 
  ```
  Clear field → Type new vehicle number → Field auto-saves
  ```

**Party Code**
- **Current Value:** TAFEMDU or TAFEDBR (branch-dependent)
- **Edit if:** N/A (Read-only)
- **Mapping:**
  - Madurai → TAFEMDU
  - Bangalore → TAFEDBR
  - Doddaballapur → TAFEDBR

#### **5.2 Kanban Details Section**

**No. of Pieces**
- **Description:** Number of individual items in the shipment
- **Default:** Same as Quantity from PDF
- **Example:** 1 (if quantity is 1)
- **Edit:** Yes, change if needed
- **Action:**
  ```
  Click field → Clear → Type number (0-999)
  ```

**No. of Packages**
- **Description:** Number of packages/containers
- **Default:** 1
- **Example:** 1 package
- **Edit:** Yes, change if needed
- **Action:**
  ```
  Click field → Type number (1+)
  ```

**Total Nos**
- **Description:** Total count/units
- **Default:** 20
- **Example:** 20 units
- **Edit:** Yes, change if needed
- **Action:**
  ```
  Click field → Type number
  ```

**Total Kgs**
- **Description:** Total weight of shipment
- **Default:** Empty (optional)
- **Example:** 25.5 (for 25.5 kg)
- **Edit:** Yes, must fill for some orders
- **Action:**
  ```
  Click field → Type weight (decimal OK)
  ```

#### **5.3 Crate Details Section**

**For Crate**
- **Description:** Crate part number and quantity
- **Default:** 14403 - 1 NOS
- **Format:** XXXX - X NOS
- **Edit:** Yes, if crate code differs
- **Example:** 14403 - 1 NOS
- **Action:**
  ```
  Click field → Modify → Field auto-saves
  ```

**Lid**
- **Description:** Lid part number and quantity
- **Default:** 13054 - 1 NOS
- **Format:** XXXX - X NOS
- **Edit:** Yes, if lid code differs
- **Example:** 13054 - 1 NOS
- **Action:**
  ```
  Click field → Modify → Field auto-saves
  ```

**DR Reference**
- **Description:** Delivery Request reference
- **Default:** DR {DRNumber} (e.g., DR 11559032)
- **Edit:** N/A (Read-only)
- **Usage:** For tracking and auditing

#### **5.4 Save Edited Data**
- **Click:** "Next →" button
- **System Action:** Saves all edited data to session
- **Confirmation:** "✅ Prompt saved successfully!"
- **Progress:** Advances to Step 4

---

### **STEP 6: GENERATE OUTPUT FILES (Step 4)**

#### **6.1 Generate Excel File**

**What it does:**
- Creates a standardized Excel spreadsheet
- 16 columns with all DR and prompt data
- Formatted for easy printing and sharing

**Excel Columns:**
1. DR No → 11559032
2. Date → 25-01-2025
3. Buyers Order Number → 1210000691
4. Quantity → 1
5. Vehicle Number → TN13AH0050
6. Party Name → TAFEMDU
7. Part No → 1816A1810169
8. Part Name → ASSY. SUCTION PIPE - STEERING PUMP
9. Order No → 1210000691
10. Box Type → CHEP BOX
11. Unit Size → 10
12. No of Pieces → 1
13. No of Packages → 1
14. Total Nos → 20
15. Total Kgs → [Your entered value]
16. Crate Details → 14403 - 1 NOS; 13054 - 1 NOS

**Action:**
```
Click: 📊 Generate Excel File
Wait: 2-3 seconds
Result: File automatically downloads
Filename: DR_11559032_Invoice.xlsx
Location: Your Downloads folder
```

**Verification:**
- [ ] File appears in Downloads folder
- [ ] Filename matches pattern: DR_XXXXX_Invoice.xlsx
- [ ] File size > 10KB
- [ ] Can open in Excel

---

#### **6.2 Generate Tally XML**

**What it does:**
- Creates XML file for Tally ERP accounting system
- Contains complete voucher structure
- Ready for import into Tally

**XML Structure:**
```xml
<?xml version="1.0"?>
<ENVELOPE xmlns:UDF="TallyUDF">
  <COMPANY>
    <NAME>TAFE Motors</NAME>
    <MNAME>TAFE Motors</MNAME>
  </COMPANY>
  <VOUCHER>
    <VOUCHERNUMBER>INV-11559032</VOUCHERNUMBER>
    <VOUCHERTYPE>Sales</VOUCHERTYPE>
    <DATE>25-01-2025</DATE>
    <REFERENCENUMBER>DR-11559032</REFERENCENUMBER>
    <PARTYDETAILS>
      <PARTYNAME>TAFEMDU</PARTYNAME>
      <BUYERORDERNUMBER>1210000691</BUYERORDERNUMBER>
    </PARTYDETAILS>
    <LEDGERENTRIES>
      <ITEM>
        <ITEMNAME>ASSY. SUCTION PIPE - STEERING PUMP</ITEMNAME>
        <ITEMNO>1816A1810169</ITEMNO>
        <QUANTITY>1</QUANTITY>
        <RATE>25.5</RATE>
        <AMOUNT>0</AMOUNT>
      </ITEM>
    </LEDGERENTRIES>
    <ADDITIONALDETAILS>
      <VEHICLENUMBER>TN13AH0050</VEHICLENUMBER>
      <CRATEDETAILS>DR 11559032</CRATEDETAILS>
      <NOOFPIECES>1</NOOFPIECES>
      <NOOFPACKAGES>1</NOOFPACKAGES>
    </ADDITIONALDETAILS>
  </VOUCHER>
</ENVELOPE>
```

**Action:**
```
Click: 📋 Generate Tally XML
Wait: 2-3 seconds
Result: XML preview displays + file downloads
Filename: DR_11559032_Tally.xml
Preview: Shows XML content in light blue box
```

**Verification:**
- [ ] XML preview appears in browser
- [ ] File downloads to Downloads folder
- [ ] Filename matches pattern: DR_XXXXX_Tally.xml
- [ ] XML is valid (no error symbols)

**To Import into Tally:**
1. Open Tally
2. Press Ctrl+I (Import)
3. Select: XML File
4. Browse to downloaded XML file
5. Click Import
6. Verify voucher created

---

#### **6.3 Generate Invoice**

**What it does:**
- Generates final invoice summary
- Displays all key information
- Shows status: "Generated ✅"

**Invoice Summary Includes:**
- Invoice Number: INV-11559032
- DR Number: 11559032
- Date: 25-01-2025
- Party Code: TAFEMDU
- Vehicle: TN13AH0050
- Part Number: 1816A1810169
- Part Name: ASSY. SUCTION PIPE - STEERING PUMP
- Quantity: 1
- Status: Generated

**Action:**
```
Click: 🧾 Generate Invoice
Wait: 2-3 seconds
Result: Invoice summary displays
Color: Green box (success)
Message: "✅ Invoice generated successfully!"
```

**Verification:**
- [ ] Invoice number displays (INV-XXXXX format)
- [ ] All fields populated correctly
- [ ] Status shows "Generated"
- [ ] Green success box appears

**After Generation:**
- System auto-advances to Step 5
- All invoice data saved in session
- Ready to process another DR or export

---

### **STEP 7: COMPLETE & FINISH (Step 5)**

#### **7.1 Completion Screen**

**Display Shows:**
- ✅ "Step 5: Process Complete ✅"
- Green success box: "Invoice Generated Successfully!"
- Full invoice summary with all details

#### **7.2 Available Actions**

**Option A: Process Another DR**
```
Click: 🔄 Process Another DR
Result: Form resets completely
Next: Return to Step 1 (Upload PDF)
New: Ready for next delivery request
```

**Option B: Download Files**
- Excel: Already downloaded in Step 4
- XML: Already downloaded in Step 4
- Invoice: Display as JSON in browser

**Option C: Close or Navigate**
- Can close browser
- Server continues running
- Can open new browser tab for new DR

---

## 🔄 COMPLETE WORKFLOW SUMMARY

```
START
  ↓
[STEP 1] Upload DR PDF
  ├─ Click/Drag drop PDF
  ├─ System extracts: DR#, Part#, Order#, Qty, Branch
  ├─ Status: "✅ PDF uploaded successfully!"
  └─ Auto-advance: Step 2
  ↓
[STEP 2] Verify Extracted Details
  ├─ Review read-only fields
  ├─ Check: DR Number, Part Name, Quantity
  ├─ Verify: All data correct
  └─ Action: Click "Next →"
  ↓
[STEP 3] Edit Prompt Details
  ├─ Vehicle Number: TN13AH0050 (edit if needed)
  ├─ Kanban Details: Pieces, Packages, Total Nos, Kgs (edit)
  ├─ Crate Details: For Crate, Lid (edit if needed)
  ├─ All edits save automatically
  └─ Action: Click "Next →"
  ↓
[STEP 4] Generate Output Files
  ├─ Option 1: 📊 Generate Excel File
  │  ├─ Creates XLSX with 16 columns
  │  ├─ Auto-downloads
  │  └─ Filename: DR_XXXXX_Invoice.xlsx
  ├─ Option 2: 📋 Generate Tally XML
  │  ├─ Creates XML for Tally ERP
  │  ├─ Shows XML preview
  │  ├─ Auto-downloads
  │  └─ Filename: DR_XXXXX_Tally.xml
  └─ Option 3: 🧾 Generate Invoice
     ├─ Creates invoice summary
     ├─ Displays all details
     └─ Auto-advances: Step 5
  ↓
[STEP 5] Complete & Finish
  ├─ Success message: "✅ Invoice Generated Successfully!"
  ├─ Invoice summary displays
  ├─ All files downloaded
  └─ Options:
     ├─ 🔄 Process Another DR (Loop to Step 1)
     └─ Close browser
END
```

---

## 📊 EXAMPLE: COMPLETE WALKTHROUGH

### **Example Input:**
- **PDF File:** DeliveryRequest_11559032.pdf
- **DR Number:** 11559032
- **Part:** ASSY. SUCTION PIPE - STEERING PUMP
- **Part Number:** 1816A1810169
- **Order Number:** 1210000691
- **Quantity:** 1
- **Branch:** Madurai Operations- K Patti Pl - 1000

### **Step 1 - Upload**
```
User: Drags DeliveryRequest_11559032.pdf to upload area
System: Extracts PDF data
Result: DR 11559032 data extracted ✓
Message: "✅ PDF uploaded successfully!"
Next: Auto-advance to Step 2
```

### **Step 2 - Verify**
```
Display:
- DR Number: 11559032 ✓
- Date: 25-01-2025 ✓
- Part Name: ASSY. SUCTION PIPE - STEERING PUMP ✓
- Part Number: 1816A1810169 ✓
- Order Number: 1210000691 ✓
- Box Type: CHEP BOX ✓
- Unit Size: 10 ✓
- Buyer's Order: 1210000691 ✓
- Quantity: 1 ✓

User: Clicks "Next →"
System: Generates prompt interface
```

### **Step 3 - Edit**
```
Fields Pre-filled:
- Vehicle Number: TN13AH0050 (default) → Can edit
- Party Code: TAFEMDU (auto from Madurai) → Read-only
- Kanban Pieces: 1 → User keeps
- Kanban Packages: 1 → User keeps
- Total Nos: 20 → User keeps
- Total Kgs: [empty] → User enters: 25.5
- For Crate: 14403 - 1 NOS → User keeps
- Lid: 13054 - 1 NOS → User keeps
- DR Reference: DR 11559032 → Read-only

User: Enters 25.5 in Total Kgs field
User: Clicks "Next →"
System: Saves all edits
Message: "✅ Prompt saved successfully!"
```

### **Step 4 - Generate**
```
User: Clicks "📊 Generate Excel File"
System: Creates Excel with 16 columns
Result: File downloads as DR_11559032_Invoice.xlsx
Message: "✅ Excel file downloaded!"

User: Clicks "📋 Generate Tally XML"
System: Creates Tally XML voucher
Display: XML preview shows structure
Result: File downloads as DR_11559032_Tally.xml
Message: "✅ XML file downloaded for Tally import!"

User: Clicks "🧾 Generate Invoice"
System: Generates invoice data
Result: Invoice summary displays
Message: "✅ Invoice generated successfully!"
Auto-advances to Step 5
```

### **Step 5 - Complete**
```
Display:
- ✅ Process Complete ✅
- Invoice Generated Successfully!
- Summary:
  - Invoice Number: INV-11559032
  - DR Number: 11559032
  - Date: 25-01-2025
  - Party Code: TAFEMDU
  - Vehicle: TN13AH0050
  - Part Number: 1816A1810169
  - Part Name: ASSY. SUCTION PIPE - STEERING PUMP
  - Quantity: 1
  - Status: Generated ✅

User Options:
1. Click "🔄 Process Another DR" → Back to Step 1
2. Download files from Downloads folder
3. Import XML to Tally
4. Close application
```

---

## 🎯 QUICK REFERENCE CARDS

### **Data Extraction Reference**
```
FROM PDF EXTRACTED:
├─ DR Number        → 11559032
├─ Order Number     → 1210000691
├─ Part Number      → 1816A1810169
├─ Part Name        → ASSY. SUCTION PIPE - STEERING PUMP
├─ Quantity         → 1
├─ Box Type         → CHEP BOX
├─ Unit Size        → 10
└─ Branch           → Madurai Operations- K Patti Pl - 1000

SYSTEM AUTO-DETERMINES:
├─ Party Code       → TAFEMDU (from Madurai)
├─ Invoice Number   → INV-11559032 (from DR No)
└─ Today's Date     → 25-01-2025
```

### **Editable Fields Reference**
```
USER CAN EDIT (Step 3):
├─ Vehicle Number      → Default: TN13AH0050
├─ No. of Pieces       → Default: Same as Qty
├─ No. of Packages     → Default: 1
├─ Total Nos           → Default: 20
├─ Total Kgs           → Default: Empty (optional)
├─ For Crate           → Default: 14403 - 1 NOS
└─ Lid                 → Default: 13054 - 1 NOS

READ-ONLY FIELDS (Cannot Edit):
├─ DR Number
├─ Date
├─ Part Name
├─ Part Number
├─ Order Number
├─ Box Type
├─ Unit Size
├─ Buyer's Order Number
├─ Quantity
├─ Party Code
└─ DR Reference
```

### **Output Files Reference**
```
FILE 1: Excel Spreadsheet
├─ Type:       XLSX (Microsoft Excel)
├─ Columns:    16 (all DR + Prompt data)
├─ Name:       DR_XXXXX_Invoice.xlsx
├─ Usage:      Printing, Sharing, Analysis
└─ Download:   Automatic

FILE 2: Tally XML
├─ Type:       XML (Tally Format)
├─ Structure:  ENVELOPE → COMPANY → VOUCHER
├─ Name:       DR_XXXXX_Tally.xml
├─ Usage:      Import to Tally ERP
└─ Download:   Automatic

FILE 3: Invoice Summary
├─ Type:       JSON (Browser Display)
├─ Content:    Invoice data
├─ Display:    On-screen summary
└─ Export:     Can copy/export
```

---

## ✅ VALIDATION CHECKLIST

### **Before Starting:**
- [ ] Python 3.8+ installed
- [ ] All packages installed: Flask, pandas, openpyxl, pdfplumber
- [ ] Port 5000 is available
- [ ] Test PDF file ready

### **After Starting Server:**
- [ ] Server shows "Running on http://127.0.0.1:5000"
- [ ] No errors in console
- [ ] Browser opens to landing page

### **Step 1 - Upload:**
- [ ] PDF file selected
- [ ] File shows as selected
- [ ] Status: "✅ PDF uploaded successfully!"

### **Step 2 - Verify:**
- [ ] DR Number displays
- [ ] Part Name displays without newlines
- [ ] All 9 fields populated
- [ ] Read-only fields show correct data

### **Step 3 - Edit:**
- [ ] All edit fields are active (can click and type)
- [ ] Read-only fields are grayed out
- [ ] Vehicle number can be edited
- [ ] Kanban fields editable
- [ ] Crate fields editable

### **Step 4 - Generate:**
- [ ] Excel button works → File downloads
- [ ] XML button works → File downloads + preview shows
- [ ] Invoice button works → Summary displays

### **Step 5 - Complete:**
- [ ] Success message shows
- [ ] Invoice summary displays all data
- [ ] "Process Another DR" button resets form
- [ ] Can download files from completed session

---

**Version:** 1.0 | **Updated:** January 2025 | **Status:** Ready for Production
