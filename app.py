import requests
from flask import Flask, request, Response

app = Flask(__name__)

SKIP_HEADERS = {"host", "cf-connecting-ip", "x-forwarded-for",
                "x-real-ip", "accept-encoding", "connection", "transfer-encoding"}

@app.route("/", defaults={"path": ""}, methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/<path:path>", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"])
def proxy(path):
    target = request.args.get("url")
    if not target:
        return Response("url param eksik", status=400)

    headers = {k: v for k, v in request.headers if k.lower() not in SKIP_HEADERS}
    headers["Accept-Encoding"] = "identity"
    headers["Host"] = target.split("/")[2]  # domain kısmı

    body = request.get_data() or None

    resp = requests.request(
        method=request.method,
        url=target,
        headers=headers,
        data=body,
        allow_redirects=True,
        stream=True,
    )

    excluded = {"content-encoding", "transfer-encoding"}
    resp_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}
    resp_headers["Access-Control-Allow-Origin"] = "*"

    return Response(resp.iter_content(chunk_size=8192),
                    status=resp.status_code,
                    headers=resp_headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
