"""
Darkroom — Interactive Image Compressor
Run with:  streamlit run app.py
"""

import io
import time
from typing import List, Tuple

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

# ----------------------------------------------------------------------
# Page setup + theme
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Darkroom — Image Compressor",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

RED = "#E1503D"
CYAN = "#62D9C8"
BG = "#131417"
SURFACE = "#1B1D21"
MUTED = "#92949B"

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BG}; }}
    section[data-testid="stSidebar"] {{ background-color: {SURFACE}; }}
    h1, h2, h3 {{ font-family: 'Space Grotesk', sans-serif; }}
    .eyebrow {{
        font-family: monospace; color: {RED}; letter-spacing: 0.18em;
        text-transform: uppercase; font-size: 12px; margin-bottom: 4px;
    }}
    .metric-card {{
        background: {SURFACE}; border: 1px solid #313439; border-radius: 6px;
        padding: 14px 18px; text-align:center;
    }}
    .stButton>button {{
        background-color: {RED}; color: #151515; font-weight: 700; border: none;
    }}
    div[data-baseweb="slider"] > div > div {{ background: {RED} !important; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
FORMAT_MAP = {"JPEG": "JPEG", "WEBP": "WEBP", "PNG (lossless)": "PNG"}


def fmt_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n/1024:.1f} KB"
    return f"{n/(1024*1024):.2f} MB"


def compress_image(img: Image.Image, fmt: str, quality: int, max_dim: int) -> bytes:
    """Resize (if needed) and re-encode an image, returning raw bytes."""
    work = img.copy()
    w, h = work.size
    if max(w, h) > max_dim:
        scale = max_dim / max(w, h)
        work = work.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    buf = io.BytesIO()
    save_kwargs = {}
    if fmt == "JPEG":
        if work.mode in ("RGBA", "P"):
            work = work.convert("RGB")
        save_kwargs = {"quality": quality, "optimize": True}
    elif fmt == "WEBP":
        save_kwargs = {"quality": quality}
    elif fmt == "PNG":
        if work.mode == "CMYK":
            work = work.convert("RGB")
        save_kwargs = {"optimize": True}

    work.save(buf, format=fmt, **save_kwargs)
    return buf.getvalue()


def quality_curve(img: Image.Image, fmt: str, max_dim: int, points: List[int]) -> Tuple[List[int], List[int]]:
    """Compute output size at several quality levels, for the trade-off chart."""
    sizes = []
    for q in points:
        data = compress_image(img, fmt, q, max_dim)
        sizes.append(len(data))
    return points, sizes


def channel_histogram(img: Image.Image) -> go.Figure:
    arr = np.array(img.convert("RGB"))
    fig = go.Figure()
    colors = {"R": "#E1503D", "G": "#62D9C8", "B": "#8A8DFF"}
    for i, ch in enumerate(["R", "G", "B"]):
        hist, edges = np.histogram(arr[:, :, i], bins=32, range=(0, 255))
        fig.add_trace(
            go.Scatter(
                x=edges[:-1], y=hist, mode="lines", name=ch,
                line=dict(color=colors[ch], width=2),
                fill="tozeroy", opacity=0.5,
            )
        )
    fig.update_layout(
        height=180, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        font=dict(color=MUTED, size=11),
        legend=dict(orientation="h", y=1.15),
        xaxis=dict(gridcolor="#2A2D31"), yaxis=dict(gridcolor="#2A2D31", showticklabels=False),
    )
    return fig


# ----------------------------------------------------------------------
# Sidebar controls
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="eyebrow">Controls</div>', unsafe_allow_html=True)
    st.title("Darkroom")
    st.caption("Client-side style compression, powered by Pillow.")

    uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp", "bmp"])

    fmt_label = st.selectbox("Output format", list(FORMAT_MAP.keys()), index=0)
    fmt = FORMAT_MAP[fmt_label]

    quality = st.slider("Quality", min_value=1, max_value=95, value=70, disabled=(fmt == "PNG"))
    max_dim = st.slider("Max dimension (px)", min_value=200, max_value=4000, value=2000, step=100)

    show_curve = st.checkbox("Show quality vs. size curve", value=True)
    show_hist = st.checkbox("Show color histograms", value=True)
    animate = st.checkbox("Animate compression steps", value=True)

# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
st.markdown('<div class="eyebrow">Stage 01 — Load a plate</div>', unsafe_allow_html=True)
st.title("Compress images without losing what matters.")

if uploaded is None:
    st.info("Upload an image from the sidebar to begin.")
    st.stop()

original_bytes = uploaded.getvalue()
img = Image.open(io.BytesIO(original_bytes))
img.load()

# ---- animated "process" ----
if animate:
    st.markdown('<div class="eyebrow">Stage 02 — Development</div>', unsafe_allow_html=True)
    steps = ["Reading file", "Decoding pixels", "Analyzing detail", "Re-encoding"]
    prog = st.progress(0, text=steps[0])
    for i, step in enumerate(steps):
        prog.progress(int((i + 1) / len(steps) * 100), text=step)
        time.sleep(0.25)
    prog.empty()

compressed_bytes = compress_image(img, fmt, quality, max_dim)
compressed_img = Image.open(io.BytesIO(compressed_bytes))

# ---- side-by-side compare ----
st.markdown('<div class="eyebrow">Stage 03 — Compare</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2, gap="medium")
with col1:
    st.subheader("Original")
    st.image(img, use_container_width=True)
    st.caption(f"{img.width} × {img.height} · {fmt_bytes(len(original_bytes))} · {uploaded.name}")
with col2:
    st.subheader("Compressed")
    st.image(compressed_img, use_container_width=True)
    st.caption(f"{compressed_img.width} × {compressed_img.height} · {fmt_bytes(len(compressed_bytes))} · {fmt}")

# ---- metrics ----
reduction = max(0.0, (1 - len(compressed_bytes) / len(original_bytes)) * 100)
saved = max(len(original_bytes) - len(compressed_bytes), 0)

m1, m2, m3 = st.columns(3)
m1.metric("Size reduction", f"{reduction:.0f}%")
m2.metric("Saved", fmt_bytes(saved))
m3.metric("New size", fmt_bytes(len(compressed_bytes)), delta=f"-{fmt_bytes(saved)}", delta_color="inverse")

st.download_button(
    "Download compressed image",
    data=compressed_bytes,
    file_name=f"compressed.{fmt.lower() if fmt != 'JPEG' else 'jpg'}",
    mime=f"image/{fmt.lower()}",
    use_container_width=True,
)

# ---- interactive quality/size trade-off curve ----
if show_curve and fmt != "PNG":
    st.markdown('<div class="eyebrow">Explore the trade-off</div>', unsafe_allow_html=True)
    st.caption("Size at different quality levels for this image — drag the slider above and watch your point move.")
    qs, sizes = quality_curve(img, fmt, max_dim, list(range(10, 96, 10)))
    sizes_kb = [s / 1024 for s in sizes]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=qs, y=sizes_kb, mode="lines+markers",
                              line=dict(color=CYAN, width=3), marker=dict(size=7)))
    fig.add_trace(go.Scatter(x=[quality], y=[len(compressed_bytes) / 1024], mode="markers",
                              marker=dict(size=14, color=RED, symbol="diamond"),
                              name="current"))
    fig.update_layout(
        height=280, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor=SURFACE, plot_bgcolor=SURFACE,
        font=dict(color=MUTED),
        xaxis=dict(title="Quality", gridcolor="#2A2D31"),
        yaxis=dict(title="File size (KB)", gridcolor="#2A2D31"),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

# ---- histograms ----
if show_hist:
    st.markdown('<div class="eyebrow">Color distribution</div>', unsafe_allow_html=True)
    h1, h2 = st.columns(2)
    with h1:
        st.caption("Original")
        st.plotly_chart(channel_histogram(img), use_container_width=True)
    with h2:
        st.caption("Compressed")
        st.plotly_chart(channel_histogram(compressed_img), use_container_width=True)

st.markdown("---")
st.caption("DARKROOM — Pillow-based compression · runs locally, nothing leaves your machine")
