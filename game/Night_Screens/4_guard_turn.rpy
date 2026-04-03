# ── 守卫守护 ──────────────────────────────────────────────────────────────────
screen screen_guard_turn(guard_idx):
    add Solid(BG_NIGHT)
    default guarding = -1

    vbox:
        xalign 0.5
        yalign 0.38
        spacing 30

        text "🛡  守卫请睁眼":
            xalign 0.5
            size 56
            color "#66cc66"
            font FONT

        $ glabel = "（第{}号玩家）".format(guard_idx + 1)
        text glabel:
            xalign 0.5
            size 32
            color COL_DIM
            font FONT

        if guard_last_target >= 0:
            $ last_txt = "上一夜守护了第{}号玩家，今夜不可连守".format(guard_last_target + 1)
            text last_txt:
                xalign 0.5
                size 28
                color "#cc9933"
                font FONT

        null height 10
        text "选择今夜守护的目标：":
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
                    $ can_guard = (idx != guard_last_target)
                    $ bg_c = "#1a3322" if (idx == guarding) else ("#1e1e2e" if can_guard else "#1a1a1a")
                    $ bg_h = "#2a5533" if (idx == guarding) else ("#2a2a44" if can_guard else "#1a1a1a")
                    $ txt_col = "#ffffff" if can_guard else "#555555"
                    button:
                        xsize 500
                        ysize 64
                        background Frame(Solid(bg_c), 0, 0)
                        hover_background Frame(Solid(bg_h), 0, 0)
                        action (SetScreenVariable("guarding", idx) if can_guard else NullAction())
                        xalign 0.5
                        text "第{}号玩家".format(idx+1):
                            xalign 0.5
                            yalign 0.5
                            size 32
                            color txt_col
                            font FONT
            vbox:
                for i in range(1, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
                    $ can_guard = (idx != guard_last_target)
                    $ bg_c = "#1a3322" if (idx == guarding) else ("#1e1e2e" if can_guard else "#1a1a1a")
                    $ bg_h = "#2a5533" if (idx == guarding) else ("#2a2a44" if can_guard else "#1a1a1a")
                    $ txt_col = "#ffffff" if can_guard else "#555555"
                    button:
                        xsize 500
                        ysize 64
                        background Frame(Solid(bg_c), 0, 0)
                        hover_background Frame(Solid(bg_h), 0, 0)
                        action (SetScreenVariable("guarding", idx) if can_guard else NullAction())
                        xalign 0.5
                        text "第{}号玩家".format(idx+1):
                            xalign 0.5
                            yalign 0.5
                            size 32
                            color txt_col
                            font FONT

        button:
            xsize 340
            ysize 60
            background Frame(Solid("#333333"), 0, 0)
            action [SetVariable("guard_protected_this_night", -1), Return()]
            xalign 0.5
            text "本夜不守护":
                xalign 0.5
                yalign 0.5
                size 30
                color "#aaaaaa"
                font FONT

        null height 20

        if guarding >= 0:
            button:
                xsize 340
                ysize 80
                background Frame(Solid("#226633"), 0, 0)
                hover_background Frame(Solid("#338844"), 0, 0)
                action [SetVariable("guard_protected_this_night", guarding),
                        SetVariable("guard_last_target", guarding),
                        Return()]
                xalign 0.5
                text "确认守护，闭眼  ▶":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color "#ffffff"
                    font FONT
        else:
            button:
                xsize 340
                ysize 80
                background Frame(Solid("#222233"), 0, 0)
                action NullAction()
                xalign 0.5
                text "请先选择目标":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color "#555555"
                    font FONT
