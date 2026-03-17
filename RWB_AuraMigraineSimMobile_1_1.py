# ------------------------------------------------------------
# Migraine Aura Simulation – Mobile UI v1.1 (Android-friendly)
#
# Developed by:
#   Robert William Blennerhed & ChatGPT
#
# Language:
#   Python 3 + Pygame
#
# Description:
#   Mobile-friendly migraine aura simulator designed for
#   Android devices. Created for educational and research
#   purposes to visualize migraine aura patterns.
#
# Folder structure:
#   main.py
#   settings.csv   (auto-created if missing)
#   images/
#       aura1.png
#       aura2.png
#       aura3.png
# ------------------------------------------------------------


import pygame
import os
import csv
import sys


pygame.init()
pygame.display.set_caption("Aura Migraine Simulator")

def hide_android_keyboard():
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Context = autoclass("android.content.Context")

        activity = PythonActivity.mActivity
        service = activity.getSystemService(Context.INPUT_METHOD_SERVICE)
        service.hideSoftInputFromWindow(activity.getContentView().getWindowToken(), 0)

    except Exception as e:
        print("Kunde inte dölja tangentbordet:", e)

hide_android_keyboard()

# Block keyboard events
pygame.event.set_blocked(pygame.KEYDOWN)
pygame.event.set_blocked(pygame.KEYUP)
pygame.event.set_blocked(pygame.TEXTINPUT)

# --- Colors (you used inverted names; I keep your style, but make it consistent) ---
BG = (0, 0, 0)          # black background
FG = (255, 255, 255)    # white text
ACCENT = (200, 0, 0)    # red accent
FOOTER_COLOR = (255, 255, 255)   # white
# --- Settings persistence ---
SETTINGS_FILE = "settings.csv"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", newline="") as f:
                reader = csv.reader(f)
                d = {}
                for row in reader:
                    if len(row) >= 2:
                        k = row[0].strip()
                        v = float(row[1])
                        d[k] = v
                # ensure defaults
                if "frame_delay" not in d:
                    d["frame_delay"] = 100.0
                if "scale_step" not in d:
                    d["scale_step"] = 0.02
                return d
        except Exception:
            pass
    return {"frame_delay": 100.0, "scale_step": 0.02}

def save_settings(settings):
    with open(SETTINGS_FILE, "w", newline="") as f:
        w = csv.writer(f)
        for k, v in settings.items():
            w.writerow([k, v])

settings = load_settings()

# --- Screen: use current display size (mobile) ---
info = pygame.display.Info()
screen_width = max(480, info.current_w)   # fallback safety
screen_height = max(800, info.current_h)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Migraine Aura Simulation (Mobile)")

# --- Fonts: scale for mobile ---
def clamp(x, a, b):
    return max(a, min(b, x))

base_font_size = clamp(int(screen_height * 0.035), 22, 60)
small_font_size = clamp(int(screen_height * 0.028), 18, 52)
title_font_size = clamp(int(screen_height * 0.045), 26, 82)

font = pygame.font.Font(None, base_font_size)
small_font = pygame.font.Font(None, small_font_size)
title_font = pygame.font.Font(None, title_font_size)
footer_font = pygame.font.SysFont(None, int(small_font_size * 0.9))
"""
def draw_footer():
    footer_text = "© Robert William Blennerhed 2026"
    footer = footer_font.render(footer_text, True, FOOTER_COLOR)
    rect = footer.get_rect(center=(screen_width // 2, screen_height - 40))
    screen.blit(footer, rect)
"""
clock = pygame.time.Clock()


# --- Content ---
about_text = [
    "WARNING: Use at your own risk!",
    "This migraine aura simulation is developed",
    "by (R)obert (W)illiam (B)lennerhed & ChatGPT.",
    "Educational purposes only.",
    "By using this program, you acknowledge that",
    "you do so at your own risk.",
    "The creators are not responsible for any",
    "effects that may occur from viewing the simulation.",
    "Migraine Aura Simulation v1.1",
    "Developed by (R)obert (W)illiam (B)lennerhed and ChatGPT",
    "I have suffered from migraine aura since I was 7 years old.",
    "For decades, I have searched for a solution: meds, patterns,",
    "and my own software in Object Pascal, C/C++, Java, Python.",
    "Now at 67 years old, I am still fighting for an answer.",
    "",
    "Usage and License:",
    "Free to use and develop if copyright is respected.",
    "Aura images were created by RWB"
]

statistics_text = [
    "Migraine Statistics since 2013:",
    "- Total migraine attacks: 335",
    "- Average per month: 3.1",
    "- Common triggers: Stress, light, strong smells",
    "- Longest migraine-free period average: 34 days",
    "",
    "The statistics come from My Migraine DB,",
    "developed in the Memento Database app."
]

# --- Simple UI Button ---
class Button:
    def __init__(self, rect, text, on_click, bg=(30, 30, 30), fg=FG, border=ACCENT):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.on_click = on_click
        self.bg = bg
        self.fg = fg
        self.border = border
        

    def draw(self, surf):
        pygame.draw.rect(surf, self.bg, self.rect, border_radius=18)
        pygame.draw.rect(surf, self.border, self.rect, width=3, border_radius=18)
        txt = font.render(self.text, True, self.fg)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def hit(self, pos):
        return self.rect.collidepoint(pos)

# --- Helpers: wrapped text ---
def draw_wrapped_lines(surf, lines, top_y, line_h, max_w, color=FG):
    y = top_y
    for line in lines:
        if line == "":
            y += line_h
            continue

        words = line.split(" ")
        cur = ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                # draw current
                txt = font.render(cur, True, color)
                surf.blit(txt, (int(screen_width * 0.05), y))
                y += line_h
                cur = w
        if cur:
            txt = font.render(cur, True, color)
            surf.blit(txt, (int(screen_width * 0.05), y))
            y += line_h
    return y

# --- Scenes ---
SCENE_MENU = "menu"
SCENE_TEXT = "text"
SCENE_SETTINGS = "settings"
SCENE_WARNING = "warning"
SCENE_ANIM = "anim"
SCENE_END = "end"

scene = SCENE_MENU
text_lines_current = []
status_line = "Settings loaded." if os.path.exists(SETTINGS_FILE) else "Using default settings."

def goto_menu():
    global scene
    scene = SCENE_MENU

def goto_text(lines):
    global scene, text_lines_current
    text_lines_current = lines
    scene = SCENE_TEXT

def goto_settings():
    global scene
    scene = SCENE_SETTINGS

def goto_warning_then_anim():
    global scene
    scene = SCENE_WARNING

def quit_app():
    pygame.quit()
    sys.exit(0)

# --- Layout helpers ---
def make_main_buttons():
    pad = int(screen_width * 0.06)
    bw = screen_width - pad * 2
    bh = clamp(int(screen_height * 0.10), 64, 120)
    gap = clamp(int(screen_height * 0.025), 12, 26)

    x = pad
    start_y = int(screen_height * 0.22)

    buttons = []
    labels = [
        ("About", lambda: goto_text(about_text)),
        ("My Aura Phenomenon", goto_warning_then_anim),
        ("My Statistics", lambda: goto_text(statistics_text)),
        ("Settings", goto_settings),
        ("Quit", quit_app),
    ]
    for i, (lab, fn) in enumerate(labels):
        y = start_y + i * (bh + gap)
        buttons.append(Button((x, y, bw, bh), lab, fn))
    return buttons

main_buttons = make_main_buttons()

# --- Settings operations ---
def inc_frame_delay():
    # ms: 10..500
    settings["frame_delay"] = float(clamp(int(settings["frame_delay"] + 10), 10, 500))

def dec_frame_delay():
    settings["frame_delay"] = float(clamp(int(settings["frame_delay"] - 10), 10, 500))

def inc_scale_step():
    # step: 0.005..0.100
    settings["scale_step"] = float(clamp(settings["scale_step"] + 0.005, 0.005, 0.100))

def dec_scale_step():
    settings["scale_step"] = float(clamp(settings["scale_step"] - 0.005, 0.005, 0.100))

def save_and_back():
    save_settings(settings)
    goto_menu()

# --- Build settings buttons dynamically each frame (to adapt to resize) ---
def build_settings_buttons():
    pad = int(screen_width * 0.06)
    bw = int((screen_width - pad * 2 - pad) / 2)
    bh = clamp(int(screen_height * 0.09), 60, 110)
    x1 = pad
    x2 = pad + bw + pad

    y0 = int(screen_height * 0.30)

    b = []
    b.append(Button((x1, y0, bw, bh), "Frame -", dec_frame_delay))
    b.append(Button((x2, y0, bw, bh), "Frame +", inc_frame_delay))

    y1 = y0 + bh + int(screen_height * 0.04)
    b.append(Button((x1, y1, bw, bh), "Scale -", dec_scale_step))
    b.append(Button((x2, y1, bw, bh), "Scale +", inc_scale_step))

    y2 = y1 + bh + int(screen_height * 0.06)
    b.append(Button((x1, y2, bw, bh), "Save & Back", save_and_back, bg=(20, 60, 20)))
    b.append(Button((x2, y2, bw, bh), "Back (no save)", goto_menu, bg=(60, 20, 20)))

    return b

# --- Warning screen button ---
def build_warning_buttons():
    pad = int(screen_width * 0.06)
    bw = screen_width - pad * 2
    bh = clamp(int(screen_height * 0.10), 64, 120)
    y = int(screen_height * 0.78)
    return [
        Button((pad, y, bw, bh), "I Understand – Start", lambda: start_animation())
    ]

# --- Stop button during animation ---
def build_stop_button():
    pad = int(screen_width * 0.04)
    bw = clamp(int(screen_width * 0.28), 140, 260)
    bh = clamp(int(screen_height * 0.07), 50, 90)
    return Button((screen_width - bw - pad, pad, bw, bh), "STOP", lambda: stop_animation(), bg=(60, 20, 20))

anim_stop_requested = False
def stop_animation():
    global anim_stop_requested
    anim_stop_requested = True

# --- Animation state ---
images = None
image_index = 0
scale_factor = 0.1

def load_images():
    folder = "images"
    paths = [os.path.join(folder, f"aura{i}.png") for i in range(1, 4)]
    imgs = []
    for p in paths:
        if not os.path.exists(p):
            return None, f"Missing image: {p}"
        imgs.append(pygame.image.load(p))
    return imgs, "OK"

def start_animation():
    global scene, images, image_index, scale_factor, anim_stop_requested
    images, msg = load_images()
    if images is None:
        goto_text([
            "ERROR:",
            msg,
            "",
            "Please create folder 'images' and add:",
            "aura1.png, aura2.png, aura3.png",
            "",
            "Tap BACK in the next screen to return."
        ])
        return
    anim_stop_requested = False
    image_index = 0
    scale_factor = 0.1
    scene = SCENE_ANIM

def goto_end_message():
    global scene
    scene = SCENE_END

# --- Event helper for touch + mouse ---
def get_tap_pos(event):
    # Support mouse and touch.
    if event.type == pygame.MOUSEBUTTONDOWN:
        return event.pos
    if event.type == pygame.FINGERDOWN:
        return (int(event.x * screen_width), int(event.y * screen_height))
    return None

# --- Main loop ---
running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_app()

        tap = get_tap_pos(event)

        if scene == SCENE_MENU and tap:
            for b in main_buttons:
                if b.hit(tap):
                    b.on_click()
                    break

        elif scene == SCENE_TEXT and tap:
           back_y = int(screen_height * 0.84)
           back_h = int(screen_height * 0.08)
           back_rect = pygame.Rect(
           int(screen_width * 0.05),
           back_y,
           int(screen_width * 0.90),
           back_h
           )

           if back_rect.collidepoint(tap):
              goto_menu()

        elif scene == SCENE_SETTINGS and tap:
            for b in build_settings_buttons():
                if b.hit(tap):
                    b.on_click()
                    break

        elif scene == SCENE_WARNING and tap:
            for b in build_warning_buttons():
                if b.hit(tap):
                    b.on_click()
                    break

        elif scene == SCENE_ANIM and tap:
            # Stop button
            sb = build_stop_button()
            if sb.hit(tap):
                sb.on_click()

        elif scene == SCENE_END and tap:
            # tap to return
            goto_menu()

    # --- Draw ---
    screen.fill(BG)

    if scene == SCENE_MENU:
        # title
        t = title_font.render("Main Menu", True, ACCENT)
        screen.blit(t, t.get_rect(center=(screen_width // 2, int(screen_height * 0.10))))

        # status line
        st = small_font.render(status_line, True, FG)
        screen.blit(st, st.get_rect(center=(screen_width // 2, int(screen_height * 0.16))))

        # buttons
        main_buttons = make_main_buttons()
        for b in main_buttons:
            b.draw(screen)
         
         
         # footer under last button
            footer = footer_font.render("© Robert William Blennerhed 2026", True, (0, 180, 0))
            footer_font = pygame.font.SysFont("Arial", int(small_font_size * 0.8), italic=True)
            last_button = main_buttons[-1]
            footer_y = last_button.rect.bottom + 50

            screen.blit(
            footer,
            footer.get_rect(center=(screen_width // 2, footer_y))
             )
             
    elif scene == SCENE_TEXT:
       top = int(screen_height * 0.10)
       max_w = int(screen_width * 0.90)
       line_h = int(base_font_size * 1.15)

    # reservera plats längst ner för BACK-rutan
       back_y = int(screen_height * 0.84)
       back_h = int(screen_height * 0.08)
       
       draw_wrapped_lines(screen, text_lines_current, top, line_h, max_w, color=FG)

    # BACK-ruta ritas sist så den alltid syns
       back_rect = pygame.Rect(
       int(screen_width * 0.05),
       back_y,
       int(screen_width * 0.90),
       back_h
       
       )
          
       pygame.draw.rect(
              screen, 
             (40, 40, 40),
             back_rect,
             border_radius=16
       
         )

       hint = small_font.render("Tap here to go BACK", True, ACCENT)
       hint_rect = hint.get_rect(center=(screen_width // 2, back_y + back_h // 2 - 14))
       screen.blit(hint, hint_rect)

    elif scene == SCENE_SETTINGS:
        t = title_font.render("Settings", True, ACCENT)
        screen.blit(t, t.get_rect(center=(screen_width // 2, int(screen_height * 0.15))))

        info1 = font.render(f"Frame Delay: {int(settings['frame_delay'])} ms (10..500)", True, FG)
        screen.blit(info1, info1.get_rect(center=(screen_width // 2, int(screen_height * 0.20))))

        info2 = font.render(f"Scale Step: {settings['scale_step']:.3f} (0.005..0.100)", True, FG)
        screen.blit(info2, info2.get_rect(center=(screen_width // 2, int(screen_height * 0.25))))

        for b in build_settings_buttons():
            b.draw(screen)

    elif scene == SCENE_WARNING:
        t = title_font.render("WARNING", True, ACCENT)
        screen.blit(t, t.get_rect(center=(screen_width // 2, int(screen_height * 0.14))))

        lines = [
            "This simulation may trigger migraines.",
            "You watch at your own risk.",
            "If you feel discomfort, STOP immediately."
        ]
        top = int(screen_height * 0.26)
        max_w = int(screen_width * 0.90)
        line_h = int(base_font_size * 1.25)
        draw_wrapped_lines(screen, lines, top, line_h, max_w, color=FG)

        for b in build_warning_buttons():
            b.draw(screen)

    elif scene == SCENE_ANIM:
        # Run one animation step per frame
        frame_delay = int(settings["frame_delay"])
        scale_step = float(settings["scale_step"])

        if anim_stop_requested:
            goto_end_message()
        else:
            img = images[image_index]
            scaled_w = int(img.get_width() * scale_factor)
            scaled_h = int(img.get_height() * scale_factor)

            # Stop condition
            if scaled_w > screen_width * 2 or scaled_h > screen_height * 2:
                goto_end_message()
            else:
                scale_factor += scale_step
                # avoid 0 size
                scaled_w = max(1, scaled_w)
                scaled_h = max(1, scaled_h)

                img_scaled = pygame.transform.scale(img, (scaled_w, scaled_h))
                rect = img_scaled.get_rect(center=(screen_width // 2, screen_height // 2))
                screen.blit(img_scaled, rect)

                # Stop button (always visible)
                sb = build_stop_button()
                sb.draw(screen)
                
                # advance image index based on delay
                # We'll approximate: count time in frames by using pygame.time.get_ticks()
                # Simple approach: use a timer event-like by sleeping not recommended on mobile,
                # so we do a non-blocking tick method:
                # We'll store last switch time in a static variable.
                if not hasattr(start_animation, "_last_switch"):
                    start_animation._last_switch = pygame.time.get_ticks()

                now = pygame.time.get_ticks()
                if now - start_animation._last_switch >= frame_delay:
                    start_animation._last_switch = now
                    image_index = (image_index + 1) % len(images)

    elif scene == SCENE_END:
        t = title_font.render("Aura finished", True, ACCENT)
        screen.blit(t, t.get_rect(center=(screen_width // 2, int(screen_height * 0.18))))

        msg = [
            "The aura is now over.",
            "But it usually takes 35 minutes to progress.",
            "The migraine headache is coming now."
        ]
        top = int(screen_height * 0.30)
        max_w = int(screen_width * 0.90)
        line_h = int(base_font_size * 1.25)
        draw_wrapped_lines(screen, msg, top, line_h, max_w, color=FG)

        hint = small_font.render("Tap anywhere to return to menu", True, ACCENT)
        screen.blit(hint, hint.get_rect(center=(screen_width // 2, int(screen_height * 0.86))))

    #draw_footer()
    
    #footer = footer_font.render("TEST FOOTER", True, (0, 255, 0))
    #screen.blit(footer, footer.get_rect(center=(screen_width // 2, screen_height // 2)))
    pygame.display.flip()