# RunGame.rpy —— 正式游戏流程（夜晚 / 白天循环）

init python:

    # ── 玩家状态 ────────────────────────────────────────────────────────────────
    # players[i] 对应第 i+1 号玩家（0-indexed）
    # 每条记录：
    #   top    : str   — 上牌身份英文键
    #   bottom : str   — 下牌身份英文键
    #   alive  : bool
    #   poisoned_by_witch : bool  — 被女巫毒死（猎人不能开枪）

    def make_players(assignment):
        count = len(assignment) // 2
        result = []
        for i in range(count):
            result.append({
                "top":    assignment[2 * i],
                "bottom": assignment[2 * i + 1],
                "alive":  True,
                "poisoned_by_witch": False,
            })
        return result

    WOLF_ROLES  = {"Werewolf", "Hidden Werewolf"}
    CIVIL_ROLES = {"Villager", "Duplicate"}

    def has_role(player, role):
        return player["top"] == role or player["bottom"] == role

    def is_wolf(player):
        return player["top"] in WOLF_ROLES or player["bottom"] in WOLF_ROLES

    def is_double_civil(player):
        return player["top"] in CIVIL_ROLES and player["bottom"] in CIVIL_ROLES

    def alive_players(players):
        return [i for i, p in enumerate(players) if p["alive"]]

    def alive_with_role(players, role):
        return [i for i in alive_players(players) if has_role(players[i], role)]

    def roles_display(player):
        return "{} / {}".format(role_cn(player["top"]), role_cn(player["bottom"]))


# ── 游戏全局变量 ──────────────────────────────────────────────────────────────
default players               = []
default night_count           = 0
default night_deaths          = []
default witch_save_used       = False
default witch_poison_used     = False
default wolf_kill_target      = -1
default guard_last_target     = -1
default guard_protected_this_night = -1
default game_over             = False


# ─────────────────────────────────────────────────────────────────────────────
# 入口：从 script.rpy 的 distribute_done 跳入
# ─────────────────────────────────────────────────────────────────────────────
label begin_game:
    $ players = make_players(assignment)
    $ night_count = 0
    $ witch_save_used = False
    $ witch_poison_used = False
    $ guard_last_target = -1
    $ guard_protected_this_night = -1
    $ game_over = False
    jump night_phase


# ═════════════════════════════════════════════════════════════════════════════
#  夜晚阶段
# ═════════════════════════════════════════════════════════════════════════════
label night_phase:
    $ night_count += 1
    $ night_deaths = []
    $ wolf_kill_target = -1
    $ guard_protected_this_night = -1

    call screen screen_night_transition(night_count)

    # 第一夜 8人局：双民互认
    if night_count == 1 and player_count == 8:
        $ double_civil_indices = [i for i in range(len(players)) if is_double_civil(players[i])]
        if len(double_civil_indices) >= 2:
            call screen screen_civil_recognize(double_civil_indices)

    # 狼人睁眼
    $ wolf_indices = [i for i in alive_players(players) if is_wolf(players[i])]
    if wolf_indices:
        call screen screen_wolf_turn(wolf_indices)

    # 预言家查验
    $ prophet_indices = alive_with_role(players, "Prophet")
    if prophet_indices:
        call screen screen_prophet_turn(prophet_indices[0])

    # 守卫守护
    $ guard_indices = alive_with_role(players, "Guard")
    if guard_indices:
        call screen screen_guard_turn(guard_indices[0])

    # 女巫行动
    $ witch_indices = alive_with_role(players, "Witch")
    if witch_indices:
        call screen screen_witch_turn(witch_indices[0])

    # 猎人开枪状态告知
    $ hunter_indices = alive_with_role(players, "Hunter")
    if hunter_indices:
        $ hunter_idx = hunter_indices[0]
        $ hunter_can_shoot = not players[hunter_idx]["poisoned_by_witch"]
        call screen screen_hunter_status(hunter_idx, hunter_can_shoot)

    # 结算当夜死亡（守卫守护的目标不死）
    python:
        for idx in list(night_deaths):
            if idx == guard_protected_this_night:
                night_deaths.remove(idx)
        for idx in night_deaths:
            players[idx]["alive"] = False

    jump day_phase


# ═════════════════════════════════════════════════════════════════════════════
#  白天阶段
# ═════════════════════════════════════════════════════════════════════════════
label day_phase:

    call screen screen_day_overview(night_count, night_deaths)

    call screen screen_day_action

    if _return == "explode":
        call screen screen_wolf_explode
        $ explode_idx = _return
        $ players[explode_idx]["alive"] = False
        call screen screen_explode_result(explode_idx)
        jump night_phase

    else:
        call screen screen_vote
        $ vote_result = _return
        if vote_result >= 0:
            $ players[vote_result]["alive"] = False
            call screen screen_vote_result(vote_result)
        else:
            call screen screen_vote_tie
        jump night_phase


# ═════════════════════════════════════════════════════════════════════════════
#  屏幕定义
# ═════════════════════════════════════════════════════════════════════════════

init python:
    BG_NIGHT = "#06060f"
    BG_DAY   = "#1a1208"
    COL_HEAD  = "#99ccff"
    COL_SUB   = "#aaaacc"
    COL_DIM   = "#666677"
    COL_DEAD  = "#664444"
    COL_ALIVE = "#224422"
    COL_BTN   = "#2255aa"
    COL_BTN_H = "#3366cc"
    COL_WOLF  = "#e05050"
    COL_GREEN = "#66cc88"
    FONT      = "SourceHanSansLite.ttf"


# ── 夜晚过渡 ──────────────────────────────────────────────────────────────────
screen screen_night_transition(n):
    add Solid(BG_NIGHT)
    vbox:
        xalign 0.5
        yalign 0.42
        spacing 40
        text "🌙  第 [n] 夜":
            xalign 0.5
            size 80
            color COL_HEAD
            font FONT
        text "天黑请闭眼":
            xalign 0.5
            size 42
            color COL_SUB
            font FONT
        null height 40
        button:
            xsize 340
            ysize 85
            background Frame(Solid(COL_BTN), 0, 0)
            hover_background Frame(Solid(COL_BTN_H), 0, 0)
            action Return()
            xalign 0.5
            text "进入夜晚  ▶":
                xalign 0.5
                yalign 0.5
                size 38
                color "#ffffff"
                font FONT


# ── 双民互认（仅第一夜 8人局） ───────────────────────────────────────────────
screen screen_civil_recognize(indices):
    add Solid(BG_NIGHT)
    vbox:
        xalign 0.5
        yalign 0.40
        spacing 36
        text "双民请睁眼":
            xalign 0.5
            size 58
            color COL_HEAD
            font FONT
        text "以下玩家互为双民，请相互确认：":
            xalign 0.5
            size 34
            color COL_SUB
            font FONT
        null height 10
        vbox:
            xalign 0.5
            spacing 16
            for idx in indices:
                $ label_str = "第{}号玩家　{}".format(idx+1, roles_display(players[idx]))
                text label_str:
                    xalign 0.5
                    size 36
                    color COL_GREEN
                    font FONT
        null height 30
        text "双民请闭眼":
            xalign 0.5
            size 38
            color COL_SUB
            font FONT
        null height 20
        button:
            xsize 340
            ysize 85
            background Frame(Solid(COL_BTN), 0, 0)
            hover_background Frame(Solid(COL_BTN_H), 0, 0)
            action Return()
            xalign 0.5
            text "确认，继续  ▶":
                xalign 0.5
                yalign 0.5
                size 36
                color "#ffffff"
                font FONT


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

        text "本局狼人阵营：":
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

        vbox:
            xalign 0.5
            spacing 12
            for idx in alive_players(players):
                if not is_wolf(players[idx]):
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
                action [SetVariable("wolf_kill_target", selected), Return()]
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

        vbox:
            xalign 0.5
            spacing 12
            for idx in alive_players(players):
                if idx != prophet_idx:
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

        if checked >= 0:
            null height 10
            $ target_p = players[checked]
            $ check_wolf = is_wolf(target_p)
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
                action Return()
                xalign 0.5
                text "已知晓，闭眼  ▶":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color "#ffffff"
                    font FONT


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

        vbox:
            xalign 0.5
            spacing 12
            for idx in alive_players(players):
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
            vbox:
                xalign 0.5
                spacing 10
                for idx in alive_players(players):
                    if idx != witch_idx:
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


init python:
    def witch_resolve(action, kill_target, p_target):
        global witch_save_used, witch_poison_used, night_deaths, players
        if action == "save":
            witch_save_used = True
            # kill_target 被救，不加入 night_deaths
        elif action == "poison":
            witch_poison_used = True
            players[p_target]["poisoned_by_witch"] = True
            if p_target not in night_deaths:
                night_deaths.append(p_target)
        # 若不行动或毒人，狼人击杀目标照常加入 night_deaths
        if action != "save" and kill_target >= 0:
            if kill_target not in night_deaths:
                night_deaths.append(kill_target)


# ── 猎人开枪状态 ─────────────────────────────────────────────────────────────
screen screen_hunter_status(hunter_idx, can_shoot):
    add Solid(BG_NIGHT)

    vbox:
        xalign 0.5
        yalign 0.42
        spacing 36

        text "🏹  猎人请睁眼":
            xalign 0.5
            size 56
            color "#ff9933"
            font FONT

        $ hlabel = "（第{}号玩家）".format(hunter_idx + 1)
        text hlabel:
            xalign 0.5
            size 32
            color COL_DIM
            font FONT

        null height 20

        if can_shoot:
            text "今夜开枪状态：✔ 可以开枪":
                xalign 0.5
                size 42
                color COL_GREEN
                font FONT
            text "若今夜死亡，可带走一名玩家":
                xalign 0.5
                size 30
                color COL_SUB
                font FONT
        else:
            text "今夜开枪状态：✘ 不可开枪":
                xalign 0.5
                size 42
                color COL_WOLF
                font FONT
            text "你已被女巫毒杀，无法开枪":
                xalign 0.5
                size 30
                color "#cc6655"
                font FONT

        null height 30

        button:
            xsize 340
            ysize 80
            background Frame(Solid(COL_BTN), 0, 0)
            hover_background Frame(Solid(COL_BTN_H), 0, 0)
            action Return()
            xalign 0.5
            text "已知晓，闭眼  ▶":
                xalign 0.5
                yalign 0.5
                size 34
                color "#ffffff"
                font FONT


# ── 白天：法官总览 ────────────────────────────────────────────────────────────
screen screen_day_overview(night_n, deaths):
    add Solid(BG_DAY)

    vbox:
        xalign 0.5
        yalign 0.04
        spacing 24

        text "☀  第 [night_n] 夜结束  —  法官总览":
            xalign 0.5
            size 50
            color "#ffcc66"
            font FONT

        # 昨夜死亡公告
        if deaths:
            hbox:
                xalign 0.5
                spacing 16
                text "昨夜死亡：":
                    yalign 0.5
                    size 34
                    color COL_WOLF
                    font FONT
                for idx in deaths:
                    text "第{}号".format(idx+1):
                        yalign 0.5
                        size 34
                        color "#ff8888"
                        font FONT
        else:
            text "昨夜平安，无人死亡":
                xalign 0.5
                size 34
                color COL_GREEN
                font FONT

        null height 6

        text "全员身份一览（仅法官可见）：":
            xalign 0.5
            size 30
            color COL_DIM
            font FONT

        # 用两列 hbox 代替 grid，避免动态行数报错
        hbox:
            xalign 0.5
            spacing 20

            # 左列：奇数序号玩家（0, 2, 4, 6）
            vbox:
                spacing 12
                for i in range(0, len(players), 2):
                    $ p = players[i]
                    $ bg = COL_DEAD if not p["alive"] else COL_ALIVE
                    $ status = "† 死亡" if not p["alive"] else "存活"
                    $ status_col = "#cc7777" if not p["alive"] else COL_GREEN
                    frame:
                        xsize 700
                        ysize 76
                        background Frame(Solid(bg), 0, 0)
                        padding (16, 8, 16, 8)
                        hbox:
                            yalign 0.5
                            spacing 20
                            text "第{}号".format(i+1):
                                yalign 0.5
                                size 28
                                color "#cccccc"
                                font FONT
                            text roles_display(p):
                                yalign 0.5
                                size 26
                                color "#ffffff"
                                font FONT
                            text status:
                                yalign 0.5
                                size 26
                                color status_col
                                font FONT

            # 右列：偶数序号玩家（1, 3, 5, 7）
            vbox:
                spacing 12
                for i in range(1, len(players), 2):
                    $ p = players[i]
                    $ bg = COL_DEAD if not p["alive"] else COL_ALIVE
                    $ status = "† 死亡" if not p["alive"] else "存活"
                    $ status_col = "#cc7777" if not p["alive"] else COL_GREEN
                    frame:
                        xsize 700
                        ysize 76
                        background Frame(Solid(bg), 0, 0)
                        padding (16, 8, 16, 8)
                        hbox:
                            yalign 0.5
                            spacing 20
                            text "第{}号".format(i+1):
                                yalign 0.5
                                size 28
                                color "#cccccc"
                                font FONT
                            text roles_display(p):
                                yalign 0.5
                                size 26
                                color "#ffffff"
                                font FONT
                            text status:
                                yalign 0.5
                                size 26
                                color status_col
                                font FONT

        null height 16

        button:
            xsize 380
            ysize 80
            background Frame(Solid("#664400"), 0, 0)
            hover_background Frame(Solid("#886600"), 0, 0)
            action Return()
            xalign 0.5
            text "进入白天讨论  ▶":
                xalign 0.5
                yalign 0.5
                size 36
                color "#ffffff"
                font FONT


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


# ── 狼人自爆 ──────────────────────────────────────────────────────────────────
screen screen_wolf_explode():
    add Solid(BG_DAY)
    default explode_sel = -1

    vbox:
        xalign 0.5
        yalign 0.38
        spacing 30

        text "💥  狼人自爆":
            xalign 0.5
            size 60
            color COL_WOLF
            font FONT

        text "请法官选择自爆的狼人玩家：":
            xalign 0.5
            size 34
            color COL_SUB
            font FONT

        vbox:
            xalign 0.5
            spacing 12
            for idx in alive_players(players):
                if is_wolf(players[idx]):
                    $ bg_e = "#553333" if (idx == explode_sel) else "#1e1e2e"
                    $ bg_eh = "#774444" if (idx == explode_sel) else "#2a2a44"
                    button:
                        xsize 520
                        ysize 68
                        background Frame(Solid(bg_e), 0, 0)
                        hover_background Frame(Solid(bg_eh), 0, 0)
                        action SetScreenVariable("explode_sel", idx)
                        xalign 0.5
                        $ elabel = "第{}号玩家　{}".format(idx+1, roles_display(players[idx]))
                        text elabel:
                            xalign 0.5
                            yalign 0.5
                            size 32
                            color "#ffffff"
                            font FONT

        null height 20

        if explode_sel >= 0:
            button:
                xsize 360
                ysize 80
                background Frame(Solid("#882222"), 0, 0)
                hover_background Frame(Solid("#aa3333"), 0, 0)
                action Return(explode_sel)
                xalign 0.5
                text "确认自爆，直接入夜  ▶":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color "#ffffff"
                    font FONT
        else:
            button:
                xsize 360
                ysize 80
                background Frame(Solid("#441111"), 0, 0)
                action NullAction()
                xalign 0.5
                text "请先选择自爆玩家":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color "#555555"
                    font FONT


# ── 自爆结果 ──────────────────────────────────────────────────────────────────
screen screen_explode_result(idx):
    add Solid(BG_DAY)
    vbox:
        xalign 0.5
        yalign 0.42
        spacing 36
        text "💥  第{}号玩家宣布自爆出局".format(idx+1):
            xalign 0.5
            size 52
            color COL_WOLF
            font FONT
        text roles_display(players[idx]):
            xalign 0.5
            size 40
            color "#ff8888"
            font FONT
        text "无投票环节，直接进入下一夜":
            xalign 0.5
            size 34
            color COL_SUB
            font FONT
        null height 30
        button:
            xsize 340
            ysize 80
            background Frame(Solid(COL_BTN), 0, 0)
            hover_background Frame(Solid(COL_BTN_H), 0, 0)
            action Return()
            xalign 0.5
            text "进入下一夜  ▶":
                xalign 0.5
                yalign 0.5
                size 36
                color "#ffffff"
                font FONT


# ── 投票放逐 ──────────────────────────────────────────────────────────────────
screen screen_vote():
    add Solid(BG_DAY)
    default vote_sel = -1

    vbox:
        xalign 0.5
        yalign 0.38
        spacing 30

        text "🗳  投票放逐":
            xalign 0.5
            size 58
            color "#88aaff"
            font FONT

        text "请法官记录投票结果，选择出局玩家：":
            xalign 0.5
            size 32
            color COL_SUB
            font FONT

        vbox:
            xalign 0.5
            spacing 12
            for idx in alive_players(players):
                $ bg_v = "#1a2244" if (idx == vote_sel) else "#1e1e2e"
                $ bg_vh = "#2a3466" if (idx == vote_sel) else "#2a2a44"
                button:
                    xsize 500
                    ysize 64
                    background Frame(Solid(bg_v), 0, 0)
                    hover_background Frame(Solid(bg_vh), 0, 0)
                    action SetScreenVariable("vote_sel", idx)
                    xalign 0.5
                    text "第{}号玩家".format(idx+1):
                        xalign 0.5
                        yalign 0.5
                        size 32
                        color "#ffffff"
                        font FONT

        null height 20

        hbox:
            xalign 0.5
            spacing 60

            button:
                xsize 280
                ysize 75
                background Frame(Solid("#333344"), 0, 0)
                hover_background Frame(Solid("#444466"), 0, 0)
                action Return(-1)
                text "平票，无人出局":
                    xalign 0.5
                    yalign 0.5
                    size 28
                    color "#aaaaaa"
                    font FONT

            if vote_sel >= 0:
                button:
                    xsize 320
                    ysize 75
                    background Frame(Solid("#224488"), 0, 0)
                    hover_background Frame(Solid("#336699"), 0, 0)
                    action Return(vote_sel)
                    text "确认放逐  ▶":
                        xalign 0.5
                        yalign 0.5
                        size 34
                        color "#ffffff"
                        font FONT
            else:
                button:
                    xsize 320
                    ysize 75
                    background Frame(Solid("#1a1a2a"), 0, 0)
                    action NullAction()
                    text "请先选择玩家":
                        xalign 0.5
                        yalign 0.5
                        size 34
                        color "#555555"
                        font FONT


# ── 投票结果 ──────────────────────────────────────────────────────────────────
screen screen_vote_result(idx):
    add Solid(BG_DAY)
    vbox:
        xalign 0.5
        yalign 0.42
        spacing 36
        text "第{}号玩家被放逐出局".format(idx+1):
            xalign 0.5
            size 54
            color "#ffcc66"
            font FONT
        text roles_display(players[idx]):
            xalign 0.5
            size 40
            color "#ffaa88"
            font FONT
        null height 30
        button:
            xsize 340
            ysize 80
            background Frame(Solid(COL_BTN), 0, 0)
            hover_background Frame(Solid(COL_BTN_H), 0, 0)
            action Return()
            xalign 0.5
            text "进入下一夜  ▶":
                xalign 0.5
                yalign 0.5
                size 36
                color "#ffffff"
                font FONT


# ── 平票 ──────────────────────────────────────────────────────────────────────
screen screen_vote_tie():
    add Solid(BG_DAY)
    vbox:
        xalign 0.5
        yalign 0.42
        spacing 36
        text "平票——无人出局":
            xalign 0.5
            size 56
            color "#aaaacc"
            font FONT
        text "进入下一夜":
            xalign 0.5
            size 36
            color COL_SUB
            font FONT
        null height 30
        button:
            xsize 340
            ysize 80
            background Frame(Solid(COL_BTN), 0, 0)
            hover_background Frame(Solid(COL_BTN_H), 0, 0)
            action Return()
            xalign 0.5
            text "进入下一夜  ▶":
                xalign 0.5
                yalign 0.5
                size 36
                color "#ffffff"
                font FONT
