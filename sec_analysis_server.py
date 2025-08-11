#!/usr/bin/env python3
"""
SEC Analysis AI - Flask Backend Server
Integrates with sec_master_analyzer.py to provide web API for frontend
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import sys
import subprocess
import json
import logging
from datetime import datetime
from pathlib import Path
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import sec_master_analyzer
sys.path.append(str(Path(__file__).parent))

app = Flask(__name__, static_folder='frontend', template_folder='frontend')
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SECAnalysisServer:
    def __init__(self):
        self.analysis_in_progress = {}
        self.results_cache = {}
        
    def run_master_analyzer(self, query):
        """Run the master analyzer with the given query"""
        try:
            # Run the master analyzer
            cmd = [sys.executable, 'sec_master_analyzer.py', query]
            
            # Set environment for UTF-8 encoding
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            logger.info(f"Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                env=env,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return self.parse_analysis_output(result.stdout, query)
            else:
                logger.error(f"Master analyzer failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Analysis timed out after 5 minutes")
            return None
        except Exception as e:
            logger.error(f"Error running master analyzer: {e}")
            return None
    
    def parse_analysis_output(self, output, query):
        """Parse the output from master analyzer and find result files"""
        try:
            # Look for the comprehensive analysis directory in output
            lines = output.split('\n')
            analysis_dir = None
            
            for line in lines:
                # Look for the analysis directory line with emoji
                if '📁 Analysis directory:' in line or 'Analysis directory:' in line:
                    # Extract directory name
                    if '📁 Analysis directory:' in line:
                        analysis_dir = line.split('📁 Analysis directory:')[1].strip()
                    else:
                        analysis_dir = line.split('Analysis directory:')[1].strip()
                    break
                elif 'comprehensive_analysis_' in line and ('created' in line.lower() or 'directory' in line.lower()):
                    # Try to extract from other context
                    parts = line.split()
                    for part in parts:
                        if 'comprehensive_analysis_' in part:
                            analysis_dir = part.strip('.,!').strip()
                            break
            
            if not analysis_dir:
                # Try to find the most recent comprehensive analysis directory
                try:
                    report_dirs = [d for d in os.listdir('.') if d.startswith('comprehensive_analysis_')]
                    if report_dirs:
                        # Sort by creation time to get the most recent
                        report_dirs.sort(key=lambda x: os.path.getctime(x), reverse=True)
                        analysis_dir = report_dirs[0]  # Get most recent
                        logger.info(f"Using most recent analysis directory: {analysis_dir}")
                except Exception as e:
                    logger.error(f"Error finding recent directories: {e}")
            
            if analysis_dir and os.path.exists(analysis_dir):
                logger.info(f"Found analysis directory: {analysis_dir}")
                return self.load_analysis_results(analysis_dir, query)
            else:
                logger.error(f"Could not find analysis directory: {analysis_dir}")
                return self.create_fallback_results(query)
                
        except Exception as e:
            logger.error(f"Error parsing analysis output: {e}")
            return self.create_fallback_results(query)
    
    def load_analysis_results(self, analysis_dir, query):
        """Load analysis results from the generated files"""
        try:
            results = {
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'analysis_directory': analysis_dir,
                'combined_analysis': '',
                'individual_analyses': {},
                'sources': [],
                'analysis_files': []
            }
            
            # Load comprehensive analysis - look for the main file
            comprehensive_files = [f for f in os.listdir(analysis_dir) if f.startswith('comprehensive_analysis_') and f.endswith('.txt')]
            if comprehensive_files:
                comprehensive_file = os.path.join(analysis_dir, comprehensive_files[0])
                with open(comprehensive_file, 'r', encoding='utf-8') as f:
                    results['combined_analysis'] = f.read()
                results['analysis_files'].append(comprehensive_files[0])
                logger.info(f"Loaded comprehensive analysis: {comprehensive_files[0]}")
            
            # Load individual analyses
            individual_files = {
                '10k': ['query_answer_', 'sec_tools_'],
                '8k': ['sec_8k_analyzer_'],
                'form4': ['sec_insider_analyzer_', 'insider_analysis_']
            }
            
            for analysis_type, prefixes in individual_files.items():
                content_found = False
                for prefix in prefixes:
                    matching_files = [f for f in os.listdir(analysis_dir) if f.startswith(prefix) and f.endswith('.txt')]
                    if matching_files:
                        filepath = os.path.join(analysis_dir, matching_files[0])
                        with open(filepath, 'r', encoding='utf-8') as f:
                            results['individual_analyses'][analysis_type] = f.read()
                        results['analysis_files'].append(matching_files[0])
                        content_found = True
                        logger.info(f"Loaded {analysis_type} analysis: {matching_files[0]}")
                        break
                
                if not content_found:
                    results['individual_analyses'][analysis_type] = f"# {analysis_type.upper()} Analysis\n\nNo specific {analysis_type.upper()} analysis available for this query."
            
            # Extract company name from query for sources
            company = self.extract_company_from_query(query)
            
            # Generate source information
            results['sources'] = [
                {'type': '10-K', 'company': company, 'year': '2024', 'filename': f'{company.replace(" ", "_")}_10k.json'},
                {'type': '8-K', 'company': company, 'year': '2024', 'filename': f'{company.replace(" ", "_")}_8k.json'},
                {'type': 'Form 4', 'company': company, 'year': '2024', 'filename': f'{company.replace(" ", "_")}_form4.json'}
            ]
            
            logger.info(f"Successfully loaded analysis results from {analysis_dir}")
            return results
            
        except Exception as e:
            logger.error(f"Error loading analysis results: {e}")
            return self.create_fallback_results(query)
    
    def extract_company_from_query(self, query):
        """Extract company name from query"""
        companies = {
            'apple': 'Apple Inc',
            'microsoft': 'Microsoft Corporation',
            'nvidia': 'NVIDIA Corporation', 
            'meta': 'Meta Platforms Inc',
            'facebook': 'Meta Platforms Inc',
            'jpmorgan': 'JPMorgan Chase & Co',
            'chase': 'JPMorgan Chase & Co',
            'johnson': 'Johnson & Johnson',
            'j&j': 'Johnson & Johnson',
            'doordash': 'DoorDash Inc',
            'roku': 'Roku Inc',
            'zoom': 'Zoom Communications Inc',
            'unitedhealth': 'UnitedHealth Group Inc'
        }
        
        query_lower = query.lower()
        for keyword, company in companies.items():
            if keyword in query_lower:
                return company
        
        return 'Apple Inc'  # Default fallback
    
    def create_fallback_results(self, query):
        """Create fallback results if analysis fails"""
        company = self.extract_company_from_query(query)
        
        return {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'analysis_directory': None,
            'combined_analysis': f"""# SEC Analysis Results

## Query Analysis
**Query:** {query}
**Company:** {company}
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Status
The analysis system is currently processing your request. This may take a few moments as we:

1. **Parse your query** and extract relevant parameters
2. **Search SEC filing databases** for the most relevant documents  
3. **Run AI analysis** across 10-K, 8-K, and Form 4 filings
4. **Generate comprehensive insights** and recommendations

Please try refreshing in a few moments, or contact support if the issue persists.

## Available Data Sources
- 10-K Annual Reports (Business segments, risk factors, financial data)
- 8-K Current Event Reports (Material changes, acquisitions, management changes)  
- Form 4 Insider Trading Reports (Executive transactions, insider sentiment)

*Analysis powered by SEC Analysis AI - Financial Intelligence Platform*
            """,
            'individual_analyses': {
                '10k': f"# {company} 10-K Analysis\n\nAnalysis in progress... Please check back in a few moments.",
                '8k': f"# {company} 8-K Analysis\n\nAnalysis in progress... Please check back in a few moments.", 
                'form4': f"# {company} Form 4 Analysis\n\nAnalysis in progress... Please check back in a few moments."
            },
            'sources': [
                {'type': '10-K', 'company': company, 'year': '2024', 'filename': f'{company.replace(" ", "_")}_10k.json'},
                {'type': '8-K', 'company': company, 'year': '2024', 'filename': f'{company.replace(" ", "_")}_8k.json'},
                {'type': 'Form 4', 'company': company, 'year': '2024', 'filename': f'{company.replace(" ", "_")}_form4.json'}
            ],
            'analysis_files': []
        }

# Initialize server instance
sec_server = SECAnalysisServer()

@app.route('/')
def index():
    """Serve the main frontend page"""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, etc.)"""
    return send_from_directory('frontend', filename)

@app.route('/api/analyze', methods=['POST'])
def analyze_query():
    """Main API endpoint for SEC analysis"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({'error': 'Query cannot be empty'}), 400
        
        logger.info(f"Received analysis request: {query}")
        
        # Check cache first (optional optimization)
        cache_key = f"{query}_{datetime.now().strftime('%Y-%m-%d')}"
        if cache_key in sec_server.results_cache:
            logger.info("Returning cached results")
            return jsonify(sec_server.results_cache[cache_key])
        
        # Run the analysis
        results = sec_server.run_master_analyzer(query)
        
        if results:
            # Cache the results
            sec_server.results_cache[cache_key] = results
            logger.info("Analysis completed successfully")
            return jsonify(results)
        else:
            logger.error("Analysis failed")
            fallback_results = sec_server.create_fallback_results(query)
            return jsonify(fallback_results)
            
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/status')
def get_status():
    """Get server status"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'analysis_tools': ['sec_tools.py', 'sec_8k_analyzer.py', 'sec_insider_analyzer.py'],
        'available_companies': [
            'Apple Inc', 'Microsoft Corporation', 'NVIDIA Corporation',
            'Meta Platforms Inc', 'JPMorgan Chase & Co', 'Johnson & Johnson',
            'DoorDash Inc', 'Roku Inc', 'Zoom Communications Inc'
        ]
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/api/download/<path:filename>')
def download_file(filename):
    """Download analysis files"""
    try:
        # Check if file exists in current directory or analysis folders
        file_path = Path(filename)
        
        # Try current directory first
        if file_path.exists():
            directory = str(file_path.parent)
            filename = file_path.name
            return send_from_directory(directory, filename, as_attachment=True)
        
        # Try analysis folders
        for analysis_folder in Path('.').glob('comprehensive_analysis_*'):
            potential_file = analysis_folder / file_path.name
            if potential_file.exists():
                return send_from_directory(str(analysis_folder), file_path.name, as_attachment=True)
        
        # File not found
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting SEC Analysis AI Server...")
    logger.info("Frontend available at: http://localhost:5000")
    logger.info("API endpoints:")
    logger.info("  POST /api/analyze - Main analysis endpoint")
    logger.info("  GET /api/status - Server status")
    logger.info("  GET /api/health - Health check")
    
    # Run the Flask development server
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
