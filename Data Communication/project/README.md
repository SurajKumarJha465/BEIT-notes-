# Darkroom — Interactive Image Compressor (Streamlit)

A Python/Streamlit web app that compresses images and lets you explore the
process interactively.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

This opens the app in your browser (usually http://localhost:8501).

## Features

- Upload JPG / PNG / WEBP / BMP images
- Choose output format: JPEG, WEBP, or lossless PNG
- Live quality slider (1–95) and max-dimension resize control
- Animated "process" bar: Reading → Decoding → Analyzing → Re-encoding
- Side-by-side original vs. compressed preview with size, dimensions, and
  reduction % metrics
- **Interactive quality-vs-size curve** — see how file size changes across
  quality levels for your specific image, with your current setting marked
- **Color histograms** comparing the original and compressed image's
  R/G/B channel distributions
- One-click download of the compressed file

## Notes

- All processing happens locally via Pillow — nothing is uploaded to a
  server other than your own machine running Streamlit.
- The "Max dimension" slider downsamples large images before re-encoding,
  which is often the single biggest lever for file size.
