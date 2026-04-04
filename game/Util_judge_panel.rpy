# ── 法官快速查看按钮（全局覆盖）────────────────────────────────────────────
init python:
    if "judge_overlay_button" not in config.overlay_screens:
        config.overlay_screens.append("judge_overlay_button")

screen judge_overlay_button():
    zorder 100
    hbox:
        xalign 1.0
        yalign 0.0
        spacing 10
        frame:
            background Frame(Solid("#00000088"), 0, 0)
            padding (8, 6, 8, 6)
            button:
                action Show("screen_judge_panel")
                text "查看状态":
                    size 22
                    color "#ffffff"
                    font FONT

# ── 法官面板（当前身份 + 存活）──────────────────────────────────────────
screen screen_judge_panel():

    modal True
    zorder 200
    add Solid("#000000cc")

    vbox:
        xalign 0.5
        yalign 0.1
        spacing 20

        text "📋 法官面板（全场状态）":
            xalign 0.5
            size 44
            color "#ffffff"
            font FONT

        # 玩家列表
        hbox:
            xalign 0.5
            spacing 20

            vbox:
                spacing 10
                for i in range(0, len(players), 2):
                    $ p = players[i]
                    $ lives = int(p["top_alive"]) + int(p["bottom_alive"])
                    $ status = "死亡" if lives == 0 else ("{}命".format(lives))
                    frame:
                        xsize 600
                        background Frame(Solid("#222222"), 0, 0)
                        padding (10, 6, 10, 6)
                        hbox:
                            spacing 12
                            text "第{}号".format(i+1):
                                size 26
                                color "#cccccc"
                                font FONT
                            text roles_display(p):
                                size 24
                                color "#ffffff"
                                font FONT
                            text status:
                                size 24
                                color ("#cc6666" if lives==0 else "#66cc88")
                                font FONT

            vbox:
                spacing 10
                for i in range(1, len(players), 2):
                    $ p = players[i]
                    $ lives = int(p["top_alive"]) + int(p["bottom_alive"])
                    $ status = "死亡" if lives == 0 else ("{}命".format(lives))
                    frame:
                        xsize 600
                        background Frame(Solid("#222222"), 0, 0)
                        padding (10, 6, 10, 6)
                        hbox:
                            spacing 12
                            text "第{}号".format(i+1):
                                size 26
                                color "#cccccc"
                                font FONT
                            text roles_display(p):
                                size 24
                                color "#ffffff"
                                font FONT
                            text status:
                                size 24
                                color ("#cc6666" if lives==0 else "#66cc88")
                                font FONT

        null height 20

        button:
            xsize 260
            ysize 70
            background Frame(Solid("#444444"), 0, 0)
            action Hide("screen_judge_panel")
            xalign 0.5
            text "关闭":
                xalign 0.5
                yalign 0.5
                size 30
                color "#ffffff"
                font FONT
