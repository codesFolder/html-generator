from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """API health check"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok', 'message': 'HTML Generator API is running'}).encode())
    
    def do_POST(self):
        """Generate HTML file"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Extract data
            heading = data.get('heading', 'Quick Links')
            links = data.get('links', [])
            
            # Validation
            if not heading or not heading.strip():
                raise ValueError('Heading is required')
            
            if not links or len(links) == 0:
                raise ValueError('At least one link is required')
            
            # Validate each link
            for idx, link in enumerate(links):
                if not link.get('text') or not link.get('text').strip():
                    raise ValueError(f'Link {idx + 1} is missing text')
                if not link.get('url') or not link.get('url').strip():
                    raise ValueError(f'Link {idx + 1} is missing URL')
            
            # Generate HTML
            html_content = generate_html_page(heading, links)
            
            # Send HTML file
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Content-Disposition', 'attachment; filename="page.html"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(html_content.encode('utf-8'))
            
        except ValueError as e:
            # Validation errors
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
        
        except Exception as e:
            # Server errors
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': f'Server error: {str(e)}'}).encode())


def generate_html_page(heading, links):
    """Generate the HTML page with heading and buttons"""
    
    # Generate button HTML
    buttons_html = '\n'.join([
        f'        <a href="{link["url"]}" class="btn">{link["text"]}</a>'
        for link in links
    ])
    
    # Complete HTML template
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{heading}</title>
    <style>
        :root {{
            --color-background: #fcfcf9;
            --color-text: #13343b;
            --color-primary: #21808d;
            --color-primary-hover: #1d7480;
            --font-family-base: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --color-background: #1f2121;
                --color-text: #f5f5f5;
                --color-primary: #32b8c6;
                --color-primary-hover: #2da6b2;
            }}
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 40px 20px;
            font-family: var(--font-family-base);
            background-color: var(--color-background);
            color: var(--color-text);
        }}

        .container {{
            max-width: 600px;
            margin: 0 auto;
        }}

        h1 {{
            margin: 0 0 32px 0;
            font-size: 24px;
            font-weight: 600;
            text-align: center;
        }}

        .btn {{
            display: block;
            width: 100%;
            padding: 12px 16px;
            margin-bottom: 12px;
            background: var(--color-primary);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            text-align: center;
            text-decoration: none;
            cursor: pointer;
            transition: background 0.2s;
        }}

        .btn:hover {{
            background: var(--color-primary-hover);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{heading}</h1>
{buttons_html}
    </div>
</body>
</html>'''
    
    return html
