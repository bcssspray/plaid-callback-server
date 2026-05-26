from flask import Flask, request
import os

app = Flask(__name__)

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
var params = new URLSearchParams(window.location.search);
var oauthStateId = params.get('oauth_state_id');

if (!oauthStateId) {
  document.getElementById('root').innerHTML =
    '<h2 style="color:#f87171">Missing oauth_state_id</h2>' +
    '<p>Please restart link_accounts.py and try again.</p>';
} else {
  fetch('/get_token?oauth_state_id=' + oauthStateId)
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
}
</script>
</body>
</html>"""
    return html


# In-memory store for link tokens keyed by oauth_state_id
token_store = {}

@app.route('/store_token')
def store_token():
    oauth_state_id = request.args.get('oauth_state_id')
    link_token = request.args.get('link_token')
    if oauth_state_id and link_token:
        token_store[oauth_state_id] = link_token
        return {'status': 'ok'}
    return {'status': 'error'}, 400

@app.route('/get_token')
def get_token():
    oauth_state_id = request.args.get('oauth_state_id')
    link_token = token_store.get(oauth_state_id)
    return {'link_token': link_token}

@app.route('/health')
def health():
    return {'status': 'ok'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
