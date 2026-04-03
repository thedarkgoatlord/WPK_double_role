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
                "top_alive": True,
                "bottom_alive": True,
                "poisoned_by_witch": False,
                "idiot_revealed": False,   # 白痴是否已翻牌
            })
        return result

    WOLF_ROLES  = {"Werewolf", "Hidden Werewolf"}
    CIVIL_ROLES = {"Villager", "Duplicate"}
    ELDER_ROLES = {"Elder"}

    def has_role(player, role):
        return player["top"] == role or player["bottom"] == role

    def is_wolf(player):
        return (
            (player["top_alive"] and player["top"] in WOLF_ROLES) or
            (not player["top_alive"] and player["bottom_alive"] and player["bottom"] in WOLF_ROLES)
        )
    def is_wolf_night(player):
        # 决定晚上是否睁眼
        return is_wolf(player) or (player["bottom_alive"] and player["bottom"] == "Hidden Werewolf")

    def is_double_civil(player):
        return player["top"] in CIVIL_ROLES and player["bottom"] in CIVIL_ROLES

    def is_elder(player):
        return (
            (player["top_alive"] and player["top"] in ELDER_ROLES) or
            (player["bottom_alive"] and player["bottom"] in ELDER_ROLES)
        )

    def alive_players(players):
        return [i for i, p in enumerate(players) if (p["top_alive"] or p["bottom_alive"])]

    def alive_with_role(players, role):
        return [i for i in alive_players(players) if has_role(players[i], role)]

    def roles_display(player):
        top_role = role_cn(player["top"])
        bottom_role = role_cn(player["bottom"])

        if not player["top_alive"]:
            top_role = "{s}" + top_role + "{/s}"

        if not player["bottom_alive"]:
            bottom_role = "{s}" + bottom_role + "{/s}"

        return "{} / {}".format(top_role, bottom_role)


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
default game_log            = []   # 每天/每夜的事件记录
default current_phase_log   = None # 当前阶段临时记录
default silenced_players = []
default _last_witch_target = None


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
    $ current_phase_log = {"phase": "night", "day": night_count, "events": []}
    $ current_phase_log["actions"] = []
    $ wolf_kill_target = -1
    $ guard_protected_this_night = -1
    $ silenced_players = []

    call screen screen_night_transition(night_count)

    # 第一夜 8人局：双民互认
    if night_count == 1 and player_count == 8:
        $ double_civil_indices = [i for i in range(len(players)) if is_double_civil(players[i])]
        if len(double_civil_indices) >= 2:
            call screen screen_civil_recognize(double_civil_indices)

    # 狼人睁眼
    $ wolf_indices = [i for i in alive_players(players) if is_wolf_night(players[i])]
    if wolf_indices:
        call screen screen_wolf_turn(wolf_indices)
        if wolf_kill_target >= 0:
            $ current_phase_log["actions"].append({
                "type": "wolf_kill",
                "target": wolf_kill_target,
                "participants": list(wolf_indices)
            })

    # 预言家查验
    $ prophet_indices = alive_with_role(players, "Prophet")
    if prophet_indices:
        $ p_idx = prophet_indices[0]
        call screen screen_prophet_turn(p_idx)
        $ checked_target = _return

        if checked_target is not None:
            $ result = is_wolf(players[checked_target])
            $ current_phase_log["actions"].append({
                "type": "prophet_check",
                "actor": p_idx,
                "target": checked_target,
                "result": result
            })

    # 守卫守护
    $ guard_indices = alive_with_role(players, "Guard")
    if guard_indices:
        $ g_idx = guard_indices[0]
        call screen screen_guard_turn(g_idx)
        $ current_phase_log["actions"].append({
            "type": "guard",
            "target": guard_protected_this_night
        })

    # 女巫行动
    $ witch_indices = alive_with_role(players, "Witch")
    if witch_indices:
        $ w_idx = witch_indices[0]
        call screen screen_witch_turn(w_idx)
        $ current_phase_log["actions"].append({
            "type": "witch",
            "save_used": witch_save_used,
            "poison_used": witch_poison_used,
            "target": _last_witch_target
        })

    # 禁言长老行动
    $ elder_indices = [i for i in alive_players(players) if is_elder(players[i])]
    if elder_indices:
        $ e_idx = elder_indices[0]
        call screen screen_elder_turn(e_idx)
        if silenced_players:
            $ current_phase_log["actions"].append({
                "type": "elder",
                "targets": list(silenced_players)
            })

    # 猎人开枪状态告知
    $ hunter_indices = alive_with_role(players, "Hunter")
    if hunter_indices:
        $ hunter_idx = hunter_indices[0]

        # 当前存活命数
        $ lives = int(players[hunter_idx]["top_alive"]) + int(players[hunter_idx]["bottom_alive"])

        # 判断这一夜是否会死亡（被刀或被毒）
        $ will_die_tonight = (hunter_idx in night_deaths)

        # 判断死亡的是否是猎人这一层（只要还有命且本夜被击杀，就视为触发）
        $ hunter_can_shoot = (will_die_tonight and not players[hunter_idx]["poisoned_by_witch"])

        call screen screen_hunter_status(hunter_idx, hunter_can_shoot)

    # 结算当夜死亡（守卫守护的目标不死，奶穿机制）
    python:
        for idx in list(night_deaths):
            # 奶穿机制：如果同时被守卫守护且被女巫解药救，则仍然死亡
            saved_by_witch = (idx == _last_witch_target and witch_save_used)
            guarded = (idx == guard_protected_this_night)

            if guarded and not players[idx]["poisoned_by_witch"]:
                if saved_by_witch:
                    # 奶穿：守卫 + 解药 → 仍然死亡（不移除）
                    pass
                else:
                    # 只有守卫生效 → 挡刀
                    night_deaths.remove(idx)

        for idx in night_deaths:
            # 判断本次死亡的是哪一层身份
            if players[idx]["top_alive"]:
                dying_role = players[idx]["top"]
                cause = "poison" if players[idx]["poisoned_by_witch"] else "wolf"
                current_phase_log["events"].append({
                    "player": idx,
                    "role": dying_role,
                    "layer": "top",
                    "cause": cause
                })
                if dying_role == "Hunter" and not players[idx]["poisoned_by_witch"]:
                    renpy.call_screen("screen_hunter_shoot", idx)
                players[idx]["top_alive"] = False

            elif players[idx]["bottom_alive"]:
                dying_role = players[idx]["bottom"]
                cause = "poison" if players[idx]["poisoned_by_witch"] else "wolf"
                current_phase_log["events"].append({
                    "player": idx,
                    "role": dying_role,
                    "layer": "bottom",
                    "cause": cause
                })
                if dying_role == "Hunter" and not players[idx]["poisoned_by_witch"]:
                    renpy.call_screen("screen_hunter_shoot", idx)
                players[idx]["bottom_alive"] = False

    $ game_log.append(current_phase_log)

    jump day_phase
# ── 禁言长老行动 ──────────────────────────────────────────────────────────────
screen screen_elder_turn(elder_idx):
    add Solid(BG_NIGHT)
    default silence_target = -1

    vbox:
        xalign 0.5
        yalign 0.38
        spacing 30

        text "🕯  禁言长老请睁眼":
            xalign 0.5
            size 56
            color "#cccc66"
            font FONT

        $ elabel = "（第{}号玩家）".format(elder_idx + 1)
        text elabel:
            xalign 0.5
            size 32
            color COL_DIM
            font FONT

        null height 10
        text "选择今夜要禁言的目标：":
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
                        xsize 500
                        ysize 64
                        background Frame(Solid("#333322"), 0, 0)
                        hover_background Frame(Solid("#555533"), 0, 0)
                        action SetScreenVariable("silence_target", idx)
                        text "第{}号玩家".format(idx+1):
                            xalign 0.5
                            yalign 0.5
                            size 32
                            color "#ffffff"
                            font FONT
            vbox:
                for i in range(1, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
                    button:
                        xsize 500
                        ysize 64
                        background Frame(Solid("#333322"), 0, 0)
                        hover_background Frame(Solid("#555533"), 0, 0)
                        action SetScreenVariable("silence_target", idx)
                        text "第{}号玩家".format(idx+1):
                            xalign 0.5
                            yalign 0.5
                            size 32
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
                text "确认禁言，闭眼  ▶":
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
                text "请先选择目标":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color "#555555"
                    font FONT


# ═════════════════════════════════════════════════════════════════════════════
#  白天阶段
# ═════════════════════════════════════════════════════════════════════════════
label day_phase:
    $ current_phase_log = {"phase": "day", "day": night_count, "events": []}

    call screen screen_day_overview(night_count, night_deaths)

    call screen screen_day_action

    if _return == "explode":
        call screen screen_wolf_explode
        $ explode_idx = _return
        if players[explode_idx]["top_alive"]:
            $ dying_role = players[explode_idx]["top"]
            if dying_role == "Hunter" and not players[explode_idx]["poisoned_by_witch"]:
                call screen screen_hunter_shoot(explode_idx)
            $ players[explode_idx]["top_alive"] = False
        elif players[explode_idx]["bottom_alive"]:
            $ dying_role = players[explode_idx]["bottom"]
            if dying_role == "Hunter" and not players[explode_idx]["poisoned_by_witch"]:
                call screen screen_hunter_shoot(explode_idx)
            $ players[explode_idx]["bottom_alive"] = False
        call screen screen_explode_result(explode_idx)
        jump night_phase

    else:
        call screen screen_vote
        $ vote_result = _return
        if vote_result >= 0:

            # 判断当前被投掉的是哪一层
            if players[vote_result]["top_alive"]:
                $ dying_role = players[vote_result]["top"]
                $ layer = "top"
            elif players[vote_result]["bottom_alive"]:
                $ dying_role = players[vote_result]["bottom"]
                $ layer = "bottom"

            # ── 白痴逻辑：第一次被投不死，只翻牌 ──
            if dying_role == "Idiot" and not players[vote_result]["idiot_revealed"]:
                $ players[vote_result]["idiot_revealed"] = True
                call screen screen_idiot_reveal(vote_result, layer)
                $ current_phase_log["events"].append({
                    "player": vote_result,
                    "role": dying_role,
                    "layer": layer,
                    "cause": "vote_saved"
                })
            else:
                # 正常死亡流程
                $ current_phase_log["events"].append({
                    "player": vote_result,
                    "role": dying_role,
                    "layer": layer,
                    "cause": "vote"
                })
                if dying_role == "Hunter" and not players[vote_result]["poisoned_by_witch"]:
                    call screen screen_hunter_shoot(vote_result)

                if layer == "top":
                    $ players[vote_result]["top_alive"] = False
                else:
                    $ players[vote_result]["bottom_alive"] = False

                call screen screen_vote_result(vote_result)
            $ game_log.append(current_phase_log)
        else:
            call screen screen_vote_tie
        jump night_phase
# ── 白痴翻牌 ──────────────────────────────────────────────────────────────
screen screen_idiot_reveal(idx, layer):
    add Solid(BG_DAY)
    vbox:
        xalign 0.5
        yalign 0.42
        spacing 36

        text "白痴翻牌！":
            xalign 0.5
            size 56
            color "#66ccff"
            font FONT

        text "第{}号玩家是白痴，本次不出局".format(idx+1):
            xalign 0.5
            size 36
            color "#ffffff"
            font FONT

        if layer == "top":
            $ role_txt = role_cn(players[idx]["top"])
        else:
            $ role_txt = role_cn(players[idx]["bottom"])

        text "已翻开身份：{}".format(role_txt):
            xalign 0.5
            size 34
            color "#aaccff"
            font FONT

        text "下一次被投票时将正常出局":
            xalign 0.5
            size 30
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
            text "继续游戏  ▶":
                xalign 0.5
                yalign 0.5
                size 36
                color "#ffffff"
                font FONT


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






init python:
    def witch_resolve(action, kill_target, p_target):
        global witch_save_used, witch_poison_used, night_deaths, players
        if action == "save":
            witch_save_used = True
            renpy.store._last_witch_target = kill_target
            # 核心修复：从死亡列表中移除狼人目标
            if kill_target in night_deaths:
                night_deaths.remove(kill_target)

        elif action == "poison":
            witch_poison_used = True
            renpy.store._last_witch_target = p_target
            players[p_target]["poisoned_by_witch"] = True
            if p_target not in night_deaths:
                night_deaths.append(p_target)

        # 若不行动或毒人，狼人击杀目标照常加入 night_deaths
        if action != "save" and kill_target >= 0:
            if kill_target not in night_deaths:
                night_deaths.append(kill_target)

    def elder_silence_resolve(target):
        global silenced_players
        if target not in silenced_players:
            silenced_players.append(target)



# ── 白天：法官总览 ────────────────────────────────────────────────────────────
screen screen_day_overview(night_n, deaths):
    add Solid(BG_DAY)

    vbox:
        xalign 0.5
        yalign 0.04
        spacing 24

        hbox:
            xalign 0.0
            yalign 0.0
            button:
                xsize 160
                ysize 60
                background Frame(Solid("#333333"), 0, 0)
                hover_background Frame(Solid("#555555"), 0, 0)
                action Show("screen_game_log")
                text "记录":
                    xalign 0.5
                    yalign 0.5
                    size 24
                    color "#ffffff"
                    font FONT

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
                    $ bg = COL_DEAD if not (p["top_alive"] or p["bottom_alive"]) else COL_ALIVE
                    $ lives = int(p["top_alive"]) + int(p["bottom_alive"])
                    $ status = "† 死亡" if lives == 0 else ("剩余{}条命".format(lives))
                    $ status_col = "#cc7777" if lives == 0 else COL_GREEN
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
                    $ bg = COL_DEAD if not (p["top_alive"] or p["bottom_alive"]) else COL_ALIVE
                    $ lives = int(p["top_alive"]) + int(p["bottom_alive"])
                    $ status = "† 死亡" if lives == 0 else ("剩余{}条命".format(lives))
                    $ status_col = "#cc7777" if lives == 0 else COL_GREEN
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
            text "结束白天讨论  ▶":
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

        $ alive_idxs = [idx for idx in alive_players(players) if is_wolf(players[idx])]
        hbox:
            xalign 0.5
            spacing 40
            vbox:
                for i in range(0, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
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
            vbox:
                for i in range(1, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
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

        $ alive_idxs = alive_players(players)
        hbox:
            xalign 0.5
            spacing 40
            vbox:
                for i in range(0, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
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
            vbox:
                for i in range(1, len(alive_idxs), 2):
                    $ idx = alive_idxs[i]
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

# ── 猎人遗言/开枪 ──────────────────────────────────────────────────────────────
screen screen_hunter_shoot(hunter_idx):
    add Solid(BG_DAY)
    default shoot_target = -1

    vbox:
        xalign 0.5
        yalign 0.4
        spacing 30

        text "猎人遗言阶段":
            xalign 0.5
            size 50
            color "#ffaa44"
            font FONT

        text "是否开枪并带走一条命？":
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
                        xsize 460
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
                        xsize 460
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

        if shoot_target >= 0:
            button:
                xsize 300
                ysize 70
                background Frame(Solid("#aa4444"), 0, 0)
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

init python:
    def hunter_shoot_resolve(target):
        global players

        # 判断击杀的是哪一层
        if players[target]["top_alive"]:
            layer = "top"
            role = players[target]["top"]
            players[target]["top_alive"] = False
        elif players[target]["bottom_alive"]:
            layer = "bottom"
            role = players[target]["bottom"]
            players[target]["bottom_alive"] = False
        else:
            return

        # 写入日志
        if current_phase_log is not None:
            current_phase_log["events"].append({
                "player": target,
                "role": role,
                "layer": layer,
                "cause": "hunter_shoot"
            })

    def wolf_kill_resolve(target):
        global night_deaths
        if target not in night_deaths:
            night_deaths.append(target)


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

    # TODO: 在白天阶段根据 silenced_players 禁止发言或操作