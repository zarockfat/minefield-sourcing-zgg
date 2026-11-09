#!/usr/bin/env python3
"""openboost MCP 直连小工具（绕过原生 connector 注册）

用法：
  python3 -I openboost_mcp.py list                  # 列出全部工具
  python3 -I openboost_mcp.py info                  # 账号/套餐/余额
  python3 -I openboost_mcp.py call <tool> '<json>'  # 调用工具
  python3 -I openboost_mcp.py schema <tool>         # 查看某工具入参 schema

密钥从环境变量 OPENBOOST_KEY 读取，不写死在文件里。
"""
import json
import os
import sys
import urllib.request

URL = "https://mcp.openboostai.com/mcp-servers/openboost-all-mcp"
KEY = os.environ.get("OPENBOOST_KEY", "")


def rpc(payload):
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "secret-key": KEY,
        },
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        body = r.read().decode()
    # 兼容 SSE 输出
    if body.lstrip().startswith("event:") or body.lstrip().startswith("data:"):
        for line in body.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip())
    return json.loads(body)


def initialize():
    return rpc({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "cowork", "version": "1.0"},
        },
    })


DOC_MARK = "### 原始响应 JSON"


def _extract_doc_wrapped(text):
    """部分专利接口返回「字段说明 markdown + 末尾内嵌原始 JSON」。

    形如：...### 原始响应 JSON（网关解析后的完整对象）\n      "{...}"
    这里把内嵌的那段 JSON 抠出来解析。
    """
    idx = text.rfind(DOC_MARK)
    if idx < 0:
        return None
    tail = text[idx:]
    start = tail.find("{" if '"' not in tail[:0] else '"')
    # 末尾是一个 JSON 字符串字面量，先按字面量解析再解析其内容
    q = tail.find('"')
    if q < 0:
        return None
    literal = tail[q:]
    try:
        inner = json.loads(literal if literal.endswith('"') else literal + '"')
        return json.loads(inner)
    except Exception:
        # 兜底：直接从第一个 { 到最后一个 }
        b, e = tail.find("{"), tail.rfind("}")
        if b >= 0 and e > b:
            try:
                return json.loads(tail[b:e + 1])
            except Exception:
                return None
    return None


def unwrap(res):
    """服务端把结果序列化了两层（偶尔是 markdown 文档包 JSON），逐层拆到 dict。"""
    if "error" in res:
        return {"error": res["error"]}
    r = res.get("result", {})
    text = r["content"][0]["text"] if r.get("content") else ""
    if r.get("isError"):
        return {"isError": True, "detail": text[:800]}
    if DOC_MARK in text:
        parsed = _extract_doc_wrapped(text)
        if parsed is not None:
            return parsed
    out = text
    for _ in range(3):
        if isinstance(out, str):
            try:
                out = json.loads(out)
            except Exception:
                break
        else:
            break
    return out


def main():
    if not KEY:
        sys.exit("请先设置环境变量 OPENBOOST_KEY")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        initialize()
        for t in rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})["result"]["tools"]:
            print(f'{t["name"]}\t{(t.get("description") or "").splitlines()[0][:100]}')
        return
    if cmd == "schema":
        initialize()
        for t in rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})["result"]["tools"]:
            if t["name"] == sys.argv[2]:
                print(json.dumps(t, ensure_ascii=False, indent=2))
                return
        sys.exit(f"没有工具 {sys.argv[2]}")
    initialize()
    name = "account_info" if cmd == "info" else sys.argv[2]
    args = json.loads(sys.argv[3]) if cmd == "call" and len(sys.argv) > 3 else {}
    print(json.dumps(unwrap(rpc({
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": name, "arguments": args},
    })), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
