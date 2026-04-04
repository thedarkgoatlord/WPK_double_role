# Ending.rpy —— 结局检测 & 胜利画面

# ═════════════════════════════════════════════════════════════════════════════
#  结局检测函数（在 init python 中定义，供任何地方调用）
# ═════════════════════════════════════════════════════════════════════════════
init python:

    def check_ending():
        """
        每次有人出局后调用。
        返回 "wolf"   —— 狼人胜利（双民全灭）
        返回 "good"   —— 好人胜利（所有能夜间睁眼的狼消失）
        返回 None     —— 游戏继续
        """

        # ── 条件1：双民（双层均为 CIVIL_ROLES）全灭 → 狼人胜利 ──────────────
        double_civil_alive = any(
            is_double_civil(p) and (p["top_alive"] or p["bottom_alive"])
            for p in players
        )
        if not double_civil_alive:
            return "wolf"

        # ── 条件2：没有任何夜间睁眼的狼 → 好人胜利 ─────────────────────────
        night_wolf_alive = any(
            is_wolf_night(p)
            for p in players
            if p["top_alive"] or p["bottom_alive"]
        )
        if not night_wolf_alive:
            return "good"

        return None


# ═════════════════════════════════════════════════════════════════════════════
#  结局跳转 label（在需要检测的节点插入：$ _ending = check_ending(); if _ending: jump ending_check）
# ═════════════════════════════════════════════════════════════════════════════
label ending_check:
    if _ending == "wolf":
        call screen screen_wolf_wins
    elif _ending == "good":
        call screen screen_good_wins
    jump begin_game   # 游戏结束后重置回起点（或改为 return / 主菜单）


# ═════════════════════════════════════════════════════════════════════════════
#  狼人胜利画面
# ═════════════════════════════════════════════════════════════════════════════
screen screen_wolf_wins():
    add Solid("#08040f")

    # 背景血色光晕
    add Solid("#3a000a"):
        xsize 900
        ysize 900
        xalign 0.5
        yalign 0.5
        alpha 0.35

    vbox:
        xalign 0.5
        yalign 0.42
        spacing 40

        # 主标题
        text "🐺  狼人胜利":
            xalign 0.5
            size 80
            color "#cc2222"
            font FONT
            outlines [(4, "#000000", 0, 0)]

        # 副标题
        text "双民阵营已全灭":
            xalign 0.5
            size 40
            color "#ff8888"
            font FONT

        null height 20

        # 存活玩家一览（仅显示仍有命的）
        text "存活玩家：":
            xalign 0.5
            size 30
            color "#aa6666"
            font FONT

        hbox:
            xalign 0.5
            spacing 20

            # 左列（偶数 index）
            vbox:
                spacing 10
                for i in range(0, len(players), 2):
                    $ p = players[i]
                    if p["top_alive"] or p["bottom_alive"]:
                        $ wolf_mark = "🐺 " if is_wolf_night(p) else ""
                        frame:
                            xsize 520
                            ysize 64
                            background Frame(Solid("#2a0a0a"), 0, 0)
                            padding (14, 6, 14, 6)
                            hbox:
                                yalign 0.5
                                spacing 16
                                text "{}{}号".format(wolf_mark, i+1):
                                    yalign 0.5
                                    size 26
                                    color "#ff9999"
                                    font FONT
                                text roles_display(p):
                                    yalign 0.5
                                    size 24
                                    color "#dddddd"
                                    font FONT

            # 右列（奇数 index）
            vbox:
                spacing 10
                for i in range(1, len(players), 2):
                    $ p = players[i]
                    if p["top_alive"] or p["bottom_alive"]:
                        $ wolf_mark = "🐺 " if is_wolf_night(p) else ""
                        frame:
                            xsize 520
                            ysize 64
                            background Frame(Solid("#2a0a0a"), 0, 0)
                            padding (14, 6, 14, 6)
                            hbox:
                                yalign 0.5
                                spacing 16
                                text "{}{}号".format(wolf_mark, i+1):
                                    yalign 0.5
                                    size 26
                                    color "#ff9999"
                                    font FONT
                                text roles_display(p):
                                    yalign 0.5
                                    size 24
                                    color "#dddddd"
                                    font FONT

        null height 30

        button:
            xsize 360
            ysize 80
            background Frame(Solid("#661111"), 0, 0)
            hover_background Frame(Solid("#882222"), 0, 0)
            action Return()
            xalign 0.5
            text "结束本局  ▶":
                xalign 0.5
                yalign 0.5
                size 38
                color "#ffffff"
                font FONT


# ═════════════════════════════════════════════════════════════════════════════
#  好人胜利画面
# ═════════════════════════════════════════════════════════════════════════════
screen screen_good_wins():
    add Solid("#040a14")

    # 背景蓝色光晕
    add Solid("#002244"):
        xsize 900
        ysize 900
        xalign 0.5
        yalign 0.5
        alpha 0.4

    vbox:
        xalign 0.5
        yalign 0.42
        spacing 40

        # 主标题
        text "✨  好人胜利":
            xalign 0.5
            size 80
            color "#44aaff"
            font FONT
            outlines [(4, "#000000", 0, 0)]

        # 副标题
        text "所有夜间狼已消灭":
            xalign 0.5
            size 40
            color "#88ccff"
            font FONT

        null height 20

        # 存活玩家一览
        text "存活玩家：":
            xalign 0.5
            size 30
            color "#6699aa"
            font FONT

        hbox:
            xalign 0.5
            spacing 20

            # 左列（偶数 index）
            vbox:
                spacing 10
                for i in range(0, len(players), 2):
                    $ p = players[i]
                    if p["top_alive"] or p["bottom_alive"]:
                        frame:
                            xsize 520
                            ysize 64
                            background Frame(Solid("#0a1a2a"), 0, 0)
                            padding (14, 6, 14, 6)
                            hbox:
                                yalign 0.5
                                spacing 16
                                text "{}号".format(i+1):
                                    yalign 0.5
                                    size 26
                                    color "#88ccff"
                                    font FONT
                                text roles_display(p):
                                    yalign 0.5
                                    size 24
                                    color "#dddddd"
                                    font FONT

            # 右列（奇数 index）
            vbox:
                spacing 10
                for i in range(1, len(players), 2):
                    $ p = players[i]
                    if p["top_alive"] or p["bottom_alive"]:
                        frame:
                            xsize 520
                            ysize 64
                            background Frame(Solid("#0a1a2a"), 0, 0)
                            padding (14, 6, 14, 6)
                            hbox:
                                yalign 0.5
                                spacing 16
                                text "{}号".format(i+1):
                                    yalign 0.5
                                    size 26
                                    color "#88ccff"
                                    font FONT
                                text roles_display(p):
                                    yalign 0.5
                                    size 24
                                    color "#dddddd"
                                    font FONT

        null height 30

        button:
            xsize 360
            ysize 80
            background Frame(Solid("#114466"), 0, 0)
            hover_background Frame(Solid("#226688"), 0, 0)
            action Return()
            xalign 0.5
            text "结束本局  ▶":
                xalign 0.5
                yalign 0.5
                size 38
                color "#ffffff"
                font FONT
