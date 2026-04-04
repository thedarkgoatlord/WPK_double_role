# ── 夜晚过渡 ──────────────────────────────────────────────────────────────────
screen screen_night_transition(n):
    add Solid(BG_NIGHT)
    vbox:
        xalign 0.5
        yalign 0.42
        spacing 40
        text "🌙  第 [n] 夜":
            xalign 0.5
            size 80
            color COL_HEAD
            font FONT
        text "天黑请闭眼":
            xalign 0.5
            size 42
            color COL_SUB
            font FONT
        null height 40
        button:
            xsize 340
            ysize 85
            background Frame(Solid(COL_BTN), 0, 0)
            hover_background Frame(Solid(COL_BTN_H), 0, 0)
            action Return()
            xalign 0.5
            text "进入夜晚  ▶":
                xalign 0.5
                yalign 0.5
                size 38
                color "#ffffff"
                font FONT
