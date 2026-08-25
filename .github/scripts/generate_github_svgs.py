#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path

import requests

USERNAME = os.getenv('GITHUB_USERNAME', '8585vishal')
OUT_DIR = Path('assets/github')
OUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {'Accept': 'application/vnd.github.v3+json'}


def fetch_json(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def generate_repository_metrics(user, repos):
    public_repos = user.get('public_repos') if user else None
    followers = user.get('followers') if user else None
    following = user.get('following') if user else None
    total_stars = sum(r.get('stargazers_count', 0) for r in (repos or []))

    # Build a simple SVG with four metric cards
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="160" viewBox="0 0 1000 160">
  <defs>
    <linearGradient id="g1" x1="0" x2="1"><stop offset="0" stop-color="#06202a"/><stop offset="1" stop-color="#071026"/></linearGradient>
    <filter id="f1" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#0ea5a4" flood-opacity="0.06"/></filter>
  </defs>
  <rect rx="8" ry="8" width="100%" height="100%" fill="#080d16" />
  <g transform="translate(24,20)" filter="url(#f1)">
    <g>
      <rect x="0" y="0" width="230" height="120" rx="8" fill="#071426" stroke="#164a5e"/>
      <text x="16" y="30" fill="#8b5cf6" font-family="JetBrains Mono,monospace" font-size="12">PUBLIC REPOS</text>
      <text x="16" y="74" fill="#e2e8f0" font-family="JetBrains Mono,monospace" font-size="32">{public_repos if public_repos is not None else '—'}</text>
    </g>
    <g transform="translate(250,0)">
      <rect x="0" y="0" width="230" height="120" rx="8" fill="#071426" stroke="#164a5e"/>
      <text x="16" y="30" fill="#22d3ee" font-family="JetBrains Mono,monospace" font-size="12">STARS</text>
      <text x="16" y="74" fill="#e2e8f0" font-family="JetBrains Mono,monospace" font-size="32">{total_stars}</text>
    </g>
    <g transform="translate(500,0)">
      <rect x="0" y="0" width="230" height="120" rx="8" fill="#071426" stroke="#164a5e"/>
      <text x="16" y="30" fill="#22d3ee" font-family="JetBrains Mono,monospace" font-size="12">FOLLOWERS</text>
      <text x="16" y="74" fill="#e2e8f0" font-family="JetBrains Mono,monospace" font-size="32">{followers if followers is not None else '—'}</text>
    </g>
    <g transform="translate(750,0)">
      <rect x="0" y="0" width="230" height="120" rx="8" fill="#071426" stroke="#164a5e"/>
      <text x="16" y="30" fill="#8b5cf6" font-family="JetBrains Mono,monospace" font-size="12">FOLLOWING</text>
      <text x="16" y="74" fill="#e2e8f0" font-family="JetBrains Mono,monospace" font-size="32">{following if following is not None else '—'}</text>
    </g>
  </g>
</svg>'''
    return svg


def generate_language_matrix(repos):
    # Count languages
    counts = {}
    for r in (repos or []):
        lang = r.get('language')
        if lang:
            counts[lang] = counts.get(lang, 0) + 1

    # Keep known languages order
    known = ['Python', 'TypeScript', 'JavaScript', 'Java', 'C', 'C++']
    bars = []
    maxv = max((counts.get(k, 0) for k in known), default=0)
    for i, k in enumerate(known):
        v = counts.get(k, 0)
        width = int((v / maxv) * 320) if maxv else 0
        bars.append((k, v, width))

    svg_lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="760" height="220" viewBox="0 0 760 220">',
                 '<rect width="100%" height="100%" fill="#080d16" rx="8"/>',
                 '<g transform="translate(28,28)">',
                 '<text x="0" y="0" fill="#22d3ee" font-size="14" font-family="JetBrains Mono,monospace">LANGUAGE MATRIX</text>']
    y = 26
    for name, count, w in bars:
        svg_lines.append(f'<text x="0" y="{y+28}" fill="#e2e8f0" font-size="12" font-family="JetBrains Mono,monospace">{name}</text>')
        svg_lines.append(f'<rect x="120" y="{y+12}" width="{320}" height="16" rx="8" fill="#071426" stroke="#164a5e"/>')
        svg_lines.append(f'<rect x="120" y="{y+12}" width="{w}" height="16" rx="8" fill="#22d3ee" opacity="0.9">')
        svg_lines.append('</rect>')
        svg_lines.append(f'<text x="460" y="{y+24}" fill="#64748b" font-size="12" font-family="JetBrains Mono,monospace">{count if count else ""}</text>')
        y += 40
    svg_lines.append('</g>')
    svg_lines.append('</svg>')
    return '\n'.join(svg_lines)


def generate_contribution_grid(repos):
    # Decorative fallback grid (7x10)
    cols = 14
    rows = 6
    cell = 12
    gap = 6
    width = cols * cell + (cols - 1) * gap + 56
    height = rows * cell + (rows - 1) * gap + 56
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           f'<rect width="100%" height="100%" fill="#080d16" rx="8"/>',
           '<g transform="translate(28,28)">']
    for r in range(rows):
        for c in range(cols):
            x = c * (cell + gap)
            y = r * (cell + gap)
            intensity = ((r * cols + c) % 4)
            color = ['#03202a', '#042b33', '#06404a', '#0e7f9a'][intensity]
            svg.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{color}">')
            # subtle pulse
            svg.append(f'<animate attributeName="opacity" values="0.7;1;0.7" dur="{3 + (c%3)}s" repeatCount="indefinite" begin="{(r+c)*0.1}s"/>')
            svg.append('</rect>')
    svg.append('</g>')
    svg.append('</svg>')
    return '\n'.join(svg)


def generate_activity_svg(repos):
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="160" viewBox="0 0 760 160">
  <rect width="100%" height="100%" fill="#080d16" rx="8"/>
  <g transform="translate(40,28)">
    <text x="0" y="0" fill="#22d3ee" font-size="14" font-family="JetBrains Mono,monospace">CONTRIBUTION ACTIVITY</text>
    <path d="M10,60 C60,10 120,110 180,60 C240,10 300,110 360,60 C420,10 480,110 540,60" stroke="#8b5cf6" stroke-width="2" fill="none" stroke-linecap="round"/>
    <g fill="#22d3ee">
      <circle cx="10" cy="60" r="4"><animate attributeName="r" values="3;6;3" dur="4s" repeatCount="indefinite"/></circle>
      <circle cx="180" cy="60" r="4"><animate attributeName="r" values="3;6;3" dur="3.2s" repeatCount="indefinite" begin="0.8s"/></circle>
      <circle cx="360" cy="60" r="4"><animate attributeName="r" values="3;6;3" dur="4.4s" repeatCount="indefinite" begin="1.6s"/></circle>
      <circle cx="540" cy="60" r="4"><animate attributeName="r" values="3;6;3" dur="3.6s" repeatCount="indefinite" begin="2.4s"/></circle>
    </g>
  </g>
</svg>'''
    return svg


def generate_command_center():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="420" viewBox="0 0 1000 420">
  <defs>
    <radialGradient id="rg" cx="50%" cy="30%">
      <stop offset="0%" stop-color="#071426"/>
      <stop offset="100%" stop-color="#04060a"/>
    </radialGradient>
  </defs>
  <rect width="100%" height="100%" fill="#05070D"/>
  <g transform="translate(40,28)">
    <text x="0" y="18" fill="#22d3ee" font-size="16" font-family="JetBrains Mono,monospace">GITHUB COMMAND CENTER</text>
    <g transform="translate(0,36)">
      <rect x="0" y="0" width="640" height="320" rx="12" fill="url(#rg)" stroke="#164a5e"/>
      <!-- Holographic core -->
      <g transform="translate(320,160)">
        <g>
          <circle r="48" fill="#071426" stroke="#22d3ee" stroke-width="1.2" opacity="0.95"/>
          <circle r="88" fill="none" stroke="#8b5cf6" stroke-opacity="0.12" stroke-width="2">
            <animateTransform attributeName="transform" attributeType="XML" type="rotate" from="0" to="360" dur="18s" repeatCount="indefinite"/>
          </circle>
          <circle r="8" fill="#8b5cf6"/>
        </g>
        <g transform="translate(-220,-90)" fill="#22d3ee" font-family="JetBrains Mono,monospace" font-size="11">
          <text x="0" y="0">REPOSITORIES</text>
        </g>
        <g transform="translate(220,-90)" fill="#22d3ee" font-family="JetBrains Mono,monospace" font-size="11">
          <text x="-40" y="0">CONTRIBUTIONS</text>
        </g>
      </g>
    </g>
  </g>
</svg>'''
    return svg


def safe_write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    old = ''
    if path.exists():
        old = path.read_text(encoding='utf-8')
    if old.strip() != content.strip():
        path.write_text(content, encoding='utf-8')
        print(f'WROTE: {path}')
    else:
        print(f'UNCHANGED: {path}')


def main():
    user = fetch_json(f'https://api.github.com/users/{USERNAME}')
    repos = fetch_json(f'https://api.github.com/users/{USERNAME}/repos?per_page=200')

    try:
        safe_write(OUT_DIR / 'repository-metrics.svg', generate_repository_metrics(user, repos))
        safe_write(OUT_DIR / 'language-matrix.svg', generate_language_matrix(repos))
        safe_write(OUT_DIR / 'contribution-grid.svg', generate_contribution_grid(repos))
        safe_write(OUT_DIR / 'activity.svg', generate_activity_svg(repos))
        safe_write(OUT_DIR / 'command-center.svg', generate_command_center())
    except Exception as e:
        print('ERROR generating svgs', e)
        sys.exit(1)


if __name__ == '__main__':
    main()
