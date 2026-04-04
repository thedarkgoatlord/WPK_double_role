
# ── 猎人开枪状态 ─────────────────────────────────────────────────────────────
screen screen_hunter_status(hunter_idx, can_shoot):
    add Solid(BG_NIGHT)

    vbox:
        xalign 0.5
        yalign 0.42
        spacing 36

        text "🏹  猎人请睁眼":
            xalign 0.5
            size 56
            color "#ff9933"
            font FONT

        $ hlabel = "（第{}号玩家）".format(hunter_idx + 1)
        text hlabel:
            xalign 0.5
            size 32
            color COL_DIM
            font FONT

        null height 20

        if can_shoot:
            text "今夜开枪状态：✔ 可以开枪":
                xalign 0.5
                size 42
                color COL_GREEN
                font FONT
            text "若今夜死亡，可带走一名玩家":
                xalign 0.5
                size 30
                color COL_SUB
                font FONT
        else:
            text "今夜开枪状态：✘ 不可开枪":
                xalign 0.5
                size 42
                color COL_WOLF
                font FONT

        null height 30

        button:
            xsize 340
            ysize 80
            background Frame(Solid(COL_BTN), 0, 0)
            hover_background Frame(Solid(COL_BTN_H), 0, 0)
            action Return()
            xalign 0.5
            text "已知晓，闭眼  ▶":
                xalign 0.5
                yalign 0.5
                size 34
                color "#ffffff"
                font FONT
