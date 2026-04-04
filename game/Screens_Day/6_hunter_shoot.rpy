
# ── 猎人遗言/开枪 ──────────────────────────────────────────────────────────────
screen screen_hunter_shoot(hunter_idx):
    add Solid(BG_NIGHT)
    default shoot_target = -1

    vbox:
        xalign 0.5
        yalign 0.4
        spacing 30

        text "🔫 猎人开枪":
            xalign 0.5
            size 52
            color "#ffaa44"
            font FONT

        text "请选择一名玩家带走（或放弃）":
            xalign 0.5
            size 30
            color COL_SUB
            font FONT

        $ alive_idxs = [idx for idx in alive_players(players) if idx != hunter_idx]

        hbox:
            xalign 0.5
            spacing 40

            vbox:
                for i in range(0, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
                    button:
                        xsize 440
                        ysize 60
                        background Frame(Solid("#333333"), 0, 0)
                        hover_background Frame(Solid("#555555"), 0, 0)
                        action SetScreenVariable("shoot_target", idx)
                        text "第{}号玩家".format(idx+1):
                            xalign 0.5
                            yalign 0.5
                            size 28
                            color "#ffffff"
                            font FONT

            vbox:
                for i in range(1, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
                    button:
                        xsize 440
                        ysize 60
                        background Frame(Solid("#333333"), 0, 0)
                        hover_background Frame(Solid("#555555"), 0, 0)
                        action SetScreenVariable("shoot_target", idx)
                        text "第{}号玩家".format(idx+1):
                            xalign 0.5
                            yalign 0.5
                            size 28
                            color "#ffffff"
                            font FONT

        null height 20

        if shoot_target >= 0:
            button:
                xsize 300
                ysize 70
                background Frame(Solid("#aa4444"), 0, 0)
                hover_background Frame(Solid("#cc5555"), 0, 0)
                action [Function(hunter_shoot_resolve, shoot_target), Return()]
                xalign 0.5
                text "开枪":
                    xalign 0.5
                    yalign 0.5
                    size 32
                    color "#ffffff"
                    font FONT

        button:
            xsize 300
            ysize 70
            background Frame(Solid("#444444"), 0, 0)
            action Return()
            xalign 0.5
            text "不开枪":
                xalign 0.5
                yalign 0.5
                size 30
                color "#cccccc"
                font FONT
