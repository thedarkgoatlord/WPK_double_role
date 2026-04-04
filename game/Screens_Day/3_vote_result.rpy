# ── 投票结果 ──────────────────────────────────────────────────────────────────
screen screen_vote_result(idx):
    add Solid(BG_DAY)
    vbox:
        xalign 0.5
        yalign 0.42
        spacing 36
        text "第{}号玩家被放逐出局".format(idx+1):
            xalign 0.5
            size 54
            color "#ffcc66"
            font FONT
        text roles_display(players[idx]):
            xalign 0.5
            size 40
            color "#ffaa88"
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

# ── 平票/全员弃票 ─────────────────────────────────────────────────────────────────────
screen screen_vote_tie():
    add Solid(BG_DAY)
    vbox:
        xalign 0.5
        yalign 0.42
        spacing 36
        text "无人出局":
            xalign 0.5
            size 56
            color "#aaaacc"
            font FONT
        text "进入下一夜":
            xalign 0.5
            size 36
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
