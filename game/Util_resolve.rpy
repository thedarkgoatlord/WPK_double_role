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
        global silenced_player
        silenced_player = target
