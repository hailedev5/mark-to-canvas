#!/usr/bin/env python3
"""
MarkToCanvas (mark-to-canvas)
Transforms standard Markdown files into dynamic, interactive HTML5 Canvas presentations.
Zero external dependencies required.
"""

import argparse
import json
import re
import sys
from pathlib import Path


class MarkdownCanvasParser:
    def __init__(self):
        pass

    def parse_markdown(self, md_content: str):
        """
        Parses markdown text into structured slide objects based on '---' horizontal rules or '# ' headers.
        """
        raw_slides = re.split(r"\n---\n", md_content)
        slides = []

        for slide_text in raw_slides:
            slide_text = slide_text.strip()
            if not slide_text:
                continue

            slide_data = {
                "title": "",
                "subtitle": "",
                "bullet_points": [],
                "code_block": "",
            }

            lines = slide_text.split("\n")
            in_code_block = False
            code_lines = []

            for line in lines:
                line_str = line.strip()

                # Handle code blocks
                if line_str.startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    code_lines.append(line)
                    continue

                # Main Title (# Title)
                if line_str.startswith("# ") and not slide_data["title"]:
                    slide_data["title"] = line_str[2:].strip()
                # Subtitle (## Subtitle)
                elif line_str.startswith("## ") and not slide_data["subtitle"]:
                    slide_data["subtitle"] = line_str[3:].strip()
                # Bullet points (- or * item)
                elif line_str.startswith("- ") or line_str.startswith("* "):
                    slide_data["bullet_points"].append(line_str[2:].strip())
                # Fallback paragraph text into bullet points if no prefix
                elif line_str and not slide_data["title"]:
                    slide_data["title"] = line_str

            if code_lines:
                slide_data["code_block"] = "\n".join(code_lines)

            slides.append(slide_data)

        return slides


def generate_html_canvas_viewer(slides_data):
    """
    Generates a single self-contained HTML file containing Canvas rendering logic and animations.
    """
    slides_json = json.dumps(slides_data, indent=2)

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MarkToCanvas Presentation</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body, html {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: #0d1117;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        #canvas-container {{
            position: relative;
            width: 100vw;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        canvas {{
            display: block;
            background: #161b22;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
            border-radius: 12px;
        }}
        .controls {{
            position: absolute;
            bottom: 20px;
            display: flex;
            gap: 15px;
            align-items: center;
            z-index: 10;
        }}
        button {{
            background: #21262d;
            color: #c9d1d9;
            border: 1px solid #30363d;
            padding: 10px 18px;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        button:hover {{
            background: #30363d;
            color: #58a6ff;
            border-color: #8b949e;
        }}
        .slide-num {{
            color: #8b949e;
            font-size: 14px;
            font-family: monospace;
        }}
    </style>
</head>
<body>

    <div id="canvas-container">
        <canvas id="slideCanvas"></canvas>
        <div class="controls">
            <button onclick="prevSlide()">&#8592; Previous</button>
            <span class="slide-num" id="slideIndicator">1 / 1</span>
            <button onclick="nextSlide()">Next &#8594;</button>
        </div>
    </div>

    <script>
        const slides = {slides_json};
        let currentSlide = 0;

        const canvas = document.getElementById('slideCanvas');
        const ctx = canvas.getContext('2d');

        // Particle background animation state
        let particles = [];
        const numParticles = 40;

        function resizeCanvas() {{
            const aspectRatio = 16 / 9;
            let width = window.innerWidth * 0.85;
            let height = width / aspectRatio;

            if (height > window.innerHeight * 0.85) {{
                height = window.innerHeight * 0.85;
                width = height * aspectRatio;
            }}

            canvas.width = width;
            canvas.height = height;
            initParticles();
            render();
        }}

        function initParticles() {{
            particles = [];
            for (let i = 0; i < numParticles; i++) {{
                particles.push({{
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    radius: Math.random() * 2 + 1,
                    vx: (Math.random() - 0.5) * 0.5,
                    vy: (Math.random() - 0.5) * 0.5,
                    alpha: Math.random() * 0.5 + 0.2
                }});
            }}
        }}

        function updateParticles() {{
            particles.forEach(p => {{
                p.x += p.vx;
                p.y += p.vy;

                if (p.x < 0) p.x = canvas.width;
                if (p.x > canvas.width) p.x = 0;
                if (p.y < 0) p.y = canvas.height;
                if (p.y > canvas.height) p.y = 0;
            }});
        }}

        function drawParticles() {{
            particles.forEach(p => {{
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(88, 166, 255, ${{p.alpha}})`;
                ctx.fill();
            }});
        }}

        function render() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Draw Background Grid
            ctx.strokeStyle = "rgba(48, 54, 61, 0.4)";
            ctx.lineWidth = 1;
            const gridSize = 40;
            for (let x = 0; x < canvas.width; x += gridSize) {{
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, canvas.height);
                ctx.stroke();
            }}
            for (let y = 0; y < canvas.height; y += gridSize) {{
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(canvas.width, y);
                ctx.stroke();
            }}

            // Draw Background Particles
            drawParticles();

            const slide = slides[currentSlide];
            if (!slide) return;

            const scale = canvas.width / 960; // Scale factors based on 960x540 canvas base
            let currentY = 80 * scale;

            // Render Title
            if (slide.title) {{
                ctx.font = `bold ${{32 * scale}}px sans-serif`;
                ctx.fillStyle = "#58a6ff";
                ctx.fillText(slide.title, 60 * scale, currentY);
                currentY += 45 * scale;
            }}

            // Render Subtitle
            if (slide.subtitle) {{
                ctx.font = `${{22 * scale}}px sans-serif`;
                ctx.fillStyle = "#8b949e";
                ctx.fillText(slide.subtitle, 60 * scale, currentY);
                currentY += 40 * scale;
            }}

            // Accent Line Separator
            ctx.strokeStyle = "#30363d";
            ctx.lineWidth = 2 * scale;
            ctx.beginPath();
            ctx.moveTo(60 * scale, currentY);
            ctx.lineTo(canvas.width - 60 * scale, currentY);
            ctx.stroke();
            currentY += 40 * scale;

            // Render Bullet Points
            if (slide.bullet_points && slide.bullet_points.length > 0) {{
                ctx.font = `${{18 * scale}}px sans-serif`;
                ctx.fillStyle = "#c9d1d9";

                slide.bullet_points.forEach(point => {{
                    // Bullet symbol
                    ctx.fillStyle = "#58a6ff";
                    ctx.beginPath();
                    ctx.arc(70 * scale, currentY - 6 * scale, 4 * scale, 0, Math.PI * 2);
                    ctx.fill();

                    // Text
                    ctx.fillStyle = "#c9d1d9";
                    ctx.fillText(point, 90 * scale, currentY);
                    currentY += 35 * scale;
                }});
            }}

            // Render Code Block Box
            if (slide.code_block) {{
                currentY += 10 * scale;
                const boxX = 60 * scale;
                const boxY = currentY;
                const boxWidth = canvas.width - (120 * scale);
                const codeLines = slide.code_block.split('\\n');
                const boxHeight = (codeLines.length * 24 + 20) * scale;

                // Code Background Box
                ctx.fillStyle = "#0d1117";
                ctx.strokeStyle = "#30363d";
                ctx.lineWidth = 1 * scale;
                ctx.beginPath();
                ctx.roundRect(boxX, boxY, boxWidth, boxHeight, 8 * scale);
                ctx.fill();
                ctx.stroke();

                // Code Lines
                ctx.font = `${{15 * scale}}px monospace`;
                ctx.fillStyle = "#79c0ff";
                codeLines.forEach((codeLine, idx) => {{
                    ctx.fillText(codeLine, boxX + (20 * scale), boxY + ((idx + 1) * 24 * scale));
                }});
            }}

            // Update UI Indicator
            document.getElementById('slideIndicator').innerText = `${{currentSlide + 1}} / ${{slides.length}}`;
        }}

        function animate() {{
            updateParticles();
            render();
            requestAnimationFrame(animate);
        }}

        function nextSlide() {{
            if (currentSlide < slides.length - 1) {{
                currentSlide++;
            }}
        }}

        function prevSlide() {{
            if (currentSlide > 0) {{
                currentSlide--;
            }}
        }}

        // Keyboard navigation bindings
        window.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
            if (e.key === 'ArrowLeft') prevSlide();
        }});

        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();
        animate();
    </script>
</body>
</html>
"""
    return html_template


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown documents into HTML5 Canvas presentations."
    )
    parser.add_argument(
        "-i", "--input", help="Path to input Markdown file", required=False
    )
    parser.add_argument(
        "-o",
        "--output",
        default="presentation.html",
        help="Output HTML file name (default: presentation.html)",
    )

    args = parser.parse_args()

    sample_markdown = """# MarkToCanvas Presentation
## An Interactive HTML5 Canvas Slideshow Engine

- Parsed entirely from structured Markdown files.
- Built without external frontend frameworks or heavy dependencies.
- Perfect for offline presentations, GitHub pages, and visual docs.

---

# Key Features & Tech Stack
## Python + Native HTML5 Canvas

- Lightweight and fast execution.
- Keyboard navigation (Left / Right Arrow keys supported).
- Auto-scaling canvas UI adapted for any viewport size.

---

# Code Snippet Support
## Embed code directly in your slides

```python
def hello_world():
    print("Generated with MarkToCanvas!")
    return True
"""

if args.input:
    input_path = Path(args.input)