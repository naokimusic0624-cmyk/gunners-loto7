import streamlit as st
import requests
import re
import json
import os
import random

# ==========================================
# ページ基本設定 & モダンCSSデザイン
# ==========================================
st.set_page_config(page_title="Gunners Loto 7 (2026-27)", page_icon="⚽", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
:root{--red:#d71920;--navy:#14233a;--muted:#728096;--line:#e2e8f0;--bg:#f4f7fa}
.stApp{background:var(--bg);color:var(--navy)} .block-container{max-width:1500px;padding:0 1.2rem 3rem} #MainMenu,footer{visibility:hidden}
.hero{margin:0 -1.2rem;background:linear-gradient(120deg,#e31b23,#b80e17);color:#fff;padding:26px 34px;display:flex;justify-content:space-between;align-items:center;min-height:118px;position:relative;overflow:hidden}.hero:after{content:"";position:absolute;right:-80px;top:-80px;width:380px;height:240px;background:rgba(90,0,8,.25);transform:skewX(-28deg)}.hero-brand{z-index:1;display:flex;align-items:center;gap:16px}.hero-logo{width:68px}.hero-title{font-size:31px;font-weight:900}.hero-sub{font-size:14px;margin-top:8px}.hero-motto{z-index:1;text-align:right;font-weight:800;letter-spacing:.12em;line-height:1.7}
.stTabs [data-baseweb="tab-list"]{gap:10px;background:#fff;padding:10px 0 12px;margin-bottom:20px;border-bottom:1px solid var(--line)}.stTabs [data-baseweb="tab"]{flex:1;justify-content:center;background:#f3f5f7;border:1px solid #edf0f3;border-radius:8px;min-height:50px;font-weight:800;color:#4d5d74}.stTabs [aria-selected="true"]{background:#d71920!important;color:#fff!important}.stTabs [data-baseweb="tab-highlight"]{display:none}
.panel,.match-card,.ticket,.summary{background:#fff;border:1px solid var(--line);border-radius:14px;padding:17px;margin-bottom:15px}.panel-title{font-size:17px;font-weight:900;margin-bottom:8px}.panel-copy,.tiny{font-size:12px;color:var(--muted);line-height:1.55}.mini{font-size:11px;color:var(--muted);font-weight:800;letter-spacing:.04em}
.stButton>button{min-height:42px;border-radius:8px!important;font-weight:800!important}.stTextInput input,div[data-baseweb="select"]>div,.stNumberInput input{background:#fff!important;border:1px solid #d7dfe8!important;border-radius:8px!important}.stSelectbox label,.stTextInput label,.stNumberInput label{font-size:12px!important;font-weight:800!important}
.match-top{display:flex;justify-content:space-between;border-bottom:1px solid #edf1f5;padding-bottom:10px}.comp{font-size:11px;color:#68768a;font-weight:800}.ft{background:#eaf8ef;color:#16864b;border-radius:999px;padding:6px 10px;font-size:11px;font-weight:900}.score-row{display:grid;grid-template-columns:1fr 110px 1fr;align-items:center;padding:18px 0}.team{font-size:18px;font-weight:900}.team.r{text-align:right}.score{text-align:center;font-size:36px;font-weight:950}.venue{text-align:center;font-size:9px;color:#8b98a8;letter-spacing:.15em}.match-bottom{display:grid;grid-template-columns:1fr 1fr;gap:10px}.pill{background:#f8fafc;border:1px solid #e6ebf1;border-radius:8px;padding:11px;font-size:13px;font-weight:800}.pill.r{text-align:right}
.balls{display:flex;gap:8px;flex-wrap:wrap}.ball{width:38px;height:38px;border-radius:50%;border:1.5px solid #ccd5df;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:900}.ball.gold{border-color:#ebc45d;background:#fffaf0;color:#7d5200}.ticket-title{font-size:14px;font-weight:900;margin-bottom:12px}.red{color:#d71920}.goldt{color:#b97b00}.ticket-note{font-size:11px;color:#8995a4;margin-top:9px}
.summary-title{font-size:17px;font-weight:900;margin-bottom:12px}.balance{border:1px solid #f0d9dc;border-radius:10px;overflow:hidden}.balance-h{background:#fff0f1;color:#c4141c;padding:10px;font-weight:800;font-size:13px}.balance-v{text-align:center;color:#c4141c;font-size:31px;font-weight:950;padding:10px}.metric-grid{display:grid;grid-template-columns:1fr 1fr;border-top:1px solid var(--line)}.metric{padding:12px;border-right:1px solid var(--line);border-bottom:1px solid var(--line)}.metric:nth-child(2n){border-right:0}.metric-k{font-size:11px;color:var(--muted)}.metric-v{font-size:17px;font-weight:900;margin-top:2px}.hist{padding:10px 0;border-bottom:1px solid #edf1f5;font-size:12px;display:flex;justify-content:space-between}.pos{color:#16864b;font-weight:900}
.help{background:#fff9e9;border:1px solid #f0e3b8;border-radius:14px;padding:15px}.step{display:flex;gap:9px;margin:10px 0;font-size:12px}.n{min-width:25px;height:25px;border-radius:50%;background:#d71920;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:900}
@media(max-width:900px){.hero-motto{display:none}.hero-title{font-size:23px}.score-row{grid-template-columns:1fr 80px 1fr}.team{font-size:14px}.score{font-size:29px}}
</style>
""", unsafe_allow_html=True)
# ==========================================
# 永続データ管理（試合データ & 収支）
# ==========================================
MATCH_STORAGE_FILE = "saved_matches.json"
HISTORY_FILE = "match_history.json"

def load_saved_matches():
    if os.path.exists(MATCH_STORAGE_FILE):
        try:
            with open(MATCH_STORAGE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_match_data_to_file(round_num, data):
    all_data = load_saved_matches()
    all_data[str(round_num)] = data
    with open(MATCH_STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(data):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==========================================
# 2026-27シーズン 全38節公式日程マスター
# ==========================================
SCHEDULE_2026_27 = [
    {"round": 1, "opp": "コヴェントリー・シティ", "ha": "H", "day": 22},
    {"round": 2, "opp": "アストン・ヴィラ", "ha": "A", "day": 1},
    {"round": 3, "opp": "チェルシー", "ha": "H", "day": 7},
    {"round": 4, "opp": "サンダーランド", "ha": "A", "day": 13},
    {"round": 5, "opp": "ブライトン", "ha": "A", "day": 19},
    {"round": 6, "opp": "リーズ・ユナイテッド", "ha": "H", "day": 10},
    {"round": 7, "opp": "ノッティンガム・フォレスト", "ha": "A", "day": 19},
    {"round": 8, "opp": "エヴァートン", "ha": "H", "day": 24},
    {"round": 9, "opp": "リヴァプール", "ha": "A", "day": 2},
    {"round": 10, "opp": "ハル・シティ", "ha": "H", "day": 8},
    {"round": 11, "opp": "ニューカッスル・ユナイテッド", "ha": "A", "day": 22},
    {"round": 12, "opp": "マンチェスター・シティ", "ha": "H", "day": 29},
    {"round": 13, "opp": "ブレントフォード", "ha": "A", "day": 5},
    {"round": 14, "opp": "トッテナム・ホットスパー", "ha": "A", "day": 12},
    {"round": 15, "opp": "ボーンマス", "ha": "H", "day": 19},
    {"round": 16, "opp": "マンチェスター・ユナイテッド", "ha": "H", "day": 26},
    {"round": 17, "opp": "クリスタル・パレス", "ha": "A", "day": 29},
    {"round": 18, "opp": "フラム", "ha": "A", "day": 2},
    {"round": 19, "opp": "イプスウィッチ・タウン", "ha": "H", "day": 16},
    {"round": 20, "opp": "ブレントフォード", "ha": "H", "day": 23},
    {"round": 21, "opp": "ハル・シティ", "ha": "A", "day": 30},
    {"round": 22, "opp": "ニューカッスル・ユナイテッド", "ha": "H", "day": 6},
    {"round": 23, "opp": "マンチェスター・シティ", "ha": "A", "day": 13},
    {"round": 24, "opp": "リヴァプール", "ha": "H", "day": 20},
    {"round": 25, "opp": "イプスウィッチ・タウン", "ha": "A", "day": 27},
    {"round": 26, "opp": "フラム", "ha": "H", "day": 6},
    {"round": 27, "opp": "マンチェスター・ユナイテッド", "ha": "A", "day": 13},
    {"round": 28, "opp": "クリスタル・パレス", "ha": "H", "day": 3},
    {"round": 29, "opp": "チェルシー", "ha": "A", "day": 10},
    {"round": 30, "opp": "サンダーランド", "ha": "H", "day": 17},
    {"round": 31, "opp": "コヴェントリー・シティ", "ha": "A", "day": 24},
    {"round": 32, "opp": "アストン・ヴィラ", "ha": "H", "day": 1},
    {"round": 33, "opp": "ボーンマス", "ha": "A", "day": 8},
    {"round": 34, "opp": "トッテナム・ホットスパー", "ha": "H", "day": 15},
    {"round": 35, "opp": "リーズ・ユナイテッド", "ha": "A", "day": 19},
    {"round": 36, "opp": "ノッティンガム・フォレスト", "ha": "H", "day": 23},
    {"round": 37, "opp": "エヴァートン", "ha": "A", "day": 26},
    {"round": 38, "opp": "ブライトン", "ha": "H", "day": 30}
]

ARSENAL_SQUAD_NUMBERS = {
    "raya": 1, "kepa": 13, "meslier": 30,
    "white": 4, "timber": 12, "saliba": 2, "mosquera": 3,
    "gabriel": 6, "konsa": 15, "hincapié": 5, "hincapie": 5,
    "calafiori": 33, "lewis-skelly": 49, "skelly": 49,
    "rice": 41, "odegaard": 8, "merino": 23, "zubimendi": 36,
    "guimarães": 39, "guimaraes": 39, "eze": 10, "dowman": 56,
    "saka": 7, "madueke": 20, "tzolis": 17, "gyökeres": 14,
    "gyokeres": 14, "havertz": 29
}

# ==========================================
# ロト7 採番ロジック（①〜⑩ 完全順次判定・重複排除）
# ==========================================
def convert_to_loto_number(val):
    try:
        n = int(val)
        while n > 37:
            n -= 37
        return n if n > 0 else 1
    except (ValueError, TypeError):
        return 1

def generate_ticket_1(stats):
    selected = []
    log_details = []

    def try_add(val, label):
        if len(selected) >= 7 or val is None:
            return False
        num = convert_to_loto_number(val)
        if num not in selected:
            selected.append(num)
            orig = f"({val}➔{num:02d})" if int(val) > 37 else f"({num:02d})"
            log_details.append(f"{label}: {orig}")
            return True
        return False

    # ① 得点者全員の背番号
    for sc in stats.get("scorers", []):
        try_add(sc, "①得点者")

    # ② 先制点 アシスト者
    if stats.get("assist") is not None:
        try_add(stats["assist"], "②アシスト")

    # ③ 先制ゴール時間
    if stats.get("goal_time") is not None:
        try_add(stats["goal_time"], "③ゴール時間")

    # ④ パス成功数 1位
    if stats.get("passer") is not None:
        passer_val = stats["passer"]
        if passer_val in [1, "1", 0, "0"]:
            passer_val = 49
        try_add(passer_val, "④パス1位")

    # ⑤ チーム総シュート数
    if stats.get("shots") is not None:
        try_add(stats["shots"], "⑤シュート数")

    # ⑥ ボール支配率
    if stats.get("poss") is not None:
        try_add(stats["poss"], "⑥支配率")

    # ⑦ 試合開催日
    if stats.get("day") is not None:
        try_add(stats["day"], "⑦開催日")

    # ⑧ 守備陣最上位 / GK
    def_candidates = stats.get("def_gk_candidates", [2, 4, 6, 12, 1])
    for d_num in def_candidates:
        if len(selected) >= 7:
            break
        try_add(d_num, "⑧最高評価DF/GK")

    # ⑨ クラブ伝統枠（14 ➔ 13 ➔ 18 ➔ 01）
    tradition_list = stats.get("tradition_candidates", [14, 13, 18, 1])
    for t_num in tradition_list:
        if len(selected) >= 7:
            break
        label_name = {14: "アンリ/ギェケレシュ#14", 13: "ケパ#13", 18: "創設年#18", 1: "ラヤ#01"}.get(t_num, f"#{t_num}")
        try_add(t_num, f"⑨クラブ伝統枠({label_name})")

    # ⑩ ファースト・サブ
    if stats.get("first_sub") is not None:
        try_add(stats["first_sub"], "⑩ファースト・サブ")

    return sorted(selected), log_details

def generate_ticket_2():
    while True:
        nums = sorted(random.sample(range(1, 38), 7))
        odds = sum(1 for n in nums if n % 2 != 0)
        total = sum(nums)
        zones = set((n - 1) // 10 for n in nums)
        if odds in [3, 4] and 115 <= total <= 145 and len(zones) >= 3:
            return nums, odds, 7 - odds, total

def generate_ticket_qp():
    return sorted(random.sample(range(1, 38), 7))

# ==========================================
# Webページ解析
# ==========================================
def fetch_from_fotmob_page(url_or_text, is_home):
    if not url_or_text:
        return None, "URLが入力されていません"

    clean_url = url_or_text.strip()
    m_url = re.search(r'(https?://[^\s]+)', clean_url)
    if m_url:
        clean_url = m_url.group(1).split('#')[0]
    else:
        m_id = re.search(r'(\d{6,10})', clean_url)
        if m_id:
            clean_url = f"https://www.fotmob.com/matches/{m_id.group(1)}"
        else:
            return None, "有効なFotMobのURLが見つかりませんでした"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/"
    }

    try:
        res = requests.get(clean_url, headers=headers, timeout=8)
        if res.status_code != 200:
            return None, f"ページ取得エラー (HTTP {res.status_code})"

        html = res.text
        json_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if not json_match:
            return None, "試合データタグが見つかりませんでした"

        next_data = json.loads(json_match.group(1))
        page_props = next_data.get("props", {}).get("pageProps", {})
        
        content = page_props.get("content", {})
        header = page_props.get("header", {})
        general = page_props.get("general", {})

        teams = header.get("teams", [])
        ars_idx = 0
        if len(teams) >= 2:
            t1_name = teams[1].get("name", "").lower()
            if "arsenal" in t1_name:
                ars_idx = 1
            h_sc = teams[0].get("score", 0)
            a_sc = teams[1].get("score", 0)
        else:
            h_sc, a_sc = 0, 0
        is_finished = header.get("status", {}).get("finished", False)

        player_number_map = {}
        lineup = content.get("lineup", {})
        ars_side = "homeTeam" if ars_idx == 0 else "awayTeam"
        
        starters = lineup.get(ars_side, {}).get("starters", [])
        subs = lineup.get(ars_side, {}).get("subs", [])
        ars_players_all = starters + subs

        for p in ars_players_all:
            pid = str(p.get("id", ""))
            shirt = p.get("shirt") or p.get("shirtNumber")
            pname = p.get("name", "").lower()
            pnum = int(shirt) if shirt else None
            if not pnum:
                for k, v in ARSENAL_SQUAD_NUMBERS.items():
                    if k in pname:
                        pnum = v
                        break
            if pnum and pid:
                player_number_map[pid] = pnum

        shots = 15
        possession = 55
        
        stats_sections = []
        if "stats" in content:
            if "Periods" in content["stats"]:
                p_data = content["stats"]["Periods"].get("All", {}).get("stats", [])
                stats_sections.extend(p_data)
            if "stats" in content["stats"]:
                stats_sections.extend(content["stats"]["stats"])

        for sec in stats_sections:
            sec_stats = sec.get("stats", [])
            for item in sec_stats:
                title = str(item.get("title", "")).lower()
                vals = item.get("stats", [])
                if len(vals) >= 2:
                    if "possession" in title or "ポゼッション" in title:
                        p_str = str(vals[ars_idx]).replace("%", "").strip()
                        if p_str.isdigit():
                            possession = int(p_str)
                    elif ("shot" in title or "シュート" in title) and ("total" in title or "総数" in title or "attempts" in title or len(title) < 15):
                        s_str = str(vals[ars_idx]).strip()
                        if s_str.isdigit():
                            shots = int(s_str)

        # 評価点順DF/GK候補抽出
        def_gk_scored = []
        for p in ars_players_all:
            pid = str(p.get("id", ""))
            shirt = p.get("shirt") or p.get("shirtNumber")
            pname = p.get("name", "").lower()
            pos = str(p.get("position", "")).lower()
            role = str(p.get("role", "")).lower()
            
            pnum = int(shirt) if shirt else player_number_map.get(pid, 0)
            if not pnum:
                for k, v in ARSENAL_SQUAD_NUMBERS.items():
                    if k in pname:
                        pnum = v
                        break

            rating = 0.0
            rc = p.get("rating", {})
            if isinstance(rc, dict):
                try:
                    rating = float(rc.get("num", 0))
                except:
                    pass
            elif isinstance(rc, (int, float)):
                rating = float(rc)

            is_def_gk = ("gk" in pos or "def" in pos or "keeper" in role or "defender" in role or 
                         pnum in [1, 2, 3, 4, 5, 6, 12, 13, 15, 33])

            if is_def_gk and pnum:
                def_gk_scored.append((rating, pnum))

        def_gk_scored.sort(key=lambda x: x[0], reverse=True)
        def_candidates = [num for rat, num in def_gk_scored]
        
        for fallback_n in [33, 2, 4, 6, 12, 1, 3, 5, 15]:
            if fallback_n not in def_candidates:
                def_candidates.append(fallback_n)

        first_sub_num = 56
        if subs and len(subs) > 0:
            first_sub_p = subs[0]
            fs_id = str(first_sub_p.get("id", ""))
            fs_shirt = first_sub_p.get("shirt") or first_sub_p.get("shirtNumber")
            fs_name = first_sub_p.get("name", "").lower()
            if fs_shirt:
                first_sub_num = int(fs_shirt)
            elif fs_id in player_number_map:
                first_sub_num = player_number_map[fs_id]
            else:
                for k, v in ARSENAL_SQUAD_NUMBERS.items():
                    if k in fs_name:
                        first_sub_num = v
                        break

        top_passer_number = 49

        events = content.get("matchFacts", {}).get("events", {}).get("events", [])
        scorers = []
        first_assist = None
        first_time = None

        for ev in events:
            if ev.get("type") in ["Goal", "goal"]:
                ev_is_home = ev.get("isHome", True)
                if (ars_idx == 0 and ev_is_home) or (ars_idx == 1 and not ev_is_home):
                    pid = str(ev.get("playerId") or ev.get("player", {}).get("id", ""))
                    pname = ev.get("player", {}).get("name", "").lower()
                    num = player_number_map.get(pid)
                    if not num:
                        for k, v in ARSENAL_SQUAD_NUMBERS.items():
                            if k in pname:
                                num = v
                                break
                    if not num:
                        num = 7
                    scorers.append(num)

                    if first_time is None:
                        first_time = int(ev.get("time", 20))
                        aid = str(ev.get("assistPlayerId") or ev.get("assist", {}).get("id", ""))
                        aname = ev.get("assist", {}).get("name", "").lower()
                        if aid and aid in player_number_map:
                            first_assist = player_number_map[aid]
                        else:
                            for k, v in ARSENAL_SQUAD_NUMBERS.items():
                                if k in aname:
                                    first_assist = v
                                    break

        match_id_found = str(general.get("matchId") or (re.search(r'(\d{6,10})', clean_url).group(1) if re.search(r'(\d{6,10})', clean_url) else ""))

        return {
            "match_id": match_id_found,
            "h_score": int(h_sc) if h_sc is not None else 0,
            "a_score": int(a_sc) if a_sc is not None else 0,
            "is_finished": is_finished,
            "scorers": scorers if scorers else [7],
            "assist": first_assist or 8,
            "goal_time": first_time or 20,
            "passer": top_passer_number,
            "shots": shots,
            "possession": possession,
            "def_gk_candidates": def_candidates,
            "first_sub": first_sub_num
        }, None

    except Exception as e:
        return None, f"解析エラー: {str(e)[:30]}"

# ==========================================
# メイン画面 UI — イメージ画像準拠ダッシュボード
# ==========================================
saved_matches = load_saved_matches()
history = load_history()
total_spent = sum(x.get("cost",0) for x in history)
total_won = sum(x.get("hit_amount",0) for x in history)
net_balance = total_won-total_spent
roi = (total_won/total_spent*100) if total_spent else 0

st.markdown('''<div class="hero"><div class="hero-brand"><img class="hero-logo" src="https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png"><div><div class="hero-title">Gunners Loto 7 (2026-27)</div><div class="hero-sub">アーセナルの試合結果で楽しむ ロト7風予想アプリ</div></div></div><div class="hero-motto">ONCE A GUNNER<br>ALWAYS A GUNNER</div></div>''', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⌂ ホーム / 試合データ", "▥ 購入履歴・収支"])

with tab1:
    labels=[]
    for item in SCHEDULE_2026_27:
        r,opp,ha=item["round"],item["opp"],item["ha"]
        if str(r) in saved_matches:
            sm=saved_matches[str(r)]
            labels.append(f"第{r}節: アーセナル {sm.get('h_score',0)} - {sm.get('a_score',0)} {opp}（保存済）")
        else:
            txt=f"アーセナル vs {opp}" if ha=="H" else f"{opp} vs アーセナル"
            labels.append(f"第{r}節: {txt} ({ha})")
    selected_idx=st.selectbox("表示する試合", range(len(labels)), format_func=lambda i:labels[i])
    m=SCHEDULE_2026_27[selected_idx]; round_num=m["round"]; opp_name=m["opp"]; ha=m["ha"]; is_home=(ha=="H")
    state_key=f"match_data_{round_num}"
    if state_key not in st.session_state or not isinstance(st.session_state[state_key],dict):
        st.session_state[state_key]=saved_matches.get(str(round_num), {"match_id":"","h_score":0,"a_score":0,"is_finished":False,"scorers":[7],"assist":8,"goal_time":20,"passer":49,"shots":15,"poss":55,"day":m.get("day",1),"def_gk_candidates":[2,4,6,12,1],"tradition_candidates":[14,13,18,1],"first_sub":56}).copy()
    cur=st.session_state[state_key]
    if cur.get("passer") in [1,"1",0,"0"]: cur["passer"]=49
    h_team="アーセナルFC" if is_home else opp_name; a_team=opp_name if is_home else "アーセナルFC"
    ars_score=cur.get("h_score",0) if is_home else cur.get("a_score",0); opp_score=cur.get("a_score",0) if is_home else cur.get("h_score",0); gd=ars_score-opp_score
    has_result=cur.get("is_finished",False) or cur.get("h_score",0)>0 or cur.get("a_score",0)>0
    tickets=max(0,min(5,gd)) if has_result and gd>0 else 0; cost=tickets*300
    t2_key=f"t2_{round_num}"; t3_key=f"t3_{round_num}"
    if t2_key not in st.session_state: st.session_state[t2_key]=generate_ticket_2()
    if t3_key not in st.session_state: st.session_state[t3_key]=generate_ticket_qp()
    t2_nums,t2_odd,t2_even,t2_total=st.session_state[t2_key]; t3_nums=st.session_state[t3_key]
    t1,logs=generate_ticket_1(cur) if tickets>0 else ([],[])

    left,center,right=st.columns([1.05,2.45,1.15], gap="large")
    with left:
        st.markdown('<div class="panel"><div class="panel-title">◉ 試合データ取得</div><div class="panel-copy">FotMobから最新の試合結果と主要スタッツを取得します。</div></div>', unsafe_allow_html=True)
        user_url_input=st.text_input("FotMob URL", placeholder="https://www.fotmob.com/matches/...", key=f"url_{round_num}", label_visibility="collapsed")
        sync_clicked=st.button("↓ 最新データを取得", use_container_width=True, type="primary", key=f"sync_{round_num}")
        if sync_clicked:
            if user_url_input:
                with st.spinner("スタッツを解析中..."):
                    fetched,err=fetch_from_fotmob_page(user_url_input,is_home)
                    if fetched:
                        cur.update({"match_id":fetched["match_id"],"h_score":fetched["h_score"],"a_score":fetched["a_score"],"is_finished":fetched["is_finished"],"scorers":fetched["scorers"],"assist":fetched["assist"],"goal_time":fetched["goal_time"],"passer":49,"shots":fetched["shots"],"poss":fetched["possession"],"def_gk_candidates":fetched["def_gk_candidates"],"first_sub":fetched["first_sub"]})
                        save_match_data_to_file(round_num,cur); st.success("更新しました"); st.rerun()
                    else: st.error(err)
            else: st.warning("FotMob URLを入力してください。")
        st.markdown(f'<div class="panel"><div class="panel-title">⚙ 表示設定</div><div class="mini">SEASON</div><div style="font-weight:900;margin:4px 0 12px">2026-27</div><div class="mini">CURRENT MATCH</div><div class="tiny" style="margin-top:4px">第{round_num}節 / {"HOME" if is_home else "AWAY"}</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="help"><div class="panel-title">💡 使い方</div><div class="step"><span class="n">1</span><span>試合を選択</span></div><div class="step"><span class="n">2</span><span>FotMobデータを取得</span></div><div class="step"><span class="n">3</span><span>番号を自動生成</span></div><div class="step"><span class="n">4</span><span>収支管理に登録</span></div></div>', unsafe_allow_html=True)

    with center:
        st.markdown('<div class="panel-title" style="font-size:23px">⚽ 直近の試合結果</div><div class="panel-copy">選択した試合結果とロト7予想番号</div>', unsafe_allow_html=True)
        status='● 試合終了 FT' if cur.get('is_finished',False) else '● キックオフ前'
        st.markdown(f'<div class="match-card"><div class="match-top"><span class="comp">PREMIER LEAGUE 2026-27 ・ 第{round_num}節</span><span class="ft">{status}</span></div><div class="score-row"><div class="team">{h_team}</div><div><div class="score">{f"{cur.get("h_score",0)} - {cur.get("a_score",0)}" if has_result else "VS"}</div><div class="venue">{"HOME" if is_home else "AWAY"}</div></div><div class="team r">{a_team}</div></div><div class="match-bottom"><div class="pill">得失点差 <strong>{"+" if gd>0 else ""}{gd}</strong></div><div class="pill r">購入予定 <strong>{tickets}口 ・ {cost:,}円</strong></div></div></div>', unsafe_allow_html=True)
        with st.expander("📝 スコア & スタッツ詳細（①〜⑩ 手動補正・再判定）"):
            c1,c2=st.columns(2)
            with c1: cur["h_score"]=st.number_input(f"{h_team} 得点",min_value=0,value=int(cur.get("h_score",0)),key=f"hs_{round_num}")
            with c2: cur["a_score"]=st.number_input(f"{a_team} 得点",min_value=0,value=int(cur.get("a_score",0)),key=f"as_{round_num}")
            c1,c2=st.columns(2)
            with c1:
                sc=st.text_input("① 得点者 背番号",value=", ".join(map(str,cur.get("scorers",[7]))),key=f"sc_{round_num}"); cur["scorers"]=[int(x.strip()) for x in sc.split(",") if x.strip().isdigit()]
                cur["assist"]=st.number_input("② 先制アシスト 背番号",0,99,int(cur.get("assist",8)),key=f"asst_{round_num}"); cur["goal_time"]=st.number_input("③ 先制ゴール時間",1,120,int(cur.get("goal_time",20)),key=f"gt_{round_num}"); cur["passer"]=st.number_input("④ パス成功数1位 背番号",1,99,int(cur.get("passer",49)),key=f"pass_{round_num}"); cur["shots"]=st.number_input("⑤ 総シュート数",0,value=int(cur.get("shots",15)),key=f"sh_{round_num}")
            with c2:
                cur["poss"]=st.number_input("⑥ ボール支配率",0,100,int(cur.get("poss",55)),key=f"poss_{round_num}"); cur["day"]=st.number_input("⑦ 試合開催日",1,31,int(cur.get("day",m.get("day",1))),key=f"day_{round_num}")
                di=st.text_input("⑧ 最高評価DF/GK候補",value=", ".join(map(str,cur.get("def_gk_candidates",[2,4,6,12,1]))),key=f"def_{round_num}"); cur["def_gk_candidates"]=[int(x.strip()) for x in di.split(",") if x.strip().isdigit()]
                ti=st.text_input("⑨ クラブ伝統枠",value=", ".join(map(str,cur.get("tradition_candidates",[14,13,18,1]))),key=f"trad_{round_num}"); cur["tradition_candidates"]=[int(x.strip()) for x in ti.split(",") if x.strip().isdigit()]
                cur["first_sub"]=st.number_input("⑩ ファースト・サブ",1,99,int(cur.get("first_sub",56)),key=f"sub_{round_num}")
            if st.button("↻ 番号を再判定",use_container_width=True,key=f"rejudge_{round_num}"): save_match_data_to_file(round_num,cur); st.success("再判定しました"); st.rerun()
        if tickets>0:
            st.markdown(f'<div class="ticket"><div class="ticket-title red">1口目【マッチスタッツ連動型】</div><div class="balls">{"".join(f"<span class=\"ball\">{n:02d}</span>" for n in t1)}</div><div class="ticket-note">{" / ".join(logs)}</div></div>', unsafe_allow_html=True)
            if tickets>=2: st.markdown(f'<div class="ticket"><div class="ticket-title goldt">2口目【AI統計分析型（動的生成）】</div><div class="balls">{"".join(f"<span class=\"ball gold\">{n:02d}</span>" for n in t2_nums)}</div><div class="ticket-note">奇数{t2_odd}:偶数{t2_even} / 合計値{t2_total}</div></div>', unsafe_allow_html=True)
            if tickets>=3: st.markdown(f'<div class="ticket"><div class="ticket-title">3口目【クイックピック（QP）】</div><div class="balls">{"".join(f"<span class=\"ball\">{n:02d}</span>" for n in t3_nums)}</div></div>', unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                if st.button("💾 試合データを保存",use_container_width=True,key=f"save_{round_num}"): cur["is_finished"]=True; save_match_data_to_file(round_num,cur); st.rerun()
            with c2:
                if st.button("▥ 収支管理に登録",use_container_width=True,key=f"hist_{round_num}"):
                    h=load_history(); h.insert(0,{"round":round_num,"opponent":f"{opp_name} ({ha})","score":f"{ars_score}-{opp_score}","tickets":tickets,"cost":cost,"ticket_1":t1,"ticket_2":t2_nums if tickets>=2 else [],"hit_amount":0,"status":"未抽せん"}); save_history(h); st.rerun()
        else: st.info("勝利時のみ購入番号を表示します。" if has_result else "キックオフ前です。FotMob自動取得または手動入力で結果を反映してください。")

    with right:
        st.markdown(f'<div class="summary"><div class="summary-title">▥ 収支サマリー</div><div class="balance"><div class="balance-h">総収支</div><div class="balance-v">{"+" if net_balance>0 else ""}{net_balance:,}<span style="font-size:14px"> 円</span></div><div class="metric-grid"><div class="metric"><div class="metric-k">購入金額</div><div class="metric-v">{total_spent:,}円</div></div><div class="metric"><div class="metric-k">払戻金額</div><div class="metric-v">{total_won:,}円</div></div><div class="metric"><div class="metric-k">購入試合数</div><div class="metric-v">{len(history)}試合</div></div><div class="metric"><div class="metric-k">回収率</div><div class="metric-v">{roi:.1f}%</div></div></div></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="panel"><div class="panel-title">▤ 最近の購入履歴</div>', unsafe_allow_html=True)
        if history:
            for rec in history[:6]:
                hit=rec.get("hit_amount",0)
                st.markdown(f'<div class="hist"><span>第{rec.get("round","")}節<br>vs {rec.get("opponent","")}</span><span class="{"pos" if hit>0 else ""}">{f"+{hit:,}円" if hit>0 else "0円"}</span></div>', unsafe_allow_html=True)
        else: st.markdown('<div class="tiny">まだ購入履歴はありません。</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    history=load_history(); total_spent=sum(x.get("cost",0) for x in history); total_won=sum(x.get("hit_amount",0) for x in history); net_balance=total_won-total_spent; roi=(total_won/total_spent*100) if total_spent else 0
    st.markdown(f'<div class="summary"><div class="summary-title">シーズン収支・購入履歴</div><div class="balance"><div class="balance-h">2026-27 SEASON TOTAL</div><div class="balance-v">{"+" if net_balance>0 else ""}{net_balance:,} 円</div><div class="metric-grid"><div class="metric"><div class="metric-k">総投資</div><div class="metric-v">{total_spent:,}円</div></div><div class="metric"><div class="metric-k">総回収</div><div class="metric-v">{total_won:,}円</div></div><div class="metric"><div class="metric-k">登録試合</div><div class="metric-v">{len(history)}試合</div></div><div class="metric"><div class="metric-k">回収率</div><div class="metric-v">{roi:.1f}%</div></div></div></div></div>', unsafe_allow_html=True)
    if history:
        for idx,rec in enumerate(history):
            with st.expander(f"第{rec.get('round','')}節 vs {rec.get('opponent','')} ({rec.get('score','')}) - {rec.get('tickets',0)}口"):
                c1,c2=st.columns(2)
                with c1: st.write(f"購入額: {rec.get('cost',0):,}円"); st.write(f"1口目: {rec.get('ticket_1',[])}"); st.write(f"2口目: {rec.get('ticket_2',[])}" if rec.get('ticket_2') else "")
                with c2:
                    won=st.number_input("当せん金額 (円)",min_value=0,step=1000,value=rec.get("hit_amount",0),key=f"won_{idx}_{rec.get('round',idx)}")
                    if won!=rec.get("hit_amount",0): history[idx]["hit_amount"]=int(won); history[idx]["status"]=f"{won:,}円 当せん" if won>0 else "ハズレ"; save_history(history); st.rerun()
    else: st.caption("購入履歴データはありません。")
    if st.button("🗑️ 履歴データをリセット",key="reset_history"): save_history([]); st.rerun()
