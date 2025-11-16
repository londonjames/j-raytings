# Minimal test function to verify Python works on Vercel
def handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': '{"status": "ok", "message": "Python function works!"}'
    }

