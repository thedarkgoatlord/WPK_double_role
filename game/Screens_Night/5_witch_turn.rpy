
# ── 女巫行动 ──────────────────────────────────────────────────────────────────
screen screen_witch_turn(witch_idx):
    add Solid(BG_NIGHT)
    default witch_action = "none"
    default poison_target = -1

    vbox:
        xalign 0.5
        yalign 0.35
        spacing 26

        text "🧪  女巫请睁眼":
            xalign 0.5
            size 56
            color "#cc66ff"
            font FONT

        $ wlabel = "（第{}号玩家）".format(witch_idx + 1)
        text wlabel:
            xalign 0.5
            size 32
            color COL_DIM
            font FONT

        null height 6

        if wolf_kill_target >= 0:
            $ killed_label = "今夜被狼人击杀：第{}号玩家".format(wolf_kill_target + 1)
            text killed_label:
                xalign 0.5
                size 34
                color COL_WOLF
                font FONT
        else:
            text "今夜狼人未击杀任何人":
                xalign 0.5
                size 34
                color COL_SUB
                font FONT

        null height 10

        hbox:
            xalign 0.5
            spacing 30

            if not witch_save_used and wolf_kill_target >= 0:
                button:
                    xsize 300
                    ysize 80
                    background Frame(Solid("#226633" if witch_action == "save" else "#1e2e1e"), 0, 0)
                    hover_background Frame(Solid("#338844"), 0, 0)
                    action SetScreenVariable("witch_action", "save")
                    text "使用解药  💊":
                        xalign 0.5
                        yalign 0.5
                        size 32
                        color "#aaffcc"
                        font FONT
            else:
                frame:
                    xsize 300
                    ysize 80
                    background Frame(Solid("#1a1a1a"), 0, 0)
                    text "解药已用 / 无目标":
                        xalign 0.5
                        yalign 0.5
                        size 28
                        color "#555555"
                        font FONT

            if not witch_poison_used:
                button:
                    xsize 300
                    ysize 80
                    background Frame(Solid("#552266" if witch_action == "poison" else "#1e1e2e"), 0, 0)
                    hover_background Frame(Solid("#773388"), 0, 0)
                    action SetScreenVariable("witch_action", "poison")
                    text "使用毒药  ☠":
                        xalign 0.5
                        yalign 0.5
                        size 32
                        color "#dd88ff"
                        font FONT
            else:
                frame:
                    xsize 300
                    ysize 80
                    background Frame(Solid("#1a1a1a"), 0, 0)
                    text "毒药已用":
                        xalign 0.5
                        yalign 0.5
                        size 28
                        color "#555555"
                        font FONT

        if witch_action == "poison":
            null height 10
            text "选择毒杀目标：":
                xalign 0.5
                size 30
                color COL_SUB
                font FONT
            $ alive_idxs = [idx for idx in alive_players(players) if idx != witch_idx]
            hbox:
                xalign 0.5
                spacing 40
                vbox:
                    for i in range(0, len(alive_idxs), 2):
                        $ idx = alive_idxs[i]
                        $ bg_p = "#441133" if (idx == poison_target) else "#1e1e2e"
                        $ bg_ph = "#662244" if (idx == poison_target) else "#2a2a44"
                        button:
                            xsize 460
                            ysize 58
                            background Frame(Solid(bg_p), 0, 0)
                            hover_background Frame(Solid(bg_ph), 0, 0)
                            action SetScreenVariable("poison_target", idx)
                            xalign 0.5
                            text "第{}号玩家".format(idx+1):
                                xalign 0.5
                                yalign 0.5
                                size 30
                                color "#ffffff"
                                font FONT
                vbox:
                    for i in range(1, len(alive_idxs), 2):
                        $ idx = alive_idxs[i]
                        $ bg_p = "#441133" if (idx == poison_target) else "#1e1e2e"
                        $ bg_ph = "#662244" if (idx == poison_target) else "#2a2a44"
                        button:
                            xsize 460
                            ysize 58
                            background Frame(Solid(bg_p), 0, 0)
                            hover_background Frame(Solid(bg_ph), 0, 0)
                            action SetScreenVariable("poison_target", idx)
                            xalign 0.5
                            text "第{}号玩家".format(idx+1):
                                xalign 0.5
                                yalign 0.5
                                size 30
                                color "#ffffff"
                                font FONT

        null height 16

        button:
            xsize 300
            ysize 64
            background Frame(Solid("#222233" if witch_action == "none" else "#1a1a2a"), 0, 0)
            hover_background Frame(Solid("#333355"), 0, 0)
            action SetScreenVariable("witch_action", "none")
            xalign 0.5
            text "本夜不行动":
                xalign 0.5
                yalign 0.5
                size 30
                color "#aaaaaa"
                font FONT

        null height 20

        $ can_confirm = (witch_action != "poison") or (poison_target >= 0)
        if can_confirm:
            button:
                xsize 360
                ysize 80
                background Frame(Solid(COL_BTN), 0, 0)
                hover_background Frame(Solid(COL_BTN_H), 0, 0)
                xalign 0.5
                action [Function(witch_resolve, witch_action, wolf_kill_target, poison_target), Return()]
                text "确认行动，闭眼  ▶":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color "#ffffff"
                    font FONT
