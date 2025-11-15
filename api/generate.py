from http.server import BaseHTTPRequestHandler
import json
import html
from urllib.parse import urlparse

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
    
        # --- Build buttons with optional favicons ---
    def _domain_of(url):
        try:
            parsed = urlparse(url if url.startswith(('http://','https://')) else 'https://' + url)
            host = parsed.netloc or url
            # remove leading www.
            if host.startswith('www.'):
                host = host[4:]
            return host
        except Exception:
            return url

    buttons_parts = []
    for link in links:
        safe_url = html.escape(link["url"])
        safe_text = html.escape(link["text"])
        domain = html.escape(_domain_of(link["url"]))
        favicon_src = f'https://www.google.com/s2/favicons?domain={domain}'
        # a small inline img + text; keep button class as before
        buttons_parts.append(
            f'        <a href="{safe_url}" class="btn link-btn"{target_attr}>'
            f'<img src="{favicon_src}" alt="" style="width:18px;height:18px;vertical-align:middle;margin-right:10px;border-radius:4px;">'
            f'{safe_text}</a>'
        )
    buttons_html = '\n'.join(buttons_parts)

    # small copy-all button (placed before the list)
    copy_all_button_html = '''
        <button id="copyAllBtn" class="btn" style="margin-bottom:8px; font-size:13px; padding:8px 12px;" onclick="copyAll()">📋 Copy all links</button>
    '''

    
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
        script_html = f'''
    <script>
        const MAX_LINKS = {num_links}; 

        function openRange() {{
            const start = parseInt(document.getElementById('start-link').value, 10);
            const end = parseInt(document.getElementById('end-link').value, 10);
            
            if (isNaN(start) || isNaN(end) || start < 1 || end > MAX_LINKS || start > end) {{
                // **** THIS LINE IS FIXED ****
                // I've escaped the ${...} by doubling the {{...}}
                // This tells Python to ignore it, so JavaScript can read it.
                alert(`Invalid range. Please enter numbers between 1 and ${{MAX_LINKS}}.`);
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

        # small script always included for copy and other small utilities
    universal_script = '''
    <script>
    function copyAll() {
        try {
            const links = Array.from(document.querySelectorAll('.link-btn'));
            if (links.length === 0) {
                alert('No links to copy');
                return;
            }
            const lines = links.map(a => {
                // get visible text and href
                const text = (a.textContent || a.innerText || '').trim();
                const href = a.href || a.getAttribute('href') || '';
                return `${text} → ${href}`;
            });
            const payload = lines.join('\\n');
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(payload).then(()=> {
                    alert('All links copied to clipboard');
                }).catch(()=> {
                    fallbackCopy(payload);
                });
            } else {
                fallbackCopy(payload);
            }
        } catch (err) {
            alert('Copy failed: ' + err);
        }
    }
    function fallbackCopy(text) {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.left = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        try {
            document.execCommand('copy');
            alert('All links copied (fallback)');
        } catch (e) {
            alert('Could not copy automatically — please select and copy manually.');
        }
        document.body.removeChild(ta);
    }
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
{universal_script}
</body>
</html>'''
    
    return html_output
