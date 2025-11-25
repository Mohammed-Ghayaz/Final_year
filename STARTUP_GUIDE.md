# 🚀 DR TO INVOICE GENERATOR - STARTUP GUIDE

## ⚡ FASTEST STARTUP (2 minutes)

### **Windows Users - Click and Go**

1. **Double-click:** `start.bat`
   - Window opens automatically
   - Server starts
   - Browser opens to http://127.0.0.1:5000
   - Done! ✓

---

## 📋 MANUAL STARTUP (3 minutes)

### **Option 1: PowerShell**

```powershell
# Open PowerShell and navigate to project folder
cd "C:\Users\abhin\OneDrive\Documents\Final_year"

# Start Flask app
python app.py
```

**Output should show:**
```
 * Running on http://127.0.0.1:5000
```

**Then:**
1. Open web browser
2. Go to: `http://127.0.0.1:5000`
3. You should see the app interface

---

### **Option 2: Command Prompt (CMD)**

```cmd
cd "C:\Users\abhin\OneDrive\Documents\Final_year"
python app.py
```

---

### **Option 3: PowerShell Script**

```powershell
# Right-click on start.ps1
# Select "Run with PowerShell"
# App starts automatically
```

---

## ✅ VERIFICATION CHECKLIST

### **After starting, verify:**

- [ ] **Console Output**
  - Shows: "Running on http://127.0.0.1:5000" ✓
  - Shows: "Press CTRL+C to quit" ✓
  - Shows: "Debugger is active!" ✓

- [ ] **Browser Opens**
  - URL shows: 127.0.0.1:5000 ✓
  - Page title: "DR to Invoice Generator" ✓
  - Upload area visible ✓

- [ ] **Upload Area**
  - Large dashed box visible ✓
  - Text: "Click to upload" ✓
  - Step indicators visible (1-5) ✓

- [ ] **Ready to Use**
  - Can drag-drop files ✓
  - Can click to browse ✓
  - All buttons visible ✓

---

## 🎯 FIRST USE - 5-MINUTE TEST

### **Test the system with sample PDF:**

```
1. Click upload area (or drag-drop)
2. Select: DeliveryRequest_11559032.pdf
3. Wait 2-3 seconds for extraction
4. See green message: "✅ PDF uploaded successfully!"
5. Click "Next →"
6. Review extracted data (Step 2)
7. Click "Next →"
8. See editable fields (Step 3)
9. Keep defaults
10. Click "Next →"
11. Click "📊 Generate Excel File"
12. File downloads: DR_11559032_Invoice.xlsx ✓
13. Click "📋 Generate Tally XML"
14. File downloads: DR_11559032_Tally.xml ✓
15. Click "🧾 Generate Invoice"
16. See success message ✓
17. Complete! ✅
```

**Total time:** ~5 minutes

---

## 📊 EXPECTED OUTPUT - FIRST RUN

### **Server Console Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 132-171-980
```

### **Browser Display:**
```
DR to Invoice Generator
Delivery Request → Excel → XML → Tally → Invoice

[Step 1] [Step 2] [Step 3] [Step 4] [Step 5]

========== UPLOAD AREA ===========
📄 Click to upload or drag and drop
PDF files only (Max 50MB)
```

### **After upload:**
```
✅ PDF uploaded successfully!

File Selected: DeliveryRequest_11559032.pdf

[Next →]
```

---

## ⚠️ COMMON STARTUP ISSUES

### **Issue 1: "Port 5000 already in use"**

**Error Message:**
```
OSError: [WinError 48] Address already in use
```

**Solution:**
1. Find what's using port 5000:
   ```powershell
   netstat -ano | findstr :5000
   ```

2. Kill the process:
   ```powershell
   taskkill /PID [process_id] /F
   ```

3. Try again:
   ```powershell
   python app.py
   ```

**OR use different port:**
- Edit `app.py` last line:
  ```python
  app.run(debug=True, host='127.0.0.1', port=5001)
  ```
- Access: `http://127.0.0.1:5001`

---

### **Issue 2: "Python not found"**

**Error Message:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
1. Verify Python installed:
   ```
   python --version
   ```

2. If not installed:
   - Download Python from python.org
   - Install (CHECK: "Add Python to PATH")

3. Restart PowerShell

4. Try again:
   ```
   python app.py
   ```

---

### **Issue 3: "ModuleNotFoundError: No module named 'flask'"**

**Error Message:**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
1. Install dependencies:
   ```powershell
   pip install flask pandas openpyxl pdfplumber werkzeug
   ```

2. Wait for installation to complete

3. Try again:
   ```
   python app.py
   ```

---

### **Issue 4: "File not found: templates/index.html"**

**Error Message:**
```
jinja2.exceptions.FileNotFoundError: the file 'index.html' 
```

**Solution:**
1. Verify file exists:
   ```
   templates/index.html
   ```

2. Verify folder structure:
   ```
   Final_year/
   ├── app.py
   ├── templates/
   │   └── index.html   ← Must be here
   ```

3. If missing, check:
   - Is the file named correctly?
   - Is it in `templates` folder?
   - Not in `template` folder?

---

### **Issue 5: "Browser won't open"**

**Solution:**
1. Manual browser open:
   ```
   http://127.0.0.1:5000
   ```

2. Try different browsers:
   - Chrome
   - Firefox
   - Edge

3. If still not working:
   - Check firewall settings
   - Check antivirus software
   - Try `http://localhost:5000`

---

## 🔧 TROUBLESHOOTING COMMANDS

### **Check Python version:**
```powershell
python --version
# Expected: Python 3.8 or higher
```

### **Check installed packages:**
```powershell
pip list | findstr "flask pandas openpyxl pdfplumber werkzeug"
# Should show all 5 packages
```

### **Check if port is available:**
```powershell
netstat -ano | findstr :5000
# If nothing shows, port is available
```

### **Test Flask installation:**
```powershell
python -c "import flask; print(flask.__version__)"
# Should show version number
```

### **Reinstall all dependencies:**
```powershell
pip install --upgrade flask pandas openpyxl pdfplumber werkzeug
```

---

## 🎓 AFTER STARTUP - NEXT STEPS

### **Step 1: Verify Working (5 min)**
- Upload test PDF
- Review extracted data
- Generate Excel file
- Download and verify

### **Step 2: Review Documentation (10 min)**
- Read QUICK_REFERENCE.md
- Read COMPLETE_GUIDE.md
- Understand the 5 steps

### **Step 3: Practice (20 min)**
- Upload 3-5 different DR PDFs
- Try editing prompt fields
- Generate all output formats
- Test Tally XML import

### **Step 4: Deploy (if needed)**
- Follow PROJECT_SUMMARY.md
- Configure for production
- Set up monitoring
- Document customizations

---

## 🛑 STOPPING THE SERVER

### **To stop the Flask app:**

1. **In console window:** Press `Ctrl+C`

2. **Confirmation message:**
   ```
   ^C
   Keyboard interrupt received
   Shutting down
   ```

3. **Server stops** - you'll return to PowerShell prompt

### **To start again:**
```
python app.py
```

---

## 🔄 QUICK REFERENCE - STARTUP COMMANDS

```bash
# Start with batch file (easiest)
start.bat

# Start with PowerShell script
start.ps1

# Start with manual PowerShell
python app.py

# Start with different port
# (Edit app.py first, change port=5001)
python app.py

# Check if running
netstat -ano | findstr :5000

# Stop server
Ctrl+C (in console)
```

---

## 📱 BROWSER ACCESS URLS

**Main app:**
```
http://127.0.0.1:5000
http://localhost:5000
```

**If using custom port (5001):**
```
http://127.0.0.1:5001
http://localhost:5001
```

**Health check endpoint:**
```
http://127.0.0.1:5000/health
```

---

## 🔒 FIREWALL & ANTIVIRUS

### **If you get "Connection refused":**

1. **Windows Firewall:**
   - Go to: Windows Defender Firewall
   - Click: "Allow an app"
   - Find: Python
   - Check: Both Private and Public
   - Click: OK

2. **Antivirus:**
   - Check settings
   - Add Python to whitelist
   - Add Flask to whitelist

3. **Router Firewall:**
   - Usually not an issue (localhost only)
   - If accessing from another computer: Configure router

---

## 📞 STARTUP HELP

| Problem | Solution |
|---------|----------|
| Port in use | See Issue 1 above |
| Python not found | See Issue 2 above |
| Module errors | See Issue 3 above |
| File not found | See Issue 4 above |
| Browser won't open | See Issue 5 above |
| App runs but PDF fails | Check PDF format (must be PDF not image) |
| App is slow | Check disk space, restart computer |
| Extraction missing data | Check PDF table structure |

---

## ✅ SUCCESS INDICATORS

### **Green Light - Ready to Use:**
✅ Console shows "Running on http://127.0.0.1:5000"
✅ Browser opens to app page
✅ Upload area visible
✅ All 5 steps visible
✅ Can upload PDF

### **Red Light - Problem:**
❌ Console shows error
❌ Port 5000 in use
❌ Python not found
❌ Module import error
❌ Browser won't connect

---

## 🎯 QUICK START DIAGRAM

```
1. Click start.bat
        ↓
2. Console window opens
   "Running on 127.0.0.1:5000"
        ↓
3. Browser opens automatically
        ↓
4. See app interface
        ↓
5. Upload PDF
        ↓
6. Follow 5 steps
        ↓
7. Download files
        ↓
8. Complete! ✅
```

---

## 📝 STARTUP CHECKLIST

Before first use:

- [ ] Python installed (`python --version`)
- [ ] Dependencies installed (`pip list`)
- [ ] Project files present (app.py, templates/)
- [ ] Test PDF ready (DeliveryRequest_11559032.pdf)
- [ ] Firewall allows Python
- [ ] Port 5000 available
- [ ] Browser ready

Ready to go? **Start the app:**
```
python app.py
```

---

## 🎓 NEXT DOCUMENT TO READ

After startup, read:
1. **QUICK_REFERENCE.md** - 3 minute overview
2. **COMPLETE_GUIDE.md** - 25 minute detailed guide

---

**Startup Guide v1.0** | **Ready to Launch** ✅
