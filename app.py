import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime
import base64

# --- 1. CONFIGURAÇÃO DA PÁGINA E CSS GERAL ---
st.set_page_config(
    page_title="Gestão de Alarmes - Jovi Mobile", 
    layout="wide", 
    page_icon="🚨"
)

# CSS Personalizado
st.markdown("""
<style>
    /* ============================================================
       SIDEBAR & MENU
       ============================================================ */
    
    .stRadio > div[role="radiogroup"] > label > div:first-child {
        display: none;
    }

    .stRadio > div[role="radiogroup"] > label {
        background-color: transparent;
        padding: 12px 20px;
        border-radius: 8px;
        margin-bottom: 6px;
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid transparent;
        display: flex;
        align-items: center;
        color: var(--text-color);
    }
    
    .stRadio > div[role="radiogroup"] > label:hover {
        background-color: rgba(128, 128, 128, 0.1);
        border-color: rgba(128, 128, 128, 0.3);
    }
    
    .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #e8f0fe;
        color: #1976d2 !important;
        font-weight: bold;
        border: 1px solid #d0e2ff;
    }
    
    /* Card de Perfil */
    .profile-card {
        background-color: rgba(255, 255, 255, 0.05);        
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .profile-avatar {
        width: 70px; 
        height: 70px; 
        border-radius: 50%; 
        margin-bottom: 10px;
        border: 2px solid #1976d2;
    }
    
    .profile-name { 
        font-weight: bold; 
        color: var(--text-color); 
        font-size: 16px; 
        margin-bottom: 4px; 
    }
    
    .profile-sub { 
        font-size: 12px; 
        color: var(--text-color); 
        opacity: 0.7; 
    }
    
    .admin-badge {
        background-color: rgba(255, 75, 75, 0.2);
        color: #ff4b4b;
        padding: 5px 12px; 
        border-radius: 15px;
        font-size: 11px; 
        font-weight: bold; 
        border: 1px solid #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)

# --- DEFINIÇÃO DOS SUPER ADMINS ---
ADMIN_EMAILS = [
    "douglas.oliveira@jovimobile.com",
    "diego.dantas@jovimobile.com"
]

# --- 2. SISTEMA DE LOGIN E SESSÃO ---
def check_session():
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False
        st.session_state['usuario_atual'] = ''

def login_screen():
    def get_base64_image(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except FileNotFoundError:
            return ""

    bg_page_img = get_base64_image("transferir (9).jpg")
    bg_container_img = get_base64_image("j.png")
    bg_input_img = get_base64_image("image_d9a9c9.png")
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{bg_page_img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .main-container {{
            max-width: 450px;
            margin: auto;
            padding: 80px;
            background-image: linear-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.1)), url("data:image/png;base64,{bg_container_img}");
            animation: slideIn 1.2s ease-out;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        
        /* --- CORREÇÃO DO INPUT --- */
        .stTextInput input {{
            background-image: url("data:image/png;base64,{bg_input_img}") !important;
            background-size: 100% 100% !important;
            background-color: transparent !important;
            border: none !important;
            
            /* MUDANÇA AQUI: Cor escura (#31333F) para contrastar com fundo branco */
            color: #31333F !important;
            caret-color: #31333F !important; /* Cor do cursor piscando */
            
            padding: 15px 20px !important;
            height: 50px !important;
            border-radius: 15px !important;
        }}
        
        /* Cor do placeholder (texto de dica) também escuro */
        .stTextInput input::placeholder {{
            color: rgba(49, 51, 63, 0.6) !important;
        }}
        
        .stTextInput label {{ color: white !important; font-size: 14px; margin-bottom: 5px; }}
        h1, h3 {{ color: white !important; text-align: center; text-shadow: 0 2px 4px rgba(0,0,0,0.5); }}
        
        /* Botão Entrar Personalizado para Primary */
        .stButton button {{
            background-color: var(--primary-color) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            border-radius: 12px;
            height: 45px;
            font-weight: bold;
            width: 100% !important;
            transition: all 0.3s ease;
            text-transform: uppercase;
        }}
        .stButton button:hover {{
            filter: brightness(1.1);
            transform: scale(1.02);
            border-color: white !important;
        }}
        
        @keyframes slideIn {{ from {{ opacity: 0; transform: translateY(30px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        </style>
        """, unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("")
        st.write("")
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        st.title("🔐 Acesso")
        st.markdown("<h3 style='margin-bottom: 30px;'>Controle de Alarmes</h3>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            email = st.text_input("E-mail", placeholder="seu.email@jovimobile.com")
            senha = st.text_input("Senha", type="password", placeholder="******") 
            st.markdown("<br>", unsafe_allow_html=True)
            
            submit = st.form_submit_button("ENTRAR", type="primary", use_container_width=True)
            
            if submit:
                email_limpo = email.strip().lower()
                if email_limpo.endswith("@jovimobile.com"):
                    st.session_state['logado'] = True
                    st.session_state['usuario_atual'] = email_limpo
                    st.success(f"Bem-vindo(a), {email_limpo}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("🚫 Acesso negado. Domínio inválido.")
        st.markdown('</div>', unsafe_allow_html=True)

def logout():
    st.session_state['logado'] = False
    st.session_state['usuario_atual'] = ''
    st.rerun()

# --- 3. SISTEMA PRINCIPAL (PÓS-LOGIN) ---
def main_system():
    
    # --- BANCO DE DADOS ---
    def get_connection():
        return sqlite3.connect('alarmes.db')

    def init_db():
        conn = get_connection()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS lojas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome_loja TEXT UNIQUE,
                        estoque_atual INTEGER
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS ocorrencias (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        loja_id INTEGER,
                        quantidade INTEGER,
                        motivo TEXT,
                        tipo TEXT, 
                        status TEXT DEFAULT 'CONCLUIDO',
                        id_vinculado INTEGER,
                        data_registro TIMESTAMP,
                        usuario TEXT,
                        FOREIGN KEY(loja_id) REFERENCES lojas(id)
                    )''')
        c.execute('''CREATE TABLE IF NOT EXISTS permissoes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT,
                        loja_id INTEGER,
                        FOREIGN KEY(loja_id) REFERENCES lojas(id),
                        UNIQUE(email, loja_id)
                    )''')
        
        cols_check = [("usuario", "TEXT"), ("tipo", "TEXT"), ("status", "TEXT DEFAULT 'CONCLUIDO'"), ("id_vinculado", "INTEGER")]
        for col, tipo in cols_check:
            try: c.execute(f"ALTER TABLE ocorrencias ADD COLUMN {col} {tipo}")
            except: pass
            
        conn.commit()
        return conn

    conn = init_db()
    c = conn.cursor()

    # --- FUNÇÕES LEITURA ---
    def get_lojas_permitidas():
        u = st.session_state['usuario_atual']
        if u in ADMIN_EMAILS:
            return pd.read_sql("SELECT id, nome_loja, estoque_atual FROM lojas", conn)
        else:
            return pd.read_sql("SELECT l.id, l.nome_loja, l.estoque_atual FROM lojas l JOIN permissoes p ON l.id = p.loja_id WHERE p.email = ?", conn, params=(u,))

    def get_todas_ocorrencias():
        return pd.read_sql("SELECT o.id, l.nome_loja, o.quantidade, o.motivo, o.data_registro, o.status, o.usuario FROM ocorrencias o JOIN lojas l ON o.loja_id = l.id WHERE o.tipo = 'SAIDA'", conn)

    def get_chamados_pendentes(lid=None):
        q = "SELECT o.id, l.nome_loja, o.quantidade, o.motivo, o.data_registro, o.usuario FROM ocorrencias o JOIN lojas l ON o.loja_id = l.id WHERE o.tipo = 'SAIDA' AND o.status = 'PENDENTE'"
        if lid: q += f" AND o.loja_id = {lid}"
        return pd.read_sql(q, conn)

    def get_historico_solucoes():
        query = """
            SELECT 
                strftime('%d/%m %H:%M', solucao.data_registro) as data_solucao,
                l.nome_loja, 
                solucao.quantidade as qtd_reposta, 
                problema.motivo as problema_original, 
                solucao.motivo as solucao_detalhe,
                solucao.usuario as responsavel_solucao 
            FROM ocorrencias solucao 
            JOIN ocorrencias problema ON solucao.id_vinculado = problema.id 
            JOIN lojas l ON solucao.loja_id = l.id 
            WHERE solucao.tipo = 'ENTRADA' 
            ORDER BY solucao.data_registro DESC
        """
        return pd.read_sql(query, conn)

    # --- FUNÇÕES AÇÃO ---
    def cadastrar_loja(n, q):
        try:
            c.execute("INSERT INTO lojas (nome_loja, estoque_atual) VALUES (?, ?)", (n, q))
            conn.commit()
            st.toast("✅ Loja Criada!")
            time.sleep(1); st.rerun()
        except: st.error("Loja já existe.")

    def remover_loja(nome):
        c.execute("SELECT id FROM lojas WHERE nome_loja = ?", (nome,))
        res = c.fetchone()
        if res:
            lid = res[0]
            for t in ['ocorrencias', 'permissoes', 'lojas']:
                col = 'loja_id' if t != 'lojas' else 'id'
                c.execute(f"DELETE FROM {t} WHERE {col} = ?", (lid,))
            conn.commit()
            st.toast("🗑️ Removido!"); time.sleep(1); st.rerun()

    def reduzir_estoque_admin(loja, qtd, mot):
        c.execute("SELECT id, estoque_atual FROM lojas WHERE nome_loja = ?", (loja,))
        d = c.fetchone()
        if d:
            lid, est = d
            if est >= qtd:
                c.execute("INSERT INTO ocorrencias (loja_id, quantidade, motivo, tipo, status, data_registro, usuario) VALUES (?,?,?, 'AJUSTE_ADM', 'CONCLUIDO', ?, ?)", (lid, qtd, mot, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state['usuario_atual']))
                c.execute("UPDATE lojas SET estoque_atual = ? WHERE id = ?", (est-qtd, lid))
                conn.commit()
                st.success("✅ Ajuste OK"); time.sleep(1); st.rerun()
            else: st.error("Estoque Baixo.")

    def vincular_usuario(e, l):
        c.execute("SELECT id FROM lojas WHERE nome_loja = ?", (l,))
        res = c.fetchone()
        if res:
            try:
                c.execute("INSERT INTO permissoes (email, loja_id) VALUES (?, ?)", (e.strip().lower(), res[0]))
                conn.commit(); st.success("OK")
            except: st.warning("Já existe")

    def desvincular_usuario(pid):
        c.execute("DELETE FROM permissoes WHERE id = ?", (pid,))
        conn.commit(); st.rerun()

    def abrir_chamado(l, q, m):
        c.execute("SELECT id, estoque_atual FROM lojas WHERE nome_loja = ?", (l,))
        d = c.fetchone()
        if d:
            lid, est = d
            if est >= q:
                c.execute("INSERT INTO ocorrencias (loja_id, quantidade, motivo, tipo, status, data_registro, usuario) VALUES (?,?,?, 'SAIDA', 'PENDENTE', ?, ?)", (lid, q, m, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state['usuario_atual']))
                c.execute("UPDATE lojas SET estoque_atual = ? WHERE id = ?", (est-q, lid))
                conn.commit(); st.toast("🚨 Chamado!"); time.sleep(1); st.rerun()
            else: st.error("Estoque Baixo.")

    def resolver_chamado(id_o, q, obs):
        c.execute("SELECT loja_id FROM ocorrencias WHERE id = ?", (id_o,))
        res = c.fetchone()
        if res:
            lid = res[0]
            c.execute("SELECT estoque_atual FROM lojas WHERE id = ?", (lid,))
            est = c.fetchone()[0]
            mot = f"{obs}"
            c.execute("INSERT INTO ocorrencias (loja_id, quantidade, motivo, tipo, status, id_vinculado, data_registro, usuario) VALUES (?,?,?, 'ENTRADA', 'CONCLUIDO', ?, ?, ?)", (lid, q, mot, id_o, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), st.session_state['usuario_atual']))
            c.execute("UPDATE ocorrencias SET status = 'RESOLVIDO' WHERE id = ?", (id_o,))
            c.execute("UPDATE lojas SET estoque_atual = ? WHERE id = ?", (est+q, lid))
            conn.commit(); st.success("✅ Resolvido!"); time.sleep(1); st.rerun()

    # --- SIDEBAR ---
    with st.sidebar:
        user = st.session_state['usuario_atual']
        nome_display = user.split('@')[0].title() if user else "Visitante"
        avatar_url = f"https://ui-avatars.com/api/?name={nome_display}&background=e8f0fe&color=1976d2&size=128"
        
        st.markdown(f"""
            <div class="profile-card">
                <img src="{avatar_url}" class="profile-avatar">
                <div class="profile-name">{nome_display}</div>
                <div class="profile-sub">Jovi Mobile</div>
            </div>
        """, unsafe_allow_html=True)

        if user in ADMIN_EMAILS:
            st.markdown('<div style="text-align: center; margin-bottom: 15px;"><span class="admin-badge">🛡️ ADMINISTRADOR</span></div>', unsafe_allow_html=True)

        st.markdown("---")
        
        opts = {
            "📊 Painel de Chamados": "Painel de Chamados",
            "🏭 Estoque Atual": "Estoque Atual",
            "🔥 Reportar Queima": "Abrir Chamado (Queima)",
            "📦 Repor Estoque": "Resolver Chamado (Reposição)"
        }
        
        if user in ADMIN_EMAILS:
            opts["⚙️ Administração"] = "ADMINISTRAÇÃO"
            
        sel = st.radio("Navegação", list(opts.keys()), label_visibility="collapsed")
        menu = opts[sel]

        st.markdown("---")
        if st.button("🚪 Sair / Logout", use_container_width=True):
            logout()

    # --- CONTEÚDO DAS PÁGINAS ---
    if menu == "Painel de Chamados":
        st.title("📊 Monitoramento de Chamados")
        df_my = get_lojas_permitidas()
        lst = df_my['nome_loja'].tolist()
        
        df_all = get_todas_ocorrencias()
        if user not in ADMIN_EMAILS: 
            df_all = df_all[df_all['nome_loja'].isin(lst)]
        
        if not df_all.empty:
            k1, k2, k3 = st.columns(3)
            k1.metric("Total de Ocorrências", len(df_all))
            k2.metric("Resolvidos", len(df_all[df_all['status']=='RESOLVIDO']))
            k3.metric("Pendentes", len(df_all[df_all['status']=='PENDENTE']), delta_color="inverse")
            
            st.markdown("---")
            g1, g2 = st.columns(2)
            with g1: 
                st.caption("Status Geral")
                st.bar_chart(df_all['status'].value_counts(), use_container_width=True)
            with g2: 
                st.caption("Ocorrências por Loja")
                if not df_all.empty: st.bar_chart(df_all['nome_loja'].value_counts(), use_container_width=True)
        else: st.info("Sem registros no momento.")
        
        st.divider()
        
        col_pend, col_solucao = st.columns(2)
        
        df_p = get_chamados_pendentes()
        df_s = get_historico_solucoes()
        
        if user not in ADMIN_EMAILS: 
            df_p = df_p[df_p['nome_loja'].isin(lst)]
            df_s = df_s[df_s['nome_loja'].isin(lst)]
        
        with col_pend:
            st.subheader("🔴 Pendentes")
            if not df_p.empty:
                st.dataframe(df_p[['id','nome_loja','quantidade','motivo']], use_container_width=True, hide_index=True)
            else: 
                st.success("Nada pendente.")
            
        with col_solucao:
            st.subheader("🟢 Histórico de Soluções")
            if not df_s.empty:
                st.dataframe(
                    df_s[['data_solucao', 'nome_loja', 'problema_original', 'solucao_detalhe', 'responsavel_solucao']], 
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "data_solucao": st.column_config.TextColumn("Quando", width="small"),
                        "nome_loja": "Loja",
                        "problema_original": "Problema",
                        "solucao_detalhe": "Solução/Obs",
                        "responsavel_solucao": "Resp."
                    }
                )
            else: st.info("Nenhuma solução registrada.")

    elif menu == "Estoque Atual":
        st.title("🏭 Estoque")
        df = get_lojas_permitidas()
        if not df.empty:
            st.bar_chart(df.set_index('nome_loja')['estoque_atual'], use_container_width=True)
            st.dataframe(df[['nome_loja','estoque_atual']].style.map(lambda x: 'background-color: rgba(255,0,0,0.2)' if x<10 else '', subset=['estoque_atual']), use_container_width=True)
        else: st.info("Sem acesso a lojas.")

    elif menu == "Abrir Chamado (Queima)":
        st.title("🔥 Reportar Queima")
        df = get_lojas_permitidas()
        lst = df['nome_loja'].tolist()
        if lst:
            with st.form("f1"):
                l=st.selectbox("Loja", lst); q=st.number_input("Qtd",1); m=st.text_input("Defeito")
                if st.form_submit_button("Enviar", use_container_width=True): abrir_chamado(l,q,m)
        else: st.warning("Sem lojas.")

    elif menu == "Resolver Chamado (Reposição)":
        st.title("📦 Reposição")
        df = get_lojas_permitidas()
        lst = df['nome_loja'].tolist()
        df_p = get_chamados_pendentes()
        
        if user not in ADMIN_EMAILS: 
            df_p = df_p[df_p['nome_loja'].isin(lst)]
        
        if not df_p.empty:
            opts = df_p.apply(lambda x: f"ID {x['id']} | {x['nome_loja']} | Qtd: {x['quantidade']} | {x['motivo']}", axis=1)
            sel = st.selectbox("Selecione o Chamado para Resolver:", opts)
            idx = int(sel.split(" |")[0].replace("ID ",""))
            row = df_p[df_p['id']==idx].iloc[0]
            
            st.info(f"Resolvendo Problema: **{row['motivo']}** da loja **{row['nome_loja']}**")
            
            with st.form("f2"):
                q=st.number_input("Quantidade Reposta", int(row['quantidade'])); obs=st.text_input("Observação da Solução / Nº Pedido")
                if st.form_submit_button("Concluir e Dar Baixa", use_container_width=True): resolver_chamado(idx,q,obs)
        else: st.success("Nenhum chamado pendente para reposição.")

    elif menu == "ADMINISTRAÇÃO":
        if user not in ADMIN_EMAILS: 
            st.error("Acesso Negado")
        else:
            st.title("⚙️ Admin")
            t1, t2, t3 = st.tabs(["➕ Criar Loja", "🔧 Gerenciar Estoque", "🔐 Permissões"])
            
            with t1:
                with st.form("fa"):
                    st.subheader("Nova Loja")
                    c1,c2=st.columns([2,1])
                    n=c1.text_input("Nome"); q=c2.number_input("Estoque Inicial",0)
                    if st.form_submit_button("Salvar"):
                        cadastrar_loja(n, q)
            
            with t2:
                all_l = pd.read_sql("SELECT nome_loja, estoque_atual FROM lojas", conn)
                lst = all_l['nome_loja'].tolist()
                if lst:
                    sel = st.selectbox("Selecione a Loja:", lst)
                    est = all_l.loc[all_l['nome_loja']==sel, 'estoque_atual'].values[0]
                    st.info(f"📦 Estoque Atual: **{est}**")
                    st.markdown("---")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        with st.container(border=True):
                            st.markdown("### 📉 Baixa Manual (Ajuste)")
                            with st.form("fb"):
                                qb=st.number_input("Qtd",1); mb=st.text_input("Motivo","Ajuste Adm")
                                if st.form_submit_button("Baixar", type="primary"): reduzir_estoque_admin(sel,qb,mb)
                    with c2:
                        with st.container(border=True):
                            st.markdown("### 🗑️ Excluir Loja")
                            st.warning(f"Apagar {sel}?")
                            if st.button("Confirmar Exclusão"):
                                remover_loja(sel)
                else: st.warning("Vazio.")

            with t3:
                c1,c2=st.columns(2)
                lst = pd.read_sql("SELECT nome_loja FROM lojas", conn)['nome_loja'].tolist()
                with c1:
                    with st.container(border=True):
                        st.markdown("**Vincular Usuário**")
                        if lst:
                            l=st.selectbox("Loja",lst,key="pl"); e=st.text_input("Email User (@jovimobile.com)")
                            if st.button("Conceder Acesso"): vincular_usuario(e,l)
                with c2:
                    st.markdown("**Permissões Ativas**")
                    dfp = pd.read_sql("SELECT p.id, p.email, l.nome_loja FROM permissoes p JOIN lojas l ON p.loja_id=l.id", conn)
                    for i, r in dfp.iterrows():
                        cc1, cc2 = st.columns([4,1])
                        cc1.text(f"{r['email']} -> {r['nome_loja']}")
                        if cc2.button("🗑️", key=f"d{r['id']}"): desvincular_usuario(r['id'])

# --- EXECUÇÃO ---
check_session()
if st.session_state['logado']:
    main_system()
else:
    login_screen()