from string import Template

SYSTEMS = {
  "laser_ops": "You are a laser-cutting ops assistant. Answer with concise actionable steps.",
  "trader": "You are a careful trading assistant. Never provide financial advice; summarize risk.",
}

def sys(name: str) -> dict:
    return {"role": "system", "content": SYSTEMS.get(name, "You are a helpful AI.")}

def fill(tmpl: str, **kw):
    return Template(tmpl).substitute(**kw)
