import streamlit as st
import requests
import re
import json
import os
import random

# ==========================================
# ページ基本設定 & 洗練されたCSSデザイン
# ==========================================
st.set_page_config(
    page_title="Gunners Loto 7 (2026-27)",
    page_icon="https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 全体背景 & フォント */
    .stApp {
        background-color: #090D16;
        color: #F1F5F9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* ヘッダーデザイン */
    .arsenal-header {
        background: linear-gradient(135deg, #DC2626 0%, #991B1B 100%);
        padding: 16px 24px;
        border-radius: 14px;
        color: white;
        font-weight: 800;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(220, 38, 38, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    /* 一般カードコンテナ */
    .modern-card {
        background-color: #111827;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }

    /* スタッツ入力専用セクション（視認性を高めた明るめの専用カード） */
    .stats-input-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 16px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
    }
    .stats-input-card label {
        color: #F8FAFC !important;
        font-weight: 700 !important;
        font-size: 13px !important;
    }
    
    /* ロトボールデザイン */
    .ball-container {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 15px 0;
    }
    .loto-ball {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 17px;
        color: #0F172A;
        background: radial-gradient(circle at 35% 35%, #FFFFFF 0%, #CBD5E1 100%);
        box-shadow: 0 4px 10px rgba(0,0,0,0.6), inset 0 2px 4px rgba(255,255,255,0.8);
        border: 2px solid #94A3B8;
    }
    .loto-ball-gold {
        background: radial-gradient(circle at 35% 35%, #FDE68A 0%, #D97706 100%);
        color: #451A03;
        border: 2px solid #F59E0B;
    }
    
    /* バッジ・ステータス */
    .status-badge {
        background: rgba(220, 38, 38, 0.15);
        border: 1px solid rgba(220, 38, 38, 0.4);
        color: #FCA5A5;
        border-radius: 10px;
        padding: 10px 16px;
        font-size: 14px;
        font-weight: 700;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 12px;
    }
    
    /* タブの洗練 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #111827;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94A3B8;
        font-weight: 600;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #DC2626 !important;
        color: white !important;
    }

    /* 入力フォームの視認性向上 */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] input, div[data-baseweb="base-input"] input {
        background-color: #0F172A !important;
        border-color: #475569 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    
    /* ボタンの立体感とホバー */
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.4);
    }
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
# メイン画面 UI (100点クオリティ版)
# ==========================================
saved_matches = load_saved_matches()

st.markdown("""
<div class="arsenal-header">
    <div style="display:flex; align-items:center; gap:12px;">
        <img src="https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png" width="34" height="34" style="object-fit:contain;">
        <span style="font-size:20px; letter-spacing:0.5px;">GUNNERS LOTO 7</span>
    </div>
    <span style="background:rgba(0,0,0,0.3); padding:5px 12px; border-radius:20px; font-size:12px; border:1px solid #F87171;">Premier League 2026-27</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚽ 試合 & ナンバー算出", "📊 シーズン収支管理"])

with tab1:
    labels = []
    for item in SCHEDULE_2026_27:
        r = item["round"]
        opp = item["opp"]
        ha = item["ha"]
        r_str = str(r)
        if r_str in saved_matches:
            sm = saved_matches[r_str]
            labels.append(f"第{r}節: アーセナル {sm.get('h_score', 0)} - {sm.get('a_score', 0)} {opp} (保存済)")
        else:
            txt = f"アーセナル vs {opp}" if ha == "H" else f"{opp} vs アーセナル"
            labels.append(f"第{r}節: {txt} ({ha})")

    selected_idx = st.selectbox(
        "📅 試合を選択してください（第1節〜第38節）",
        range(len(labels)),
        format_func=lambda i: labels[i]
    )

    m = SCHEDULE_2026_27[selected_idx]
    round_num = m["round"]
    opp_name = m["opp"]
    ha = m["ha"]
    is_home = (ha == "H")
    r_key_str = str(round_num)

    state_key = f"match_data_{round_num}"
    if state_key not in st.session_state or not isinstance(st.session_state[state_key], dict):
        if r_key_str in saved_matches:
            st.session_state[state_key] = saved_matches[r_key_str].copy()
        else:
            st.session_state[state_key] = {
                "match_id": "",
                "h_score": 0,
                "a_score": 0,
                "is_finished": False,
                "scorers": [7],
                "assist": 8,
                "goal_time": 20,
                "passer": 49,
                "shots": 15,
                "poss": 55,
                "day": m.get("day", 1),
                "def_gk_candidates": [2, 4, 6, 12, 1],
                "tradition_candidates": [14, 13, 18, 1],
                "first_sub": 56
            }

    cur = st.session_state[state_key]
    if cur.get("passer") in [1, "1", 0, "0"]:
        cur["passer"] = 49

    h_team = "アーセナルFC" if is_home else opp_name
    a_team = opp_name if is_home else "アーセナルFC"

    # FotMob自動取得連携カード
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown("**⚡ FotMobスタッツ自動連携**")
    col_u1, col_u2 = st.columns([3, 1])
    with col_u1:
        user_url_input = st.text_input(
            "FotMob URL",
            value="",
            placeholder="https://www.fotmob.com/matches/...",
            key=f"url_in_{round_num}",
            label_visibility="collapsed"
        )
    with col_u2:
        sync_clicked = st.button("🔄 自動取得", use_container_width=True)

    if sync_clicked:
        if user_url_input:
            with st.spinner("スタッツを解析中..."):
                fetched, err = fetch_from_fotmob_page(user_url_input, is_home)
                if fetched:
                    cur["match_id"] = fetched["match_id"]
                    cur["h_score"] = fetched["h_score"]
                    cur["a_score"] = fetched["a_score"]
                    cur["is_finished"] = fetched["is_finished"]
                    cur["scorers"] = fetched["scorers"]
                    cur["assist"] = fetched["assist"]
                    cur["goal_time"] = fetched["goal_time"]
                    cur["passer"] = 49
                    cur["shots"] = fetched["shots"]
                    cur["poss"] = fetched["possession"]
                    cur["def_gk_candidates"] = fetched["def_gk_candidates"]
                    cur["first_sub"] = fetched["first_sub"]
                    
                    save_match_data_to_file(round_num, cur)
                    st.success("自動取得・更新しました！")
                    st.rerun()
                else:
                    st.error(err)
        else:
            st.warning("URLを入力してください。")
    st.markdown('</div>', unsafe_allow_html=True)

    # 📝 スコア & スタッツ詳細（リデザインされた高視認性カード）
    st.markdown('<div class="stats-input-card">', unsafe_allow_html=True)
    st.markdown("<div style='font-size:16px; font-weight:800; color:#F8FAFC; margin-bottom:14px;'>📝 スコア & スタッツ詳細（①〜⑩ 手動補正・再判定）</div>", unsafe_allow_html=True)
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        cur["h_score"] = st.number_input(f"{h_team} 得点", min_value=0, value=int(cur.get("h_score", 0)), key=f"hs_{round_num}")
    with col_m2:
        cur["a_score"] = st.number_input(f"{a_team} 得点", min_value=0, value=int(cur.get("a_score", 0)), key=f"as_{round_num}")

    st.markdown("<div style='margin: 12px 0; border-top: 1px solid #334155;'></div>", unsafe_allow_html=True)
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        sc_str = ", ".join([str(n) for n in cur.get("scorers", [7])])
        scorers_input = st.text_input("① 得点者 背番号（カンマ区切り）", value=sc_str, key=f"sc_{round_num}")
        cur["scorers"] = [int(s.strip()) for s in scorers_input.split(",") if s.strip().isdigit()]
        
        cur["assist"] = st.number_input("② 先制アシスト 背番号", min_value=0, max_value=99, value=int(cur.get("assist", 8)), key=f"asst_{round_num}")
        cur["goal_time"] = st.number_input("③ 先制ゴール時間（分）", min_value=1, max_value=120, value=int(cur.get("goal_time", 20)), key=f"gt_{round_num}")
        cur["passer"] = st.number_input("④ パス成功数1位 背番号", min_value=1, max_value=99, value=int(cur.get("passer", 49)), key=f"pass_{round_num}")
        cur["shots"] = st.number_input("⑤ チーム総シュート数", min_value=0, value=int(cur.get("shots", 15)), key=f"sh_{round_num}")

    with col_s2:
        cur["poss"] = st.number_input("⑥ ボール支配率 (%)", min_value=0, max_value=100, value=int(cur.get("poss", 55)), key=f"poss_{round_num}")
        cur["day"] = st.number_input("⑦ 試合開催日（日）", min_value=1, max_value=31, value=int(cur.get("day", m.get("day", 1))), key=f"day_{round_num}")
        
        def_cands_str = ", ".join([str(n) for n in cur.get("def_gk_candidates", [2, 4, 6, 12, 1])])
        def_input = st.text_input("⑧ 最高評価DF/GK候補（優先順）", value=def_cands_str, key=f"def_{round_num}")
        cur["def_gk_candidates"] = [int(s.strip()) for s in def_input.split(",") if s.strip().isdigit()]

        trad_str = ", ".join([str(n) for n in cur.get("tradition_candidates", [14, 13, 18, 1])])
        trad_input = st.text_input("⑨ クラブ伝統枠（順序）", value=trad_str, key=f"trad_{round_num}")
        cur["tradition_candidates"] = [int(s.strip()) for s in trad_input.split(",") if s.strip().isdigit()]

        cur["first_sub"] = st.number_input("⑩ ファースト・サブ 背番号", min_value=1, max_value=99, value=int(cur.get("first_sub", 56)), key=f"sub_{round_num}")

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 番号を再判定する", use_container_width=True):
        save_match_data_to_file(round_num, cur)
        st.success("再判定しました！")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    ars_score = cur.get("h_score", 0) if is_home else cur.get("a_score", 0)
    opp_score = cur.get("a_score", 0) if is_home else cur.get("h_score", 0)
    gd = ars_score - opp_score

    has_result = cur.get("is_finished", False) or (cur.get("h_score", 0) > 0 or cur.get("a_score", 0) > 0)
    tickets = max(0, min(5, gd)) if (has_result and gd > 0) else 0
    cost = tickets * 300

    # 試合概要カード
    st.markdown(f"""
    <div class="modern-card">
        <div style="display:flex; justify-content:space-between; font-size:12px; color:#94A3B8; margin-bottom:8px;">
            <span>Premier League 2026-27 • 第{round_num}節</span>
            <span style="color:{'#34D399' if cur.get('is_finished', False) else '#F59E0B'}; font-weight:bold;">
                {'■ 試合終了 (FT)' if cur.get('is_finished', False) else '□ キックオフ前'}
            </span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; margin:16px 0;">
            <div style="text-align:center; width:130px; font-weight:800; font-size:16px;">{h_team}</div>
            <div style="text-align:center;">
                <div style="font-size:38px; font-weight:900; letter-spacing:3px; color:#F8FAFC;">
                    {f"{cur.get('h_score', 0)} - {cur.get('a_score', 0)}" if has_result else "VS"}
                </div>
                <div style="font-size:11px; color:#64748B; margin-top:2px;">{'HOME' if is_home else 'AWAY'}</div>
            </div>
            <div style="text-align:center; width:130px; font-weight:800; font-size:16px;">{a_team}</div>
        </div>
        <div class="status-badge">
            <span>🎯 得失点差: {'+' if gd > 0 else ''}{gd}点差</span>
            <span>🛒 購入口数: {tickets}口 ({cost:,}円)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    t2_key = f"t2_{round_num}"
    if t2_key not in st.session_state:
        st.session_state[t2_key] = generate_ticket_2()
    t2_nums, t2_odd, t2_even, t2_total = st.session_state[t2_key]

    t3_key = f"t3_{round_num}"
    if t3_key not in st.session_state:
        st.session_state[t3_key] = generate_ticket_qp()
    t3_nums = st.session_state[t3_key]

    if tickets > 0:
        t1, logs = generate_ticket_1(cur)

        # 抽出結果カード
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown("<div style='font-weight:800; margin-bottom:8px; color:#FCA5A5;'>1口目【マッチスタッツ連動型】</div>", unsafe_allow_html=True)
        b1 = "".join([f'<div class="loto-ball">{n:02d}</div>' for n in t1])
        st.markdown(f'<div class="ball-container">{b1}</div>', unsafe_allow_html=True)
        st.caption(" ➔ " + " / ".join(logs))
        st.markdown('</div>', unsafe_allow_html=True)

        if tickets >= 2:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown("<div style='font-weight:800; margin-bottom:8px; color:#FBBF24;'>2口目【AI統計分析型（動的生成）】</div>", unsafe_allow_html=True)
            b2 = "".join([f'<div class="loto-ball loto-ball-gold">{n:02d}</div>' for n in t2_nums])
            st.markdown(f'<div class="ball-container">{b2}</div>', unsafe_allow_html=True)
            st.caption(f" ➔ 統計分析: 奇数{t2_odd}:偶数{t2_even} / 合計値{t2_total}")
            st.markdown('</div>', unsafe_allow_html=True)

        if tickets >= 3:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown("<div style='font-weight:800; margin-bottom:8px;'>3口目【クイックピック（QP）】</div>", unsafe_allow_html=True)
            b3 = "".join([f'<div class="loto-ball">{n:02d}</div>' for n in t3_nums])
            st.markdown(f'<div class="ball-container">{b3}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        copy_text = f"""【ロト7 購入シート】第{round_num}節 vs {opp_name} ({ha})
購入口数: {tickets}口 ({cost:,}円)
1口目: {' '.join([f'{n:02d}' for n in t1])}"""
        if tickets >= 2:
            copy_text += f"\n2口目: {' '.join([f'{n:02d}' for n in t2_nums])}"
        if tickets >= 3:
            copy_text += f"\n3口目: {' '.join([f'{n:02d}' for n in t3_nums])} (QP)"

        st.markdown("**📋 購入用テキスト**")
        st.code(copy_text, language="text")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("💾 試合データを保存（確定）", use_container_width=True):
                cur["is_finished"] = True
                save_match_data_to_file(round_num, cur)
                st.success("保存しました！")
                st.rerun()

        with col_b2:
            if st.button("📊 収支管理に登録", use_container_width=True):
                history = load_history()
                new_record = {
                    "round": round_num,
                    "opponent": f"{opp_name} ({ha})",
                    "score": f"{ars_score}-{opp_score}",
                    "tickets": tickets,
                    "cost": cost,
                    "ticket_1": t1,
                    "ticket_2": t2_nums if tickets >= 2 else [],
                    "hit_amount": 0,
                    "status": "未抽せん"
                }
                history.insert(0, new_record)
                save_history(history)
                st.success("収支管理に登録しました！")
    else:
        if has_result:
            st.info("引き分けまたは敗戦のため、購入対象外（0口）です。")
        else:
            st.info("キックオフ前です。URL自動取得または上の手動詳細からスコアを入力してください。")

# ==========================================
# TAB 2: シーズン収支管理
# ==========================================
with tab2:
    history = load_history()
    total_spent = sum([item.get("cost", 0) for item in history])
    total_won = sum([item.get("hit_amount", 0) for item in history])
    net_balance = total_won - total_spent
    roi = (total_won / total_spent * 100) if total_spent > 0 else 0

    st.markdown(f"""
    <div class="modern-card">
        <div style="font-size:12px; color:#94A3B8;">2026-27 SEASON OVERVIEW (収支概要)</div>
        <div style="font-size:30px; font-weight:900; color:{'#34D399' if net_balance >= 0 else '#F87171'}; margin:8px 0;">
            {'+' if net_balance > 0 else ''}{net_balance:,} 円
        </div>
        <div style="display:flex; justify-content:space-between; font-size:13px; border-top:1px solid rgba(255,255,255,0.08); padding-top:10px; color:#94A3B8;">
            <span>総投資: <strong style="color:#F8FAFC;">-{total_spent:,}円</strong></span>
            <span>総回収: <strong style="color:#F8FAFC;">+{total_won:,}円</strong></span>
            <span>回収率: <strong style="color:#F8FAFC;">{roi:.1f}%</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if history:
        for idx, rec in enumerate(history):
            with st.expander(f"第{rec.get('round', '')}節 vs {rec['opponent']} ({rec['score']}) - {rec['tickets']}口"):
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    st.write(f"購入額: {rec['cost']:,}円")
                    st.write(f"1口目: {rec['ticket_1']}")
                    if rec.get("ticket_2"):
                        st.write(f"2口目: {rec['ticket_2']}")
                with col_h2:
                    won_input = st.number_input(
                        f"当せん金額 (円)",
                        min_value=0,
                        step=1000,
                        value=rec.get("hit_amount", 0),
                        key=f"won_{idx}_{rec.get('round', idx)}"
                    )
                    if won_input != rec.get("hit_amount", 0):
                        history[idx]["hit_amount"] = int(won_input)
                        history[idx]["status"] = f"{won_input:,}円 当せん" if won_input > 0 else "ハズレ"
                        save_history(history)
                        st.rerun()
    else:
        st.caption("購入履歴データはありません。")

    if st.button("🗑️ 履歴データをリセット"):
        save_history([])
        st.rerun()
