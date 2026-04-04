# ── 自爆结果 ──────────────────────────────────────────────────────────────────
screen screen_explode_result(idx):
    add Solid(BG_DAY)
    vbox:
        xalign 0.5
        yalign 0.42
        spacing 36
        text "💥  第{}号玩家宣布自爆出局".format(idx+1):
            xalign 0.5
            size 52
            color COL_WOLF
            font FONT
        text roles_display(players[idx]):
            xalign 0.5
            size 40
            color "#ff8888"
            font FONT
        text "无投票环节，直接进入下一夜":
            xalign 0.5
            size 34
            color COL_SUB
            font FONT
        null height 30
        button:
            xsize 340
            ysize 80
            background Frame(Solid(COL_BTN), 0, 0)
            hover_background Frame(Solid(COL_BTN_H), 0, 0)
            action Return()
            xalign 0.5
            text "进入下一夜  ▶":
                xalign 0.5
                yalign 0.5
                size 36
                color "#ffffff"
                font FONT
