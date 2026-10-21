"""
app.py - Flask Web Server for DevLang Compiler Web Application.
Bridges the web frontend to the existing Python compiler backend (main.py).
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from main import compile_devlang

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/compile', methods=['POST'])
def compile_code():
    data = request.get_json()
    source_code = data.get('code', '')
    
    # Aapka existing backend compiler orchestrator call ho raha hai
    result = compile_devlang(source_code)
    
    return jsonify({
        'success': result.success,
        'failed_phase': result.failed_phase,
        'tokens': [{'type': t.type.name, 'value': str(t.value), 'line': t.line, 'col': t.column} for t in result.tokens],
        'ast': result.ast_representation,
        'symbol_table': result.symbol_table_dump,
        'tac': result.tac_instructions,
        'error_report': result.error_report
    })

if __name__ == '__main__':
    print("Starting DevLang Web Server on http://127.0.0.1:5000")
    app.run(port=5000, debug=True)