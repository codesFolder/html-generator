from http.server import BaseHTTPRequestHandler
import json
import html

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
            open_in_new_tab = data.get('openInNewTab', True) 
            
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
            
            # Generate HTML, passing the new option
            html_content = generate_html_page(heading, links, open_in_new_tab)
            
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


# --- CORRECTED FUNCTION ---
def generate_html_page(heading, links, open_in_new_tab=True):
    """Generate the HTML page with heading and buttons"""
    
    safe_heading = html.escape(heading)
    target_attr = ' target="_blank" rel="noopener noreferrer"' if open_in_new_tab else ''
    
    buttons_html = '\n'.join([
        f'        <a href="{html.escape(link["url"])}" class="btn link-btn"{target_attr}>{html.escape(link["text"])}</a>'
        for link in links
    ])
    
    num_links = len(links)
    
    # 3. Generate the range opener HTML
    range_opener_html = ''
    if num_links > 1:
        range_opener_html = f'''
        <div class="range-opener">
            <label>Open Range:</label>
            <div>
                <label for="start-link">From</label>
                <input type="number" id="start-link" placeholder="1" min="1" value="1">
            </div>
            <div>
                <label for="end-link">To</label>
                <input type="number" id="end-link" placeholder="{num_links}" min="1" value="{num_links}">
            </div>
            <button class="btn-open" onclick="openRange()">🚀 Open</button>
        </div>
        '''

    # 4. Generate the script (only if range opener is present)
    script_html = ''
    if num_links > 1:
        # --- THIS BLOCK IS FIXED ---
        # Pass the Python 'num_links' variable directly into a JavaScript constant.
        # This avoids all DOM querying and fixes the NameError.
        script_html = f'''
    <script>
        const MAX_LINKS = {num_links}; 

        function openRange() {{
            const start = parseInt(document.getElementById('start-link').value, 10);
            const end = parseInt(document.getElementById('end-link').value, 10);
            
            if (isNaN(start) || isNaN(end) || start < 1 || end > MAX_LINKS || start > end) {{
                // This ${MAX_LINKS} is now a JS template literal, which is correct.
                alert(`Invalid range. Please enter numbers between 1 and ${MAX_LINKS}.`);
                return;
            }}

            const links = document.querySelectorAll('.link-btn');
            
            for (let i = start - 1; i < end; i++) {{
                if (links[i] && links[i].href) {{
                    window.open(links[i].href, '_blank');
                }}
            }}
        }}
        
        // Set max value for inputs dynamically
        document.addEventListener('DOMContentLoaded', () => {{
            const startInput = document.getElementById('start-link');
            const endInput = document.getElementById('end-link');
            
            if (startInput) {{
                startInput.max = MAX_LINKS;
            }}
            if (endInput) {{
                endInput.max = MAX_LINKS;
            }}
        }});
    </script>
    '''

    # 5. Complete HTML template
    html_output = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_heading}</title>
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
        * {{ box-sizing: border-box; }}
        body {{
            margin: 0;
            padding: 40px 20px;
            font-family: var(--font-family-base);
            background-color: var(--color-background);
            color: var(--color-text);
        }}
        .container {{ max-width: 600px; margin: 0 auto; }}
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
        .btn:hover {{ background: var(--color-primary-hover); }}
        
        /* Styles for Range Opener */
        .range-opener {{
            background: rgba(var(--color-text), 0.05);
            border: 1px solid rgba(var(--color-text), 0.1);
            padding: 16px;
            border-radius: 8px;
            margin: -16px 0 32px 0;
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .range-opener label {{
            font-size: 14px;
            font-weight: 500;
            color: var(--color-text);
        }}
        .range-opener input[type="number"] {{
            width: 70px;
            padding: 8px 10px;
            border: 1px solid rgba(var(--color-text), 0.2);
            background: var(--color-background);
            color: var(--color-text);
            border-radius: 6px;
            font-family: var(--font-family-base);
            font-size: 14px;
            text-align: center;
        }}
        .range-opener .btn-open {{
            padding: 8px 14px;
            font-size: 13px;
            background: var(--color-primary);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
            margin-left: auto;
        }}
        .range-opener .btn-open:hover {{ background: var(--color-primary-hover); }}
        .range-opener > div {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        @media (max-width: 600px) {{
            .range-opener {{
                flex-direction: column;
                gap: 16px;
                align-items: stretch;
            }}
            .range-opener .btn-open {{ margin-left: 0; }}
            .range-opener > div {{ justify-content: space-between; }}
            .range-opener input[type="number"] {{ flex: 1; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{safe_heading}</h1>
{range_opener_html}
{buttons_html}
    </div>
{script_html}
</body>
</html>'''
    
    return html_output
