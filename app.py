import streamlit as st
import pandas as pd
import sqlite3
from database import init_db, get_connection

# Inicializa banco de dados SQLite
init_db()

# Configuração da página para mobile
st.set_page_config(
    page_title="Roteiro Europa",
    page_icon="✈️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilização CSS Mobile-First
st.markdown("""
<style>
    /* Ajustes globais para telas pequenas */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.6rem !important;
        padding-right: 0.6rem !important;
        max-width: 100% !important;
    }
    
    /* Header Estilo Passaporte Mobile */
    .main-title {
        background: linear-gradient(135deg, #1B2A41 0%, #0F172A 100%);
        color: #F7F3E9;
        padding: 18px 16px;
        border-radius: 14px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .badge-gold {
        color: #C9A227;
        font-family: monospace;
        font-size: 11px;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    
    /* Cards de Estatísticas Responsivos */
    .mobile-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 8px;
    }
    
    .mobile-card-title {
        font-size: 11px;
        color: #64748B;
        text-transform: uppercase;
        font-weight: 600;
    }
    
    .mobile-card-value {
        font-size: 16px;
        font-weight: 700;
        color: #1E293B;
        font-family: monospace;
    }

    div[data-testid="stExpander"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        margin-bottom: 8px !important;
        background-color: #FFFFFF !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Cores e Estilos por Cidade
CITY_STYLE = {
    "Trânsito":  {"bg": "#EDECE6", "text": "#5A5A52"},
    "Praga":     {"bg": "#E1EEEE", "text": "#1F5658"},
    "Cracóvia":  {"bg": "#EBE4F0", "text": "#573C68"},
    "Budapeste": {"bg": "#F7ECD6", "text": "#8E6A21"},
    "Viena":     {"bg": "#E1EBE3", "text": "#2E5637"},
    "Liubliana": {"bg": "#F1E3DA", "text": "#7E4931"},
    "Londres":   {"bg": "#F0DEE3", "text": "#602E3A"},
}

# --- FUNÇÕES DE BANCO DE DADOS (CRUD) ---
def load_data():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM dias", conn)
    configs = pd.read_sql_query("SELECT * FROM config", conn).set_index("chave")["valor"].to_dict()
    conn.close()
    return df, configs

def update_val(day_id, col, val):
    conn = get_connection()
    c = conn.cursor()
    c.execute(f"UPDATE dias SET {col} = ? WHERE id = ?", (val, day_id))
    conn.commit()
    conn.close()

def update_config(chave, val):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO config (chave, valor) VALUES (?, ?)", (chave, float(val)))
    conn.commit()
    conn.close()

def add_new_day(new_id, dia, data, dow, cidade, atividade):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO dias (id, dia, data, dow, cidade, atividade, hospedagem_val, transporte_val, alimentacao_val, passeio_val)
        VALUES (?, ?, ?, ?, ?, ?, 0, 0, 0, 0)
    ''', (new_id, dia, data, dow, cidade, atividade))
    conn.commit()
    conn.close()

def delete_day(day_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM dias WHERE id = ?", (day_id,))
    conn.commit()
    conn.close()

# Carregamento dos dados
df, configs = load_data()
rate = configs.get("rate", 5.4)
extra_food_usd = configs.get("extra_food_usd", 1465.0)
extra_food_pago = bool(configs.get("extra_food_pago", 0))

# --- HEADER COMPACTO MOBILE ---
st.markdown("""
<div class="main-title">
    <div class="badge-gold">21 DIAS · EUROPA 2026</div>
    <h2 style="margin:2px 0 0 0; color:#F7F3E9; font-size:22px;">Roteiro de Viagem</h2>
    <p style="color:#B9C3D6; margin:4px 0 0 0; font-size:12px;">Praga → Cracóvia → Budapeste → Viena → Liubliana → Londres</p>
</div>
""", unsafe_allow_html=True)

# --- CÁLCULOS GERAIS ---
tot_hosp = df["hospedagem_val"].sum()
tot_transp = df["transporte_val"].sum()
tot_passeio = df["passeio_val"].sum()
tot_food_usd = df["alimentacao_val"].sum()
tot_food_brl = tot_food_usd * rate
extra_food_brl = extra_food_usd * rate

total_geral = tot_hosp + tot_transp + tot_passeio + tot_food_brl + extra_food_brl
total_por_pessoa = total_geral / 2

pago_hosp = df[df["hospedagem_pago"] == 1]["hospedagem_val"].sum()
pago_transp = df[df["transporte_pago"] == 1]["transporte_val"].sum()
pago_passeio = df[df["passeio_pago"] == 1]["passeio_val"].sum()
pago_food_brl = df[df["alimentacao_pago"] == 1]["alimentacao_val"].sum() * rate
pago_extra_food_brl = extra_food_brl if extra_food_pago else 0.0

total_pago = pago_hosp + pago_transp + pago_passeio + pago_food_brl + pago_extra_food_brl
total_pendente = max(0.0, total_geral - total_pago)
pct_pago = int((total_pago / total_geral * 100)) if total_geral > 0 else 0

# --- PAINEL DE RESUMO RETRÁTIL ---
with st.expander("📊 **Resumo Financeiro & Cotação**", expanded=False):
    col_rate, col_extra = st.columns([1, 1])
    with col_rate:
        new_rate = st.number_input("Cotação (USD)", value=rate, step=0.05, format="%.2f")
        if new_rate != rate:
            update_config("rate", new_rate)
            st.rerun()
            
    with col_extra:
        st.caption(f"Extra Alimentação: US$ {extra_food_usd:,.0f}")
        chk_extra = st.checkbox("Pago (Extra)", value=extra_food_pago)
        if chk_extra != extra_food_pago:
            update_config("extra_food_pago", 1 if chk_extra else 0)
            st.rerun()

    st.markdown("---")
    
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"""<div class="mobile-card"><div class="mobile-card-title">Hospedagem</div><div class="mobile-card-value">R$ {tot_hosp:,.2f}</div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="mobile-card"><div class="mobile-card-title">Alimentação</div><div class="mobile-card-value">US$ {tot_food_usd:,.0f}</div></div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="mobile-card"><div class="mobile-card-title">Transporte</div><div class="mobile-card-value">R$ {tot_transp:,.2f}</div></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="mobile-card"><div class="mobile-card-title">Passeios</div><div class="mobile-card-value">R$ {tot_passeio:,.2f}</div></div>""", unsafe_allow_html=True)

# --- CARD TOTAL DE DESTAQUE ---
st.markdown(f"""
<div style="background-color: #1E293B; color: white; padding: 14px; border-radius: 12px; margin-bottom: 12px;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span style="font-size: 10px; color: #94A3B8; letter-spacing: 1px;">TOTAL GERAL</span>
            <div style="font-size: 20px; font-weight: bold; color: #F8FAFC;">R$ {total_geral:,.2f}</div>
        </div>
        <div style="text-align: right;">
            <span style="font-size: 10px; color: #94A3B8;">POR PESSOA</span>
            <div style="font-size: 15px; font-weight: 600; color: #38BDF8;">R$ {total_por_pessoa:,.2f}</div>
        </div>
    </div>
    <div style="margin-top: 10px;">
        <div style="display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 4px;">
            <span style="color: #4ADE80;">Pago: R$ {total_pago:,.2f} ({pct_pago}%)</span>
            <span style="color: #F87171;">Pendente: R$ {total_pendente:,.2f}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.progress(pct_pago / 100)

# --- FILTROS COMPACTOS ---
col_f1, col_f2 = st.columns([1.2, 1])
with col_f1:
    cidades = ["Todas"] + list(CITY_STYLE.keys())
    cidade_selected = st.selectbox("Filtrar Cidade", cidades, label_visibility="collapsed")
with col_f2:
    apenas_pendentes = st.checkbox("Só pendentes", value=False)

df_filtered = df.copy()
if cidade_selected != "Todas":
    df_filtered = df_filtered[df_filtered["cidade"] == cidade_selected]

if apenas_pendentes:
    def tem_pendencia(row):
        cond_h = row["hospedagem_val"] > 0 and row["hospedagem_pago"] == 0
        cond_t = row["transporte_val"] > 0 and row["transporte_pago"] == 0
        cond_a = row["alimentacao_val"] > 0 and row["alimentacao_pago"] == 0
        cond_p = row["passeio_val"] > 0 and row["passeio_pago"] == 0
        return cond_h or cond_t or cond_a or cond_p
    df_filtered = df_filtered[df_filtered.apply(tem_pendencia, axis=1)]

st.caption(f"Exibindo **{len(df_filtered)}** dia(s)")

# --- LISTAGEM DOS DIAS (COM EDIÇÃO DE ATIVIDADE E CUSTOS) ---
for idx, row in df_filtered.iterrows():
    day_total_brl = row['hospedagem_val'] + row['transporte_val'] + row['passeio_val'] + (row['alimentacao_val'] * rate)
    
    val_items = [
        (row['hospedagem_val'], row['hospedagem_pago']),
        (row['transporte_val'], row['transporte_pago']),
        (row['alimentacao_val'], row['alimentacao_pago']),
        (row['passeio_val'], row['passeio_pago'])
    ]
    active_items = [item for item in val_items if item[0] > 0]
    paid_items = [item for item in active_items if item[1] == 1]
    
    if len(active_items) == 0:
        status_icon = "⚪"
    elif len(paid_items) == len(active_items):
        status_icon = "🟢"
    elif len(paid_items) > 0:
        status_icon = "🟡"
    else:
        status_icon = "🔴"

    header_title = f"{status_icon} D{row['dia']} · {row['cidade']} | R$ {day_total_brl:,.0f}"

    with st.expander(header_title):
        st.caption(f"📅 **Data:** {row['data']} ({row['dow'].upper()})")
        
        # --- CAMPO DE EDIÇÃO DA ATIVIDADE/ROTEIRO ---
        new_atividade = st.text_area("✏️ **Roteiro / Atividades do Dia:**", value=row['atividade'], key=f"ativ_{row['id']}", height=80)
        if new_atividade != row['atividade']:
            update_val(row['id'], "atividade", new_atividade)
            st.rerun()

        # Checkbox Reservado
        is_res = st.checkbox("📌 Marcado como Reservado", value=bool(row["reservado"]), key=f"res_{row['id']}")
        if is_res != bool(row["reservado"]):
            update_val(row['id'], "reservado", 1 if is_res else 0)
            st.rerun()

        st.divider()
        st.caption("💰 **Custos do Dia & Pagamentos**")

        g1, g2 = st.columns(2)
        # Hospedagem
        with g1:
            h_val = st.number_input("Hospedagem (R$)", value=float(row["hospedagem_val"]), key=f"hv_{row['id']}")
            h_pago = st.checkbox("Pago", value=bool(row["hospedagem_pago"]), key=f"hp_{row['id']}")
            if h_val != row["hospedagem_val"]:
                update_val(row['id'], "hospedagem_val", h_val)
                st.rerun()
            if h_pago != bool(row["hospedagem_pago"]):
                update_val(row['id'], "hospedagem_pago", 1 if h_pago else 0)
                st.rerun()

        # Transporte
        with g2:
            t_val = st.number_input("Transporte (R$)", value=float(row["transporte_val"]), key=f"tv_{row['id']}")
            t_pago = st.checkbox("Pago ", value=bool(row["transporte_pago"]), key=f"tp_{row['id']}")
            if t_val != row["transporte_val"]:
                update_val(row['id'], "transporte_val", t_val)
                st.rerun()
            if t_pago != bool(row["transporte_pago"]):
                update_val(row['id'], "transporte_pago", 1 if t_pago else 0)
                st.rerun()

        g3, g4 = st.columns(2)
        # Alimentação
        with g3:
            a_val = st.number_input("Alimentação (US$)", value=float(row["alimentacao_val"]), key=f"av_{row['id']}")
            a_pago = st.checkbox("Pago  ", value=bool(row["alimentacao_pago"]), key=f"ap_{row['id']}")
            if a_val != row["alimentacao_val"]:
                update_val(row['id'], "alimentacao_val", a_val)
                st.rerun()
            if a_pago != bool(row["alimentacao_pago"]):
                update_val(row['id'], "alimentacao_pago", 1 if a_pago else 0)
                st.rerun()

        # Passeios
        with g4:
            p_val = st.number_input("Passeios (R$)", value=float(row["passeio_val"]), key=f"pv_{row['id']}")
            p_pago = st.checkbox("Pago   ", value=bool(row["passeio_pago"]), key=f"pp_{row['id']}")
            if p_val != row["passeio_val"]:
                update_val(row['id'], "passeio_val", p_val)
                st.rerun()
            if p_pago != bool(row["passeio_pago"]):
                update_val(row['id'], "passeio_pago", 1 if p_pago else 0)
                st.rerun()

        # Campo de edição de observações extras
        new_obs = st.text_input("📝 Observações:", value=row['obs'] if row['obs'] else "", key=f"obs_{row['id']}")
        if new_obs != (row['obs'] if row['obs'] else ""):
            update_val(row['id'], "obs", new_obs)
            st.rerun()

        # Botão de exclusão do dia
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Excluir este dia", key=f"del_{row['id']}", type="secondary"):
            delete_day(row['id'])
            st.rerun()

# --- ADICIONAR NOVO DIA AO ROTEIRO ---
st.divider()
with st.expander("➕ **Adicionar Novo Dia ao Roteiro**"):
    with st.form("form_add_day"):
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            n_dia = st.text_input("Número do Dia (ex: 21)")
            n_data = st.text_input("Data (ex: 23/11)")
        with col_a2:
            n_dow = st.text_input("Dia da Semana (ex: seg)")
            n_cidade = st.selectbox("Cidade", list(CITY_STYLE.keys()))
        
        n_ativ = st.text_area("Atividade / Roteiro inicial")
        btn_salvar = st.form_submit_button("Salvar Novo Dia")
        
        if btn_salvar and n_dia and n_data:
            new_id = f"d{n_dia}_{n_cidade.lower()}"
            add_new_day(new_id, n_dia, n_data, n_dow, n_cidade, n_ativ)
            st.success("Novo dia adicionado com sucesso!")
            st.rerun()