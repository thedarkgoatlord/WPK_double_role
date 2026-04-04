
# ── 狼人自爆 ──────────────────────────────────────────────────────────────────
screen screen_wolf_explode():
    add Solid(BG_DAY)
    default explode_sel = -1

    vbox:
        xalign 0.5
        yalign 0.38
        spacing 30

        text "💥  狼人自爆":
            xalign 0.5
            size 60
            color COL_WOLF
            font FONT

        text "请法官选择自爆的狼人玩家：":
            xalign 0.5
            size 34
            color COL_SUB
            font FONT

        $ alive_idxs = [idx for idx in alive_players(players) if is_wolf(players[idx])]
        hbox:
            xalign 0.5
            spacing 40
            vbox:
                for i in range(0, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
                    $ bg_e = "#553333" if (idx == explode_sel) else "#1e1e2e"
                    $ bg_eh = "#774444" if (idx == explode_sel) else "#2a2a44"
                    button:
                        xsize 520
                        ysize 68
                        background Frame(Solid(bg_e), 0, 0)
                        hover_background Frame(Solid(bg_eh), 0, 0)
                        action SetScreenVariable("explode_sel", idx)
                        xalign 0.5
                        $ elabel = "第{}号玩家　{}".format(idx+1, roles_display(players[idx]))
                        text elabel:
                            xalign 0.5
                            yalign 0.5
                            size 32
                            color "#ffffff"
                            font FONT
            vbox:
                for i in range(1, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
                    $ bg_e = "#553333" if (idx == explode_sel) else "#1e1e2e"
                    $ bg_eh = "#774444" if (idx == explode_sel) else "#2a2a44"
                    button:
                        xsize 520
                        ysize 68
                        background Frame(Solid(bg_e), 0, 0)
                        hover_background Frame(Solid(bg_eh), 0, 0)
                        action SetScreenVariable("explode_sel", idx)
                        xalign 0.5
                        $ elabel = "第{}号玩家　{}".format(idx+1, roles_display(players[idx]))
                        text elabel:
                            xalign 0.5
                            yalign 0.5
                            size 32
                            color "#ffffff"
                            font FONT

        null height 20

        if explode_sel >= 0:
            button:
                xsize 360
                ysize 80
                background Frame(Solid("#882222"), 0, 0)
                hover_background Frame(Solid("#aa3333"), 0, 0)
                action Return(explode_sel)
                xalign 0.5
                text "确认自爆，直接入夜  ▶":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color "#ffffff"
                    font FONT
        else:
            button:
                xsize 360
                ysize 80
                background Frame(Solid("#441111"), 0, 0)
                action NullAction()
                xalign 0.5
                text "请先选择自爆玩家":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color "#555555"
                    font FONT

