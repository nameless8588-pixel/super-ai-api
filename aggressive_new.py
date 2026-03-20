@app.get("/aggressive")
def aggressive_attack(url: str, key: str = Depends(verify_key)):
    import requests
    from urllib.parse import urljoin
    import time

    start_time = time.time()
    results = []

    results.append("‚ö†Ô∏è ETHICAL USE ONLY: Test only your own websites!")
    
    # Header analysis
    try:
        r = requests.get(url, timeout=10)
        missing = [h for h in ['X-Frame-Options', 'X-Content-Type-Options', 'Strict-Transport-Security', 'Content-Security-Policy'] if h not in r.headers]
        results.append(f"‚ùå Missing headers: {', '.join(missing)}" if missing else "‚úÖ Security headers present")
    except Exception as e:
        results.append(f"‚ùå Header error: {e}")

    # XSS
    xss_payloads = ['<script>alert(1)</script>', '<img src=x onerror=alert(1)>']
    xss_found = []
    for p in xss_payloads:
        try:
            test_url = url + ('?q=' + p if '?' not in url else '&q=' + p)
            r = requests.get(test_url, timeout=10)
            if p in r.text:
                xss_found.append(p)
        except:
            pass
    results.append(f"Ì¥¥ XSS: {', '.join(xss_found)}" if xss_found else "‚úÖ No XSS")

    # SQLi
    sqli_payloads = ["' OR '1'='1", "admin'--"]
    sqli_found = []
    for p in sqli_payloads:
        try:
            test_url = url + ('?id=' + p if '?' not in url else '&id=' + p)
            r = requests.get(test_url, timeout=10)
            if 'sql' in r.text.lower() or 'mysql' in r.text.lower():
                sqli_found.append(p)
        except:
            pass
    results.append(f"Ì¥¥ SQLi: {', '.join(sqli_found)}" if sqli_found else "‚úÖ No SQLi")

    # Directory scan
    dirs = ['admin', 'backup', '.env', 'robots.txt']
    found = []
    for d in dirs:
        try:
            r = requests.get(urljoin(url, d), timeout=5)
            if r.status_code == 200:
                found.append(d)
        except:
            pass
    results.append(f"Ì≥Å Found: {', '.join(found)}" if found else "‚úÖ No sensitive files")

    # SSL
    if url.startswith('https'):
        try:
            import ssl, socket
            host = url.split('/')[2]
            ctx = ssl.create_default_context()
            with socket.create_connection((host, 443), timeout=5) as sock:
                ctx.wrap_socket(sock, server_hostname=host)
                results.append("‚úÖ SSL OK")
        except:
            results.append("‚ùå SSL issue")

    # AI analysis
    prompt = f"Target: {url}\nResults:\n" + "\n".join(results) + "\n\nBatao: kya vulnerabilities? Kaunsa attack successful? Top 3 fixes? Hinglish mein short."
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )
    return {
        "url": url,
        "test_results": results,
        "ai_analysis": resp.choices[0].message.content.strip(),
        "response_time": f"{round(time.time()-start_time, 2)}s"
    }
