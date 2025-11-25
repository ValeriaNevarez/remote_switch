import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

def handler(request):
    """Vercel serverless function handler for cron job"""
    try:
        # Get the path to helloworld.py
        # From app/api/cron/helloworld.py to python/helloworld.py
        current_dir = Path(__file__).parent
        script_path = current_dir.parent.parent.parent / 'python' / 'helloworld.py'
        
        # Execute the Python script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        error = result.stderr
        
        if result.returncode != 0:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'error': error or 'Script execution failed',
                    'output': output,
                    'timestamp': datetime.now().isoformat()
                })
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'message': 'Script executed successfully',
                'output': output,
                'timestamp': datetime.now().isoformat()
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

