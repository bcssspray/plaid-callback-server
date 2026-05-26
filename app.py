from flask import Flask, request, jsonify
import os
import json

app = Flask(__name__)

# In-memory stores
latest_token = {"link_token": None}
pending_tokens = {}  # item_id -> public_token

@app.route('/callback')
def callback():
    html = """<!DOCTYPE html>
<html>
<head>
<title>Credit Card Tracker — Completing link</title>
<script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
<style>
  body { font-family: -apple-system, sans-serif; background: #0a0a0f; color: #fff;
         display: flex; align-items: center; justify-content: center;
         height: 100vh; margin: 0; text-align: center; }
  h2 { margin-bottom: 0.5rem; }
  p { color: #888; margin: 0.25rem 0; }
  .token-box { margin-top: 1.5rem; background: #1a1a2e; border: 1px solid #333;
                border-radius: 8px; padding: 1rem 1.5rem; word-break: break-all;
                font-family: monospace; font-size: 13px; color: #4ade80; }
  .label { font-size: 12px; color: #666; margin-bottom: 0.5rem; }
</style>
</head>
<body>
<div id="root">
  <h2>Completing link...</h2>
  <p>Please wait.</p>
</div>
<script>
fetch('/get_token')
  .then(r => r.json())
  .then(data => {
    if (!data.link_token) {
      document.getElementById('root').innerHTML =
        '<h2 style="color:#f87171">No link token found</h2>' +
        '<p>Please restart link_accounts.py and try again.</p>';
      return;
    }
    var handler = Plaid.create({
      token: data.link_token,
      receivedRedirectUri: window.location.href,
      onSuccess: function(public_token, metadata) {
        var inst = metadata.institution ? metadata.institution.name : 'Unknown Bank';
        document.getElementById('root').innerHTML =
          '<h2 style="color:#4ade80">✅ ' + inst + ' authenticated!</h2>' +
          '<p>Copy the token below and paste it into Terminal when prompted.</p>' +
          '<div class="token-box">' +
            '<div class="label">Institution: ' + inst + '</div>' +
            '<div>' + public_token + '</div>' +
          '</div>' +
          '<p style="margin-top:1rem;font-size:13px;">After pasting in Terminal, you can close this tab.</p>';
      },
      onExit: function(err) {
        document.getElementById('root').innerHTML =
          '<h2 style="color:' + (err ? '#f87171' : '#888') + '">' +
          (err ? '❌ Error' : 'Cancelled') + '</h2>' +
          '<p>' + (err ? (err.display_message || JSON.stringify(err)) : 'Close this tab and try again.') + '</p>';
      }
    });
    handler.open();
  });
</script>
</body>
</html>"""
    return html


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json(silent=True) or {}
    webhook_type = data.get('webhook_type')
    webhook_code = data.get('webhook_code')
    
    print(f"Webhook received: {webhook_type}/{webhook_code}")
    print(json.dumps(data, indent=2))

    # Handle OAuth completion webhook
    if webhook_type == 'ITEM' and webhook_code == 'PENDING_EXPIRATION':
        pass
    elif webhook_type == 'LINK' and webhook_code == 'SESSION_FINISHED':
        public_token = data.get('public_token')
        item_id = data.get('item_id', 'latest')
        institution = data.get('institution', {}).get('name', 'Unknown')
        if public_token:
            pending_tokens[item_id] = {
                'public_token': public_token,
                'institution': institution
            }
            print(f"Stored public_token for {institution}")

    return jsonify({'status': 'ok'})


@app.route('/store_token')
def store_token():
    link_token = request.args.get('link_token')
    if link_token:
        latest_token["link_token"] = link_token
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'}), 400


@app.route('/get_token')
def get_token():
    return jsonify({'link_token': latest_token.get("link_token")})


@app.route('/get_pending')
def get_pending():
    """Poll this to check if a public_token arrived via webhook."""
    return jsonify(pending_tokens)


@app.route('/clear_pending')
def clear_pending():
    pending_tokens.clear()
    return jsonify({'status': 'ok'})


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
