#!/usr/bin/env python3
"""
Generate an SVG diagram of the 6-state DFA chess move validator.
Uses only the Python standard library.
"""

import math
import xml.etree.ElementTree as ET


SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def create_svg(width, height):
    svg = ET.Element("svg", {
        "xmlns": SVG_NS,
        "width": str(width),
        "height": str(height),
        "viewBox": f"0 0 {width} {height}",
    })
    defs = ET.SubElement(svg, "defs")

    filter_elem = ET.SubElement(defs, "filter", {"id": "shadow", "x": "-20%", "y": "-20%", "width": "140%", "height": "140%"})
    ET.SubElement(filter_elem, "feDropShadow", {
        "dx": "2", "dy": "3", "stdDeviation": "3", "flood-opacity": "0.25"
    })

    marker = ET.SubElement(defs, "marker", {
        "id": "arrowhead", "markerWidth": "10", "markerHeight": "7",
        "refX": "9", "refY": "3.5", "orient": "auto",
    })
    ET.SubElement(marker, "polygon", {"points": "0 0, 10 3.5, 0 7", "fill": "#4a4a4a"})

    marker_green = ET.SubElement(defs, "marker", {
        "id": "arrowhead-green", "markerWidth": "10", "markerHeight": "7",
        "refX": "9", "refY": "3.5", "orient": "auto",
    })
    ET.SubElement(marker_green, "polygon", {"points": "0 0, 10 3.5, 0 7", "fill": "#2e7d32"})

    marker_red = ET.SubElement(defs, "marker", {
        "id": "arrowhead-red", "markerWidth": "10", "markerHeight": "7",
        "refX": "9", "refY": "3.5", "orient": "auto",
    })
    ET.SubElement(marker_red, "polygon", {"points": "0 0, 10 3.5, 0 7", "fill": "#b3261e"})

    return svg


def add_rounded_rect(parent, x, y, w, h, r, fill, stroke, stroke_width=1, shadow=True):
    attrs = {
        "x": str(x), "y": str(y), "width": str(w), "height": str(h),
        "rx": str(r), "ry": str(r), "fill": fill, "stroke": stroke, "stroke-width": str(stroke_width),
    }
    if shadow:
        attrs["filter"] = "url(#shadow)"
    return ET.SubElement(parent, "rect", attrs)


def add_circle(parent, cx, cy, r, fill, stroke, stroke_width=2, shadow=True):
    attrs = {"cx": str(cx), "cy": str(cy), "r": str(r), "fill": fill, "stroke": stroke, "stroke-width": str(stroke_width)}
    if shadow:
        attrs["filter"] = "url(#shadow)"
    return ET.SubElement(parent, "circle", attrs)


def add_text(parent, x, y, text, font_size=14, fill="#2f2417", font_weight="normal", anchor="middle", font_family="Georgia, serif"):
    elem = ET.SubElement(parent, "text", {
        "x": str(x), "y": str(y), "fill": fill, "font-size": str(font_size),
        "font-family": font_family, "font-weight": font_weight, "text-anchor": anchor,
    })
    elem.text = text
    return elem


def add_line(parent, x1, y1, x2, y2, stroke="#4a4a4a", stroke_width=2, marker_end="url(#arrowhead)"):
    return ET.SubElement(parent, "line", {
        "x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2),
        "stroke": stroke, "stroke-width": str(stroke_width), "marker-end": marker_end,
    })


def add_path(parent, d, stroke="#4a4a4a", stroke_width=2, fill="none", marker_end="url(#arrowhead)"):
    return ET.SubElement(parent, "path", {
        "d": d, "stroke": stroke, "stroke-width": str(stroke_width), "fill": fill, "marker-end": marker_end,
    })


def draw_state(svg, cx, cy, label, sublabel, color_fill, color_stroke, is_double=False):
    r = 42
    if is_double:
        add_circle(svg, cx, cy, r + 4, color_fill, color_stroke, stroke_width=2, shadow=False)
    add_circle(svg, cx, cy, r, color_fill, color_stroke, stroke_width=3)
    add_text(svg, cx, cy - 6, label, font_size=15, font_weight="bold")
    add_text(svg, cx, cy + 12, sublabel, font_size=11, fill="#5a4a3a")


def circle_edge(cx, cy, r, angle_deg):
    rad = math.radians(angle_deg)
    return (cx + r * math.cos(rad), cy + r * math.sin(rad))


def draw_reject_arrow(svg, sx, sy, tx, ty, color="#b3261e"):
    mx = (sx + tx) / 2
    my = (sy + ty) / 2 + 30
    d = f"M {sx} {sy} Q {mx} {my} {tx} {ty}"
    add_path(svg, d, stroke=color, stroke_width=1.5, marker_end="url(#arrowhead-red)")


def wrap_text(text, max_chars):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = f"{current} {word}" if current else word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped_text(svg, x, y, text, max_chars, line_height, font_size=10, fill="#4a4a4a", font_family="monospace"):
    lines = wrap_text(text, max_chars)
    for i, line in enumerate(lines):
        add_text(svg, x, y + i * line_height, line, font_size=font_size, fill=fill, anchor="start", font_family=font_family)
    return len(lines) * line_height


def main():
    W, H = 1100, 660
    svg = create_svg(W, H)

    bg = ET.SubElement(svg, "rect", {"width": str(W), "height": str(H), "fill": "#f6f0e5"})
    svg.insert(0, bg)

    add_text(svg, W / 2, 40, "Chess Automaton — DFA Move Validator", font_size=22, font_weight="bold", fill="#2f2417")
    add_text(svg, W / 2, 64, "6-State Deterministic Finite Automaton Pipeline", font_size=13, fill="#72614d")

    start_x = 90
    y_main = 150
    spacing = 170

    s0_x = start_x + spacing * 0
    s1_x = start_x + spacing * 1
    s2_x = start_x + spacing * 2
    s3_x = start_x + spacing * 3
    s4_x = start_x + spacing * 4
    s5_x = start_x + spacing * 5

    y_reject = 340
    reject_x = (s2_x + s3_x) / 2
    reject_r = 42

    C_S0 = ("#e3f2fd", "#1565c0")
    C_S1 = ("#e8f5e9", "#2e7d32")
    C_S2 = ("#fff3e0", "#ef6c00")
    C_S3 = ("#f3e5f5", "#6a1b9a")
    C_S4 = ("#fce4ec", "#c62828")
    C_S5 = ("#d4edda", "#2e7d32")
    C_REJECT = ("#ffebee", "#b3261e")

    draw_state(svg, s0_x, y_main, "S0", "INPUT", C_S0[0], C_S0[1])
    draw_state(svg, s1_x, y_main, "S1", "BOUNDS", C_S1[0], C_S1[1])
    draw_state(svg, s2_x, y_main, "S2", "PIECE", C_S2[0], C_S2[1])
    draw_state(svg, s3_x, y_main, "S3", "RULES", C_S3[0], C_S3[1])
    draw_state(svg, s4_x, y_main, "S4", "SAFETY", C_S4[0], C_S4[1])
    draw_state(svg, s5_x, y_main, "S5", "ACCEPT", C_S5[0], C_S5[1], is_double=True)

    draw_state(svg, reject_x, y_reject, "REJECT", "Illegal Move", C_REJECT[0], C_REJECT[1])

    # Start arrow
    add_line(svg, s0_x - 70, y_main, s0_x - 44, y_main, stroke="#4a4a4a", stroke_width=2)
    add_text(svg, s0_x - 58, y_main - 10, "Start", font_size=11, fill="#4a4a4a")

    # Forward transitions
    add_line(svg, s0_x + 44, y_main, s1_x - 44, y_main, stroke="#2e7d32", stroke_width=2, marker_end="url(#arrowhead-green)")
    add_text(svg, (s0_x + s1_x) / 2, y_main - 10, "valid format", font_size=10, fill="#2e7d32")

    add_line(svg, s1_x + 44, y_main, s2_x - 44, y_main, stroke="#2e7d32", stroke_width=2, marker_end="url(#arrowhead-green)")
    add_text(svg, (s1_x + s2_x) / 2, y_main - 10, "in bounds", font_size=10, fill="#2e7d32")

    add_line(svg, s2_x + 44, y_main, s3_x - 44, y_main, stroke="#2e7d32", stroke_width=2, marker_end="url(#arrowhead-green)")
    add_text(svg, (s2_x + s3_x) / 2, y_main - 10, "valid piece", font_size=10, fill="#2e7d32")

    add_line(svg, s3_x + 44, y_main, s4_x - 44, y_main, stroke="#2e7d32", stroke_width=2, marker_end="url(#arrowhead-green)")
    add_text(svg, (s3_x + s4_x) / 2, y_main - 10, "valid rules", font_size=10, fill="#2e7d32")

    add_line(svg, s4_x + 44, y_main, s5_x - 44, y_main, stroke="#2e7d32", stroke_width=2, marker_end="url(#arrowhead-green)")
    add_text(svg, (s4_x + s5_x) / 2, y_main - 10, "king safe", font_size=10, fill="#2e7d32")

    # Reject transitions — aim at actual edge of reject circle
    s0_src = circle_edge(s0_x, y_main, 42, 90)
    s1_src = circle_edge(s1_x, y_main, 42, 90)
    s2_src = circle_edge(s2_x, y_main, 42, 90)
    s3_src = circle_edge(s3_x, y_main, 42, 90)
    s4_src = circle_edge(s4_x, y_main, 42, 90)

    t0 = circle_edge(reject_x, y_reject, reject_r, -130)
    t1 = circle_edge(reject_x, y_reject, reject_r, -110)
    t2 = circle_edge(reject_x, y_reject, reject_r, -90)
    t3 = circle_edge(reject_x, y_reject, reject_r, -70)
    t4 = circle_edge(reject_x, y_reject, reject_r, -50)

    draw_reject_arrow(svg, s0_src[0], s0_src[1], t0[0], t0[1], color="#b3261e")
    draw_reject_arrow(svg, s1_src[0], s1_src[1], t1[0], t1[1], color="#b3261e")
    draw_reject_arrow(svg, s2_src[0], s2_src[1], t2[0], t2[1], color="#b3261e")
    draw_reject_arrow(svg, s3_src[0], s3_src[1], t3[0], t3[1], color="#b3261e")
    draw_reject_arrow(svg, s4_src[0], s4_src[1], t4[0], t4[1], color="#b3261e")

    # Info box at bottom
    box_x = 50
    box_y = 430
    box_w = W - 100
    box_h = 210
    add_rounded_rect(svg, box_x, box_y, box_w, box_h, 8, "#fffaf1", "#d7ccc8", stroke_width=1, shadow=True)

    col_w = (box_w - 40) / 2
    left_x = box_x + 20
    right_x = left_x + col_w + 10
    line_h = 16
    max_chars = 52

    add_text(svg, left_x, box_y + 20, "STATE DESCRIPTIONS:", font_size=11, fill="#2f2417", anchor="start", font_family="monospace", font_weight="bold")
    state_lines = [
        "S0 INPUT — Parse algebraic notation",
        "S1 BOUNDS — Verify coordinates in 8x8 board",
        "S2 PIECE — Source square has active player's piece",
        "S3 RULES — Piece geometry, path, captures, castling",
        "S4 SAFETY — Simulate move; reject if king in check",
        "S5 ACCEPT — All gates passed; move is legal",
    ]
    cy_left = box_y + 38
    for line in state_lines:
        used = draw_wrapped_text(svg, left_x, cy_left, line, max_chars, line_h, font_size=10, fill="#4a4a4a")
        cy_left += used + 4

    add_text(svg, right_x, box_y + 20, "REJECT TRANSITIONS:", font_size=11, fill="#b3261e", anchor="start", font_family="monospace", font_weight="bold")
    reject_lines = [
        "S0 -> REJECT : E001 invalid format",
        "S1 -> REJECT : E001 out of bounds",
        "S2 -> REJECT : E002 empty square / E003 wrong color",
        "S3 -> REJECT : E004 illegal move / E005 path blocked / E007 self-capture",
        "S4 -> REJECT : E006 king would be in check",
    ]
    cy_right = box_y + 38
    for line in reject_lines:
        used = draw_wrapped_text(svg, right_x, cy_right, line, max_chars, line_h, font_size=10, fill="#5a4a3a")
        cy_right += used + 4

    tree = ET.ElementTree(svg)
    output_path = "/home/ejang/Desktop/automata/chess_automaton/main/DFA_diagram.svg"
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"Saved DFA diagram to: {output_path}")


if __name__ == "__main__":
    main()
