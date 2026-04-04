
# ── 预言家查验 ────────────────────────────────────────────────────────────────
screen screen_prophet_turn(prophet_idx):
    add Solid(BG_NIGHT)
    default checked = -1

    vbox:
        xalign 0.5
        yalign 0.38
        spacing 30

        text "🔮  预言家请睁眼":
            xalign 0.5
            size 56
            color "#50aaff"
            font FONT

        $ plabel = "（第{}号玩家）".format(prophet_idx + 1)
        text plabel:
            xalign 0.5
            size 32
            color COL_DIM
            font FONT

        null height 10
        text "请选择今夜查验的目标：":
            xalign 0.5
            size 32
            color COL_SUB
            font FONT

        $ alive_idxs = [idx for idx in alive_players(players) if idx != prophet_idx]
        hbox:
            xalign 0.5
            spacing 40
            vbox:
                for i in range(0, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
                    $ is_sel = (idx == checked)
                    $ bg_c = "#1a2a44" if is_sel else "#1e1e2e"
                    $ bg_h = "#2a3a66" if is_sel else "#2a2a44"
                    button:
                        xsize 500
                        ysize 64
                        background Frame(Solid(bg_c), 0, 0)
                        hover_background Frame(Solid(bg_h), 0, 0)
                        action SetScreenVariable("checked", idx)
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
                    $ is_sel = (idx == checked)
                    $ bg_c = "#1a2a44" if is_sel else "#1e1e2e"
                    $ bg_h = "#2a3a66" if is_sel else "#2a2a44"
                    button:
                        xsize 500
                        ysize 64
                        background Frame(Solid(bg_c), 0, 0)
                        hover_background Frame(Solid(bg_h), 0, 0)
                        action SetScreenVariable("checked", idx)
                        xalign 0.5
                        text "第{}号玩家".format(idx+1):
                            xalign 0.5
                            yalign 0.5
                            size 32
                            color "#ffffff"
                            font FONT

        button:
            xsize 300
            ysize 60
            background Frame(Solid("#333333"), 0, 0)
            action Return()
            xalign 0.5
            text "本夜不查验":
                xalign 0.5
                yalign 0.5
                size 28
                color "#aaaaaa"
                font FONT

        if checked >= 0:
            null height 10
            $ target_p = players[checked]
            $ check_wolf = is_wolf_prophet(target_p)
            $ result_col = COL_WOLF if check_wolf else COL_GREEN
            $ result_txt = "狼人阵营 !" if check_wolf else "好人阵营"
            frame:
                xalign 0.5
                xsize 520
                ysize 100
                background Frame(Solid("#111122"), 0, 0)
                padding (20, 10, 20, 10)
                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 6
                    text "第{}号玩家  查验结果：".format(checked+1):
                        xalign 0.5
                        size 28
                        color COL_SUB
                        font FONT
                    text result_txt:
                        xalign 0.5
                        size 44
                        color result_col
                        font FONT

            null height 16
            button:
                xsize 340
                ysize 80
                background Frame(Solid(COL_BTN), 0, 0)
                hover_background Frame(Solid(COL_BTN_H), 0, 0)
                action Return(checked)
                xalign 0.5
                text "已知晓，闭眼  ▶":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color "#ffffff"
                    font FONT
