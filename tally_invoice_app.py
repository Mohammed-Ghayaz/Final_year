"""
Tally Invoice Generator from DR PDF
Complete Desktop Application
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import re
import pdfplumber
import pandas as pd
from datetime import datetime
from io import BytesIO, StringIO
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import shutil

app = Flask(__name__)
app.secret_key = 'tally_invoice_secret_2025'

# Create output folder
OUTPUT_FOLDER = 'output_xml'
UPLOAD_FOLDER = 'uploads'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =====================================================
# EXTRACTION LOGIC
# =====================================================

class PDFExtractor:
    """Extract DR data from PDF with multiple fallback methods"""
    
    @staticmethod
    def extract_dr_details(pdf_path):
        """
        Priority 1: pdfplumber table extraction
        Priority 2: pdfplumber text extraction
        Priority 3: Fallback regex patterns
        """
        details = {
            'DR No': '',
            'Buyer Order No': '',
            'Quantity': '',
            'Branch': '',
            'Part Name': '',
            'Order No': '',
            'Part No': '',
            'Box Type': '',
            'Unit Size': '',
            'Item Description': '',
            'HSN Code': '',
            'Rate': '',
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[0]
                
                # PRIORITY 1: Table extraction
                tables = page.extract_tables()
                if tables:
                    details = PDFExtractor._extract_from_table(tables, details)
                
                # PRIORITY 2: Text extraction (for fields not in table)
                text = page.extract_text()
                if text:
                    details = PDFExtractor._extract_from_text(text, details)
                
                return details
        
        except Exception as e:
            print(f"PDF extraction error: {e}")
            return details
    
    @staticmethod
    def _extract_from_table(tables, details):
        """Extract from PDF table"""
        try:
            main_table = tables[0]
            
            for row in main_table[:10]:
                if not row:
                    continue
                row_text = " ".join([str(c) for c in row if c])
                
                # DR Number
                m = re.search(r"Delivery\s*Request\s*No\.?\s*[:\-]?\s*(\d{5,12})", row_text, re.I)
                if m:
                    details['DR No'] = m.group(1).strip()
                
                # Branch
                m = re.search(r"Request\s*[:\-]?\s*([A-Za-z\-\s]+(?:Operations|Plant|Pl)[A-Za-z0-9\s\-]*)", row_text, re.I)
                if m:
                    details['Branch'] = m.group(1).strip()
            
            # Extract table data
            for i, row in enumerate(main_table):
                row_text = " ".join([str(c) for c in row if c]).upper()
                if "ORDER NO" in row_text and "PART NO" in row_text:
                    if i + 1 < len(main_table):
                        data_row = main_table[i + 1]
                        if data_row:
                            details['Order No'] = str(data_row[0]).strip() if data_row[0] else ""
                            details['Buyer Order No'] = details['Order No']
                            details['Part No'] = str(data_row[1]).strip() if len(data_row) > 1 and data_row[1] else ""
                            details['Part Name'] = str(data_row[2]).strip().replace('\n', ' ') if len(data_row) > 2 and data_row[2] else ""
                            details['Box Type'] = str(data_row[3]).strip() if len(data_row) > 3 and data_row[3] else ""
                            details['Quantity'] = str(data_row[4]).strip() if len(data_row) > 4 and data_row[4] else "1"
                            details['Unit Size'] = str(data_row[9]).strip() if len(data_row) > 9 and data_row[9] else ""
                    break
        
        except Exception as e:
            print(f"Table extraction error: {e}")
        
        return details
    
    @staticmethod
    def _extract_from_text(text, details):
        """Extract from raw text"""
        try:
            # DR Number
            m = re.search(r"Delivery\s*Request\s*No\.?\s*[:\-]?\s*(\d{5,12})", text, re.I)
            if m and not details['DR No']:
                details['DR No'] = m.group(1).strip()
            
            # Quantity
            m = re.search(r"Qty|Quantity\s*[:\-]?\s*(\d+)", text, re.I)
            if m and not details['Quantity']:
                details['Quantity'] = m.group(1).strip()
            
            # Buyer Order
            m = re.search(r"Buyer.*Order.*[:\-]?\s*(\d+)", text, re.I)
            if m and not details['Buyer Order No']:
                details['Buyer Order No'] = m.group(1).strip()
        
        except Exception as e:
            print(f"Text extraction error: {e}")
        
        return details


# =====================================================
# TALLY INVOICE GENERATOR
# =====================================================

class TallyInvoiceGenerator:
    """Generate Tally-compliant invoice XML"""
    
    # Item master data (simulated)
    ITEM_MASTER = {
        '1816A1810169': {
            'name': 'ASSY. SUCTION PIPE - STEERING PUMP',
            'hsn': '8409991090',
            'gst': 5,
            'rate': 2003.30,
        }
    }
    
    @staticmethod
    def determine_tax_type(branch):
        """Determine tax type based on branch"""
        if 'Madurai' in branch:
            return 'CGST_SGST', 'TN'
        else:
            return 'IGST', 'KA'
    
    @staticmethod
    def generate_xml(dr_data, prompt_data):
        """Generate Tally invoice XML"""
        
        # Get item details
        part_no = dr_data.get('Part No', '')
        item_data = TallyInvoiceGenerator.ITEM_MASTER.get(part_no, {
            'name': dr_data.get('Part Name', 'Unknown Part'),
            'hsn': '8409991090',
            'gst': 5,
            'rate': 2003.30,
        })
        
        # Calculate amounts
        quantity = float(prompt_data.get('quantity', 1))
        rate = float(item_data.get('rate', 0))
        taxable_amount = quantity * rate
        gst_rate = item_data.get('gst', 5)
        gst_amount = (taxable_amount * gst_rate) / 100
        total_amount = taxable_amount + gst_amount
        
        tax_type, state = TallyInvoiceGenerator.determine_tax_type(dr_data.get('Branch', ''))
        
        # Create XML structure
        root = ET.Element('ENVELOPE')
        root.set('xmlns:UDF', 'TallyUDF')
        
        # Header
        header = ET.SubElement(root, 'HEADER')
        ET.SubElement(header, 'TALLYREQUEST').text = 'Export'
        ET.SubElement(header, 'TALLYRESPONSE').text = 'MasterList'
        
        # Body with Voucher
        body = ET.SubElement(root, 'BODY')
        list_elem = ET.SubElement(body, 'TALLYLIST')
        list_elem.set('NAME', 'Voucher')
        
        # Company
        company = ET.SubElement(list_elem, 'TALLYCOMPANY')
        ET.SubElement(company, 'NAME').text = 'TAFE Motors'
        
        # Voucher
        voucher = ET.SubElement(list_elem, 'VOUCHER')
        
        # Basic Details
        ET.SubElement(voucher, 'VOUCHERNUMBER').text = f"INV_{dr_data['DR No']}"
        ET.SubElement(voucher, 'REFERENCENUMBER').text = f"DR_{dr_data['DR No']}"
        ET.SubElement(voucher, 'VOUCHERTYPE').text = 'Sales'
        ET.SubElement(voucher, 'VOUCHERTYPENAME').text = 'Sales'
        ET.SubElement(voucher, 'DATE').text = datetime.now().strftime('%d-%m-%Y')
        ET.SubElement(voucher, 'ORDERREFERENCE').text = dr_data.get('Order No', '')
        
        # Party Details
        party = ET.SubElement(voucher, 'PARTYDETAILS')
        ET.SubElement(party, 'PARTYNAME').text = prompt_data.get('party_name', 'TAFEMDU')
        ET.SubElement(party, 'BUYERORDERNUMBER').text = dr_data.get('Buyer Order No', '')
        
        # Line Items
        items = ET.SubElement(voucher, 'LINEITEMSLIST')
        
        lineitem = ET.SubElement(items, 'LINEITEM')
        ET.SubElement(lineitem, 'ITEMNAME').text = item_data.get('name', '')
        ET.SubElement(lineitem, 'ITEMNO').text = part_no
        ET.SubElement(lineitem, 'HSNCODE').text = item_data.get('hsn', '')
        ET.SubElement(lineitem, 'QUANTITY').text = str(int(quantity))
        ET.SubElement(lineitem, 'UNIT').text = 'NOS'
        ET.SubElement(lineitem, 'RATE').text = str(rate)
        ET.SubElement(lineitem, 'AMOUNT').text = str(round(taxable_amount, 2))
        ET.SubElement(lineitem, 'TAXRATE').text = str(gst_rate)
        ET.SubElement(lineitem, 'TAXTYPE').text = tax_type
        ET.SubElement(lineitem, 'TAXAMOUNT').text = str(round(gst_amount, 2))
        ET.SubElement(lineitem, 'GROSSAMOUNT').text = str(round(total_amount, 2))
        
        # Tax Details
        taxes = ET.SubElement(voucher, 'TAXDETAILS')
        
        if tax_type == 'CGST_SGST':
            cgst = gst_amount / 2
            sgst = gst_amount / 2
            
            cgst_tax = ET.SubElement(taxes, 'TAX')
            ET.SubElement(cgst_tax, 'TAXNAME').text = 'CGST'
            ET.SubElement(cgst_tax, 'TAXRATE').text = str(gst_rate / 2)
            ET.SubElement(cgst_tax, 'TAXAMOUNT').text = str(round(cgst, 2))
            
            sgst_tax = ET.SubElement(taxes, 'TAX')
            ET.SubElement(sgst_tax, 'TAXNAME').text = 'SGST'
            ET.SubElement(sgst_tax, 'TAXRATE').text = str(gst_rate / 2)
            ET.SubElement(sgst_tax, 'TAXAMOUNT').text = str(round(sgst, 2))
        
        else:  # IGST
            igst_tax = ET.SubElement(taxes, 'TAX')
            ET.SubElement(igst_tax, 'TAXNAME').text = 'IGST'
            ET.SubElement(igst_tax, 'TAXRATE').text = str(gst_rate)
            ET.SubElement(igst_tax, 'TAXAMOUNT').text = str(round(gst_amount, 2))
        
        # Totals
        totals = ET.SubElement(voucher, 'TOTALS')
        ET.SubElement(totals, 'TAXABLEAMOUNT').text = str(round(taxable_amount, 2))
        ET.SubElement(totals, 'TAXAMOUNT').text = str(round(gst_amount, 2))
        ET.SubElement(totals, 'ROUNDOFF').text = '0.00'
        ET.SubElement(totals, 'TOTALAMOUNT').text = str(round(total_amount, 2))
        
        # Additional Details
        additional = ET.SubElement(voucher, 'ADDITIONALDETAILS')
        ET.SubElement(additional, 'VEHICLENUMBER').text = prompt_data.get('vehicle_number', 'TN13AH0050')
        ET.SubElement(additional, 'CRATEDETAILS').text = f"DR_{dr_data['DR No']}"
        ET.SubElement(additional, 'NOOFPIECES').text = str(prompt_data.get('no_of_pieces', quantity))
        ET.SubElement(additional, 'NOOFPACKAGES').text = str(prompt_data.get('no_of_packages', 1))
        ET.SubElement(additional, 'TOTALKGS').text = prompt_data.get('total_kgs', '0')
        
        # Narration
        narration = ET.SubElement(voucher, 'NARRATION')
        ET.SubElement(narration, 'TEXT').text = f"DR {dr_data['DR No']} - {dr_data.get('Part Name', '')}"
        
        return root


# =====================================================
# FLASK ROUTES
# =====================================================

@app.route('/')
def index():
    return render_template('invoice_app.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    """Upload PDF and extract details"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file.filename.endswith('.pdf'):
            return jsonify({'error': 'Only PDF files allowed'}), 400
        
        # Save temporarily
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        # Extract
        extractor = PDFExtractor()
        details = extractor.extract_dr_details(filepath)
        
        # Cleanup
        os.remove(filepath)
        
        if not details.get('DR No'):
            return jsonify({'error': 'Could not extract DR number'}), 400
        
        return jsonify({
            'success': True,
            'details': details
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-xml', methods=['POST'])
def generate_xml():
    """Generate and download invoice XML"""
    try:
        data = request.json
        dr_data = data.get('dr_data', {})
        prompt_data = data.get('prompt_data', {})
        
        if not dr_data.get('DR No'):
            return jsonify({'error': 'Missing DR number'}), 400
        
        # Generate XML
        generator = TallyInvoiceGenerator()
        root = generator.generate_xml(dr_data, prompt_data)
        
        # Pretty print
        xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent='  ')
        xml_string = '\n'.join([line for line in xml_string.split('\n') if line.strip()])
        
        # Save to output folder
        dr_no = dr_data['DR No']
        filename = f"INV_{dr_no}.xml"
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_string)
        
        # Return download
        output = BytesIO(xml_string.encode('utf-8'))
        
        return send_file(
            output,
            mimetype='application/xml',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
