# ── 禁言长老行动 ──────────────────────────────────────────────────────────────
screen screen_elder_turn(elder_idx):
    # 返回一个 Integer，即被禁言的人编号
    add Solid(BG_NIGHT)
    default silence_target = -1

    vbox:
        xalign 0.5
        yalign 0.38
        spacing 30

        text "🕯 禁言长老行动":
            xalign 0.5
            size 56
            color "#cccc66"
            font FONT

        text "请选择一名玩家在明天无法发言":
            xalign 0.5
            size 32
            color COL_SUB
            font FONT

        $ alive_idxs = [idx for idx in alive_players(players) if idx != elder_idx]

        hbox:
            xalign 0.5
            spacing 40

            vbox:
                for i in range(0, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
                    button:
                        xsize 460
                        ysize 64
                        background Frame(Solid("#333322"), 0, 0)
                        hover_background Frame(Solid("#555533"), 0, 0)
                        action SetScreenVariable("silence_target", idx)
                        text "第{}号玩家".format(idx+1):
                            xalign 0.5
                            yalign 0.5
                            size 30
                            color "#ffffff"
                            font FONT

            vbox:
                for i in range(1, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
                    button:
                        xsize 460
                        ysize 64
                        background Frame(Solid("#333322"), 0, 0)
                        hover_background Frame(Solid("#555533"), 0, 0)
                        action SetScreenVariable("silence_target", idx)
                        text "第{}号玩家".format(idx+1):
                            xalign 0.5
                            yalign 0.5
                            size 30
                            color "#ffffff"
                            font FONT

        null height 20

        if silence_target >= 0:
            button:
                xsize 340
                ysize 80
                background Frame(Solid("#666633"), 0, 0)
                hover_background Frame(Solid("#888844"), 0, 0)
                action [Function(elder_silence_resolve, silence_target), Return()]
                xalign 0.5
                text "确认禁言":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color "#ffffff"
                    font FONT
        else:
            button:
                xsize 340
                ysize 80
                background Frame(Solid("#222222"), 0, 0)
                action NullAction()
                xalign 0.5
                text "请选择目标":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color "#555555"
                    font FONT

