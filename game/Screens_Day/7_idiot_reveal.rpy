# ── 白痴翻牌 ──────────────────────────────────────────────────────────────
screen screen_idiot_reveal(idx, layer):
    add Solid(BG_DAY)
    vbox:
        xalign 0.5
        yalign 0.42
        spacing 36

        text "白痴翻牌！":
            xalign 0.5
            size 56
            color "#66ccff"
            font FONT

        text "第{}号玩家是白痴，本次不出局".format(idx+1):
            xalign 0.5
            size 36
            color "#ffffff"
            font FONT

        if layer == "top":
            $ role_txt = role_cn(players[idx]["top"])
        else:
            $ role_txt = role_cn(players[idx]["bottom"])

        text "已翻开身份：{}".format(role_txt):
            xalign 0.5
            size 34
            color "#aaccff"
            font FONT

        text "下一次被投票时将正常出局":
            xalign 0.5
            size 30
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
            text "继续游戏  ▶":
                xalign 0.5
                yalign 0.5
                size 36
                color "#ffffff"
                font FONT
