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
    page_title="Gunners Loto 7",
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
# 永続データ管理（収支・履歴用 JSON）
# ==========================================
DATA_FILE = "match_history.json"

def load_history():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==========================================
# ロト7 採番ロジック
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
    """1口目：スタッツ連動型（可変得点者スロット ＋ 優先順位 ＋ 重複フォールバック）"""
    selected = []
    log_details = []

    # ① 得点者全員の背番号
    scorers = stats.get("scorers", [])
    for sc in scorers:
        num = convert_to_loto_number(sc)
        if num not in selected and len(selected) < 7:
            selected.append(num)
            log_details.append(f"得点者: {num:02d}")

    # ② 先制アシスト者
    if len(selected) < 7 and stats.get("assist"):
        num = convert_to_loto_number(stats["assist"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"先制アシスト: {num:02d}")

    # ③ 先制ゴール時間（分）
    if len(selected) < 7 and stats.get("goal_time"):
        num = convert_to_loto_number(stats["goal_time"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"ゴール時間: {num:02d}分")

    # ④ パス成功数 1位
    if len(selected) < 7 and stats.get("top_passer"):
        num = convert_to_loto_number(stats["top_passer"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"パス1位: {num:02d}")

    # ⑤ チーム総シュート数
    if len(selected) < 7 and stats.get("shots"):
        num = convert_to_loto_number(stats["shots"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"総シュート数: {num:02d}")

    # ⑥ ボール支配率（%）
    if len(selected) < 7 and stats.get("possession"):
        num = convert_to_loto_number(stats["possession"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"支配率: {num:02d}")

    # ⑦ 試合開催日（日）
    if len(selected) < 7 and stats.get("match_day"):
        num = convert_to_loto_number(stats["match_day"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"開催日: {num:02d}日")

    # 重複時の予備差し替え（⑧守備 ➔ ⑨伝統枠 ➔ ⑩サブ）
    fallback_pool = [
        stats.get("top_defender", 2),
        14, 13, 18, 1,
        stats.get("first_sub", 19)
    ]
    fb_idx = 0
    while len(selected) < 7 and fb_idx < len(fallback_pool):
        cand = convert_to_loto_number(fallback_pool[fb_idx])
        if cand not in selected:
            selected.append(cand)
            log_details.append(f"予備枠: {cand:02d}")
        fb_idx += 1

    return sorted(selected), log_details

def generate_ticket_2():
    patterns = [
        [4, 9, 13, 18, 22, 30, 31],
        [2, 7, 14, 19, 23, 30, 35],
        [3, 8, 12, 17, 26, 31, 34],
        [5, 10, 15, 20, 24, 28, 33]
    ]
    return random.choice(patterns)

def generate_ticket_qp():
    return sorted(random.sample(range(1, 38), 7))

# ==========================================
# FotMob API パース関数（URL / ID両対応）
# ==========================================
def extract_match_id(input_str):
    match = re.search(r'(\d{6,8})', input_str)
    return match.group(1) if match else input_str.strip()

def fetch_from_fotmob(match_id):
    if not match_id:
        return {"success": False}
        
    url = f"https://www.fotmob.com/api/matchDetails?matchId={match_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.fotmob.com/"
    }
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            general = data.get("general", {})
            header = data.get("header", {})
            teams = header.get("teams", [])
            
            home_name = teams[0].get("name", "Home") if len(teams) > 0 else "Arsenal"
            away_name = teams[1].get("name", "Away") if len(teams) > 1 else "Opponent"
            home_score = teams[0].get("score", 0) if len(teams) > 0 else 0
            away_score = teams[1].get("score", 0) if len(teams) > 1 else 0
            
            is_arsenal_home = "arsenal" in home_name.lower()
            arsenal_score = home_score if is_arsenal_home else away_score
            opp_score = away_score if is_arsenal_home else home_score
            
            match_date_str = general.get("matchTimeUTC", "")
            match_day = int(match_date_str[8:10]) if len(match_date_str) >= 10 else 17
            
            return {
                "success": True,
                "match_name": f"{home_name} vs {away_name}",
                "date": match_date_str[:10],
                "match_day": match_day,
                "home_team": home_name,
                "away_team": away_name,
                "home_score": int(home_score),
                "away_score": int(away_score),
                "arsenal_score": int(arsenal_score),
                "opp_score": int(opp_score),
                "fotmob_url": f"https://www.fotmob.com/matches/{match_id}"
            }
    except Exception:
        pass
    return {"success": False}

# ==========================================
# メイン画面 UI
# ==========================================
st.markdown("""
<div class="arsenal-header">
    <div style="display:flex; align-items:center; gap:10px;">
        <img src="https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png" width="30" height="30" style="object-fit:contain;">
        <span style="font-size:18px; letter-spacing:0.5px;">GUNNERS LOTO 7</span>
    </div>
    <span style="background:rgba(0,0,0,0.3); padding:4px 10px; border-radius:20px; font-size:12px; border:1px solid #9C824A;">Official Match Mode</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚽ 試合 & ナンバー算出", "📊 シーズン収支管理"])

with tab1:
    st.markdown("**1. FotMob 試合URL または Match ID を入力**")

    # スマホ向け操作ガイド（折りたたみ）
    with st.expander("📱 FotMobアプリからのURL取得方法（タップで開く）"):
        st.markdown("""
        1. **FotMobアプリ**でアーセナルの試合を開く
        2. 右上の **共有アイコン（シェアボタン）** をタップ
        3. **「リンクをコピー」** を選択
        4. 下の入力欄にそのままペースト（末尾のMatch IDを自動抽出します）
        """)

    match_input = st.text_input(
        "URLまたはIDを入力",
        value="https://www.fotmob.com/matches/arsenal-vs-wolverhampton-wanderers/4506307",
        placeholder="https://fotmob.com/match/... または Match ID"
    )

    match_id = extract_match_id(match_input)
    api_result = fetch_from_fotmob(match_id)

    if api_result.get("success"):
        st.success(f"✅ FotMobから試合データを自動取得しました: {api_result['match_name']}")
        def_home = api_result["home_team"]
        def_away = api_result["away_team"]
        def_h_score = api_result["home_score"]
        def_a_score = api_result["away_score"]
        def_day = api_result["match_day"]
        def_url = api_result["fotmob_url"]
    else:
        st.info("💡 URLまたはIDからスタッツを設定します（数値を手動調整できます）。")
        def_home = "Arsenal"
        def_away = "Wolves"
        def_h_score = 2
        def_a_score = 0
        def_day = 17
        def_url = f"https://www.fotmob.com/matches/{match_id}" if match_id else "https://www.fotmob.com"

    # スタッツ確認 & 調整セクション
    with st.expander("📝 試合情報 & スタッツ詳細（OG補正・微調整）", expanded=True):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            h_team = st.text_input("ホームチーム", value=def_home)
            h_score = st.number_input("ホーム得点", min_value=0, value=def_h_score)
        with col_m2:
            a_team = st.text_input("アウェイチーム", value=def_away)
            a_score = st.number_input("アウェイ得点", min_value=0, value=def_a_score)

        st.caption("【ロト7連動スタッツ】※OG発生時は誘発選手の背番号を入力")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            scorers_str = st.text_input("① 得点者 背番号（カンマ区切り）", value="29, 7", help="例: 29, 7")
            assist_num = st.number_input("② 先制アシスト 背番号（0でなし）", min_value=0, max_value=99, value=7)
            goal_time = st.number_input("③ 先制ゴール時間（分）", min_value=1, max_value=120, value=25)
        with col_s2:
            passer_num = st.number_input("④ パス数1位 背番号", min_value=1, max_value=99, value=6)
            shots_num = st.number_input("⑤ チーム総シュート数", min_value=0, value=18)
            possession_num = st.number_input("⑥ ボール支配率 (%)", min_value=0, max_value=100, value=53)
            match_day_num = st.number_input("⑦ 試合開催日 (日)", min_value=1, max_value=31, value=def_day)

    # 勝敗判定 & 口数計算
    is_ars_home = "arsenal" in h_team.lower()
    ars_score = h_score if is_ars_home else a_score
    opp_score = a_score if is_ars_home else h_score
    gd = ars_score - opp_score
    tickets_count = max(0, min(5, gd)) if gd > 0 else 0
    total_cost = tickets_count * 300

    # スコアカード
    st.markdown(f"""
    <div class="match-card">
        <div style="display:flex; justify-content:space-between; font-size:12px; color:#94A3B8; margin-bottom:8px;">
            <span>Match ID: {match_id}</span>
            <span style="color:#34D399; font-weight:bold;">FT (試合終了)</span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; margin:12px 0;">
            <div style="text-align:center; font-weight:bold; font-size:16px;">{h_team}</div>
            <div style="font-size:34px; font-weight:900; letter-spacing:3px;">{h_score} - {a_score}</div>
            <div style="text-align:center; font-weight:bold; font-size:16px;">{a_team}</div>
        </div>
        <div class="badge-win">
            <span>🎯 判定: 得失点差 {'+' if gd > 0 else ''}{gd}点差</span>
            <span>🛒 購入口数: {tickets_count}口 ({total_cost:,}円)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.link_button("🔗 FotMobでこの試合の詳細ページを開く", def_url, use_container_width=True)

    scorers_list = []
    for s in scorers_str.split(","):
        s = s.strip()
        if s.isdigit():
            scorers_list.append(int(s))

    current_stats = {
        "scorers": scorers_list,
        "assist": assist_num if assist_num > 0 else None,
        "goal_time": goal_time,
        "top_passer": passer_num,
        "shots": shots_num,
        "possession": possession_num,
        "match_day": match_day_num,
        "top_defender": 2,
        "first_sub": 19
    }

    # ロト7採番結果表示
    if tickets_count > 0:
        t1_nums, t1_logs = generate_ticket_1(current_stats)
        t2_nums = generate_ticket_2()
        t3_nums = generate_ticket_qp()

        st.markdown("**1口目【マッチスタッツ連動型】**")
        balls_html_1 = "".join([f'<div class="loto-ball">{n:02d}</div>' for n in t1_nums])
        st.markdown(f'<div class="ball-container">{balls_html_1}</div>', unsafe_allow_html=True)
        st.caption(" ➔ " + " / ".join(t1_logs))

        if tickets_count >= 2:
            st.markdown("**2口目【過去3年 AI統計分析型】**")
            balls_html_2 = "".join([f'<div class="loto-ball loto-ball-gold">{n:02d}</div>' for n in t2_nums])
            st.markdown(f'<div class="ball-container">{balls_html_2}</div>', unsafe_allow_html=True)
            st.caption(" ➔ 統計構成: 奇数3:偶数4 / 合計127 / 連番30-31")

        if tickets_count >= 3:
            st.markdown("**3口目【クイックピック（QP）】**")
            balls_html_3 = "".join([f'<div class="loto-ball">{n:02d}</div>' for n in t3_nums])
            st.markdown(f'<div class="ball-container">{balls_html_3}</div>', unsafe_allow_html=True)
            st.caption(" ➔ 自動ランダム採番")

        # コピペ用テキスト生成
        st.divider()
        copy_text = f"""【ロト7 購入シート】
対戦: {h_team} {h_score} - {a_score} {a_team}
購入口数: {tickets_count}口 ({total_cost:,}円)
1口目: {' '.join([f'{n:02d}' for n in t1_nums])}"""
        if tickets_count >= 2:
            copy_text += f"\n2口目: {' '.join([f'{n:02d}' for n in t2_nums])}"
        if tickets_count >= 3:
            copy_text += f"\n3口目: {' '.join([f'{n:02d}' for n in t3_nums])} (QP)"

        st.markdown("**📋 購入用テキスト（右上のアイコンで1タップコピー）**")
        st.code(copy_text, language="text")

        # 購入履歴保存ボタン
        if st.button("💾 この試合を購入履歴に保存", use_container_width=True):
            history = load_history()
            opp_name = a_team if is_ars_home else h_team
            new_record = {
                "date": f"2026-08-{match_day_num:02d}",
                "opponent": opp_name,
                "score": f"{ars_score}-{opp_score}",
                "tickets": tickets_count,
                "cost": total_cost,
                "ticket_1": t1_nums,
                "ticket_2": t2_nums if tickets_count >= 2 else [],
                "hit_amount": 0,
                "status": "未抽せん"
            }
            history.insert(0, new_record)
            save_history(history)
            st.success(f"{h_team} vs {a_team} の購入データを保存しました！")
    else:
        st.info("引き分けまたは敗戦のため、ロト7の購入はありません（0口）。")

with tab2:
    history = load_history()
    total_spent = sum([item.get("cost", 0) for item in history])
    total_won = sum([item.get("hit_amount", 0) for item in history])
    net_balance = total_won - total_spent
    roi = (total_won / total_spent * 100) if total_spent > 0 else 0

    st.markdown(f"""
    <div class="match-card">
        <div style="font-size:12px; color:#94A3B8;">SEASON OVERVIEW (収支概要)</div>
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
            with st.expander(f"{rec.get('date', '')} vs {rec['opponent']} ({rec['score']}) - {rec['tickets']}口"):
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    st.write(f"購入額: {rec['cost']:,}円")
                    st.write(f"1口目: {rec['ticket_1']}")
                with col_h2:
                    won_input = st.number_input(f"当せん金額 (円)", min_value=0, step=1000, value=rec.get("hit_amount", 0), key=f"won_{idx}")
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
