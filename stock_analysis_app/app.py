"""
Stock Analysis Web Application
Main Flask application for generating financial analysis reports
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import sys
from datetime import datetime
from pathlib import Path
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.fundamental import generate_fundamental_report
from api.technical import generate_technical_report
from api.sector import generate_sector_analysis
# from api.action_plan import generate_action_plan  # Disabled for now

app = Flask(__name__)
CORS(app)

# Configuration
app.config['REPORTS_DIR'] = Path(__file__).parent / 'reports'
app.config['REPORTS_DIR'].mkdir(exist_ok=True)


@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint
    Accepts: ticker, report_types (list)
    Returns: Generated report paths and status
    """
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').upper().strip()
        report_types = data.get('report_types', [])

        if not ticker:
            return jsonify({'error': 'Ticker symbol is required'}), 400

        if not report_types:
            return jsonify({'error': 'At least one report type must be selected'}), 400

        results = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'reports': []
        }

        # Generate requested reports
        if 'fundamental' in report_types:
            try:
                report = generate_fundamental_report(ticker)
                result_item = {
                    'type': 'fundamental',
                    'status': 'success',
                    'path': report['path'],
                    'url': f'/api/report/{report["filename"]}',
                    'note': report.get('note')
                }
                if report.get('html_filename'):
                    result_item['html_url'] = f'/api/report/{report["html_filename"]}'
                results['reports'].append(result_item)
            except Exception as e:
                results['reports'].append({
                    'type': 'fundamental',
                    'status': 'error',
                    'error': str(e)
                })

        if 'technical' in report_types:
            try:
                report = generate_technical_report(ticker)
                result_item = {
                    'type': 'technical',
                    'status': 'success',
                    'path': report['path'],
                    'chart_path': report.get('chart_path'),
                    'url': f'/api/report/{report["filename"]}',
                    'chart_url': f'/api/report/{report.get("chart_filename")}' if report.get('chart_filename') else None
                }
                if report.get('html_filename'):
                    result_item['html_url'] = f'/api/report/{report["html_filename"]}'
                results['reports'].append(result_item)
            except Exception as e:
                results['reports'].append({
                    'type': 'technical',
                    'status': 'error',
                    'error': str(e)
                })

        # Scenario Analysis - Disabled for now
        # if 'action_plan' in report_types:
        #     try:
        #         report = generate_action_plan(ticker)
        #         result_item = {
        #             'type': 'action_plan',
        #             'status': 'success',
        #             'path': report['path'],
        #             'url': f'/api/report/{report["filename"]}'
        #         }
        #         if report.get('pdf_filename'):
        #             result_item['pdf_url'] = f'/api/report/{report["pdf_filename"]}'
        #         results['reports'].append(result_item)
        #     except Exception as e:
        #         results['reports'].append({
        #             'type': 'action_plan',
        #             'status': 'error',
        #             'error': str(e)
        #         })

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/report/<filename>')
def get_report(filename):
    """Serve generated report files"""
    try:
        file_path = app.config['REPORTS_DIR'] / filename
        if file_path.exists():
            return send_file(file_path, as_attachment=False)
        else:
            return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sector/generate', methods=['POST'])
def generate_sector():
    """Generate sector rotation analysis"""
    try:
        result = generate_sector_analysis()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Stock Analysis Web Application")
    print("=" * 60)

    # Support deployment platforms (Render, Railway, etc.)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') != 'production'

    print(f"Starting server on port {port}...")
    print(f"Debug mode: {debug}")
    if debug:
        print(f"Access the application at: http://localhost:{port}")
    print("=" * 60)

    app.run(debug=debug, host='0.0.0.0', port=port)
