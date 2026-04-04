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
        # 接收一个 player 类型，返回 Boolean
        # 最上面的目前是否是狼牌
        return (
            (player["top_alive"] and player["top"] in WOLF_ROLES) or
            (not player["top_alive"] and player["bottom"] in WOLF_ROLES)
        )
    def is_wolf_prophet(player):
        # 接收一个 player 类型，返回 Boolean
        # 用于预言家查验
        if player_count == 6:
            if player["top"] in WOLF_ROLES and player["bottom"] in WOLF_ROLES:
                return False
            if player["top"] in WOLF_ROLES and player["bottom"] == "Duplicate":
                return False
            if player["bottom"] in WOLF_ROLES and player["top"] == "Duplicate":
                return False
        else:
            return is_wolf(player)
    def is_wolf_night(player):
        # 接收一个 player 类型，返回 Boolean
        # 决定晚上是否睁眼
        return is_wolf(player) or (player["bottom_alive"] and player["bottom"] == "Hidden Werewolf") or (player["top"]=="Duplicate" and player["bottom"] in WOLF_ROLES) or (player["bottom"]=="Duplicate" and player["top"] in WOLF_ROLES)

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
default silenced_player = None
default _last_witch_target = None
default _ending = None


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
    $ silenced_player = -1

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

    # 预言家查验（固定流程）
    $ prophet_indices = alive_with_role(players, "Prophet")
    if prophet_indices:
        $ p_idx = prophet_indices[0]
        call screen screen_prophet_turn(p_idx)
        $ checked_target = _return

        if checked_target is not None:
            $ result = is_wolf_prophet(players[checked_target])
            $ current_phase_log["actions"].append({
                "type": "prophet_check",
                "actor": p_idx,
                "target": checked_target,
                "result": result
            })
    else:
        call screen screen_prophet_turn(None)

    # 守卫守护（固定流程）
    $ guard_indices = alive_with_role(players, "Guard")
    if guard_indices:
        $ g_idx = guard_indices[0]
        call screen screen_guard_turn(g_idx)

        if guard_protected_this_night >= 0:
            $ current_phase_log["actions"].append({
                "type": "guard",
                "target": guard_protected_this_night
            })
    else:
        call screen screen_guard_turn(None)

    # 女巫行动（固定流程）
    $ witch_indices = alive_with_role(players, "Witch")
    if witch_indices:
        $ w_idx = witch_indices[0]
        call screen screen_witch_turn(w_idx)

        if witch_save_used or witch_poison_used:
            $ current_phase_log["actions"].append({
                "type": "witch",
                "save_used": witch_save_used,
                "poison_used": witch_poison_used,
                "target": _last_witch_target
            })
    else:
        call screen screen_witch_turn(None)

    # 禁言长老行动（固定流程）
    $ elder_indices = [i for i in alive_players(players) if is_elder(players[i])]
    if elder_indices:
        $ e_idx = elder_indices[0]
        call screen screen_elder_turn(e_idx)

        if silenced_player != -1:
            $ current_phase_log["actions"].append({
                "type": "elder",
                "targets": silenced_player
            })
    else:
        call screen screen_elder_turn(None)

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

    # ── 夜晚结算后检测结局 ──
    $ _ending = check_ending()
    if _ending:
        jump ending_check

    jump day_phase

# ═════════════════════════════════════════════════════════════════════════════
#  白天阶段
# ═════════════════════════════════════════════════════════════════════════════
label day_phase:
    $ current_phase_log = {"phase": "day", "day": night_count, "events": []}

    call screen screen_day_overview(night_count, night_deaths, silenced_player)

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
        # ── 自爆后检测结局 ──
        $ _ending = check_ending()
        if _ending:
            jump ending_check
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
                # ── 投票出局后检测结局 ──
                $ _ending = check_ending()
                if _ending:
                    jump ending_check
            $ game_log.append(current_phase_log)
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





# ── 白天：法官总览 ────────────────────────────────────────────────────────────
screen screen_day_overview(night_n, deaths, silenced):
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

        # 禁言提示
        if silenced != -1:
            hbox:
                xalign 0.5
                spacing 16
                text "被禁言：":
                    yalign 0.5
                    size 34
                    color "#cccc66"
                    font FONT

                text "第{}号".format(silenced):
                    yalign 0.5
                    size 34
                    color "#ffffaa"
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




