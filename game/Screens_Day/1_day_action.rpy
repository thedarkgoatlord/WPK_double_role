# ── 白天：选择结束方式 ────────────────────────────────────────────────────────
screen screen_day_action():
    add Solid(BG_DAY)

    vbox:
        xalign 0.5
        yalign 0.40
        spacing 50

        text "白天讨论结束":
            xalign 0.5
            size 56
            color "#ffcc66"
            font FONT

        text "请选择本轮结束方式：":
            xalign 0.5
            size 36
            color COL_SUB
            font FONT

        hbox:
            xalign 0.5
            spacing 100

            button:
                xsize 340
                ysize 120
                background Frame(Solid("#224488"), 0, 0)
                hover_background Frame(Solid("#336699"), 0, 0)
                action Return("vote")
                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 8
                    text "🗳  投票放逐":
                        xalign 0.5
                        size 38
                        color "#ffffff"
                        font FONT
                    text "投票选出出局玩家":
                        xalign 0.5
                        size 26
                        color "#aaccff"
                        font FONT

            button:
                xsize 340
                ysize 120
                background Frame(Solid("#882222"), 0, 0)
                hover_background Frame(Solid("#aa3333"), 0, 0)
                action Return("explode")
                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 8
                    text "💥  狼人自爆":
                        xalign 0.5
                        size 38
                        color "#ffffff"
                        font FONT
                    text "自爆出局，直接入夜":
                        xalign 0.5
                        size 26
                        color "#ffaaaa"
                        font FONT

