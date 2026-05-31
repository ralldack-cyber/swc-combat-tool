import streamlit as st
import pandas as pd

st.set_page_config(page_title="SWC Combat Optimiser", layout="wide")

# -----------------------------------
# WEAPON DATA
# -----------------------------------
weapons = {
    "A280": (9,5,13,4,14,3,15,55),
    "A295": (7,3,11,2,12,1,13,5),
    "Amban Sniper Rifle": (13,9,17,8,18,7,19,45),
    "AXM-50": (4,0,8,0,9,0,10,5),
    "Bowcaster": (5,1,9,0,10,0,11,12.5),
    "Bryar Pistol": (2,2,2,1,3,0,4,5),
    "Bryar Rifle": (3,3,3,2,4,1,5,6.5),
    "DC-15A": (9,5,13,4,14,3,15,19),
    "DL-44": (2,2,2,1,3,0,4,10.5),
    "DLT-20a": (4,0,8,0,9,0,10,8.5),
    "E-11": (5,1,9,0,10,0,11,6),
    "HB-5": (5,1,9,0,10,0,11,9),
    "Nightstinger": (13,10,16,9,17,8,18,67),
    "Valken-38": (6,2,10,1,11,0,12,7),
    "X-45": (13,9,17,8,18,7,19,65),
}

ranges = list(range(20))

# -----------------------------------
# CURVE FUNCTION
# -----------------------------------
def curve(opt,r75l,r75h,r50l,r50h,r25l,r25h):
    vals=[]
    for r in ranges:
        if r==opt:
            vals.append(100); continue
        if r<r25l or r>r25h:
            vals.append(0); continue

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

# -----------------------------------
# BUILD EXPECTED DAMAGE TABLE
# -----------------------------------
exp_data = {}
for w,(opt,r75l,r75h,r50l,r50h,r25l,r25h,avg) in weapons.items():
    vals = curve(opt,r75l,r75h,r50l,r50h,r25l,r25h)
    exp_data[w] = [v/100 * avg for v in vals]

exp_df = pd.DataFrame(exp_data, index=ranges)

# -----------------------------------
# UI
# -----------------------------------
st.title("⚔️ SWC Combat Optimiser")

tab1, tab2 = st.tabs(["⚙️ Setup", "📊 Results"])

# -----------------------------------
# SETUP TAB
# -----------------------------------
with tab1:

    col1, col2 = st.columns(2)

    # YOUR SQUAD
    with col1:
        st.subheader("Your Squad")
        your_weapon = st.selectbox("Weapon (12 units)", list(weapons.keys()))

    # ENEMY SQUAD
    with col2:
        st.subheader("Enemy Squad Builder")

        if "enemy" not in st.session_state:
            st.session_state.enemy = [["","","",""] for _ in range(12)]

        # PRESETS
        st.markdown("### Presets")
        p1,p2,p3,p4 = st.columns(4)

        if p1.button("Snipers"):
            st.session_state.enemy = [["X-45","","",""] for _ in range(12)]
        if p2.button("Carbines"):
            st.session_state.enemy = [["Valken-38","","",""] for _ in range(12)]
