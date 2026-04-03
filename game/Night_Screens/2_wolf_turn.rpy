# ── 狼人睁眼 & 选择击杀目标 ──────────────────────────────────────────────────
screen screen_wolf_turn(wolf_indices):
    add Solid(BG_NIGHT)
    default selected = -1

    vbox:
        xalign 0.5
        yalign 0.38
        spacing 30

        text "🐺  狼人请睁眼":
            xalign 0.5
            size 56
            color COL_WOLF
            font FONT

        text "今晚醒着的狼：":
            xalign 0.5
            size 32
            color COL_SUB
            font FONT
        vbox:
            xalign 0.5
            spacing 10
            for idx in wolf_indices:
                $ wlabel = "第{}号玩家　{}".format(idx+1, roles_display(players[idx]))
                text wlabel:
                    xalign 0.5
                    size 34
                    color COL_WOLF
                    font FONT

        null height 20
        text "选择今夜击杀目标：":
            xalign 0.5
            size 32
            color COL_SUB
            font FONT

        $ alive_idxs = [idx for idx in alive_players(players)]
        hbox:
            xalign 0.5
            spacing 40
            vbox:
                for i in range(0, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
                    $ is_sel = (idx == selected)
                    $ bg_col = "#553333" if is_sel else "#1e1e2e"
                    $ bg_hov = "#774444" if is_sel else "#2a2a44"
                    button:
                        xsize 500
                        ysize 64
                        background Frame(Solid(bg_col), 0, 0)
                        hover_background Frame(Solid(bg_hov), 0, 0)
                        action SetScreenVariable("selected", idx)
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
                    $ is_sel = (idx == selected)
                    $ bg_col = "#553333" if is_sel else "#1e1e2e"
                    $ bg_hov = "#774444" if is_sel else "#2a2a44"
                    button:
                        xsize 500
                        ysize 64
                        background Frame(Solid(bg_col), 0, 0)
                        hover_background Frame(Solid(bg_hov), 0, 0)
                        action SetScreenVariable("selected", idx)
                        xalign 0.5
                        text "第{}号玩家".format(idx+1):
                            xalign 0.5
                            yalign 0.5
                            size 32
                            color "#ffffff"
                            font FONT

        null height 20

        if selected >= 0:
            button:
                xsize 340
                ysize 80
                background Frame(Solid("#882222"), 0, 0)
                hover_background Frame(Solid("#aa3333"), 0, 0)
                action [SetVariable("wolf_kill_target", selected), Function(wolf_kill_resolve, selected), Return()]
                xalign 0.5
                text "确认击杀，闭眼  ▶":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color "#ffffff"
                    font FONT
        else:
            button:
                xsize 340
                ysize 80
                background Frame(Solid("#442222"), 0, 0)
                action NullAction()
                xalign 0.5
                text "请先选择目标":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color "#888888"
                    font FONT
