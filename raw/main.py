import json
import math
import statistics

# --------------------
# Load JSON
# --------------------
with open("JSONNAME.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# --------------------
# Load ID lists
# --------------------
def load_id_list(path):
    with open(path, "r") as f:
        return set(int(x) for x in f.read().split())

abyssal_cv = load_id_list("abyssal_cv.txt")
friendly_cv = load_id_list("friendly_cv.txt")
abyssal_ss = load_id_list("abyssal_ss.txt")
friendly_ss = load_id_list("friendly_ss.txt")

# Find total number of battles
nodenum = max(len(d["battles"]) for d in data)

tally = []
index = 0

# Main loop
for i, entry in enumerate(data):

    if len(entry["battles"]) != nodenum:
        entry["time"] = float("nan")
        continue

    index += 1

    detection_plane = 0
    detection_noplane = 0
    dogfight_single = 0
    dogfight_double = 0
    AACI = 0
    otorp = 0
    single = 0
    DA = 0
    cvshell = 0
    cvci = 0
    bbci = 0
    asw = 0
    ctorp = 0
    yasen = 0
    nzci = 0
    gunci = 0
    tci = 0

    for j in range(nodenum):
        battle = entry["battles"][j]
        d = battle["data"]

        # Detection
        detection = d["api_search"][0]
        if 1 <= detection <= 4:
            detection_plane += 1
        elif detection == 5:
            detection_noplane += 1

        # Air battle
        if sum(d["api_stage_flag"][1:3]) != 0:
            s1 = d["api_kouku"]["api_stage1"]
            if s1["api_f_count"] != 0 and s1["api_e_count"] != 0:
                dogfight_double += 1
            else:
                dogfight_single += 1

            if d["api_stage_flag"][1] == 1:
                if "api_air_fire" in d["api_kouku"].get("api_stage2", {}):
                    AACI += 1

        # OASW
        if d.get("api_opening_taisen_flag", 0) == 1:
            asw += len(d["api_opening_taisen"]["api_at_list"])

        # Opening torpedo
        if d["api_opening_flag"] == 1:
            otorp += 1

        # Defender index
        def get_def_idx(df):
            if isinstance(df, list):
                return min(df) + 1
            return df + 1

        # First shelling
        if d["api_hourai_flag"][0] == 1:
            h = d["api_hougeki1"]
            single += len(h["api_at_list"])

            for k in range(len(h["api_at_list"])):
                atk_enemy = h["api_at_eflag"][k] == 1
                atk_idx = h["api_at_list"][k] + 1
                atk_type = h["api_at_type"][k]

                # CV shelling
                is_cv = (
                    (atk_enemy and d["api_ship_ke"][atk_idx - 1] in abyssal_cv) or
                    (not atk_enemy and entry["fleet1"][atk_idx - 1]["mst_id"] in friendly_cv)
                )

                if is_cv:
                    if atk_type == 7:
                        cvci += 1
                    else:
                        cvshell += 1
                    single -= 1
                else:
                    df_idx = get_def_idx(h["api_df_list"][k])
                    if (
                        (not atk_enemy and d["api_ship_ke"][df_idx - 1] in abyssal_ss) or
                        (atk_enemy and entry["fleet1"][df_idx - 1]["mst_id"] in friendly_ss)
                    ):
                        asw += 1
                        single -= 1

                # Artillery spotting
                if 3 <= atk_type <= 6:
                    bbci += 1
                    single -= 1

                # DA
                if atk_type == 2:
                    DA += 1
                    single -= 1

        # Second shelling
        if d["api_hourai_flag"][1] == 1:
            h = d["api_hougeki2"]
            single += len(h["api_at_list"])

            for k in range(len(h["api_at_list"])):
                atk_enemy = h["api_at_eflag"][k] == 1
                atk_idx = h["api_at_list"][k] + 1
                atk_type = h["api_at_type"][k]

                is_cv = (
                    (atk_enemy and d["api_ship_ke"][atk_idx - 1] in abyssal_cv) or
                    (not atk_enemy and entry["fleet1"][atk_idx - 1]["mst_id"] in friendly_cv)
                )

                if is_cv:
                    if atk_type == 7:
                        cvci += 1
                    else:
                        cvshell += 1
                    single -= 1
                else:
                    df_idx = get_def_idx(h["api_df_list"][k])
                    if (
                        (not atk_enemy and d["api_ship_ke"][df_idx - 1] in abyssal_ss) or
                        (atk_enemy and entry["fleet1"][df_idx - 1]["mst_id"] in friendly_ss)
                    ):
                        asw += 1
                        single -= 1

                if 3 <= atk_type <= 6:
                    bbci += 1
                    single -= 1

                if atk_type == 2:
                    DA += 1
                    single -= 1

        # Closing torpedo
        if d["api_hourai_flag"][3] == 1:
            ctorp += 1

        # Night battle
        if battle.get("yasen"):
            yasen += 1
            h = battle["yasen"]["api_hougeki"]
            single += len(h["api_at_list"])

            for k in range(len(h["api_at_list"])):
                atk_enemy = h["api_at_eflag"][k] == 1
                atk_idx = h["api_at_list"][k] + 1
                sp = h["api_sp_list"][k]

                is_cv = (
                    (atk_enemy and d["api_ship_ke"][atk_idx - 1] in abyssal_cv) or
                    (not atk_enemy and entry["fleet1"][atk_idx - 1]["mst_id"] in friendly_cv)
                )

                if is_cv:
                    if sp == 6:
                        cvci += 1
                    else:
                        cvshell += 1
                    single -= 1
                else:
                    df_idx = get_def_idx(h["api_df_list"][k])
                    if (
                        (not atk_enemy and d["api_ship_ke"][df_idx - 1] in abyssal_ss) or
                        (atk_enemy and entry["fleet1"][df_idx - 1]["mst_id"] in friendly_ss)
                    ):
                        asw += 1
                        single -= 1

                if sp == 1:
                    DA += 1
                    single -= 1
                elif sp == 200:
                    nzci += 1
                    single -= 1
                elif sp in (4, 5):
                    gunci += 1
                    single -= 1
                elif sp in (2, 3, 7, 8):
                    tci += 1
                    single -= 1

    # Time calculation
    baseline = 0 # Base time for sortie outside of battle animations, edit if needed
    animations = [
        detection_plane, detection_noplane,
        dogfight_single, dogfight_double, AACI,
        single, DA, otorp, ctorp,
        cvshell, cvci, bbci, asw,
        yasen, nzci, gunci, tci
    ]

    weights = [
        5.1, 4.0, 8.4, 11.5, 3.2, 1.7, 2.8, 3.5, 5.3,
        3.7, 6.3, 6.1, 2.7, 6.0, 8.3, 3.8, 5.5
    ]

    time = baseline + sum(w * a for w, a in zip(weights, animations))

    tally.append({
        "datano": i + 1,
        "time": time,
        "detection_plane": detection_plane,
        "detection_noplane": detection_noplane,
        "dogfight_single": dogfight_single,
        "dogfight_double": dogfight_double,
        "AACI": AACI,
        "single": single,
        "DA": DA,
        "otorp": otorp,
        "ctorp": ctorp,
        "cvshell": cvshell,
        "cvci": cvci,
        "bbci": bbci,
        "asw": asw,
        "yasen": yasen,
        "nzci": nzci,
        "gunci": gunci,
        "tci": tci
    })

# Statistics
times = [t["time"] for t in tally]

avgtime = statistics.mean(times)
time_std = statistics.stdev(times)

avg_detection_plane = statistics.mean(t["detection_plane"] for t in tally)
avg_detection_noplane = statistics.mean(t["detection_noplane"] for t in tally)
avg_dogfight_single = statistics.mean(t["dogfight_single"] for t in tally)
avg_dogfight_double = statistics.mean(t["dogfight_double"] for t in tally)
avg_AACI = statistics.mean(t["AACI"] for t in tally)
avg_single = statistics.mean(t["single"] for t in tally)
avg_DA = statistics.mean(t["DA"] for t in tally)
avg_otorp = statistics.mean(t["otorp"] for t in tally)
avg_ctorp = statistics.mean(t["ctorp"] for t in tally)
avg_cvshell = statistics.mean(t["cvshell"] for t in tally)
avg_cvci = statistics.mean(t["cvci"] for t in tally)
avg_bbci = statistics.mean(t["bbci"] for t in tally)
avg_asw = statistics.mean(t["asw"] for t in tally)
avg_yasen = statistics.mean(t["yasen"] for t in tally)
avg_nzci = statistics.mean(t["nzci"] for t in tally)
avg_gunci = statistics.mean(t["gunci"] for t in tally)
avg_tci = statistics.mean(t["tci"] for t in tally)

print("平均時間:", avgtime)
print("標準偏差:", time_std)
print("各アニメーション平均回数:")
print("艦載機あり索敵成功（5.1秒）:", avg_detection_plane)
print("艦載機なし索敵成功（4.0秒）:", avg_detection_noplane)
print("航空戦１艦隊のみ参加（8.4秒）:", avg_dogfight_single)
print("航空戦２艦隊とも参加（11.5秒）:", avg_dogfight_double)
print("対空CI（3.2秒）:", avg_AACI)
print("単発砲撃（1.7秒）:", avg_single)
print("連撃（2.8秒）:", avg_DA)
print("開幕雷撃（3.5秒）:", avg_otorp)
print("閉幕雷撃（5.3秒）:", avg_ctorp)
print("空母砲撃（3.7秒）:", avg_cvshell)
print("空母CI（6.3秒）:", avg_cvci)
print("弾着CI（6.1秒）:", avg_bbci)
print("対潜（2.7秒）:", avg_asw)
print("夜戦突入（6.0秒）:", avg_yasen)
print("夜間瑞雲CI（8.3秒）:", avg_nzci)
print("主主主CI（3.8秒）:", avg_gunci)

print("魚CI（5.5秒）:", avg_tci)
