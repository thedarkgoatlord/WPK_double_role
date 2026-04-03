## 游戏脚本主入口

# 角色名称翻译
init python:
    ROLE_NAMES_CN = {
        "Werewolf":        "狼人",
        "Hidden Werewolf": "隐狼",
        "Prophet":         "预言家",
        "Witch":           "女巫",
        "Hunter":          "猎人",
        "Guard":           "守卫",
        "Idiot":           "白痴",
        "Silencer":        "禁言长老",
        "Duplicate":       "盗贼",
        "Villager":        "村民",
    }

    ROLE_COLORS = {
        "Werewolf":        "#e05050",
        "Hidden Werewolf": "#c03030",
        "Prophet":         "#50aaff",
        "Witch":           "#cc66ff",
        "Hunter":          "#ff9933",
        "Guard":           "#66cc66",
        "Idiot":           "#aaaaaa",
        "Silencer":        "#888888",
        "Duplicate":       "#ffdd44",
        "Villager":        "#dddddd",
    }

    def role_cn(role):
        return ROLE_NAMES_CN.get(role, role)

    def role_color(role):
        return ROLE_COLORS.get(role, "#ffffff")


default player_count = 0
default assignment = []
default current_reveal_player = 0


# ─────────────────────────────────────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────────────────────────────────────
label start:
    scene bg room
    jump select_player_count


label select_player_count:
    call screen screen_select_player_count
    $ player_count = _return
    jump generate_roles


label generate_roles:
    $ assignment = generate_assignment(player_count)
    $ current_reveal_player = 1
    jump distribute_roles


label distribute_roles:
    if current_reveal_player > player_count:
        jump distribute_done

    # 请玩家就坐
    call screen screen_player_ready(current_reveal_player)

    # 同时展示上下两张牌
    $ top_role    = assignment[(current_reveal_player - 1) * 2]
    $ bottom_role = assignment[(current_reveal_player - 1) * 2 + 1]
    call screen screen_show_both_roles(current_reveal_player, top_role, bottom_role)

    $ current_reveal_player += 1
    jump distribute_roles


label distribute_done:
    call screen screen_distribute_done
    # "开始游戏"按钮 Return() 后跳入正式游戏
    jump begin_game


# ─────────────────────────────────────────────────────────────────────────────
# 屏幕定义
# ─────────────────────────────────────────────────────────────────────────────

## 选择人数
screen screen_select_player_count():

    add Solid("#0d0d1a")

    vbox:
        xalign 0.5
        yalign 0.42
        spacing 70

        text "狼人杀  双身份":
            xalign 0.5
            size 72
            color "#99ccff"
            font "SourceHanSansLite.ttf"

        text "法官模式  —  请选择本局玩家人数":
            xalign 0.5
            size 38
            color "#aaaacc"
            font "SourceHanSansLite.ttf"

        hbox:
            xalign 0.5
            spacing 140

            button:
                xsize 280
                ysize 200
                background Frame(Solid("#1e2244"), 0, 0)
                hover_background Frame(Solid("#2e3a6e"), 0, 0)
                action Return(6)
                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 10
                    text "6":
                        xalign 0.5
                        size 100
                        color "#ffffff"
                        font "SourceHanSansLite.ttf"
                    text "人局":
                        xalign 0.5
                        size 34
                        color "#ccddff"
                        font "SourceHanSansLite.ttf"

            button:
                xsize 280
                ysize 200
                background Frame(Solid("#1e2244"), 0, 0)
                hover_background Frame(Solid("#2e3a6e"), 0, 0)
                action Return(8)
                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 10
                    text "8":
                        xalign 0.5
                        size 100
                        color "#ffffff"
                        font "SourceHanSansLite.ttf"
                    text "人局":
                        xalign 0.5
                        size 34
                        color "#ccddff"
                        font "SourceHanSansLite.ttf"


## 等待玩家就坐
screen screen_player_ready(player_num):

    add Solid("#0d0d1a")

    vbox:
        xalign 0.5
        yalign 0.40
        spacing 55

        text "请第 [player_num]  号玩家":
            xalign 0.5
            size 56
            color "#aaaacc"
            font "SourceHanSansLite.ttf"

        text "坐到屏幕前，准备好后点击查看身份":
            xalign 0.5
            size 40
            color "#ccccdd"
            font "SourceHanSansLite.ttf"

        text "（请确保其他玩家背对屏幕或离开）":
            xalign 0.5
            size 30
            color "#666677"
            font "SourceHanSansLite.ttf"

        null height 30

        button:
            xsize 360
            ysize 90
            background Frame(Solid("#2255aa"), 0, 0)
            hover_background Frame(Solid("#3366cc"), 0, 0)
            action Return()
            xalign 0.5
            text "我准备好了":
                xalign 0.5
                yalign 0.5
                size 38
                color "#ffffff"
                font "SourceHanSansLite.ttf"


## 同时展示上下两张身份牌
screen screen_show_both_roles(player_num, top_role, bottom_role):

    add Solid("#080810")

    $ top_cn    = role_cn(top_role)
    $ bottom_cn = role_cn(bottom_role)
    $ top_col   = role_color(top_role)
    $ bot_col   = role_color(bottom_role)

    vbox:
        xalign 0.5
        yalign 0.45
        spacing 50

        text "第 [player_num] 号玩家  -  你的双重身份":
            xalign 0.5
            size 38
            color "#666688"
            font "SourceHanSansLite.ttf"

        # 两张牌并排
        hbox:
            xalign 0.5
            spacing 80

            # 上牌
            vbox:
                xalign 0.5
                spacing 18
                text "上  牌":
                    xalign 0.5
                    size 30
                    color "#aaaacc"
                    font "SourceHanSansLite.ttf"
                frame:
                    xsize 420
                    ysize 260
                    background Frame(Solid(top_col), 0, 0)
                    padding (0, 0, 0, 0)
                    text top_cn:
                        xalign 0.5
                        yalign 0.5
                        size 88
                        color "#111111"
                        font "SourceHanSansLite.ttf"

            # 下牌
            vbox:
                xalign 0.5
                spacing 18
                text "下  牌":
                    xalign 0.5
                    size 30
                    color "#aaaacc"
                    font "SourceHanSansLite.ttf"
                frame:
                    xsize 420
                    ysize 260
                    background Frame(Solid(bot_col), 0, 0)
                    padding (0, 0, 0, 0)
                    text bottom_cn:
                        xalign 0.5
                        yalign 0.5
                        size 88
                        color "#111111"
                        font "SourceHanSansLite.ttf"

        text "请记住你的两张身份牌，然后点击继续":
            xalign 0.5
            size 32
            color "#aaaacc"
            font "SourceHanSansLite.ttf"

        button:
            xsize 340
            ysize 85
            background Frame(Solid("#2255aa"), 0, 0)
            hover_background Frame(Solid("#3366cc"), 0, 0)
            action Return()
            xalign 0.5
            text "已记住":
                xalign 0.5
                yalign 0.5
                size 38
                color "#ffffff"
                font "SourceHanSansLite.ttf"


## 分发完毕
screen screen_distribute_done():

    add Solid("#0d0d1a")

    vbox:
        xalign 0.5
        yalign 0.40
        spacing 55

        text "身份分发完毕":
            xalign 0.5
            size 66
            color "#66cc88"
            font "SourceHanSansLite.ttf"

        text "所有玩家已收到身份，游戏即将开始":
            xalign 0.5
            size 38
            color "#aaaacc"
            font "SourceHanSansLite.ttf"

        null height 30

        hbox:
            xalign 0.5
            spacing 100

            button:
                xsize 340
                ysize 90
                background Frame(Solid("#226633"), 0, 0)
                hover_background Frame(Solid("#338844"), 0, 0)
                action Jump("begin_game")
                text "开始游戏  ▶":
                    xalign 0.5
                    yalign 0.5
                    size 38
                    color "#ffffff"
                    font "SourceHanSansLite.ttf"

            button:
                xsize 280
                ysize 90
                background Frame(Solid("#443333"), 0, 0)
                hover_background Frame(Solid("#664444"), 0, 0)
                action Jump("generate_roles")
                text "重新分配":
                    xalign 0.5
                    yalign 0.5
                    size 38
                    color "#ddcccc"
                    font "SourceHanSansLite.ttf"
