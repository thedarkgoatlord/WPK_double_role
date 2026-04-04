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
    call screen screen_assign_method
    if _return == "random":
        $ assignment = generate_assignment(player_count)
    else:
        call screen screen_manual_assign(player_count)
        $ assignment = _return
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
    $ result = renpy.call_screen("screen_show_both_roles", current_reveal_player, top_role, bottom_role)
    if result:
        $ assignment[(current_reveal_player - 1) * 2] = result[0]
        $ assignment[(current_reveal_player - 1) * 2 + 1] = result[1]

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

    default swapped = False
    $ display_top    = bottom_role if swapped else top_role
    $ display_bottom = top_role if swapped else bottom_role

    $ top_cn    = role_cn(display_top)
    $ bottom_cn = role_cn(display_bottom)
    $ top_col   = role_color(display_top)
    $ bot_col   = role_color(display_bottom)

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

        button:
            xsize 260
            ysize 70
            background Frame(Solid("#444488"), 0, 0)
            hover_background Frame(Solid("#6666aa"), 0, 0)
            action ToggleScreenVariable("swapped")
            xalign 0.5
            text "交换上下牌":
                xalign 0.5
                yalign 0.5
                size 30
                color "#ffffff"
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
            action Return((display_top, display_bottom))
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


## ── 选择分配方式 ────────────────────────────────────────────────────────────
screen screen_assign_method():
    add Solid("#0d0d1a")
    vbox:
        xalign 0.5
        yalign 0.40
        spacing 60

        text "选择角色分配方式":
            xalign 0.5
            size 60
            color "#99ccff"
            font "SourceHanSansLite.ttf"

        hbox:
            xalign 0.5
            spacing 120

            button:
                xsize 340
                ysize 220
                background Frame(Solid("#1a3322"), 0, 0)
                hover_background Frame(Solid("#2a5533"), 0, 0)
                action Return("random")
                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 18
                    text "🎲":
                        xalign 0.5
                        size 64
                    text "随机分配":
                        xalign 0.5
                        size 40
                        color "#88ffaa"
                        font "SourceHanSansLite.ttf"
                    text "系统自动生成合法卡组":
                        xalign 0.5
                        size 26
                        color "#66aa77"
                        font "SourceHanSansLite.ttf"

            button:
                xsize 340
                ysize 220
                background Frame(Solid("#22223a"), 0, 0)
                hover_background Frame(Solid("#33336a"), 0, 0)
                action Return("manual")
                vbox:
                    xalign 0.5
                    yalign 0.5
                    spacing 18
                    text "✋":
                        xalign 0.5
                        size 64
                    text "手动分配":
                        xalign 0.5
                        size 40
                        color "#aabbff"
                        font "SourceHanSansLite.ttf"
                    text "法官自行决定每人的卡组":
                        xalign 0.5
                        size 26
                        color "#7788aa"
                        font "SourceHanSansLite.ttf"


## ── 手动分配界面 ─────────────────────────────────────────────────────────────
init python:
    def _get_role_pool(count):
        """返回当前人数对应的角色池列表（带重复）。"""
        import copy
        return list(ROLE_POOLS.get(count, []))

    def _place_role(slots, selected, role):
        """将 role 放入 slots[selected[0]][selected[1]]，返回新的 slots 副本。"""
        si, li = selected
        return [
            [role if (ii == si and layer == li) else v
            for layer, v in enumerate(pair)]
            for ii, pair in enumerate(slots)
        ]

    def _apply_place_and_set(slots, selected, role):
        new_slots = _place_role(slots, selected, role)
        renpy.set_screen_variable("slots", new_slots)

    def _manual_assign_valid(slots, count):
        """
        验证手动分配是否合法：
        1. 每个槽的上下都已填写
        2. 所有槽使用的牌恰好用完角色池
        3. 没有 BAD_COMBOS 组合
        4. 至少有一对 SAFE_PAIRS（双民组合）
        """
        flat = []
        for top, bot in slots:
            if top is None or bot is None:
                return False, "还有空槽未填满"
            flat.append(top)
            flat.append(bot)
        pool = _get_role_pool(count)
        flat_sorted = sorted(flat)
        pool_sorted = sorted(pool)
        if flat_sorted != pool_sorted:
            return False, "牌的数量与角色池不符"
        for top, bot in slots:
            if (top, bot) in BAD_COMBOS:
                return False, "存在非法组合：{}+{}".format(top, bot)
        has_safe = any((top, bot) in SAFE_PAIRS for top, bot in slots)
        if not has_safe:
            return False, "需要至少一名双民玩家"
        return True, ""

    # ─────────────────────────────────────────────
    # 夜晚结算系统（统一伤害模型 + 奶穿机制）
    # ─────────────────────────────────────────────

    def resolve_night(players, night_events):
        """
        players: list of player objects, each must have .lives
        night_events: {
            "wolf_kill": int or None,
            "witch_poison": int or None,
            "witch_save": int or None,
            "guard_protect": int or None,
        }
        """

        wolf_target   = night_events.get("wolf_kill")
        poison_target = night_events.get("witch_poison")
        save_target   = night_events.get("witch_save")
        guard_target  = night_events.get("guard_protect")

        # 兼容：如果女巫救是“开关式”（True 表示救狼人刀目标）
        if save_target is True:
            save_target = wolf_target

        damage_map = {}

        # —— 狼人伤害（可被守卫拦截）——
        if wolf_target is not None:
            if wolf_target != guard_target:
                damage_map[wolf_target] = damage_map.get(wolf_target, 0) + 1
            # 被守卫挡掉则不计入伤害

        # —— 女巫毒（必定生效）——
        if poison_target is not None:
            damage_map[poison_target] = damage_map.get(poison_target, 0) + 1

        # 奶穿：狼人刀 + 守卫守 + 女巫救 同一人 → 强制 +1 伤害
        if wolf_target is not None:
            if wolf_target == guard_target and wolf_target == save_target:
                damage_map[wolf_target] = damage_map.get(wolf_target, 0) + 1

        # —— 女巫救（仅在没有奶穿时生效）——
        if save_target is not None:
            # 非奶穿时才生效
            if not (wolf_target is not None and save_target == wolf_target and save_target == guard_target):
                if save_target in damage_map:
                    damage_map[save_target] -= 1
                    if damage_map[save_target] <= 0:
                        del damage_map[save_target]
    
        # —— 统一扣命（基于上下层结构）——
        for target, dmg in damage_map.items():
            p = players[target]

            for _ in range(dmg):
                # 优先扣上层
                if p["top_alive"]:
                    p["top_alive"] = False
                elif p["bottom_alive"]:
                    p["bottom_alive"] = False
                else:
                    # 已经死透，不再处理
                    break

screen screen_manual_assign(count):
    """
    手动分配界面。
    slots: list of [top_role, bottom_role] or [None, None]
    selected: (slot_index, layer) 当前正在编辑的格子，None 表示无
    """
    add Solid("#0b0b18")

    $ n = count
    $ pool_all = _get_role_pool(n)

    # slots[i] = [top, bottom]，初始全 None
    default slots = [[None, None] for _ in range(n)]
    # (slot_index, "top"/"bottom") 正在选择的格子
    default selected = None
    # 用量统计：当前已放入槽中的每种角色数量
    default used = {}

    python:
        # 重新计算 used
        used = {}
        for top, bot in slots:
            if top:
                used[top] = used.get(top, 0) + 1
            if bot:
                used[bot] = used.get(bot, 0) + 1

        # 各角色总量
        pool_count = {}
        for r in pool_all:
            pool_count[r] = pool_count.get(r, 0) + 1

        # 合法性检查
        ok, err_msg = _manual_assign_valid(slots, n)

        # 当前已选槽位可用的牌（未超出配额）
        def can_place(role):
            return used.get(role, 0) < pool_count.get(role, 0)

        # 按 WOLF / SPECIAL / CIVIL 分组方便展示
        ROLE_ORDER = [
            "Werewolf", "Hidden Werewolf",
            "Prophet", "Witch", "Hunter", "Guard", "Idiot", "Silencer",
            "Duplicate", "Villager",
        ]
        unique_roles = [r for r in ROLE_ORDER if r in pool_count]

    vbox:
        xalign 0.5
        yalign 0.0
        spacing 0

        # ── 标题栏 ──────────────────────────────────────────────────────────
        frame:
            xfill True
            ysize 72
            background Frame(Solid("#111122"), 0, 0)
            padding (30, 0, 30, 0)
            hbox:
                yalign 0.5
                spacing 0
                text "✋  手动分配卡组  —  {}人局".format(n):
                    yalign 0.5
                    size 38
                    color "#99ccff"
                    font "SourceHanSansLite.ttf"
                null width 40
                if err_msg and not ok:
                    text "⚠ {}".format(err_msg):
                        yalign 0.5
                        size 28
                        color "#ffaa44"
                        font "SourceHanSansLite.ttf"

        null height 16

        hbox:
            xalign 0.5
            spacing 40

            # ── 左栏：角色池 ────────────────────────────────────────────────
            vbox:
                xsize 320
                spacing 10

                text "角色池":
                    xalign 0.5
                    size 30
                    color "#aaaacc"
                    font "SourceHanSansLite.ttf"

                text "（点击角色后，再点槽位放置）":
                    xalign 0.5
                    size 22
                    color "#666677"
                    font "SourceHanSansLite.ttf"

                null height 6

                for role in unique_roles:
                    $ remaining = pool_count[role] - used.get(role, 0)
                    $ rc = role_color(role)
                    $ dim = remaining <= 0
                    $ rc_bg = "#1a1a2a" if dim else rc
                    $ label_text = "{}  ×{}".format(role_cn(role), remaining)
                    button:
                        xsize 300
                        ysize 60
                        background Frame(Solid(rc_bg), 0, 0)
                        hover_background Frame(Solid("#555566" if dim else rc), 0, 0)
                        sensitive (selected is not None and not dim)
                        action If(
                            selected is not None and not dim,
                            [
                                Function(_apply_place_and_set, slots, selected, role),
                                SetScreenVariable("selected", None),
                            ]
                        )
                        hbox:
                            xalign 0.5
                            yalign 0.5
                            spacing 12
                            frame:
                                xsize 16
                                ysize 16
                                background Frame(Solid(rc if not dim else "#333333"), 0, 0)
                            text label_text:
                                yalign 0.5
                                size 28
                                color ("#444455" if dim else "#111111")
                                font "SourceHanSansLite.ttf"

            # ── 右栏：玩家槽位 ──────────────────────────────────────────────
            vbox:
                spacing 14

                text "玩家卡组":
                    xalign 0.5
                    size 30
                    color "#aaaacc"
                    font "SourceHanSansLite.ttf"

                text "（先选角色，再点这里的上/下牌位置放置；点已放的牌可清除）":
                    xalign 0.5
                    size 22
                    color "#666677"
                    font "SourceHanSansLite.ttf"

                null height 4

                # 两列并排显示玩家
                hbox:
                    spacing 20

                    # 左列（偶数 index：0, 2, 4, 6）
                    vbox:
                        spacing 10
                        for i in range(0, n, 2):
                            $ top_r  = slots[i][0]
                            $ bot_r  = slots[i][1]
                            $ sel_top = (selected == (i, 0))
                            $ sel_bot = (selected == (i, 1))
                            frame:
                                xsize 560
                                ysize 110
                                background Frame(Solid("#181826"), 0, 0)
                                padding (12, 8, 12, 8)
                                hbox:
                                    yalign 0.5
                                    spacing 14

                                    text "{}号".format(i+1):
                                        yalign 0.5
                                        size 28
                                        color "#aaaacc"
                                        font "SourceHanSansLite.ttf"

                                    vbox:
                                        spacing 6
                                        # 上牌槽
                                        button:
                                            xsize 220
                                            ysize 44
                                            background Frame(Solid(
                                                "#334488" if sel_top else
                                                (role_color(top_r) if top_r else "#222233")
                                            ), 0, 0)
                                            hover_background Frame(Solid("#4455aa"), 0, 0)
                                            action If(
                                                top_r is not None,
                                                # 已有牌 → 清除
                                                [
                                                    SetScreenVariable("slots",
                                                        [[None if (ii==i and li==0) else v
                                                        for li, v in enumerate(pair)]
                                                        for ii, pair in enumerate(slots)]),
                                                    SetScreenVariable("selected", None),
                                                ],
                                                # 空槽 → 选中等待
                                                SetScreenVariable("selected", (i, 0))
                                            )
                                            text ("上：{}" .format(role_cn(top_r)) if top_r else ("▶ 点击选上牌" if sel_top else "上牌 (空)")):
                                                xalign 0.5
                                                yalign 0.5
                                                size 24
                                                color ("#111111" if top_r else ("#ffffff" if sel_top else "#555566"))
                                                font "SourceHanSansLite.ttf"

                                        # 下牌槽
                                        button:
                                            xsize 220
                                            ysize 44
                                            background Frame(Solid(
                                                "#334488" if sel_bot else
                                                (role_color(bot_r) if bot_r else "#222233")
                                            ), 0, 0)
                                            hover_background Frame(Solid("#4455aa"), 0, 0)
                                            action If(
                                                bot_r is not None,
                                                [
                                                    SetScreenVariable("slots",
                                                        [[None if (ii==i and li==1) else v
                                                          for li, v in enumerate(pair)]
                                                         for ii, pair in enumerate(slots)]),
                                                    SetScreenVariable("selected", None),
                                                ],
                                                SetScreenVariable("selected", (i, 1))
                                            )
                                            text ("下：{}".format(role_cn(bot_r)) if bot_r else ("▶ 点击选下牌" if sel_bot else "下牌 (空)")):
                                                xalign 0.5
                                                yalign 0.5
                                                size 24
                                                color ("#111111" if bot_r else ("#ffffff" if sel_bot else "#555566"))
                                                font "SourceHanSansLite.ttf"

                                    # 互换上下
                                    button:
                                        xsize 60
                                        ysize 90
                                        background Frame(Solid("#333344"), 0, 0)
                                        hover_background Frame(Solid("#555566"), 0, 0)
                                        sensitive (top_r is not None and bot_r is not None)
                                        action SetScreenVariable("slots",
                                            [[bot_r if (ii==i and li==0) else
                                            top_r if (ii==i and li==1) else v
                                            for li, v in enumerate(pair)]
                                            for ii, pair in enumerate(slots)])
                                        text "🔄":
                                            xalign 0.5
                                            yalign 0.5
                                            size 30
                                            color "#aaaacc"

                    # 右列（奇数 index：1, 3, 5, 7）
                    vbox:
                        spacing 10
                        for i in range(1, n, 2):
                            $ top_r  = slots[i][0]
                            $ bot_r  = slots[i][1]
                            $ sel_top = (selected == (i, 0))
                            $ sel_bot = (selected == (i, 1))
                            frame:
                                xsize 560
                                ysize 110
                                background Frame(Solid("#181826"), 0, 0)
                                padding (12, 8, 12, 8)
                                hbox:
                                    yalign 0.5
                                    spacing 14

                                    text "{}号".format(i+1):
                                        yalign 0.5
                                        size 28
                                        color "#aaaacc"
                                        font "SourceHanSansLite.ttf"

                                    vbox:
                                        spacing 6
                                        button:
                                            xsize 220
                                            ysize 44
                                            background Frame(Solid(
                                                "#334488" if sel_top else
                                                (role_color(top_r) if top_r else "#222233")
                                            ), 0, 0)
                                            hover_background Frame(Solid("#4455aa"), 0, 0)
                                            action If(
                                                top_r is not None,
                                                [
                                                    SetScreenVariable("slots",
                                                        [[None if (ii==i and li==0) else v
                                                          for li, v in enumerate(pair)]
                                                         for ii, pair in enumerate(slots)]),
                                                    SetScreenVariable("selected", None),
                                                ],
                                                SetScreenVariable("selected", (i, 0))
                                            )
                                            text ("上：{}".format(role_cn(top_r)) if top_r else ("▶ 点击选上牌" if sel_top else "上牌 (空)")):
                                                xalign 0.5
                                                yalign 0.5
                                                size 24
                                                color ("#111111" if top_r else ("#ffffff" if sel_top else "#555566"))
                                                font "SourceHanSansLite.ttf"

                                        button:
                                            xsize 220
                                            ysize 44
                                            background Frame(Solid(
                                                "#334488" if sel_bot else
                                                (role_color(bot_r) if bot_r else "#222233")
                                            ), 0, 0)
                                            hover_background Frame(Solid("#4455aa"), 0, 0)
                                            action If(
                                                bot_r is not None,
                                                [
                                                    SetScreenVariable("slots",
                                                        [[None if (ii==i and li==1) else v
                                                          for li, v in enumerate(pair)]
                                                         for ii, pair in enumerate(slots)]),
                                                    SetScreenVariable("selected", None),
                                                ],
                                                SetScreenVariable("selected", (i, 1))
                                            )
                                            text ("下：{}".format(role_cn(bot_r)) if bot_r else ("▶ 点击选下牌" if sel_bot else "下牌 (空)")):
                                                xalign 0.5
                                                yalign 0.5
                                                size 24
                                                color ("#111111" if bot_r else ("#ffffff" if sel_bot else "#555566"))
                                                font "SourceHanSansLite.ttf"

                                    button:
                                        xsize 60
                                        ysize 90
                                        background Frame(Solid("#333344"), 0, 0)
                                        hover_background Frame(Solid("#555566"), 0, 0)
                                        sensitive (top_r is not None and bot_r is not None)
                                        action SetScreenVariable("slots",
                                            [[bot_r if (ii==i and li==0) else
                                              top_r if (ii==i and li==1) else v
                                              for li, v in enumerate(pair)]
                                             for ii, pair in enumerate(slots)])
                                        text "🔄":
                                            xalign 0.5
                                            yalign 0.5
                                            size 30
                                            color "#aaaacc"

        null height 20

        # ── 底部按钮 ─────────────────────────────────────────────────────────
        hbox:
            xalign 0.5
            spacing 60

            # 清空全部
            button:
                xsize 240
                ysize 72
                background Frame(Solid("#442222"), 0, 0)
                hover_background Frame(Solid("#663333"), 0, 0)
                action [
                    SetScreenVariable("slots", [[None, None] for _ in range(n)]),
                    SetScreenVariable("selected", None),
                ]
                text "清空全部":
                    xalign 0.5
                    yalign 0.5
                    size 32
                    color "#ffaaaa"
                    font "SourceHanSansLite.ttf"

            # 确认（合法才能点）
            button:
                xsize 320
                ysize 72
                background Frame(Solid("#226633" if ok else "#1a3322"), 0, 0)
                hover_background Frame(Solid("#338844" if ok else "#1a3322"), 0, 0)
                sensitive ok
                action Return([v for pair in slots for v in pair])
                text "确认卡组  ▶":
                    xalign 0.5
                    yalign 0.5
                    size 34
                    color ("#ffffff" if ok else "#445544")
                    font "SourceHanSansLite.ttf"
