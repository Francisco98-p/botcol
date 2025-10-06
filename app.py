from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import requests
from io import BytesIO
import json
from datetime import time, date

app = Flask(__name__)
CORS(app)

EXCEL_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTehAmmwC6fZqVfOG1Z_AyfHVZUEh1HnOnRamIIK0eYLXjtpWn9BGf7u0YZnMk__NIBgLBE9SSGkasx/pub?output=xlsx"

def convert_pandas_types(obj):
    """Convierte objetos pandas y datetime a tipos serializables"""
    if pd.isna(obj):
        return None
    elif isinstance(obj, (time, date)):
        return obj.isoformat()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, (int, float, str, bool)) or obj is None:
        return obj
    else:
        return str(obj)

def get_excel_data():
    try:
        response = requests.get(EXCEL_URL)
        response.raise_for_status()
        
        excel_data = pd.read_excel(BytesIO(response.content))
        data = excel_data.to_dict('records')
        
        # Convertir objetos no serializables
        for record in data:
            for key, value in record.items():
                record[key] = convert_pandas_types(value)
        
        return data
    except Exception as e:
        print(f"Error: {e}")
        return []

@app.route('/')
def home():
    return jsonify({
        "message": "API para gestión de citas - Excel",
        "endpoints": {
            "todas_las_citas": "/api/citas",
            "cita_especifica": "/api/citas/<id>",
            "estado": "/health"
        }
    })

@app.route('/api/citas', methods=['GET'])
def get_citas():
    try:
        data = get_excel_data()
        return jsonify({
            "success": True,
            "total_citas": len(data),
            "citas": data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "active", "service": "api-citas-excel"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
