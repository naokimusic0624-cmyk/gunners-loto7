import streamlit as st
import requests
import re
import json
import os
import random

# ==========================================
# ページ基本設定 & カスタムCSS
# ==========================================
st.set_page_config(
    page_title="Gunners Loto 7 (2026-27)",
    page_icon="https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0B0F19;
        color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .arsenal-header {
        background: linear-gradient(135deg, #DB0007 0%, #7F0004 100%);
        padding: 12px 18px;
        border-radius: 12px;
        color: white;
        font-weight: 800;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(219, 0, 7, 0.35);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .match-card {
        background-color: #1E293B;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
    }
    .ball-container {
        display: flex;
        justify-content: space-between;
        gap: 6px;
        margin: 10px 0;
    }
    .loto-ball {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 15px;
        color: #0F172A;
        background: radial-gradient(circle at 35% 35%, #FFFFFF, #CBD5E1);
        box-shadow: 0 3px 6px rgba(0,0,0,0.4);
    }
    .loto-ball-gold {
        background: radial-gradient(circle at 35% 35%, #FDE68A, #D97706);
        color: #451A03;
    }
    .badge-win {
        background-color: rgba(219, 0, 7, 0.2);
        border: 1px solid #DB0007;
        color: #FECACA;
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 13px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
        margin-top: 10px;
    }
    div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1px solid #475569 !important;
        color: #F8FAFC !important;
    }
    div[data-baseweb="select"] * {
        color: #F8FAFC !important;
    }
    div[data-baseweb="input"] input {
        color: #F8FAFC !important;
        background-color: #1E293B !important;
    }
    .stButton>button, .stLinkButton>a {
        border-radius: 10px !important;
        font-weight: bold !important;
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
    "lewis-skelly": 49, "skelly": 49, "white": 4, "rice": 41,
    "gabriel": 6, "saliba": 2, "odegaard": 8, "saka": 7,
    "havertz": 29, "martinelli": 11, "calafiori": 33, "timber": 12,
    "trossard": 19, "jesus": 9, "sterling": 30, "merino": 23,
    "nwaneri": 53, "partey": 5, "zinchenko": 17, "jorginho": 20, "raya": 22
}

# ==========================================
# ロト7 採番ロジック（確定新順序版：①〜⑩ + (-37)）
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

    # ① 得点者全員の背番号
    for sc in stats.get("scorers", []):
        num = convert_to_loto_number(sc)
        if num not in selected and len(selected) < 7:
            selected.append(num)
            orig = f"({sc}➔{num:02d})" if sc > 37 else f"({num:02d})"
            log_details.append(f"①得点者: {orig}")

    # ② 先制点 アシスト者
    if len(selected) < 7 and stats.get("assist"):
        sc = stats["assist"]
        num = convert_to_loto_number(sc)
        if num not in selected:
            selected.append(num)
            orig = f"({sc}➔{num:02d})" if sc > 37 else f"({num:02d})"
            log_details.append(f"②アシスト: {orig}")

    # ③ 先制ゴール時間
    if len(selected) < 7 and stats.get("goal_time"):
        sc = stats["goal_time"]
        num = convert_to_loto_number(sc)
        if num not in selected:
            selected.append(num)
            orig = f"({sc}分➔{num:02d})" if sc > 37 else f"({num:02d}分)"
            log_details.append(f"③ゴール時間: {orig}")

    # ④ パス成功数 1位
    passer_val = stats.get("passer", 49)
    if passer_val in [1, "1", 0, "0"]:
        passer_val = 49
    if len(selected) < 7 and passer_val:
        num = convert_to_loto_number(passer_val)
        if num not in selected:
            selected.append(num)
            orig = f"({passer_val}➔{num:02d})" if passer_val > 37 else f"({num:02d})"
            log_details.append(f"④パス1位: {orig}")

    # ⑤ チーム総シュート数
    if len(selected) < 7 and stats.get("shots"):
        sc = stats["shots"]
        num = convert_to_loto_number(sc)
        if num not in selected:
            selected.append(num)
            orig = f"({sc}本➔{num:02d})" if sc > 37 else f"({num:02d})"
            log_details.append(f"⑤シュート数: {orig}")

    # ⑥ ボール支配率
    if len(selected) < 7 and stats.get("poss"):
        sc = stats["poss"]
        num = convert_to_loto_number(sc)
        if num not in selected:
            selected.append(num)
            orig = f"({sc}%➔{num:02d})" if sc > 37 else f"({num:02d})"
            log_details.append(f"⑥支配率: {orig}")

    # ⑦ 試合開催日
    if len(selected) < 7 and stats.get("day"):
        sc = stats["day"]
        num = convert_to_loto_number(sc)
        if num not in selected:
            selected.append(num)
            orig = f"({sc}日➔{num:02d})" if sc > 37 else f"({num:02d})"
            log_details.append(f"⑦開催日: ({num:02d}日)")

    # ⑧〜⑩ 差し替え枠・補填枠プール
    replacement_pool = []
    
    # ⑧ 評価点最高GK/DF
    best_def_num = stats.get("best_def_gk_num")
    if best_def_num:
        replacement_pool.append((best_def_num, f"⑧最高評価DF/GK(# {best_def_num})"))

    # ⑨ クラブ伝統枠
    for t_num, t_label in [(14, "⑨クラブ伝統枠(アンリ#14)"), (13, "⑨クラブ伝統枠(優勝数#13)"), (18, "⑨クラブ伝統枠(創設年#18)"), (1, "⑨クラブ伝統枠(#01)")]:
        replacement_pool.append((t_num, t_label))

    # ⑩ ファースト・サブ
    replacement_pool.append((53, "⑩ファースト・サブ(ヌワネリ#53)"))
    replacement_pool.append((30, "⑩ファースト・サブ(スターリング#30)"))
    
    pool_idx = 0
    while len(selected) < 7 and pool_idx < len(replacement_pool):
        raw_val, label = replacement_pool[pool_idx]
        cand = convert_to_loto_number(raw_val)
        if cand not in selected:
            selected.append(cand)
            orig = f"({raw_val}➔{cand:02d})" if raw_val > 37 else f"({cand:02d})"
            log_details.append(f"{label}: {orig}")
        pool_idx += 1

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
# Webページ解析（評価点最高DF/GK抽出対応）
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
        ars_players_all = lineup.get(ars_side, {}).get("starters", []) + lineup.get(ars_side, {}).get("subs", [])

        # 評価点が最も高いGK/DFを特定
        best_def_gk_num = 22 # デフォルトラヤ
        highest_rating = -1.0

        for p in ars_players_all:
            pid = str(p.get("id", ""))
            shirt = p.get("shirt") or p.get("shirtNumber")
            pname = p.get("name", "").lower()
            pos = str(p.get("position", "")).lower()
            role = str(p.get("role", "")).lower()
            
            pnum = int(shirt) if shirt else None
            if not pnum and pid in player_number_map:
                pnum = player_number_map[pid]
            if not pnum:
                for k, v in ARSENAL_SQUAD_NUMBERS.items():
                    if k in pname:
                        pnum = v
                        break

            if pnum:
                player_number_map[pid] = pnum

            # 評価点取得
            rating = 0.0
            rc = p.get("rating", {})
            if isinstance(rc, dict):
                try:
                    rating = float(rc.get("num", 0))
                except:
                    pass
            elif isinstance(rc, (int, float)):
                rating = float(rc)

            # ポジション判定（GKまたはDF、あるいはバックラインの選手）
            is_def_or_gk = ("gk" in pos or "def" in pos or "keeper" in role or "defender" in role or 
                            pnum in [2, 3, 4, 6, 12, 17, 22, 33, 49])

            if is_def_or_gk and pnum:
                if rating > highest_rating:
                    highest_rating = rating
                    best_def_gk_num = pnum

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

        shots = 15
        possession = 55
        stats_periods = content.get("stats", {}).get("Periods", {}).get("All", {}).get("stats", [])
        for sec in stats_periods:
            for item in sec.get("stats", []):
                title = item.get("title", "").lower()
                vals = item.get("stats", [])
                if len(vals) >= 2:
                    if "possession" in title:
                        p_str = str(vals[ars_idx]).replace("%", "").strip()
                        if p_str.isdigit():
                            possession = int(p_str)
                    elif "shots" in title and "total" in title:
                        s_str = str(vals[ars_idx]).strip()
                        if s_str.isdigit():
                            shots = int(s_str)

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
            "best_def_gk_num": best_def_gk_num
        }, None

    except Exception as e:
        return None, f"解析エラー: {str(e)[:30]}"

# ==========================================
# メイン画面 UI
# ==========================================
saved_matches = load_saved_matches()

st.markdown("""
<div class="arsenal-header">
    <div style="display:flex; align-items:center; gap:10px;">
        <img src="https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png" width="30" height="30" style="object-fit:contain;">
        <span style="font-size:18px; letter-spacing:0.5px;">GUNNERS LOTO 7</span>
    </div>
    <span style="background:rgba(0,0,0,0.3); padding:4px 10px; border-radius:20px; font-size:12px; border:1px solid #9C824A;">Premier League 2026-27</span>
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
                "best_def_gk_num": 22
            }

    cur = st.session_state[state_key]
    if cur.get("passer") in [1, "1", 0, "0"]:
        cur["passer"] = 49

    st.markdown("**⚡ FotMobスタッツ連携（1度保存すれば次回以降リンク不要）**")
    col_u1, col_u2 = st.columns([3, 1])
    with col_u1:
        user_url_input = st.text_input(
            "FotMob URLまたは共有テキスト",
            value="",
            placeholder="FotMobの試合URLを貼り付け",
            key=f"url_in_{round_num}",
            label_visibility="collapsed"
        )
    with col_u2:
        sync_clicked = st.button("🔄 自動取得", use_container_width=True)

    if sync_clicked:
        if user_url_input:
            with st.spinner("FotMobページからスタッツと評価点を抽出中..."):
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
                    cur["best_def_gk_num"] = fetched["best_def_gk_num"]
                    
                    save_match_data_to_file(round_num, cur)
                    st.success(f"スタッツを抽出し、最高評価DF/GK（背番号 {fetched['best_def_gk_num']}）を反映・保存しました！")
                    st.rerun()
                else:
                    st.error(err)
        else:
            st.warning("FotMobの試合URLを入力してください。")

    h_team = "アーセナルFC" if is_home else opp_name
    a_team = opp_name if is_home else "アーセナルFC"

    with st.expander("📝 スコア & スタッツ詳細（手動補正・OG対応）", expanded=True):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            cur["h_score"] = st.number_input(f"{h_team} 得点", min_value=0, value=int(cur.get("h_score", 0)), key=f"hs_{round_num}")
        with col_m2:
            cur["a_score"] = st.number_input(f"{a_team} 得点", min_value=0, value=int(cur.get("a_score", 0)), key=f"as_{round_num}")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            sc_str = ", ".join([str(n) for n in cur.get("scorers", [7])])
            scorers_input = st.text_input("得点者 背番号（カンマ区切り）", value=sc_str, key=f"sc_{round_num}")
            cur["scorers"] = [int(s.strip()) for s in scorers_input.split(",") if s.strip().isdigit()]
            cur["assist"] = st.number_input("先制アシスト 背番号", min_value=0, max_value=99, value=int(cur.get("assist", 8)), key=f"asst_{round_num}")
            cur["goal_time"] = st.number_input("先制ゴール時間（分）", min_value=1, max_value=120, value=int(cur.get("goal_time", 20)), key=f"gt_{round_num}")
        with col_s2:
            cur["passer"] = st.number_input("パス1位 背番号", min_value=1, max_value=99, value=int(cur.get("passer", 49)), key=f"pass_{round_num}")
            cur["shots"] = st.number_input("チーム総シュート数", min_value=0, value=int(cur.get("shots", 15)), key=f"sh_{round_num}")
            cur["poss"] = st.number_input("ボール支配率 (%)", min_value=0, max_value=100, value=int(cur.get("poss", 55)), key=f"poss_{round_num}")
            cur["day"] = st.number_input("試合開催日（日）", min_value=1, max_value=31, value=int(cur.get("day", 1)), key=f"day_{round_num}")

    ars_score = cur.get("h_score", 0) if is_home else cur.get("a_score", 0)
    opp_score = cur.get("a_score", 0) if is_home else cur.get("h_score", 0)
    gd = ars_score - opp_score

    has_result = cur.get("is_finished", False) or (cur.get("h_score", 0) > 0 or cur.get("a_score", 0) > 0)
    tickets = max(0, min(5, gd)) if (has_result and gd > 0) else 0
    cost = tickets * 300

    st.markdown(f"""
    <div class="match-card">
        <div style="display:flex; justify-content:space-between; font-size:12px; color:#94A3B8; margin-bottom:8px;">
            <span>第{round_num}節 / 38節</span>
            <span style="color:{'#34D399' if cur.get('is_finished', False) else '#F59E0B'}; font-weight:bold;">
                {'FT (試合終了)' if cur.get('is_finished', False) else 'キックオフ前'}
            </span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; margin:12px 0;">
            <div style="text-align:center; width:120px; font-weight:bold; font-size:15px;">{h_team}</div>
            <div style="text-align:center;">
                <div style="font-size:36px; font-weight:900; letter-spacing:3px;">
                    {f"{cur.get('h_score', 0)} - {cur.get('a_score', 0)}" if has_result else "VS"}
                </div>
                <div style="font-size:11px; color:#94A3B8;">{'HOME' if is_home else 'AWAY'}</div>
            </div>
            <div style="text-align:center; width:120px; font-weight:bold; font-size:15px;">{a_team}</div>
        </div>
        <div class="badge-win">
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

        st.markdown("**1口目【マッチスタッツ連動型】**")
        b1 = "".join([f'<div class="loto-ball">{n:02d}</div>' for n in t1])
        st.markdown(f'<div class="ball-container">{b1}</div>', unsafe_allow_html=True)
        st.caption(" ➔ " + " / ".join(logs))

        if tickets >= 2:
            st.markdown("**2口目【AI統計分析型（動的生成）】**")
            b2 = "".join([f'<div class="loto-ball loto-ball-gold">{n:02d}</div>' for n in t2_nums])
            st.markdown(f'<div class="ball-container">{b2}</div>', unsafe_allow_html=True)
            st.caption(f" ➔ 統計分析: 奇数{t2_odd}:偶数{t2_even} / 合計値{t2_total}")

        if tickets >= 3:
            st.markdown("**3口目【クイックピック（QP）】**")
            b3 = "".join([f'<div class="loto-ball">{n:02d}</div>' for n in t3_nums])
            st.markdown(f'<div class="ball-container">{b3}</div>', unsafe_allow_html=True)

        st.divider()
        copy_text = f"""【ロト7 購入シート】第{round_num}節 vs {opp_name} ({ha})
購入口数: {tickets}口 ({cost:,}円)
1口目: {' '.join([f'{n:02d}' for n in t1])}"""
        if tickets >= 2:
            copy_text += f"\n2口目: {' '.join([f'{n:02d}' for n in t2_nums])}"
        if tickets >= 3:
            copy_text += f"\n3口目: {' '.join([f'{n:02d}' for n in t3_nums])} (QP)"

        st.markdown("**📋 購入用テキスト（右上のアイコンで1タップコピー）**")
        st.code(copy_text, language="text")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("💾 この節の試合データ・番号を保存（確定）", use_container_width=True):
                cur["is_finished"] = True
                save_match_data_to_file(round_num, cur)
                st.success(f"第{round_num}節のデータを保存しました！")
                st.rerun()

        with col_b2:
            if st.button("📊 収支管理に保存", use_container_width=True):
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
                st.success(f"第{round_num}節（vs {opp_name}）の購入データを収支管理に保存しました！")
    else:
        if has_result:
            st.info("引き分けまたは敗戦のため、ロト7の購入はありません（0口）。")
        else:
            st.info("キックオフ前です。FotMobのURLから自動取得するか、上の入力フォームにスコアを入れてください。")

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
    <div class="match-card">
        <div style="font-size:12px; color:#94A3B8;">2026-27 SEASON OVERVIEW (収支概要)</div>
        <div style="font-size:28px; font-weight:900; color:{'#34D399' if net_balance >= 0 else '#F87171'}; margin:6px 0;">
            {'+' if net_balance > 0 else ''}{net_balance:,} 円
        </div>
        <div style="display:flex; justify-content:space-between; font-size:12px; border-top:1px solid rgba(255,255,255,0.08); padding-top:8px;">
            <span>総投資: -{total_spent:,}円</span>
            <span>総回収: +{total_won:,}円</span>
            <span>回収率: {roi:.1f}%</span>
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
        st.caption("保存された購入履歴はありません。")

    if st.button("🗑️ 履歴データをリセット"):
        save_history([])
        st.rerun()
