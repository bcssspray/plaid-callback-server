from flask import Flask, request, jsonify
import os

app = Flask(__name__)

LINK_TOKENS = {}

@app.route('/callback')
def callback():
    received_uri = request.url
    link_token = request.args.get('link_token', '')

    html = f"""<!DOCTYPE html>
<html>
<head>
<title>Credit Card Tracker — Completing link</title>
<script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
<style>
  body {{ font-family: -apple-system, sans-serif; background: #0a0a0f; color: #fff;
         display: flex; align-items: center; justify-content: center;
         height: 100vh; margin: 0; text-align: center; }}
  h2 {{ margin-bottom: 0.5rem; }}
  p {{ color: #888; margin: 0.25rem 0; }}
  .token-box {{ margin-top: 1.5rem; background: #1a1a2e; border: 1px solid #333;
                border-radius: 8px; padding: 1rem 1.5rem; word-break: break-all;
                font-family: monospace; font-size: 13px; color: #4ade80; }}
  .label {{ font-size: 12px; color: #666; margin-bottom: 0.5rem; }}
</style>
</head>
<body>
<div id="root">
  <h2>Completing link...</h2>
  <p>Please wait.</p>
</div>
<script>
var storedToken = sessionStorage.getItem('plaid_link_token');
if (!storedToken) {{
  document.getElementById('root').innerHTML =
    '<h2 style="color:#f87171">❌ Error</h2>' +
    '<p>No link token found. Please restart link_accounts.py and try again.</p>';
}} else {{
  var handler = Plaid.create({{
    token: storedToken,
    receivedRedirectUri: window.location.href,
    onSuccess: function(public_token, metadata) {{
      var inst = metadata.institution ? metadata.institution.name : 'Unknown Bank';
      document.getElementById('root').innerHTML =
        '<h2 style="color:#4ade80">✅ ' + inst + ' authenticated!</h2>' +
        '<p>Copy the token below and paste it into Terminal when prompted.</p>' +
        '<div class="token-box">' +
          '<div class="label">Institution: ' + inst + '</div>' +
          '<div>' + public_token + '</div>' +
        '</div>' +
        '<p style="margin-top:1rem;font-size:13px;">After pasting in Terminal, you can close this tab.</p>';
    }},
    onExit: function(err) {{
      document.getElementById('root').innerHTML =
        '<h2 style="color:' + (err ? '#f87171' : '#888') + '">' +
        (err ? '❌ Error' : 'Cancelled') + '</h2>' +
        '<p>' + (err ? (err.display_message || JSON.stringify(err)) : 'Close this tab and try again.') + '</p>';
    }}
  }});
  handler.open();
}}
</script>
</body>
</html>"""
    return html


@app.route('/health')
def health():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
