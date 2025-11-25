# DR to Invoice Generator - Quick Reference Card

## 🚀 START APP

### Windows Command Line
```powershell
cd "C:\Users\abhin\OneDrive\Documents\Final_year"
python app.py
```

### Output
```
Running on http://127.0.0.1:5000
```

### Browser
```
Open: http://127.0.0.1:5000
```

---

## 📋 5-STEP WORKFLOW

| Step | Action | Input | Output | Time |
|------|--------|-------|--------|------|
| 1 | Upload PDF | `.pdf` file | Extract data | 2-5 sec |
| 2 | Verify | Review fields | Check extraction | 1 sec |
| 3 | Edit Prompt | Edit 7 fields | Save to session | 2 sec |
| 4 | Generate | 3 buttons | 3 files + preview | 3-5 sec each |
| 5 | Complete | View summary | Download/Export | 1 sec |

---

## ✏️ EDITABLE FIELDS (Step 3)

```
Vehicle Number           → Default: TN13AH0050
No. of Pieces           → Default: Same as Qty
No. of Packages         → Default: 1
Total Nos               → Default: 20
Total Kgs               → Default: Empty
For Crate               → Default: 14403 - 1 NOS
Lid                     → Default: 13054 - 1 NOS
```

---

## 📊 GENERATED FILES

```
FILE 1: Excel
├─ Name: DR_11559032_Invoice.xlsx
├─ Type: XLSX (16 columns)
├─ When: Step 4, Button 1
└─ Download: Automatic

FILE 2: XML (Tally)
├─ Name: DR_11559032_Tally.xml
├─ Type: XML (Tally Format)
├─ When: Step 4, Button 2
└─ Download: Automatic

FILE 3: Invoice
├─ Name: JSON (Display Only)
├─ Type: Summary
├─ When: Step 4, Button 3
└─ Display: On-screen
```

---

## 🔄 BRANCH → PARTY CODE

| Branch | Code |
|--------|------|
| Madurai | TAFEMDU |
| Bangalore | TAFEDBR |
| Doddaballapur | TAFEDBR |

---

## 📊 EXCEL COLUMNS (16)

1. DR No
2. Date
3. Buyers Order Number
4. Quantity
5. Vehicle Number
6. Party Name
7. Part No
8. Part Name
9. Order No
10. Box Type
11. Unit Size
12. No of Pieces
13. No of Packages
14. Total Nos
15. Total Kgs
16. Crate Details

---

## 🐛 QUICK TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Port in use | Change port in app.py to 5001 |
| No data extracted | Check PDF table structure |
| File locked error | Close Excel before generating |
| Part name has newlines | System auto-cleans them |
| Branch not recognized | Update regex in app.py |

---

## 🔌 TALLY IMPORT

1. Open Tally
2. Press Ctrl+I (Import)
3. Select XML file: `DR_XXXXX_Tally.xml`
4. Click Import
5. Verify voucher created

---

## 📁 PROJECT FILES

```
Final_year/
├── app.py                (Main Flask app)
├── dr_pdf_to_excel.py   (PDF utility)
├── templates/
│   └── index.html       (Web UI)
├── uploads/             (Temp PDFs)
├── README.md            (Full guide)
├── COMPLETE_GUIDE.md    (Step-by-step)
├── QUICK_REFERENCE.md   (This file)
├── start.bat            (Windows launcher)
└── start.ps1            (PowerShell launcher)
```

---

## ⚡ KEYBOARD SHORTCUTS

```
Ctrl+C       → Stop Flask server
Alt+Tab      → Switch windows
F5           → Refresh browser
Ctrl+Shift+I → Open browser dev tools
```

---

## 🎯 EXPECTED OUTPUTS

### Step 2 Extraction
```
✓ DR Number: 11559032
✓ Date: 25-01-2025
✓ Part Name: ASSY. SUCTION PIPE - STEERING PUMP
✓ Part Number: 1816A1810169
✓ Order Number: 1210000691
✓ Box Type: CHEP BOX
✓ Unit Size: 10
✓ Buyer's Order: 1210000691
✓ Quantity: 1
```

### Step 3 Defaults
```
✓ Vehicle Number: TN13AH0050
✓ Party Code: TAFEMDU (Madurai) or TAFEDBR (Bangalore)
✓ No. of Pieces: 1
✓ No. of Packages: 1
✓ Total Nos: 20
✓ Total Kgs: [Empty - user enters]
✓ For Crate: 14403 - 1 NOS
✓ Lid: 13054 - 1 NOS
✓ DR Reference: DR 11559032
```

### Step 4 Outputs
```
✓ Excel: DR_11559032_Invoice.xlsx (downloads)
✓ XML: DR_11559032_Tally.xml (downloads + preview)
✓ Invoice: JSON summary (displays on screen)
```

### Step 5 Complete
```
✓ Status: Generated
✓ Invoice Number: INV-11559032
✓ Summary: All fields displayed
✓ Action: Process Another DR or Download
```

---

## 📞 HELP COMMANDS

```bash
# Check Python version
python --version

# Install packages
pip install flask pandas openpyxl pdfplumber werkzeug

# Check port availability
netstat -ano | findstr :5000

# Kill process on port 5000
taskkill /PID [process_id] /F
```

---

## 💾 SESSION STORAGE

```
Session Data Structure:
├── dr_details
│   ├── DR No
│   ├── Part Name
│   ├── Quantity
│   └── ... (all extracted fields)
├── prompt_data
│   ├── vehicle_number
│   ├── kanban {...}
│   ├── bill_details {...}
│   └── crate_details {...}
├── excel_data
├── xml_data
└── invoice_data
```

---

## 📌 IMPORTANT NOTES

⚠️ **Important:**
- Session data deleted when browser closes
- PDFs auto-deleted after processing
- No database persistence (session only)
- Max file size: 50MB
- Supports PDF only (not images/scans)

✓ **Best Practices:**
- Keep PDF DPI at 100+ for better extraction
- Ensure PDF has proper table structure
- Always verify extracted data before editing
- Download files before closing browser
- Test with small batch first

---

## 🔗 API ENDPOINTS

```
POST   /upload-dr          → Upload and extract PDF
GET    /generate-prompt    → Create editable form
POST   /verify-prompt      → Save edited data
POST   /generate-excel     → Create XLSX file
POST   /generate-xml       → Create Tally XML
POST   /generate-invoice   → Generate invoice data
GET    /health             → Check server status
```

---

## 📊 DATA FLOW DIAGRAM

```
PDF File
   ↓
[Upload to Server]
   ↓
[pdfplumber Extract]
   ↓
[DR Details Dict]
   ↓
[Display Step 2]
   ↓
[User Edits Step 3]
   ↓
[Session Storage]
   ↓
├─→ [Excel Generation]  → XLSX Download
├─→ [XML Generation]    → XML Download
└─→ [Invoice Gen]       → JSON Display
   ↓
[Step 5 Complete]
```

---

## ✅ VERIFICATION CHECKLIST

Quick check before using:

- [ ] Python installed
- [ ] Flask running
- [ ] Browser at 127.0.0.1:5000
- [ ] Upload area visible
- [ ] Progress bar shows 20%
- [ ] Step indicators show 1-5
- [ ] Can select PDF file
- [ ] All fields display

---

## 🎓 EXAMPLE SCENARIO

```
User has: DeliveryRequest_11559032.pdf

Action 1: Upload PDF
Result: Extract all fields ✓

Action 2: Review (Step 2)
Result: All data correct ✓

Action 3: Edit Total Kgs = 25.5 (Step 3)
Result: Save edits ✓

Action 4: Generate Excel
Result: DR_11559032_Invoice.xlsx downloaded ✓

Action 5: Generate XML
Result: DR_11559032_Tally.xml downloaded ✓

Action 6: Generate Invoice
Result: Invoice summary displays ✓

Action 7: Complete
Result: Process Another DR or Close ✓
```

---

## 📞 SUPPORT

For issues:
1. Check troubleshooting section
2. Verify Python version
3. Check Flask output console
4. Review PDF structure
5. Restart Flask app

---

**Quick Ref v1.0** | **January 2025** | **Status: Ready**
