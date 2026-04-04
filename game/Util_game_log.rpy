# ── 游戏记录 ──────────────────────────────────────────────────────────────
screen screen_game_log():
    add Solid("#000000aa")

    vbox:
        xalign 0.5
        yalign 0.5
        spacing 20

        text "游戏记录":
            xalign 0.5
            size 50
            color "#ffffff"
            font FONT

        viewport:
            xsize 1200
            ysize 600
            scrollbars "vertical"
            mousewheel True

            vbox:
                spacing 16
                for entry in game_log:
                    $ phase_txt = "第{}夜".format(entry["day"]) if entry["phase"] == "night" else "第{}天".format(entry["day"])
                    frame:
                        background Frame(Solid("#111122"), 0, 0)
                        padding (10,10,10,10)
                        vbox:
                            spacing 6
                            text phase_txt:
                                size 30
                                color "#ccccff"
                                font FONT
                            if entry["events"]:
                                for e in entry["events"]:
                                    $ cause_map = {
                                        "wolf": "被狼人击杀",
                                        "poison": "被女巫毒死",
                                        "vote": "被投票出局",
                                        "vote_saved": "被投票但白痴免死",
                                        "hunter_shoot": "被猎人击杀"
                                    }
                                    $ txt = "{}号 （{}） {}".format(e["player"]+1, str(role_cn(e["role"])), cause_map.get(e["cause"], e["cause"]))
                                    text txt:
                                        size 26
                                        color "#ffffff"
                                        font FONT
                            else:
                                text "无事件":
                                    size 24
                                    color "#888888"
                                    font FONT
                            # Render actions if present
                            if entry.get("actions"):
                                for act in entry["actions"]:
                                    if act["type"] == "wolf_kill":
                                        $ part_txt = "，".join(["{}号".format(i+1) for i in act.get("participants", [])])
                                        $ txt = "狼人（{}）选择击杀：{}号玩家".format(part_txt if part_txt else "未知", act["target"]+1)
                                    elif act["type"] == "prophet_check":
                                        $ res_txt = "狼人" if act["result"] else "好人"
                                        $ txt = "预言家查验：{}号玩家 → {}".format(act["target"]+1, res_txt)
                                    elif act["type"] == "guard":
                                        if act["target"] >= 0:
                                            $ txt = "守卫守护：{}号玩家".format(act["target"]+1)
                                        else:
                                            $ txt = "守卫未守护"
                                    elif act["type"] == "witch":
                                        if act.get("target") is not None:
                                            $ tgt_txt = "{}号玩家".format(act["target"]+1)
                                        else:
                                            $ tgt_txt = "无目标"
                                        $ txt = "女巫行动（解药：{}，毒药：{}，目标：{}）".format("已用" if act["save_used"] else "未用", "已用" if act["poison_used"] else "未用", tgt_txt)
                                    elif act["type"] == "elder":
                                        $ txt = "长老禁言 {} 号".format(str(act["targets"]))
                                    elif act["type"] == "hunter_shoot":
                                        $ txt = "猎人带走 {} 号".format(str(act["target"]))
                                    else:
                                        $ txt = "未知行动"
                                    text txt:
                                        size 24
                                        color "#cccccc"
                                        font FONT

        button:
            xsize 300
            ysize 70
            background Frame(Solid("#444444"), 0, 0)
            action Hide("screen_game_log")
            xalign 0.5
            text "关闭":
                xalign 0.5
                yalign 0.5
                size 30
                color "#ffffff"
                font FONT
