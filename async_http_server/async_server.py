import socket
try:
    print("Running embeded")
    embedded = True
    import uasyncio as asyncio
    import uselect as select
except ImportError:
    print("RUnning normal")
    embedded = False
    import select
    import asyncio

import json

router = {}

async def handle_client(reader, writer):
    request = (await reader.read(1024)).decode('utf8')
    request = [str(i.strip()) for i in request.split("\n")]
    method, uri, http_version = request[0].split(" ")
    body = None
    if method == "POST":
        content_type = None
        for i in request:
            if i.startswith("Content-Type"):
                content_type = i.split("Content-Type:")[1].split(";")[0].strip()
                break

        body = request[-1]
        if content_type == "application/x-www-form-urlencoded":
            body_params = {}
            for form_element in body.split("&"):
                k, v = form_element.split("=")
                body_params[k] = v
            body = body_params
        elif content_type == "application/json":
            body = json.loads(body)

    params = {}
    if "?" in uri:
        path, query = uri.split("?")
        query = query.split("&")

        for p in query:
            k, v = p.split("=")
            params[k] = v
    else:
        path = uri

    log_info = "[{method}] {path}".format(method=method, path=path)
    path = path.rstrip("/")
    if path in router:
        try:
            response, code = router[path](params, body)
        except Exception as e:
            response = {
                "error": str(e)
            }
            code = 500
    else:
        # file_path = "assets" + os.path.normpath(path)
        # micropython does not have os.path
        file_path = "www" + path.replace("../", "")
        try:
            with open(file_path, "r") as f:
                response = f.read()
            code = "200"
        except Exception:
            code = "404"
            response = {"error": "Not found"}

    if isinstance(response, str):
        content_type = "text/html"
        response = response.encode()
    elif isinstance(response, dict):
        content_type = "application/json"
        response = json.dumps(response).encode()
    else:
        content_type = "unknown"

    headers = 'HTTP/1.1 {code} OK\nContent-Type: {content_type}\nContent-Length: {content_length}\nConnection: close\n\n'.format(code=code, content_type=content_type, content_length=len(response)).encode()
    if embedded:
        await writer.awrite(headers)
        await writer.awrite(response)
        await writer.aclose()
    else:
        writer.write(headers)
        writer.write(response)
        writer.close()

    print("{log_info} [{code}]".format(log_info=log_info, code=code))

