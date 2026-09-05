import streamlit as st
import requests
import json
import os
import random
from datetime import datetime

# ==========================================
# ページ基本設定 & カスタムCSS
# ==========================================
st.set_page_config(
    page_title="Gunners Loto 7 (Official Live)",
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
# 永続データ管理
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
# ① FotMob公式サーバーから現在シーズンの全日程を動的取得
# ==========================================
@st.cache_data(ttl=600)
def fetch_live_arsenal_fixtures():
    """FotMob公式APIからアーセナル（ID: 9825）の最新公式全日程をリアルタイム取得"""
    url = "https://www.fotmob.com/api/teams?id=9825"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.fotmob.com/teams/9825/overview/arsenal"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=6)
        if res.status_code == 200:
            data = res.json()
            
            # FotMobのJSONレスポンス構造から試合リストを走査
            raw_fixtures = []
            if "fixtures" in data:
                fix_data = data["fixtures"]
                if isinstance(fix_data, dict):
                    raw_fixtures = fix_data.get("allFixtures", {}).get("fixtures", []) or fix_data.get("fixtures", [])
                elif isinstance(fix_data, list):
                    raw_fixtures = fix_data
            
            if not raw_fixtures and "overview" in data:
                raw_fixtures = data["overview"].get("fixtures", [])

            extracted = []
            for item in raw_fixtures:
                # プレミアリーグの試合、または全公式戦を対象にする
                t_name = item.get("tournament", {}).get("name", "")
                home_dict = item.get("home", {})
                away_dict = item.get("away", {})
                status_dict = item.get("status", {})
                
                m_id = str(item.get("id", ""))
                h_name = home_dict.get("name", "")
                a_name = away_dict.get("name", "")
                
                # スコア判定
                is_finished = status_dict.get("finished", False)
                h_score = home_dict.get("score")
                a_score = away_dict.get("score")
                
                # 試合日時パース
                utc_str = status_dict.get("utcTime", "")
                date_str = utc_str[:10] if len(utc_str) >= 10 else "未定"
                day_num = int(utc_str[8:10]) if len(utc_str) >= 10 and utc_str[8:10].isdigit() else 1
                
                # 表示用ラベル生成
                if is_finished and h_score is not None and a_score is not None:
                    label = f"【終了】{h_name} {h_score} - {a_score} {a_name} ({date_str})"
                else:
                    label = f"【未開催】{h_name} vs {a_name} ({date_str})"
                
                extracted.append({
                    "match_id": m_id,
                    "label": label,
                    "tournament": t_name,
                    "home": h_name,
                    "away": a_name,
                    "h_score": int(h_score) if (h_score is not None and is_finished) else None,
                    "a_score": int(a_score) if (a_score is not None and is_finished) else None,
                    "is_finished": is_finished,
                    "date": date_str,
                    "day": day_num,
                    "fotmob_url": f"https://www.fotmob.com/matches/{m_id}"
                })
            
            if extracted:
                return extracted, None
        return [], f"FotMobサーバー通信エラー (HTTP {res.status_code})"
    except Exception as e:
        return [], f"取得エラー: {str(e)[:40]}"

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
    selected = []
    log_details = []

    for sc in stats.get("scorers", []):
        num = convert_to_loto_number(sc)
        if num not in selected and len(selected) < 7:
            selected.append(num)
            log_details.append(f"得点者: {num:02d}")

    if len(selected) < 7 and stats.get("assist"):
        num = convert_to_loto_number(stats["assist"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"先制アシスト: {num:02d}")

    if len(selected) < 7 and stats.get("goal_time"):
        num = convert_to_loto_number(stats["goal_time"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"ゴール時間: {num:02d}分")

    if len(selected) < 7 and stats.get("passer"):
        num = convert_to_loto_number(stats["passer"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"パス1位: {num:02d}")

    if len(selected) < 7 and stats.get("shots"):
        num = convert_to_loto_number(stats["shots"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"総シュート数: {num:02d}")

    if len(selected) < 7 and stats.get("possession"):
        num = convert_to_loto_number(stats["possession"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"支配率: {num:02d}")

    if len(selected) < 7 and stats.get("match_day"):
        num = convert_to_loto_number(stats["match_day"])
        if num not in selected:
            selected.append(num)
            log_details.append(f"開催日: {num:02d}日")

    fallback_pool = [stats.get("top_defender", 2), 14, 13, 18, 1, stats.get("first_sub", 19)]
    fb_idx = 0
    while len(selected) < 7 and fb_idx < len(fallback_pool):
        cand = convert_to_loto_number(fallback_pool[fb_idx])
        if cand not in selected:
            selected.append(cand)
            log_details.append(f"予備枠: {cand:02d}")
        fb_idx += 1

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
# メイン画面 UI
# ==========================================
st.markdown("""
<div class="arsenal-header">
    <div style="display:flex; align-items:center; gap:10px;">
        <img src="https://ssl.gstatic.com/onebox/media/sports/logos/optimized/4us2nCgl6kgZc0t3hpW75Q_500x500.png" width="30" height="30" style="object-fit:contain;">
        <span style="font-size:18px; letter-spacing:0.5px;">GUNNERS LOTO 7</span>
    </div>
    <span style="background:rgba(0,0,0,0.3); padding:4px 10px; border-radius:20px; font-size:12px; border:1px solid #9C824A;">FotMob Live Sync</span>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["⚽ 試合 & ナンバー算出", "📊 シーズン収支管理"])

with tab1:
    fixtures, err = fetch_live_arsenal_fixtures()

    if err or not fixtures:
        st.error(f"⚠️ 公式スケジュールの通信待機中: {err if err else 'データを取得できませんでした'}")
        st.info("💡 FotMobから直接取得できない場合でも、下の手動入力からスコア・スタッツを即時計算できます。")
        fixtures = [{
            "match_id": "manual_entry",
            "label": "【手動入力モード】最新試合を入力",
            "tournament": "Premier League",
            "home": "Arsenal",
            "away": "Opponent",
            "h_score": 2,
            "a_score": 0,
            "is_finished": True,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "day": datetime.now().day,
            "fotmob_url": "https://www.fotmob.com/teams/9825/overview/arsenal"
        }]
    else:
        st.caption(f"🟢 FotMob公式サーバーと同期中（取得試合数: {len(fixtures)}試合）")

    # ② プルダウンで公式試合を選択
    fixture_labels = [f["label"] for f in fixtures]
    selected_idx = st.selectbox(
        "📅 公式試合を選択（FotMobリアルタイム同期）",
        range(len(fixture_labels)),
        format_func=lambda i: fixture_labels[i]
    )

    m = fixtures[selected_idx]
    is_finished = m["is_finished"]

    with st.expander("📝 試合スコア & ロト7連動スタッツ設定", expanded=True):
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            h_score_val = st.number_input("ホーム得点", min_value=0, value=m["h_score"] if m["h_score"] is not None else 0, key=f"hs_{m['match_id']}")
        with col_m2:
            a_score_val = st.number_input("アウェイ得点", min_value=0, value=m["a_score"] if m["a_score"] is not None else 0, key=f"as_{m['match_id']}")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            scorers_str = st.text_input("得点者 背番号（カンマ区切り）", value="7", key=f"sc_{m['match_id']}")
            assist_val = st.number_input("先制アシスト者 背番号", min_value=0, max_value=99, value=8, key=f"asst_{m['match_id']}")
            goal_time_val = st.number_input("先制ゴール時間（分）", min_value=1, max_value=120, value=25, key=f"gt_{m['match_id']}")
        with col_s2:
            passer_val = st.number_input("パス数1位 背番号", min_value=1, max_value=99, value=6, key=f"pass_{m['match_id']}")
            shots_val = st.number_input("チーム総シュート数", min_value=0, value=15, key=f"sh_{m['match_id']}")
            poss_val = st.number_input("ボール支配率 (%)", min_value=0, max_value=100, value=55, key=f"poss_{m['match_id']}")

    # 得失点差と口数判定
    is_ars_home = "arsenal" in m["home"].lower()
    ars_score = h_score_val if is_ars_home else a_score_val
    opp_score = a_score_val if is_ars_home else h_score_val
    gd = ars_score - opp_score

    has_result = is_finished or (h_score_val > 0 or a_score_val > 0)
    tickets = max(0, min(5, gd)) if (has_result and gd > 0) else 0
    cost = tickets * 300

    # スコアカード表示
    st.markdown(f"""
    <div class="match-card">
        <div style="display:flex; justify-content:space-between; font-size:12px; color:#94A3B8; margin-bottom:8px;">
            <span>{m['tournament']} (ID: {m['match_id']})</span>
            <span style="color:{'#34D399' if is_finished else '#F59E0B'}; font-weight:bold;">
                {'FT (試合終了)' if is_finished else 'キックオフ前'}
            </span>
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; margin:12px 0;">
            <div style="text-align:center; width:110px;">
                <div style="font-weight:bold; font-size:15px;">{m['home']}</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:36px; font-weight:900; letter-spacing:3px;">
                    {f"{h_score_val} - {a_score_val}" if has_result else "VS"}
                </div>
                <div style="font-size:11px; color:#94A3B8;">{m['date']}</div>
            </div>
            <div style="text-align:center; width:110px;">
                <div style="font-weight:bold; font-size:15px;">{m['away']}</div>
            </div>
        </div>
        <div class="badge-win">
            <span>🎯 得失点差: {'+' if gd > 0 else ''}{gd}点差</span>
            <span>🛒 購入口数: {tickets}口 ({cost:,}円)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.link_button("🔗 FotMob公式でこの試合の詳細を見る", m["fotmob_url"], use_container_width=True)

    # ロト7 採番
    current_match_stats = {
        "scorers": [int(s.strip()) for s in scorers_str.split(",") if s.strip().isdigit()],
        "assist": assist_val if assist_val > 0 else None,
        "goal_time": goal_time_val,
        "passer": passer_val,
        "shots": shots_val,
        "possession": poss_val,
        "match_day": m["day"],
        "top_defender": 2,
        "first_sub": 19
    }

    t2_key = f"t2_{m['match_id']}"
    if t2_key not in st.session_state:
        st.session_state[t2_key] = generate_ticket_2()
    t2_nums, t2_odd, t2_even, t2_total = st.session_state[t2_key]

    t3_key = f"t3_{m['match_id']}"
    if t3_key not in st.session_state:
        st.session_state[t3_key] = generate_ticket_qp()
    t3_nums = st.session_state[t3_key]

    if tickets > 0:
        t1, logs = generate_ticket_1(current_match_stats)

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
        copy_text = f"""【ロト7 購入シート】{m['home']} vs {m['away']}
購入口数: {tickets}口 ({cost:,}円)
1口目: {' '.join([f'{n:02d}' for n in t1])}"""
        if tickets >= 2:
            copy_text += f"\n2口目: {' '.join([f'{n:02d}' for n in t2_nums])}"
        if tickets >= 3:
            copy_text += f"\n3口目: {' '.join([f'{n:02d}' for n in t3_nums])} (QP)"

        st.markdown("**📋 購入用テキスト（右上のアイコンで1タップコピー）**")
        st.code(copy_text, language="text")

        if st.button("💾 この試合を購入履歴に保存", use_container_width=True):
            history = load_history()
            opp_name = m['away'] if is_ars_home else m['home']
            new_record = {
                "match_id": m["match_id"],
                "date": m["date"],
                "opponent": opp_name,
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
            st.success(f"「{m['home']} vs {m['away']}」の購入データを保存しました！")
    else:
        if has_result:
            st.info("引き分けまたは敗戦のため、ロト7の購入はありません（0口）。")
        else:
            st.info("キックオフ前です。試合終了後にスコアを入力して採番してください。")

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
                    if rec.get("ticket_2"):
                        st.write(f"2口目: {rec['ticket_2']}")
                with col_h2:
                    won_input = st.number_input(
                        f"当せん金額 (円)",
                        min_value=0,
                        step=1000,
                        value=rec.get("hit_amount", 0),
                        key=f"won_{idx}_{rec.get('match_id', idx)}"
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
