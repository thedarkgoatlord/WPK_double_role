init python:
    def reset_night_events():
        renpy.store.night_events = {
            "wolf_kill": None,
            "witch_poison": None,
            "witch_save": None,
            "guard_protect": None,
        }

    def hunter_shoot_resolve(target):
        # 立即结算：造成1点伤害（只击杀一层），并记录日志
        if not hasattr(renpy.store, "players"):
            return

        players = renpy.store.players
        p = players[target]

        # 执行一次伤害（优先扣上层）
        if p["top_alive"]:
            p["top_alive"] = False
            layer = "上"
            dying_role = players[target]["top"]
            layer = "top"
        elif p["bottom_alive"]:
            p["bottom_alive"] = False
            layer = "下"
            dying_role = players[target]["bottom"]
            layer = "bottom"
        else:
            # 已经死透，无事发生
            return

        current_phase_log["events"].append({
            "cause": "hunter_shoot",
            "player": target,
            "role": dying_role,
            "layer": layer
        })

    def wolf_kill_resolve(target):
        # 确保 night_events 已初始化
        if not hasattr(renpy.store, "night_events"):
            reset_night_events()
        renpy.store.night_events["wolf_kill"] = target

    def witch_resolve(action, kill_target, p_target):
        global witch_save_used, witch_poison_used, _last_witch_target

        # 确保 night_events 已初始化
        if not hasattr(renpy.store, "night_events"):
            reset_night_events()

        if action == "save":
            witch_save_used = True
            renpy.store.night_events["witch_save"] = True   # 开关式

        elif action == "poison":
            witch_poison_used = True
            _last_witch_target = p_target
            renpy.store.night_events["witch_poison"] = p_target

    def elder_silence_resolve(target):
        global silenced_player
        silenced_player = target
