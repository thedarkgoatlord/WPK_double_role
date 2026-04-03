# ── 双民互认（仅第一夜 8人局） ───────────────────────────────────────────────
screen screen_civil_recognize(indices):
    add Solid(BG_NIGHT)
    vbox:
        xalign 0.5
        yalign 0.40
        spacing 36
        text "双民请睁眼":
            xalign 0.5
            size 58
            color COL_HEAD
            font FONT
        text "以下玩家互为双民，请相互确认：":
            xalign 0.5
            size 34
            color COL_SUB
            font FONT
        null height 10
        vbox:
            xalign 0.5
            spacing 16
            for idx in indices:
                $ label_str = "第{}号玩家　{}".format(idx+1, roles_display(players[idx]))
                text label_str:
                    xalign 0.5
                    size 36
                    color COL_GREEN
                    font FONT
        null height 30
        text "双民请闭眼":
            xalign 0.5
            size 38
            color COL_SUB
            font FONT
        null height 20
        button:
            xsize 340
            ysize 85
            background Frame(Solid(COL_BTN), 0, 0)
            hover_background Frame(Solid(COL_BTN_H), 0, 0)
            action Return()
            xalign 0.5
            text "确认，继续  ▶":
                xalign 0.5
                yalign 0.5
                size 36
                color "#ffffff"
                font FONT

