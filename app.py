#!/usr/bin/env python3
"""
Complete DR to Invoice Generation App
Delivery Request -> Prompt -> Excel -> XML -> Tally -> Invoice
"""

from flask import Flask, render_template, request, send_file, jsonify, session
import os
import re
import pdfplumber
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename
from io import BytesIO, StringIO
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

app = Flask(__name__)
app.secret_key = 'dr_invoice_app_secret_2025'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Default mappings
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
            
            if not tables:
                return None
            
            main_table = tables[0]
            
            # Extract header info
            for row in main_table[:7]:
                row_text = " ".join([str(c) for c in (row or []) if c])
                
                m = re.search(r"Delivery\s*Request\s*No\.?\s*[:\-]?\s*(\d{5,12})", row_text, re.I)
                if m:
                    details['DR No'] = m.group(1).strip()
                
                m = re.search(r"Request\s*[:\-]?\s*([A-Za-z\-\s]+(?:Operations|Plant|Pl)[A-Za-z0-9\s\-]*)", row_text, re.I)
                if m:
                    details['Branch'] = m.group(1).strip()
            
            # Extract table data
            header_row_idx = -1
            for i, row in enumerate(main_table):
                row_text = " ".join([str(c) for c in (row or []) if c]).upper()
                if "ORDER NO" in row_text and "PART NO" in row_text:
                    header_row_idx = i
                    break
            
            if header_row_idx >= 0:
                row = main_table[header_row_idx + 1]
                if row:
                    details['Order No'] = str(row[0]).strip() if row[0] else ""
                    details['Buyer Order No'] = details['Order No']
                    details['Part No'] = str(row[1]).strip() if row[1] else ""
                    details['Part Name'] = str(row[2]).strip().replace('\n', ' ') if row[2] else ""
                    details['Box Type'] = str(row[3]).strip() if row[3] else ""
                    details['Quantity'] = str(row[4]).strip() if row[4] else ""
                    details['Unit Size'] = str(row[9]).strip() if len(row) > 9 and row[9] else ""
        
        return details
    
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload-dr', methods=['POST'])
def upload_dr():
    """Upload DR PDF and extract details"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Please upload a PDF file'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        details = extract_dr_details(filepath)
        
        if not details:
            os.remove(filepath)
            return jsonify({'error': 'Could not extract DR data from PDF'}), 400
        
        session['dr_details'] = details
        session['pdf_filename'] = filename
        
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'details': details
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-prompt', methods=['GET'])
def generate_prompt():
    """Generate the prompt interface data"""
    try:
        dr_details = session.get('dr_details', {})
        
        if not dr_details:
            return jsonify({'error': 'No DR details found'}), 400
        
        branch = dr_details.get('Branch', '')
        branch_code = 'TAFEMDU'
        
        for branch_name, mapping in BRANCH_MAPPING.items():
            if branch_name.lower() in branch.lower():
                branch_code = mapping['code']
                break
        
        quantity = dr_details.get('Quantity', '')
        
        prompt_data = {
            'dr_no': dr_details.get('DR No', ''),
            'today_date': datetime.now().strftime('%d-%m-%Y'),
            'buyers_order_number': dr_details.get('Buyer Order No', ''),
            'quantity': quantity,
            'vehicle_number': 'TN13AH0050',
            'kanban': {
                'no_of_pieces': quantity,
                'no_of_packages': '1',
                'total_nos': '20',
                'total_kgs': ''
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
        
        session['prompt_data'] = prompt_data
        
        return jsonify({
            'success': True,
            'prompt': prompt_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verify-prompt', methods=['POST'])
def verify_prompt():
    """Verify and save prompt data"""
    try:
        updated_data = request.json.get('data')
        
        if not updated_data:
            return jsonify({'error': 'No data provided'}), 400
        
        session['prompt_data'] = updated_data
        
        return jsonify({
            'success': True,
            'message': 'Prompt data verified and saved'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-excel', methods=['POST'])
def generate_excel():
    """Generate Excel from verified prompt data"""
    try:
        prompt_data = session.get('prompt_data')
        dr_details = session.get('dr_details')
        
        if not prompt_data or not dr_details:
            return jsonify({'error': 'No data found'}), 400
        
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
        
        df = pd.DataFrame(data)
        
        output = BytesIO()
        df.to_excel(output, index=False, sheet_name='DR Invoice', engine='openpyxl')
        output.seek(0)
        
        session['excel_data'] = data
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"DR_{prompt_data['dr_no']}_Invoice.xlsx"
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-xml', methods=['POST'])
def generate_xml():
    """Generate Tally XML from prompt data"""
    try:
        prompt_data = session.get('prompt_data')
        dr_details = session.get('dr_details')
        
        if not prompt_data or not dr_details:
            return jsonify({'error': 'No data found'}), 400
        
        root = ET.Element('ENVELOPE')
        root.set('xmlns:UDF', 'TallyUDF')
        
        company = ET.SubElement(root, 'COMPANY')
        ET.SubElement(company, 'NAME').text = 'TAFE Motors'
        ET.SubElement(company, 'MNAME').text = 'TAFE Motors'
        
        voucher = ET.SubElement(root, 'VOUCHER')
        ET.SubElement(voucher, 'VOUCHERNUMBER').text = f"INV-{prompt_data['dr_no']}"
        ET.SubElement(voucher, 'VOUCHERTYPE').text = 'Sales'
        ET.SubElement(voucher, 'DATE').text = datetime.now().strftime('%d-%m-%Y')
        ET.SubElement(voucher, 'REFERENCENUMBER').text = f"DR-{prompt_data['dr_no']}"
        
        party = ET.SubElement(voucher, 'PARTYDETAILS')
        ET.SubElement(party, 'PARTYNAME').text = prompt_data['bill_details']['party_name']
        ET.SubElement(party, 'BUYERORDERNUMBER').text = prompt_data['buyers_order_number']
        
        ledgers = ET.SubElement(voucher, 'LEDGERENTRIES')
        
        item = ET.SubElement(ledgers, 'ITEM')
        ET.SubElement(item, 'ITEMNAME').text = dr_details.get('Part Name', '')
        ET.SubElement(item, 'ITEMNO').text = dr_details.get('Part No', '')
        ET.SubElement(item, 'QUANTITY').text = str(prompt_data['quantity'])
        ET.SubElement(item, 'RATE').text = prompt_data['kanban'].get('total_kgs', '0')
        ET.SubElement(item, 'AMOUNT').text = '0'
        
        additional = ET.SubElement(voucher, 'ADDITIONALDETAILS')
        ET.SubElement(additional, 'VEHICLENUMBER').text = prompt_data['vehicle_number']
        ET.SubElement(additional, 'CRATEDETAILS').text = prompt_data['crate_details']['dr_reference']
        ET.SubElement(additional, 'NOOFPIECES').text = str(prompt_data['kanban']['no_of_pieces'])
        ET.SubElement(additional, 'NOOFPACKAGES').text = str(prompt_data['kanban']['no_of_packages'])
        
        xml_string = minidom.parseString(ET.tostring(root)).toprettyxml(indent='  ')
        xml_string = '\n'.join([line for line in xml_string.split('\n') if line.strip()])
        
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

@app.route('/generate-invoice', methods=['POST'])
def generate_invoice():
    """Generate final invoice"""
    try:
        prompt_data = session.get('prompt_data')
        dr_details = session.get('dr_details')
        
        if not prompt_data or not dr_details:
            return jsonify({'error': 'No data found'}), 400
        
        invoice_data = {
            'invoice_number': f"INV-{prompt_data['dr_no']}",
            'dr_number': prompt_data['dr_no'],
            'date': prompt_data['today_date'],
            'buyers_order': prompt_data['buyers_order_number'],
            'party_code': prompt_data['bill_details']['party_name'],
            'vehicle': prompt_data['vehicle_number'],
            'part_no': dr_details.get('Part No', ''),
            'part_name': dr_details.get('Part Name', ''),
            'quantity': prompt_data['quantity'],
            'unit_size': dr_details.get('Unit Size', ''),
            'box_type': dr_details.get('Box Type', ''),
            'crate_details': prompt_data['crate_details']['dr_reference'],
            'status': 'Generated'
        }
        
        session['invoice_data'] = invoice_data
        
        return jsonify({
            'success': True,
            'invoice': invoice_data,
            'message': 'Invoice generated successfully. Ready for Tally upload.'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload-to-tally', methods=['POST'])
def upload_to_tally():
    """Upload XML to Tally (placeholder for actual Tally integration)"""
    try:
        xml_data = session.get('xml_data')
        invoice_data = session.get('invoice_data')
        
        if not xml_data or not invoice_data:
            return jsonify({'error': 'No data to upload'}), 400
        
        return jsonify({
            'success': True,
            'message': 'XML prepared for Tally upload',
            'invoice_number': invoice_data['invoice_number'],
            'tally_status': 'Ready for import',
            'xml_preview': xml_data[:500] + '...' if len(xml_data) > 500 else xml_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
