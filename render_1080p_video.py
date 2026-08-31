"""
High-Resolution Video Generator for Robot Continuity Network (RCN).
Renders the complete 96-second simulation frame-by-frame in 1080p Full HD (1920x1080)
and merges the exact ElevenLabs voiceover audio track via ffmpeg into a broadcast-quality MP4 video.
"""

import os
import sys
import math
import subprocess
from PIL import Image, ImageDraw, ImageFont

WIDTH = 1920
HEIGHT = 1080
FPS = 30
DURATION_SEC = 95.8
TOTAL_FRAMES = int(DURATION_SEC * FPS)

PROJECT_DIR = "/Users/aztecbirdmac.com/Desktop/Identity protocol demo"
AUDIO_PATH = os.path.join(PROJECT_DIR, "voice speech", "ElevenLabs_2026-08-31T09_26_42_Pablo_pvc_sp85_s70_sb96_se0_b_m2.mp3")
OUTPUT_MP4 = os.path.join(PROJECT_DIR, "Robot_Continuity_Protocol_Presentation_1080p.mp4")
FFMPEG_BIN = os.path.join(PROJECT_DIR, "ffmpeg")

# Colors
BG_DARK = (9, 13, 22)
PANEL_BG = (15, 23, 42)
CYAN = (6, 182, 212)
BLUE = (59, 130, 246)
GREEN = (16, 185, 129)
AMBER = (245, 158, 11)
RED = (239, 68, 68)
WHITE = (248, 250, 252)
MUTED = (148, 163, 184)
SLATE = (100, 116, 139)

# Load fonts
def get_font(size, bold=False):
    system_fonts = [
        "/System/Library/Fonts/SFPro-Bold.otf" if bold else "/System/Library/Fonts/SFPro-Regular.otf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNS.ttf"
    ]
    for sf in system_fonts:
        if os.path.exists(sf):
            try:
                return ImageFont.truetype(sf, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_title = get_font(32, bold=True)
font_subtitle = get_font(20, bold=False)
font_motto = get_font(38, bold=True)
font_body = get_font(22, bold=False)
font_body_bold = get_font(22, bold=True)
font_metric_val = get_font(34, bold=True)
font_metric_lbl = get_font(18, bold=True)
font_metric_sub = get_font(16, bold=False)
font_subtitles = get_font(26, bold=True)
font_tag = get_font(16, bold=True)

# Subtitle cues
SUBTITLES = [
    (0.0, 14.0, "In commercial robotics, a robot body is replaceable hardware..."),
    (14.0, 26.0, "Here, Robot Titan-04 suffers an unrecoverable drive motor stall."),
    (26.0, 37.0, "RCN instantly captures an immutable, cryptographically signed Memory Vault snapshot."),
    (37.0, 48.0, "RCN scans spare fleet bodies. Underpowered units are rejected. Chassis Beta passes."),
    (48.0, 58.0, "The adaptation layer recalculates velocity limits and sensor routing for Beta's wheelbase."),
    (58.0, 70.0, "Chassis Beta authenticates the passport and resumes pallet delivery in under 45 seconds."),
    (70.0, 82.0, "Zero facility re-mapping. Zero operational data loss."),
    (82.0, 96.0, "The body can change. The continuity remains. Explore the open standard on GitHub.")
]

def get_current_subtitle(t):
    for start, end, text in SUBTITLES:
        if start <= t < end:
            return text
    return ""

def render_frame(t):
    img = Image.new("RGBA", (WIDTH, HEIGHT), BG_DARK)
    draw = ImageDraw.Draw(img)

    # 1. Background subtle grid
    grid_size = 60
    for x in range(0, WIDTH, grid_size):
        draw.line([(x, 0), (x, HEIGHT)], fill=(255, 255, 255, 10), width=1)
    for y in range(0, HEIGHT, grid_size):
        draw.line([(0, y), (WIDTH, y)], fill=(255, 255, 255, 10), width=1)

    # 2. Header Bar
    draw.rectangle([0, 0, WIDTH, 90], fill=(10, 15, 30, 240))
    draw.line([(0, 90), (WIDTH, 90)], fill=(255, 255, 255, 25), width=2)
    
    # Brand logo & title
    draw.rounded_rectangle([40, 20, 90, 70], radius=12, fill=CYAN)
    draw.text((48, 25), "RCN", fill=(255, 255, 255), font=font_subtitle)
    draw.text((110, 22), "ROBOT CONTINUITY NETWORK", fill=WHITE, font=font_title)
    draw.text((112, 58), "Decoupled Embodied Identity • RCN-01 / RCN-02 Specifications", fill=CYAN, font=font_tag)

    # Header Status Badge
    status_text = "FLEET RUNTIME ACTIVE"
    status_color = GREEN
    if 14.0 <= t < 37.0:
        status_text = "HARDWARE FAULT DETECTED"
        status_color = RED
    elif 37.0 <= t < 58.0:
        status_text = "YARD COMPATIBILITY CHECK"
        status_color = AMBER
    elif 58.0 <= t < 72.0:
        status_text = "CONTINUITY RESTORED • RESUMED"
        status_color = GREEN
    elif t >= 72.0:
        status_text = "OPEN STANDARD • RCN-01 / RCN-02"
        status_color = CYAN

    badge_w = 340
    draw.rounded_rectangle([WIDTH - badge_w - 40, 25, WIDTH - 40, 65], radius=20, fill=(status_color[0], status_color[1], status_color[2], 35), outline=status_color, width=2)
    draw.ellipse([WIDTH - badge_w - 22, 40, WIDTH - badge_w - 10, 52], fill=status_color)
    draw.text((WIDTH - badge_w + 4, 34), status_text, fill=status_color, font=font_tag)

    # 3. Main Layout: Left Panel (Telemetry), Center (Warehouse), Right (Ledger)
    panel_y = 115
    panel_h = HEIGHT - panel_y - 85

    # LEFT PANEL: 420px
    left_w = 420
    draw.rounded_rectangle([40, panel_y, 40 + left_w, panel_y + panel_h], radius=16, fill=PANEL_BG, outline=(255, 255, 255, 25), width=2)
    draw.text((65, panel_y + 20), "PERSISTENT IDENTITY (PASSPORT)", fill=CYAN, font=font_tag)
    draw.text((65, panel_y + 45), "Callsign: Titan-04 (MiR-600)", fill=WHITE, font=font_body_bold)
    draw.text((65, panel_y + 75), "ID: urn:rcn:identity:alpha-07b9", fill=MUTED, font=font_tag)
    draw.text((65, panel_y + 100), "Owner: Logix Intralogistics Corp", fill=MUTED, font=font_tag)
    draw.text((65, panel_y + 125), "HMAC-SHA256 Digital Seal: VERIFIED", fill=GREEN, font=font_tag)

    # Chassis Alpha Card
    card_a_y = panel_y + 165
    draw.rounded_rectangle([60, card_a_y, 40 + left_w - 20, card_a_y + 160], radius=12, fill=(255, 255, 255, 8), outline=(RED if t >= 14.0 else GREEN), width=2)
    draw.text((80, card_a_y + 15), "CHASSIS ALPHA (CURRENT BODY)", fill=MUTED, font=font_tag)
    draw.text((80, card_a_y + 38), "chassis-mir-501 (MiR-600)", fill=WHITE, font=font_body)
    if t < 14.0:
        draw.text((80, card_a_y + 70), "Status: ACTIVE (In Transit)", fill=GREEN, font=font_body)
        draw.text((80, card_a_y + 100), "Payload: 340kg Pallet PL-904", fill=WHITE, font=font_tag)
        draw.text((80, card_a_y + 125), "Motor Temp: 68°C (Nominal)", fill=GREEN, font=font_tag)
    else:
        draw.text((80, card_a_y + 70), "Status: HALTED (Motor Stall)", fill=RED, font=font_body_bold)
        draw.text((80, card_a_y + 100), "Action: Atomic Vault Snapshot Captured", fill=AMBER, font=font_tag)
        draw.text((80, card_a_y + 125), "Local Storage: CRYPTO-WIPED", fill=MUTED, font=font_tag)

    # Chassis Beta Card
    card_b_y = card_a_y + 180
    b_active = t >= 58.0
    draw.rounded_rectangle([60, card_b_y, 40 + left_w - 20, card_b_y + 160], radius=12, fill=(255, 255, 255, 8), outline=(GREEN if b_active else CYAN if t >= 37.0 else SLATE), width=2)
    draw.text((80, card_b_y + 15), "CHASSIS BETA (YARD SPARE)", fill=MUTED, font=font_tag)
    draw.text((80, card_b_y + 38), "chassis-mir-882 (MiR-600-Rev2)", fill=WHITE, font=font_body)
    if t < 37.0:
        draw.text((80, card_b_y + 70), "Status: STANDBY in Facility Yard", fill=SLATE, font=font_body)
        draw.text((80, card_b_y + 100), "Sensors: 2D/3D LiDAR + Depth Cameras", fill=MUTED, font=font_tag)
    elif 37.0 <= t < 58.0:
        draw.text((80, card_b_y + 70), "Status: COMPATIBILITY PASSED (4/4)", fill=CYAN, font=font_body_bold)
        draw.text((80, card_b_y + 100), "Adaptation: Recalculating Turn Rate", fill=AMBER, font=font_tag)
        draw.text((80, card_b_y + 125), "Target Limit: 4.39 rad/s", fill=CYAN, font=font_tag)
    else:
        draw.text((80, card_b_y + 70), "Status: EMBODIED & ACTIVE", fill=GREEN, font=font_body_bold)
        draw.text((80, card_b_y + 100), "Mission: Resumed from Step 3", fill=WHITE, font=font_tag)
        draw.text((80, card_b_y + 125), "MTTR Total: < 45 Seconds", fill=GREEN, font=font_tag)

    # MTTR Metric Cards
    m_y = card_b_y + 180
    draw.rounded_rectangle([60, m_y, 235, m_y + 90], radius=10, fill=(255, 255, 255, 6), outline=CYAN, width=1)
    mttr_val = "0s"
    if 14.0 <= t < 58.0:
        mttr_val = f"{int((t - 14.0) * 1.05)}s"
    elif t >= 58.0:
        mttr_val = "42s"
    draw.text((95, m_y + 15), mttr_val, fill=CYAN, font=font_metric_val)
    draw.text((80, m_y + 55), "SWAP LATENCY (MTTR)", fill=MUTED, font=font_metric_sub)

    draw.rounded_rectangle([255, m_y, 40 + left_w - 20, m_y + 90], radius=10, fill=(255, 255, 255, 6), outline=GREEN, width=1)
    draw.text((300, m_y + 15), "0%", fill=GREEN, font=font_metric_val)
    draw.text((275, m_y + 55), "DATA LOSS (0 MIN MAP)", fill=MUTED, font=font_metric_sub)

    # RIGHT PANEL: Ledger / Audit Trail (440px)
    right_w = 440
    right_x = WIDTH - right_w - 40
    draw.rounded_rectangle([right_x, panel_y, right_x + right_w, panel_y + panel_h], radius=16, fill=PANEL_BG, outline=(255, 255, 255, 25), width=2)
    draw.text((right_x + 25, panel_y + 20), "CRYPTOGRAPHIC AUDIT LEDGER", fill=CYAN, font=font_tag)
    draw.text((right_x + 25, panel_y + 45), "IMMUTABLE SHA-256 EVENT CHAIN", fill=GREEN, font=font_tag)

    # Ledger items based on time
    logs = [
        ("[10:50:00] SYSTEM_INIT: Mounted to chassis-mir-501", CYAN),
        ("[10:50:02] PASSPORT: HMAC seal verified (Key: root_2026)", GREEN),
        ("[10:50:05] MISSION: Pallet PL-904 moving to Rack 14", WHITE)
    ]
    if t >= 14.0:
        logs.append(("[10:50:14] ALERT: Motor driver inverter thermal trip", RED))
        logs.append(("[10:50:15] SNAPSHOT: Vault urn:rcn:vault:8829 captured", AMBER))
        logs.append(("[10:50:16] IMMUTABLE_HASH: sha256:d5c2e0b57112...", CYAN))
    if t >= 37.0:
        logs.append(("[10:50:37] YARD_SCAN: Candidate 1 rejected (Payload < 300kg)", RED))
        logs.append(("[10:50:39] YARD_SCAN: Chassis-mir-882 approved (4/4)", GREEN))
        logs.append(("[10:50:41] ADAPT: Wheelbase 0.82m -> Turn 4.39 rad/s", CYAN))
        logs.append(("[10:50:42] WIPE: Local storage on chassis-501 purged", MUTED))
    if t >= 58.0:
        logs.append(("[10:50:58] REBIND: Identity bound to chassis-mir-882", GREEN))
        logs.append(("[10:50:59] RESUME: Mission continuing to Rack 14", GREEN))
        logs.append(("[10:51:00] ZERO_DOWNTIME: Facility re-map: 0 min", GREEN))

    log_y = panel_y + 85
    for text, color in logs[-9:]:
        draw.text((right_x + 25, log_y), text[:52], fill=color, font=font_tag)
        log_y += 32

    # CENTER STAGE: Warehouse Floor Plan (from 480 to right_x - 20)
    stage_x = 480
    stage_w = right_x - stage_x - 20
    stage_y = panel_y
    stage_h = panel_h

    draw.rounded_rectangle([stage_x, stage_y, stage_x + stage_w, stage_y + stage_h], radius=16, fill=(17, 24, 39), outline=(255, 255, 255, 30), width=2)

    # Zones in warehouse
    # Zone A: Inbound
    draw.rounded_rectangle([stage_x + 30, stage_y + 40, stage_x + 280, stage_y + stage_h - 40], radius=12, fill=(6, 182, 212, 15), outline=(6, 182, 212, 60), width=2)
    draw.text((stage_x + 45, stage_y + 55), "ZONE A: INBOUND DOCK", fill=CYAN, font=font_tag)

    # Zone B: Cold Storage
    draw.rounded_rectangle([stage_x + stage_w - 320, stage_y + 40, stage_x + stage_w - 30, stage_y + stage_h - 40], radius=12, fill=(59, 130, 246, 15), outline=(59, 130, 246, 60), width=2)
    draw.text((stage_x + stage_w - 305, stage_y + 55), "ZONE B: COLD STORAGE", fill=BLUE, font=font_tag)

    # Storage Racks
    rack_x = stage_x + stage_w - 270
    for i in range(4):
        ry = stage_y + 120 + i * 110
        draw.rounded_rectangle([rack_x, ry, rack_x + 220, ry + 60], radius=8, fill=(255, 255, 255, 20), outline=(255, 255, 255, 40), width=1)
        draw.text((rack_x + 20, ry + 20), f"RACK #{12 + i}", fill=SLATE, font=font_body_bold)

    # Target Rack 14 highlight
    target_ry = stage_y + 120 + 2 * 110
    draw.rounded_rectangle([rack_x - 5, target_ry - 5, rack_x + 225, target_ry + 65], radius=10, fill=(245, 158, 11, 25), outline=AMBER, width=2)
    draw.text((rack_x + 20, target_ry + 20), "TARGET: RACK 14", fill=AMBER, font=font_body_bold)

    # Planned Route Dashline
    start_pt = (stage_x + 120, stage_y + 340)
    end_pt = (rack_x - 30, target_ry + 30)
    draw.line([start_pt, end_pt], fill=(6, 182, 212, 80), width=3)

    # Robot Alpha Position
    # moves from start_pt towards mid until 14s, then freezes
    alpha_prog = min(t / 14.0, 1.0) * 0.45
    alpha_x = start_pt[0] + (end_pt[0] - start_pt[0]) * alpha_prog
    alpha_y = start_pt[1] + (end_pt[1] - start_pt[1]) * alpha_prog

    # Robot Beta Position
    # begins at yard standby (stage_x + 350, stage_y + stage_h - 150)
    # at 58s, moves from its position to end_pt
    beta_start = (stage_x + 380, stage_y + stage_h - 140)
    beta_x, beta_y = beta_start
    if t >= 58.0:
        beta_prog = min((t - 58.0) / 12.0, 1.0)
        beta_x = beta_start[0] + (end_pt[0] - beta_start[0]) * beta_prog
        beta_y = beta_start[1] + (end_pt[1] - beta_start[1]) * beta_prog

    # Draw Transfer Ray during phase 3 (37s to 58s)
    if 37.0 <= t < 58.0:
        draw.line([(alpha_x, alpha_y), (beta_x, beta_y)], fill=CYAN, width=4)
        # pulsating packet
        pct = (t * 2.5) % 1.0
        pkt_x = alpha_x + (beta_x - alpha_x) * pct
        pkt_y = alpha_y + (beta_y - alpha_y) * pct
        draw.ellipse([pkt_x - 12, pkt_y - 12, pkt_x + 12, pkt_y + 12], fill=WHITE, outline=CYAN, width=3)

    # Helper: draw a robot on canvas
    def draw_robot(rx, ry, color, label, is_fault, has_pallet):
        # Body
        draw.rounded_rectangle([rx - 45, ry - 32, rx + 45, ry + 32], radius=12, fill=color, outline=(255, 255, 255, 100), width=2)
        # Wheels
        draw.rectangle([rx - 40, ry - 38, rx - 15, ry - 32], fill=(20, 20, 20))
        draw.rectangle([rx + 15, ry - 38, rx + 40, ry - 32], fill=(20, 20, 20))
        draw.rectangle([rx - 40, ry + 32, rx - 15, ry + 38], fill=(20, 20, 20))
        draw.rectangle([rx + 15, ry + 32, rx + 40, ry + 38], fill=(20, 20, 20))
        # Pallet
        if has_pallet:
            draw.rounded_rectangle([rx - 22, ry - 22, rx + 22, ry + 22], radius=6, fill=AMBER, outline=WHITE, width=2)
            draw.text((rx - 15, ry - 10), "PL", fill=WHITE, font=font_tag)
        # Label
        draw.text((rx - 70, ry + 44), label, fill=WHITE, font=font_tag)
        if is_fault:
            draw.text((rx - 55, ry - 60), "⚡ STALLED", fill=RED, font=font_body_bold)

    # Draw Alpha
    draw_robot(alpha_x, alpha_y, (RED if t >= 14.0 else CYAN), "Titan-04 (MiR-501)", (t >= 14.0), (t < 58.0))
    
    # Draw Beta
    draw_robot(beta_x, beta_y, (GREEN if t >= 58.0 else CYAN if t >= 37.0 else SLATE), "Chassis Beta (MiR-882)", False, (t >= 58.0))

    # 4. POST-MISSION SHOWCASE OVERLAY (when t >= 72.0s)
    if t >= 72.0:
        # Semi-transparent dimmed backdrop
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (6, 10, 20, 235))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

        card_w = 1200
        card_h = 680
        cx = (WIDTH - card_w) // 2
        cy = (HEIGHT - card_h) // 2 - 20

        # Big Glassmorphism Card
        draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=24, fill=(15, 23, 42, 250), outline=CYAN, width=3)
        
        # Header Tag
        draw.text((cx + card_w // 2 - 240, cy + 45), "ROBOT CONTINUITY PROTOCOL • SPECIFICATION RCN-01 / RCN-02", fill=CYAN, font=font_tag)
        draw.text((cx + card_w // 2 - 470, cy + 85), "THE BODY CAN CHANGE. THE CONTINUITY REMAINS.", fill=WHITE, font=font_motto)

        # 3 Big Metrics
        box_w = 340
        box_h = 130
        by = cy + 175
        
        # Metric 1: MTTR
        draw.rounded_rectangle([cx + 60, by, cx + 60 + box_w, by + box_h], radius=16, fill=(255, 255, 255, 8), outline=GREEN, width=2)
        draw.text((cx + 120, by + 20), "< 45 SECONDS", fill=GREEN, font=font_metric_val)
        draw.text((cx + 90, by + 65), "SWAP RECOVERY TIME (MTTR)", fill=WHITE, font=font_metric_lbl)
        draw.text((cx + 105, by + 92), "vs. 3.5h legacy re-provisioning", fill=MUTED, font=font_metric_sub)

        # Metric 2: Re-mapping
        draw.rounded_rectangle([cx + 430, by, cx + 430 + box_w, by + box_h], radius=16, fill=(255, 255, 255, 8), outline=CYAN, width=2)
        draw.text((cx + 510, by + 20), "0 MINUTES", fill=CYAN, font=font_metric_val)
        draw.text((cx + 470, by + 65), "FACILITY RE-MAPPING TIME", fill=WHITE, font=font_metric_lbl)
        draw.text((cx + 475, by + 92), "100% semantic map preserved", fill=MUTED, font=font_metric_sub)

        # Metric 3: Experience Preserved
        draw.rounded_rectangle([cx + 800, by, cx + 800 + box_w, by + box_h], radius=16, fill=(255, 255, 255, 8), outline=AMBER, width=2)
        draw.text((cx + 885, by + 20), "ZERO LOSS", fill=AMBER, font=font_metric_val)
        draw.text((cx + 840, by + 65), "OPERATIONAL EXPERIENCE", fill=WHITE, font=font_metric_lbl)
        draw.text((cx + 835, by + 92), "Tasks, traction heuristics, credentials", fill=MUTED, font=font_metric_sub)

        # Architecture Flow Diagram
        flow_y = cy + 360
        draw.text((cx + card_w // 2 - 170, flow_y - 20), "DECOUPLED ARCHITECTURE IN ACTION", fill=MUTED, font=font_tag)

        # Flow boxes
        fn_w = 300
        fn_h = 80
        # Node Alpha
        draw.rounded_rectangle([cx + 80, flow_y + 15, cx + 80 + fn_w, flow_y + 15 + fn_h], radius=12, fill=(255, 255, 255, 8), outline=RED, width=2)
        draw.text((cx + 120, flow_y + 30), "CHASSIS ALPHA", fill=RED, font=font_body_bold)
        draw.text((cx + 105, flow_y + 58), "MiR-501 (Wiped & Retired)", fill=MUTED, font=font_metric_sub)

        # Center Node Vault
        draw.rounded_rectangle([cx + 450, flow_y + 15, cx + 450 + fn_w, flow_y + 15 + fn_h], radius=12, fill=(6, 182, 212, 25), outline=CYAN, width=3)
        draw.text((cx + 490, flow_y + 30), "RCN MEMORY VAULT", fill=CYAN, font=font_body_bold)
        draw.text((cx + 475, flow_y + 58), "Identity + Task + Map (Persists)", fill=WHITE, font=font_metric_sub)

        # Node Beta
        draw.rounded_rectangle([cx + 820, flow_y + 15, cx + 820 + fn_w, flow_y + 15 + fn_h], radius=12, fill=(255, 255, 255, 8), outline=GREEN, width=2)
        draw.text((cx + 870, flow_y + 30), "CHASSIS BETA", fill=GREEN, font=font_body_bold)
        draw.text((cx + 850, flow_y + 58), "MiR-882 (Bound & Resumed)", fill=MUTED, font=font_metric_sub)

        # Flow Arrows
        draw.line([(cx + 380, flow_y + 55), (cx + 450, flow_y + 55)], fill=CYAN, width=4)
        draw.line([(cx + 750, flow_y + 55), (cx + 820, flow_y + 55)], fill=CYAN, width=4)

        # GitHub Repo Banner
        draw.rounded_rectangle([cx + 180, cy + card_h - 100, cx + card_w - 180, cy + card_h - 35], radius=14, fill=(6, 182, 212, 20), outline=CYAN, width=2)
        draw.text((cx + 300, cy + card_h - 75), "★ github.com/Aztecbird/robot-continuity-network", fill=CYAN, font=font_subtitle)

    # 5. SUBTITLE RIBBON (At bottom)
    subtitle = get_current_subtitle(t)
    if subtitle:
        sub_box_w = min(1400, len(subtitle) * 22 + 100)
        sub_box_h = 60
        sub_box_x = (WIDTH - sub_box_w) // 2
        sub_box_y = HEIGHT - 75
        draw.rounded_rectangle([sub_box_x, sub_box_y, sub_box_x + sub_box_w, sub_box_y + sub_box_h], radius=14, fill=(6, 12, 24, 230), outline=CYAN, width=2)
        draw.ellipse([sub_box_x + 25, sub_box_y + 24, sub_box_x + 37, sub_box_y + 36], fill=CYAN)
        draw.text((sub_box_x + 52, sub_box_y + 16), subtitle, fill=WHITE, font=font_subtitles)

    return img.convert("RGB")


def main():
    print(f"Starting High-Res 1080p Video Rendering...")
    print(f"Total Duration: {DURATION_SEC}s ({TOTAL_FRAMES} frames @ {FPS} fps)")
    print(f"Audio Source: {AUDIO_PATH}")
    print(f"Output Video: {OUTPUT_MP4}")

    # Launch ffmpeg process with stdin pipe for raw frames
    ffmpeg_cmd = [
        FFMPEG_BIN,
        "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",  # Video from stdin
        "-i", AUDIO_PATH,  # Audio from file
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",  # Broadcast visual quality
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        OUTPUT_MP4
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / float(FPS)
        frame_img = render_frame(t)
        proc.stdin.write(frame_img.tobytes())

        if frame_idx % 150 == 0 or frame_idx == TOTAL_FRAMES - 1:
            pct = (frame_idx + 1) / float(TOTAL_FRAMES) * 100
            print(f"Render progress: {pct:.1f}% ({frame_idx + 1}/{TOTAL_FRAMES} frames) - timestamp: {t:.1f}s")

    proc.stdin.close()
    proc.wait()

    if proc.returncode == 0:
        print(f"\nSUCCESS! 1080p Full HD Video generated at:\n{OUTPUT_MP4}")
    else:
        print(f"Error during video generation. Return code: {proc.returncode}")


if __name__ == "__main__":
    main()
