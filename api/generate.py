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
            theme = data.get('theme', 'default') 
            
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
            html_content = generate_html_page(heading, links, open_in_new_tab, theme)
            
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


# --- THEME TEMPLATES ---
# By separating templates, we can easily add more themes in the future.

def get_default_theme_template():
    # This is your original theme's HTML structure
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_heading}</title>
    <style>
        :root {{
            --color-background: #fcfcf9; --color-text: #13343b; --color-primary: #21808d;
            --color-primary-hover: #1d7480; --font-family-base: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        @media (prefers-color-scheme: dark) {{ :root {{
            --color-background: #1f2121; --color-text: #f5f5f5; --color-primary: #32b8c6; --color-primary-hover: #2da6b2;
        }} }}
        * {{ box-sizing: border-box; }} body {{ margin: 0; padding: 40px 20px; font-family: var(--font-family-base); background-color: var(--color-background); color: var(--color-text); }}
        .container {{ max-width: 600px; margin: 0 auto; }} h1 {{ margin: 0 0 32px 0; font-size: 24px; font-weight: 600; text-align: center; }}
        .btn {{ display: block; width: 100%; padding: 12px 16px; margin-bottom: 12px; background: var(--color-primary); color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; text-align: center; text-decoration: none; cursor: pointer; transition: background 0.2s; }}
        .btn:hover {{ background: var(--color-primary-hover); }} .range-opener {{ background: rgba(var(--color-text), 0.05); border: 1px solid rgba(var(--color-text), 0.1); padding: 16px; border-radius: 8px; margin: -16px 0 32px 0; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }}
        .range-opener label {{ font-size: 14px; font-weight: 500; color: var(--color-text); }}
        .range-opener input[type="number"] {{ width: 70px; padding: 8px 10px; border: 1px solid rgba(var(--color-text), 0.2); background: var(--color-background); color: var(--color-text); border-radius: 6px; font-family: var(--font-family-base); font-size: 14px; text-align: center; }}
        .range-opener .btn-open {{ padding: 8px 14px; font-size: 13px; background: var(--color-primary); color: white; border: none; border-radius: 6px; cursor: pointer; transition: background 0.2s; margin-left: auto; }}
        .range-opener .btn-open:hover {{ background: var(--color-primary-hover); }} .range-opener > div {{ display: flex; align-items: center; gap: 8px; }}
        @media (max-width: 600px) {{ .range-opener {{ flex-direction: column; gap: 16px; align-items: stretch; }} .range-opener .btn-open {{ margin-left: 0; }} .range-opener > div {{ justify-content: space-between; }} .range-opener input[type="number"] {{ flex: 1; }} }}
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

def get_aurora_theme_template():
    # Aurora theme HTML structure
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_heading}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{ --font-family-main: 'Manrope', sans-serif; --aurora-gradient: linear-gradient(125deg, #0d324d, #7f5a83, #c96567); --color-bg: #101118; --color-surface: rgba(255, 255, 255, 0.05); --color-surface-hover: rgba(255, 255, 255, 0.1); --color-border: rgba(255, 255, 255, 0.1); --color-text-primary: #f0f0f5; --color-text-secondary: #a0a0b0; --border-radius-lg: 16px; --border-radius-md: 12px; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: var(--font-family-main); background-color: var(--color-bg); color: var(--color-text-primary); background-image: var(--aurora-gradient); background-size: 300% 300%; animation: aurora-animation 20s ease infinite; display: flex; justify-content: center; align-items: flex-start; min-height: 100vh; padding: 5vh 20px; }}
        @keyframes aurora-animation {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        .container {{ width: 100%; max-width: 600px; background: var(--color-surface); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid var(--color-border); border-radius: var(--border-radius-lg); padding: 32px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2); }}
        h1 {{ font-size: 28px; font-weight: 700; text-align: center; margin-bottom: 24px; letter-spacing: 1px; }}
        .range-opener {{ display: flex; align-items: center; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; padding: 16px; background: rgba(0,0,0,0.2); border-radius: var(--border-radius-md); }}
        .range-opener .controls {{ display: flex; flex-grow: 1; gap: 12px; align-items: center; }} .range-opener .control-group {{ display: flex; align-items: center; gap: 8px; }}
        .range-opener label {{ font-size: 14px; color: var(--color-text-secondary); }}
        .range-opener input[type="number"] {{ width: 55px; padding: 8px; background: transparent; border: 1px solid var(--color-border); border-radius: 8px; color: var(--color-text-primary); font-family: var(--font-family-main); font-size: 14px; text-align: center; transition: border-color 0.3s, box-shadow 0.3s; }}
        .range-opener input[type="number"]:focus {{ outline: none; border-color: rgba(255, 255, 255, 0.5); box-shadow: 0 0 10px rgba(255, 255, 255, 0.1); }}
        .btn-open {{ padding: 10px 18px; font-size: 14px; font-weight: 600; color: var(--color-text-primary); background: var(--aurora-gradient); background-size: 200% 200%; border: none; border-radius: 8px; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s, background-position 0.5s; }}
        .btn-open:hover {{ transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2); background-position: right center; }}
        .link-list {{ display: flex; flex-direction: column; gap: 12px; }}
        .link-item {{ display: flex; align-items: center; padding: 16px; background: transparent; border: 1px solid var(--color-border); border-radius: var(--border-radius-md); text-decoration: none; color: var(--color-text-primary); font-size: 16px; font-weight: 500; position: relative; overflow: hidden; transition: background-color 0.3s ease, transform 0.2s ease; }}
        .link-item::before {{ content: ''; position: absolute; top: 0; right: 0; bottom: 0; left: 0; z-index: -1; margin: -2px; border-radius: inherit; background: var(--aurora-gradient); opacity: 0; transition: opacity 0.3s ease; }}
        .link-item:hover {{ background-color: var(--color-surface-hover); transform: scale(1.02); }} .link-item:hover::before {{ opacity: 1; }}
        .link-item .icon {{ flex-shrink: 0; width: 22px; height: 22px; margin-right: 16px; color: var(--color-text-secondary); transition: color 0.3s; }}
        .link-item:hover .icon {{ color: var(--color-text-primary); }} .link-item .number {{ color: var(--color-text-secondary); font-weight: 400; margin-right: 8px; }}
        @media (max-width: 550px) {{ h1 {{ font-size: 24px; }} .container {{ padding: 24px; }} .range-opener {{ flex-direction: column; align-items: stretch; }} .range-opener .controls {{ justify-content: space-between; }} .btn-open {{ width: 100%; text-align: center; justify-content: center; }} }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{safe_heading}</h1>
        {range_opener_html}
        <div class="link-list">
            {buttons_html}
        </div>
    </div>
    {script_html}
</body>
</html>'''

def get_neon_grid_theme_template():
    # Neon Grid theme HTML structure
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_heading}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{ --font-family-mono: 'Fira Code', monospace; --color-bg: #0a0a14; --color-grid: rgba(0, 255, 255, 0.1); --color-primary: #00ffff; --color-secondary: #ff00ff; --color-text: #e0e0ff; --color-text-dim: #8888aa; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: var(--font-family-mono); background-color: var(--color-bg); color: var(--color-text); background-image: linear-gradient(to right, var(--color-grid) 1px, transparent 1px), linear-gradient(to bottom, var(--color-grid) 1px, transparent 1px); background-size: 40px 40px; display: flex; justify-content: center; align-items: flex-start; min-height: 100vh; padding: 5vh 20px; overflow: hidden; position: relative; }}
        body::before {{ content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(to bottom, rgba(10, 10, 20, 0) 0%, rgba(10, 10, 20, 0.5) 50%, rgba(10, 10, 20, 0) 100%); animation: scanline 8s linear infinite; pointer-events: none; z-index: 1; }}
        @keyframes scanline {{ 0% {{ transform: translateY(-100%); }} 100% {{ transform: translateY(100%); }} }}
        .container {{ width: 100%; max-width: 650px; padding: 32px; background: rgba(10, 10, 20, 0.6); border: 1px solid rgba(0, 255, 255, 0.2); box-shadow: 0 0 25px rgba(0, 255, 255, 0.1); backdrop-filter: blur(4px); z-index: 2; }}
        h1 {{ font-size: 28px; font-weight: 600; text-align: center; margin-bottom: 32px; text-transform: uppercase; letter-spacing: 3px; text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px var(--color-primary), 0 0 30px var(--color-primary); }}
        .range-opener {{ display: flex; align-items: center; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; border: 1px solid rgba(0, 255, 255, 0.2); padding: 16px; }}
        .range-opener .controls {{ display: flex; flex-grow: 1; gap: 12px; align-items: center; }}
        .range-opener label {{ font-size: 14px; color: var(--color-text-dim); text-transform: uppercase; }}
        .range-opener input {{ width: 60px; padding: 8px; background: transparent; border: 1px solid var(--color-text-dim); color: var(--color-text); font-family: var(--font-family-mono); font-size: 14px; text-align: center; transition: border-color 0.3s, box-shadow 0.3s; }}
        .range-opener input:focus {{ outline: none; border-color: var(--color-primary); box-shadow: 0 0 10px var(--color-primary); }}
        .btn-open {{ padding: 10px 18px; font-size: 14px; font-weight: 600; font-family: var(--font-family-mono); color: var(--color-bg); background-color: var(--color-primary); border: 1px solid var(--color-primary); box-shadow: 0 0 15px var(--color-primary); text-transform: uppercase; cursor: pointer; transition: background-color 0.3s, color 0.3s, box-shadow 0.3s; }}
        .btn-open:hover {{ background-color: transparent; color: var(--color-primary); box-shadow: 0 0 25px var(--color-primary); }}
        .link-list {{ display: flex; flex-direction: column; gap: 16px; }}
        .link-btn {{ position: relative; display: block; padding: 16px; border: 1px solid var(--color-primary); color: var(--color-primary); text-decoration: none; text-align: center; font-size: 16px; transition: color 0.3s, background-color 0.3s, box-shadow 0.3s; }}
        .link-btn:hover {{ color: var(--color-bg); background-color: var(--color-primary); box-shadow: 0 0 20px var(--color-primary); }}
        .link-btn::before, .link-btn::after {{ content: attr(data-text); position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: var(--color-bg); overflow: hidden; opacity: 0; }}
        .link-btn::before {{ padding: 16px; color: var(--color-secondary); animation: glitch-top 1s linear infinite; clip-path: polygon(0 0, 100% 0, 100% 33%, 0 33%); -webkit-clip-path: polygon(0 0, 100% 0, 100% 33%, 0 33%); }}
        .link-btn::after {{ padding: 16px; color: var(--color-primary); animation: glitch-bottom 1.5s linear infinite; clip-path: polygon(0 67%, 100% 67%, 100% 100%, 0 100%); -webkit-clip-path: polygon(0 67%, 100% 67%, 100% 100%, 0 100%); }}
        .link-btn:hover::before, .link-btn:hover::after {{ opacity: 1; background: transparent; }}
        @keyframes glitch-top {{ 2%, 64% {{ transform: translate(2px, -2px); }} 4%, 60% {{ transform: translate(-2px, 2px); }} 62% {{ transform: translate(12px, -1px) skew(-13deg); }} }}
        @keyframes glitch-bottom {{ 2%, 64% {{ transform: translate(-2px, 0); }} 4%, 60% {{ transform: translate(-2px, 0); }} 62% {{ transform: translate(-22px, 5px) skew(21deg); }} }}
        @media (max-width: 550px) {{ h1 {{ font-size: 22px; }} .container {{ padding: 24px; }} .range-opener {{ flex-direction: column; align-items: stretch; }} .range-opener .controls {{ justify-content: space-between; }} .btn-open {{ width: 100%; text-align: center; }} }}
    </style>
</head>
<body>
    <div class="container">
        <h1>// {safe_heading} //</h1>
        {range_opener_html}
        <div class="link-list">
            {buttons_html}
        </div>
    </div>
    {script_html}
</body>
</html>'''


# --- MAIN GENERATOR FUNCTION ---

def generate_html_page(heading, links, open_in_new_tab=True, theme='default'):
    """Generate the HTML page with a selected theme."""
    
    safe_heading = html.escape(heading)
    target_attr = ' target="_blank" rel="noopener noreferrer"' if open_in_new_tab else ''
    num_links = len(links)

    # 1. Generate theme-specific HTML for buttons
    buttons_html = ''
    if theme == 'aurora':
        # Aurora uses 'link-item' and has a number span
        buttons_html = '\n'.join([
            f'''            <a href="{html.escape(link["url"])}" class="link-item"{target_attr}>
                <svg class="icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244" /></svg>
                <span class="text"><span class="number">{idx + 1}.</span> {html.escape(link["text"])}</span>
            </a>'''
            for idx, link in enumerate(links)
        ])
    elif theme == 'neon_grid':
        # Neon Grid uses 'link-btn' and a data-text attribute for the glitch effect
        buttons_html = '\n'.join([
            f'''            <a href="{html.escape(link["url"])}" class="link-btn"{target_attr} data-text="{html.escape(link["text"])}">
                {html.escape(link["text"])}
            </a>'''
            for link in links
        ])
    else: # Default theme
        buttons_html = '\n'.join([
            f'        <a href="{html.escape(link["url"])}" class="btn link-btn"{target_attr}>{html.escape(link["text"])}</a>'
            for link in links
        ])

    # 2. Generate theme-specific HTML for the range opener
    range_opener_html = ''
    if num_links > 1:
        if theme == 'aurora':
            range_opener_html = f'''
        <div class="range-opener">
            <div class="controls">
                <div class="control-group"><label for="start-link">From</label><input type="number" id="start-link" value="1" min="1"></div>
                <div class="control-group"><label for="end-link">To</label><input type="number" id="end-link" value="{num_links}" min="1"></div>
            </div>
            <button class="btn-open" onclick="openRange()">🚀 Open Range</button>
        </div>'''
        elif theme == 'neon_grid':
            range_opener_html = f'''
        <div class="range-opener">
            <div class="controls">
                <label for="start-link">Range:</label><input type="number" id="start-link" value="1" min="1">
                <label for="end-link">to</label><input type="number" id="end-link" value="{num_links}" min="1">
            </div>
            <button class="btn-open" onclick="openRange()">Execute</button>
        </div>'''
        else: # Default theme
            range_opener_html = f'''
        <div class="range-opener">
            <label>Open Range:</label>
            <div><label for="start-link">From</label><input type="number" id="start-link" value="1" min="1"></div>
            <div><label for="end-link">To</label><input type="number" id="end-link" value="{num_links}" min="1"></div>
            <button class="btn-open" onclick="openRange()">🚀 Open</button>
        </div>'''

    # 3. Generate script (adapts to the correct link class)
    script_html = ''
    if num_links > 1:
        link_class_selector = ".link-item" if theme == 'aurora' else ".link-btn"
        alert_message = f"> ACCESS DENIED: Invalid range. Please enter numbers between 1 and ${{MAX_LINKS}}." if theme == 'neon_grid' else f"Invalid range. Please enter numbers between 1 and ${{MAX_LINKS}}."
        
        script_html = f'''
    <script>
        const MAX_LINKS = {num_links}; 
        function openRange() {{
            const start = parseInt(document.getElementById('start-link').value, 10);
            const end = parseInt(document.getElementById('end-link').value, 10);
            if (isNaN(start) || isNaN(end) || start < 1 || end > MAX_LINKS || start > end) {{
                alert(`{alert_message}`);
                return;
            }}
            const links = document.querySelectorAll('{link_class_selector}');
            for (let i = start - 1; i < end; i++) {{
                if (links[i] && links[i].href) {{ window.open(links[i].href, '_blank'); }}
            }}
        }}
        document.addEventListener('DOMContentLoaded', () => {{
            const startInput = document.getElementById('start-link');
            const endInput = document.getElementById('end-link');
            if (startInput) {{ startInput.max = MAX_LINKS; }}
            if (endInput) {{ endInput.max = MAX_LINKS; }}
        }});
    </script>'''

    # 4. Select the main HTML template based on the theme
    templates = {
        'default': get_default_theme_template(),
        'aurora': get_aurora_theme_template(),
        'neon_grid': get_neon_grid_theme_template()
    }
    # Fallback to default theme if an unknown theme is passed
    html_template = templates.get(theme, templates['default'])

    # 5. Populate the template and return
    return html_template.format(
        safe_heading=safe_heading,
        range_opener_html=range_opener_html,
        buttons_html=buttons_html,
        script_html=script_html
    )