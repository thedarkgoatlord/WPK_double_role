# ── 投票放逐 ──────────────────────────────────────────────────────────────────
screen screen_vote():
    add Solid(BG_DAY)
    default vote_sel = -1

    vbox:
        xalign 0.5
        yalign 0.38
        spacing 30

        text "🗳  投票放逐":
            xalign 0.5
            size 58
            color "#88aaff"
            font FONT

        text "请法官记录投票结果，选择出局玩家：":
            xalign 0.5
            size 32
            color COL_SUB
            font FONT

        $ alive_idxs = alive_players(players)
        hbox:
            xalign 0.5
            spacing 40
            vbox:
                for i in range(0, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
                    $ bg_v = "#1a2244" if (idx == vote_sel) else "#1e1e2e"
                    $ bg_vh = "#2a3466" if (idx == vote_sel) else "#2a2a44"
                    button:
                        xsize 500
                        ysize 64
                        background Frame(Solid(bg_v), 0, 0)
                        hover_background Frame(Solid(bg_vh), 0, 0)
                        action SetScreenVariable("vote_sel", idx)
                        xalign 0.5
                        text "第{}号玩家".format(idx+1):
                            xalign 0.5
                            yalign 0.5
                            size 32
                            color "#ffffff"
                            font FONT
            vbox:
                for i in range(1, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
                    $ bg_v = "#1a2244" if (idx == vote_sel) else "#1e1e2e"
                    $ bg_vh = "#2a3466" if (idx == vote_sel) else "#2a2a44"
                    button:
                        xsize 500
                        ysize 64
                        background Frame(Solid(bg_v), 0, 0)
                        hover_background Frame(Solid(bg_vh), 0, 0)
                        action SetScreenVariable("vote_sel", idx)
                        xalign 0.5
                        text "第{}号玩家".format(idx+1):
                            xalign 0.5
                            yalign 0.5
                            size 32
                            color "#ffffff"
                            font FONT

        null height 20

        hbox:
            xalign 0.5
            spacing 60

            button:
                xsize 280
                ysize 75
                background Frame(Solid("#333344"), 0, 0)
                hover_background Frame(Solid("#444466"), 0, 0)
                action Return(-1)
                text "平票，无人出局":
                    xalign 0.5
                    yalign 0.5
                    size 28
                    color "#aaaaaa"
                    font FONT

            if vote_sel >= 0:
                button:
                    xsize 320
                    ysize 75
                    background Frame(Solid("#224488"), 0, 0)
                    hover_background Frame(Solid("#336699"), 0, 0)
                    action Return(vote_sel)
                    text "确认放逐  ▶":
                        xalign 0.5
                        yalign 0.5
                        size 34
                        color "#ffffff"
                        font FONT
            else:
                button:
                    xsize 320
                    ysize 75
                    background Frame(Solid("#1a1a2a"), 0, 0)
                    action NullAction()
                    text "请先选择玩家":
                        xalign 0.5
                        yalign 0.5
                        size 34
                        color "#555555"
                        font FONT
