# Minimal test function to verify Python works on Vercel
# Vercel Python functions receive (req, res) not (event, context)
def handler(req, res):
    res.status(200).json({
        'status': 'ok',
        'message': 'Python function works!'
    })

