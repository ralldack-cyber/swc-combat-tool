import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SWC Combat Optimiser", layout="wide")

# -------------------------
# FULL WEAPON DATA
# -------------------------
weapons = {
    "A280": (9,5,13,4,14,3,15,55),
    "A295": (7,3,11,2,12,1,13,5),
    "Amban Sniper Rifle": (13,9,17,8,18,7,19,45),
    "AXM-50": (4,0,8,0,9,0,10,5),
    "Bowcaster": (5,1,9,0,10,0,11,12.5),
    "Bryar Pistol": (2,2,2,1,3,0,4,5),
    "Bryar Rifle": (3,3,3,2,4,1,5,6.5),
    "DC-15A": (9,5,13,4,14,3,15,19),
    "DC-15S": (3,0,6,0,7,0,8,10.5),
    "DL-18": (2,2,2,1,3,0,4,8),
    "DL-44": (2,2,2,1,3,0,4,10.5),
    "DLT-20a": (4,0,8,0,9,0,10,8.5),
    "E-11": (5,1,9,0,10,0,11,6),
    "E-11B": (5,1,9,0,10,0,11,8.5),
    "EE-3": (4,0,8,0,9,0,10,5),
    "HB-5": (5,1,9,0,10,0,11,9),
    "Nightstinger": (13,10,16,9,17,8,18,67),
    "Valken-38": (6,2,10,1,11,0,12,7),
    "X-45": (13,9,17,8,18,7,19,65),
}

ranges = list(range(20))

# -------------------------
# CURVE FUNCTION
# -------------------------
def curve(opt,r75l,r75h,r50l,r50h,r25l,r25h):
    vals=[]
    for r in ranges:
        if r==opt:
            vals.append(100)
            continue
        if r<r25l or r>r25h:
            vals.append(0)
            continue

        if r75l<=r<=r75h:
            if r<opt:
                x1,x2,y1,y2 = r75l,opt,75,100
            else:
                x1,x2,y1,y2 = opt,r75h,100,75

        elif r50l<=r<=r50h:
            if r<r75l:
                x1,x2,y1,y2 = r50l,r75l,50,75
            else:
                x1,x2,y1,y2 = r75h,r50h,75,50
        else:
            if r<r50l:
                x1,x2,y1,y2 = r25l,r50l,25,50
            else:
                x1,x2,y1,y2 = r50h,r25h,50,25

        val = y2 if x1==x2 else y1+(y2-y1)*(r-x1)/(x2-x1)
        vals.append(val)
    return vals

# -------------------------
# BUILD EXPECTED TABLE
# -------------------------
exp_data = {}
for w,(opt,r75l,r75h,r50l,r50h,r25l,r25h,avg) in weapons.items():
    hit = curve(opt,r75l,r75h,r50l,r50h,r25l,r25h)
    exp = [h/100 * avg for h in hit]
    exp_data[w] = exp

exp_df = pd.DataFrame(exp_data, index=ranges)

# -------------------------
# UI
# -------------------------
st.title("⚔️ SWC Combat Optimiser")

col1, col2 = st.columns(2)

# YOUR SQUAD
with col1:
    st.header("Your Squad")
    your_weapon = st.selectbox("Weapon (applied to all 12)", list(weapons.keys()))

# ENEMY SQUAD
with col2:
    st.header("Enemy Squad (Primary / Secondary / Tertiary)")

enemy_slots = []
for i in range(12):
    c1,c2,c3 = st.columns(3)
    w1 = c1.selectbox("Primary", [""] + list(weapons.keys()), key=f"p{i}")
    w2 = c2.selectbox("Secondary", [""] + list(weapons.keys()), key=f"s{i}")
    w3 = c3.selectbox("Tertiary", [""] + list(weapons.keys()), key=f"t{i}")
    enemy_slots.append([w1,w2,w3])

# -------------------------
# CALCULATIONS
# -------------------------
your_total = exp_df[your_weapon] * 12
enemy_total = pd.Series([0]*20, index=ranges)

for unit in enemy_slots:
    for w in unit:
        if w:
            enemy_total += exp_df[w]

net = your_total - enemy_total

# -------------------------
# RESULTS
# -------------------------
best_range = int(net.idxmax())

st.markdown(f"# ✅ Optimal Range: **{best_range}**")

chart_df = pd.DataFrame({
    "Your Damage": your_total,
    "Enemy Damage": enemy_total,
    "Net": net
})

st.line_chart(chart_df)

# Highlight best
styled = chart_df.style.apply(
    lambda row: ['background-color: #C6EFCE' if row.name == best_range else '' for _ in row],
    axis=1
)

st.dataframe(styled)
