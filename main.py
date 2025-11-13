import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import base64
import textwrap

app = FastAPI(title="AI Power API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    prompt: str

class TextResponse(BaseModel):
    prompt: str
    text: str

class ImageResponse(BaseModel):
    prompt: str
    data_url: str
    format: str = "image/svg+xml"

class ScriptResponse(BaseModel):
    prompt: str
    script: str
    estimated_minutes: int

@app.get("/")
def read_root():
    return {"message": "AI Power Backend ready"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if backend is running (DB optional for this app)"""
    return {
        "backend": "✅ Running",
        "database": "ℹ️ Not required for this prototype",
    }

SAMPLE_PROMPT = "Describe the future of AI in space exploration, with stunning visuals of advanced spacecraft."
SAMPLE_TEXT = (
    "AI in space exploration is poised to revolutionize humanity's understanding and presence beyond Earth. "
    "Imagine autonomous probes that can identify and analyze exoplanets with unprecedented speed, making real-time "
    "decisions about sample collection and data transmission. Swarms of AI-powered nanobots could construct "
    "self-repairing habitats on Mars or the Moon, using local resources with minimal human intervention.\n\n"
    "Further into the future, AI will be central to managing vast interstellar voyages. It will handle complex navigation, "
    "life support systems, and scientific data processing, freeing human astronauts to focus on discovery. AI companions "
    "will provide psychological support and act as expert assistants, capable of diagnosing system failures or identifying "
    "new biological lifeforms. From optimizing fuel efficiency for deep-space missions to enabling communication across "
    "light-years, AI is not just a tool; it's becoming an indispensable partner in our cosmic journey, pushing the "
    "boundaries of what's possible."
)

@app.post("/api/generate/text", response_model=TextResponse)
def generate_text(req: GenerateRequest):
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    if prompt.lower() == SAMPLE_PROMPT.lower():
        return {"prompt": prompt, "text": SAMPLE_TEXT}

    # Simple templated response for prototype
    body = (
        f"Here's a concise vision for '{prompt}':\n\n"
        "1) Foundation: Modern AI systems coordinate sensing, planning, and action across a network of agents.\n"
        "2) Experience: Natural, multimodal interaction translates ideas into high‑fidelity media and simulations.\n"
        "3) Reliability: Safety, monitoring, and self‑healing keep complex missions resilient.\n\n"
        "Zooming in, expect rapid iteration cycles: models reason over live data, generate options, then test them in fast,\n"
        "physics‑aware sandboxes. The result is a virtuous loop of design → simulation → deployment, guided by human intent\n"
        "and transparent constraints.\n\n"
        "In practice, this means better decisions, richer creativity, and systems that collaborate with us—augmenting human\n"
        "judgment rather than replacing it."
    )
    return {"prompt": prompt, "text": body}

# Lightweight SVG generator for a prompt-based visual
SVG_TEMPLATE = """
<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}'>
  <defs>
    <linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>
      <stop offset='0%' stop-color='{c1}' />
      <stop offset='100%' stop-color='{c2}' />
    </linearGradient>
    <filter id='glow' x='-50%' y='-50%' width='200%' height='200%'>
      <feGaussianBlur stdDeviation='8' result='blur'/>
      <feMerge><feMergeNode in='blur'/><feMergeNode in='SourceGraphic'/></feMerge>
    </filter>
  </defs>
  <rect width='100%' height='100%' fill='black' />
  <circle cx='{cx}' cy='{cy}' r='{r}' fill='url(#g)' filter='url(#glow)' opacity='0.9'/>
  <g fill='none' stroke='white' stroke-opacity='0.7'>
    <path d='M 0 {cy} C {w4} {cy2} {w2} {cy3} {w} {cy}' stroke='url(#g)' stroke-width='2'/>
    <path d='M {w2} 0 C {w3} {h4} {w4} {h3} {w2} {h}' stroke='url(#g)' stroke-width='1.5' stroke-dasharray='6 6'/>
  </g>
  <text x='{pad}' y='{pad2}' font-size='20' fill='white' font-family='Inter, system-ui, -apple-system, Segoe UI, Roboto'>AI Power · {title}</text>
  <text x='{pad}' y='{pad3}' font-size='12' fill='#cbd5e1' font-family='Inter, system-ui, -apple-system, Segoe UI, Roboto'>"{subtitle}"</text>
</svg>
"""

COLORS = [
    ("#60a5fa", "#a78bfa"),
    ("#22d3ee", "#818cf8"),
    ("#34d399", "#06b6d4"),
    ("#f472b6", "#60a5fa"),
]

def svg_for_prompt(prompt: str, w: int = 1200, h: int = 675) -> str:
    idx = abs(hash(prompt)) % len(COLORS)
    c1, c2 = COLORS[idx]
    svg = SVG_TEMPLATE.format(
        w=w, h=h,
        c1=c1, c2=c2,
        cx=w*0.7, cy=h*0.4, r=min(w, h)*0.25,
        w2=w/2, w3=w*0.75, w4=w*0.25,
        cy2=h*0.2, cy3=h*0.8,
        h2=h/2, h3=h*0.75, h4=h*0.25,
        pad=32, pad2=48, pad3=72,
        title="Futuristic Visual",
        subtitle=(prompt[:90] + ("…" if len(prompt)>90 else ""))
    )
    return svg

@app.post("/api/generate/image", response_model=ImageResponse)
def generate_image(req: GenerateRequest):
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    svg = svg_for_prompt(prompt)
    data = svg.encode("utf-8")
    b64 = base64.b64encode(data).decode("ascii")
    data_url = f"data:image/svg+xml;base64,{b64}"
    return {"prompt": prompt, "data_url": data_url, "format": "image/svg+xml"}

@app.post("/api/generate/script", response_model=ScriptResponse)
def generate_podcast_script(req: GenerateRequest):
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    if prompt.lower() == SAMPLE_PROMPT.lower():
        base = (
            "Welcome to AI Power. In today's episode, we explore the future of AI in space exploration—how intelligent systems "
            "will expand our reach and resilience beyond Earth. "
        )
    else:
        base = f"Welcome to AI Power. Today's episode explores: {prompt}. "

    sections = [
        "Origins: how autonomy moved from labs to deep space.",
        "Sensing: fusing multi-spectral data, onboard learning, and anomaly detection.",
        "Planning: model-predictive control, uncertainty, and responsible decision-making.",
        "Construction: self-assembling infrastructure and in-situ resource utilization.",
        "Health: predictive maintenance and closed-loop life-support.",
        "Human factors: copilots for cognition, creativity, and care during long missions.",
        "Interstellar scale: coordination under extreme latency and sparse information.",
        "Ethics and governance: verifiability, transparency, and alignment.",
        "Frontiers: biological discovery, terraforming aids, and cosmic archaeology.",
        "Closing: a vision of collaborative intelligence among stars.",
    ]

    paragraphs = [textwrap.fill(s, width=100) for s in sections]
    script = base + "\n\n" + "\n\n".join(paragraphs)

    # Expand to approximately 10 minutes by repeating elaborations
    elaboration = (
        "Imagine the choreography: swarms negotiate roles, exchange compressed world models, and rehearse actions in fast "
        "simulations before a single thruster fires. Each success feeds a continuously improving library of tactics, "
        "grounded by telemetry and human feedback."
    )
    # Roughly 130 words/minute -> ~1300 words for 10 minutes; we expand content to approximate length
    expanded_blocks = []
    while len(" ".join(expanded_blocks).split()) < 1200:
        expanded_blocks.append(elaboration)
    script = script + "\n\n" + "\n\n".join(expanded_blocks)

    return {"prompt": prompt, "script": script, "estimated_minutes": 10}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
