import sqlite3

DB_NAME = "roteiro_viagem.db"

# Dados iniciais baseados no arquivo JSX
INITIAL_DAYS = [
    {
        "id": "d0", "dia": "0", "data": "02/11", "dow": "seg", "cidade": "Trânsito",
        "atividade": "Voo IBERIA (IB268) GRU → PRG, escala ~3h em Madri · 15:10–11:40 (chega no dia seguinte) · loc. 7XSO7R",
        "hospedagem": None, "transporte": "Iberia (companhia aérea)", "passeio": None,
        "hospedagem_val": 0.0, "transporte_val": 13805.88, "alimentacao_val": 0.0, "passeio_val": 0.0,
        "obs": "Localizador: 7XSO7R"
    },
    {
        "id": "d1", "dia": "1", "data": "03/11", "dow": "ter", "cidade": "Praga",
        "atividade": "Chegada, check-in e jantar na Cidade Velha",
        "hospedagem": "Prague Inn", "transporte": None, "passeio": None,
        "hospedagem_val": 1300.0, "transporte_val": 0.0, "alimentacao_val": 60.0, "passeio_val": 0.0,
        "obs": "Check-in Prague Inn (2 noites)"
    },
    {
        "id": "d2", "dia": "2", "data": "04/11", "dow": "qua", "cidade": "Praga",
        "atividade": "Ponte Carlos, Praça Central e Bairro Judeu",
        "hospedagem": None, "transporte": None, "passeio": None,
        "hospedagem_val": 0.0, "transporte_val": 0.0, "alimentacao_val": 60.0, "passeio_val": 25.0,
        "obs": ""
    },
    {
        "id": "d3", "dia": "3", "data": "05/11", "dow": "qui", "cidade": "Praga",
        "atividade": "Castelo de Praga, Malá Strana e Muro de John Lennon",
        "hospedagem": None, "transporte": None, "passeio": None,
        "hospedagem_val": 0.0, "transporte_val": 0.0, "alimentacao_val": 60.0, "passeio_val": 20.0,
        "obs": ""
    },
    {
        "id": "d4", "dia": "4", "data": "06/11", "dow": "sex", "cidade": "Cracóvia",
        "atividade": "Trem Praga → Cracóvia (08:30–14:22), check-in e Rynek Główny",
        "hospedagem": "Dom Gościnny UJ", "transporte": "Trem Praga → Cracóvia (LeoExpress)", "passeio": None,
        "hospedagem_val": 1300.0, "transporte_val": 260.0, "alimentacao_val": 45.0, "passeio_val": 0.0,
        "obs": "Check-in Dom Gościnny UJ (2 noites)"
    },
    {
        "id": "d5", "dia": "5", "data": "07/11", "dow": "sáb", "cidade": "Cracóvia",
        "atividade": "Bate-volta Auschwitz-Birkenau e Minas de Sal",
        "hospedagem": None, "transporte": None, "passeio": "Tour Auschwitz-Birkenau + Minas de Sal",
        "hospedagem_val": 0.0, "transporte_val": 0.0, "alimentacao_val": 45.0, "passeio_val": 1400.0,
        "obs": ""
    },
    {
        "id": "d6", "dia": "6", "data": "08/11", "dow": "dom", "cidade": "Budapeste",
        "atividade": "Castelo de Wawel e Bairro Judeu (Kazimierz); deslocamento até o aeroporto",
        "hospedagem": None, "transporte": "Uber até aeroporto de Cracóvia", "passeio": None,
        "hospedagem_val": 0.0, "transporte_val": 100.0, "alimentacao_val": 50.0, "passeio_val": 15.0,
        "obs": ""
    },
    {
        "id": "d6b", "dia": "6b", "data": "08/11", "dow": "dom", "cidade": "Budapeste",
        "atividade": "Voo Cracóvia → Budapeste, 21:40–22:50 (Wizz Air)",
        "hospedagem": None, "transporte": "Voo Cracóvia → Budapeste (Wizz Air)", "passeio": None,
        "hospedagem_val": 0.0, "transporte_val": 500.0, "alimentacao_val": 45.0, "passeio_val": 0.0,
        "obs": "Chegada em Budapeste já de madrugada"
    },
    {
        "id": "d7", "dia": "7", "data": "09/11", "dow": "seg", "cidade": "Budapeste",
        "atividade": "Deslocamento / descanso, Parlamento à noite",
        "hospedagem": "H2 Budapest", "transporte": None, "passeio": None,
        "hospedagem_val": 1800.0, "transporte_val": 0.0, "alimentacao_val": 50.0, "passeio_val": 0.0,
        "obs": "Check-in H2 Budapest (2 noites)"
    },
    {
        "id": "d8", "dia": "8", "data": "10/11", "dow": "ter", "cidade": "Budapeste",
        "atividade": "Bastião dos Pescadores, Peste e Ruin Pubs",
        "hospedagem": None, "transporte": None, "passeio": None,
        "hospedagem_val": 0.0, "transporte_val": 0.0, "alimentacao_val": 65.0, "passeio_val": 20.0,
        "obs": ""
    },
    {
        "id": "d9", "dia": "9", "data": "11/11", "dow": "qua", "cidade": "Viena",
        "atividade": "Trem Budapeste → Viena, Rua Graben e Catedral",
        "hospedagem": "Rioca Vienna", "transporte": "Trem Budapeste → Viena (Omio)", "passeio": None,
        "hospedagem_val": 3000.0, "transporte_val": 250.0, "alimentacao_val": 80.0, "passeio_val": 15.0,
        "obs": "Check-in Rioca Vienna (4 noites)"
    },
    {
        "id": "d10", "dia": "10", "data": "12/11", "dow": "qui", "cidade": "Viena",
        "atividade": "Palácio de Schönbrunn e jardins imperiais",
        "hospedagem": "Airbnb Viena (2ª opção)", "transporte": None, "passeio": None,
        "hospedagem_val": 2200.0, "transporte_val": 0.0, "alimentacao_val": 80.0, "passeio_val": 30.0,
        "obs": "Existem 2 acomodações cadastradas em Viena (Booking + Airbnb) — confirme qual será usada"
    },
    {
        "id": "d11", "dia": "11", "data": "13/11", "dow": "sex", "cidade": "Viena",
        "atividade": "Palácio Belvedere (Klimt) e Ópera de Viena",
        "hospedagem": None, "transporte": None, "passeio": None,
        "hospedagem_val": 0.0, "transporte_val": 0.0, "alimentacao_val": 80.0, "passeio_val": 35.0,
        "obs": ""
    },
    {
        "id": "d12", "dia": "12", "data": "14/11", "dow": "sáb", "cidade": "Viena",
        "atividade": "Bate-volta Bratislava ou MuseumsQuartier",
        "hospedagem": None, "transporte": None, "passeio": None,
        "hospedagem_val": 0.0, "transporte_val": 0.0, "alimentacao_val": 75.0, "passeio_val": 20.0,
        "obs": ""
    },
    {
        "id": "d13", "dia": "13", "data": "15/11", "dow": "dom", "cidade": "Liubliana",
        "atividade": "Trem Viena → Liubliana (Alpes), Centro Histórico",
        "hospedagem": "Hotel Art Ljubljana", "transporte": "Ônibus Viena → Liubliana (FlixBus)", "passeio": None,
        "hospedagem_val": 1500.0, "transporte_val": 600.0, "alimentacao_val": 60.0, "passeio_val": 5.0,
        "obs": "Check-in Hotel Art Ljubljana (3 noites)"
    },
    {
        "id": "d14", "dia": "14", "data": "16/11", "dow": "seg", "cidade": "Liubliana",
        "atividade": "Bate-volta Lago Bled (passeio de barco)",
        "hospedagem": None, "transporte": None, "passeio": None,
        "hospedagem_val": 0.0, "transporte_val": 0.0, "alimentacao_val": 65.0, "passeio_val": 30.0,
        "obs": ""
    },
    {
        "id": "d15", "dia": "15", "data": "17/11", "dow": "ter", "cidade": "Liubliana",
        "atividade": "Caverna de Postojna e Castelo de Predjama",
        "hospedagem": None, "transporte": None, "passeio": None,
        "hospedagem_val": 0.0, "transporte_val": 0.0, "alimentacao_val": 60.0, "passeio_val": 45.0,
        "obs": ""
    },
    {
        "id": "d16", "dia": "16", "data": "18/11", "dow": "qua", "cidade": "Londres",
        "atividade": "Voo Liubliana → Londres (EZY8842); Big Ben e London Eye",
        "hospedagem": "Garden Court Hotel", "transporte": "Voo Liubliana → Londres (easyJet EZY8842)", "passeio": None,
        "hospedagem_val": 3100.0, "transporte_val": 1380.0, "alimentacao_val": 100.0, "passeio_val": 0.0,
        "obs": "Check-in Garden Court Hotel (4 noites)"
    },
    {
        "id": "d17", "dia": "17", "data": "19/11", "dow": "qui", "cidade": "Londres",
        "atividade": "Buckingham, Westminster, British Museum e Soho",
        "hospedagem": None, "transporte": None, "passeio": None,
        "hospedagem_val": 2900.0, "transporte_val": 0.0, "alimentacao_val": 110.0, "passeio_val": 30.0,
        "obs": "Valor de hospedagem no arquivo original — confira se é custo extra ou lançamento duplicado"
    },
    {
        "id": "d18", "dia": "18", "data": "20/11", "dow": "sex", "cidade": "Londres",
        "atividade": "Tower Bridge, Borough Market e Tate Modern",
        "hospedagem": None, "transporte": None, "passeio": None,
        "hospedagem_val": 0.0, "transporte_val": 0.0, "alimentacao_val": 110.0, "passeio_val": 35.0,
        "obs": ""
    },
    {
        "id": "d19", "dia": "19", "data": "21/11", "dow": "sáb", "cidade": "Londres",
        "atividade": "Notting Hill, museus de South Kensington e West End",
        "hospedagem": None, "transporte": None, "passeio": None,
        "hospedagem_val": 0.0, "transporte_val": 0.0, "alimentacao_val": 110.0, "passeio_val": 60.0,
        "obs": ""
    },
    {
        "id": "d20", "dia": "20", "data": "22/11", "dow": "dom", "cidade": "Trânsito",
        "atividade": "Retorno ao aeroporto — voo às 21:15 (LHR)",
        "hospedagem": None, "transporte": None, "passeio": None,
        "hospedagem_val": 0.0, "transporte_val": 0.0, "alimentacao_val": 50.0, "passeio_val": 0.0,
        "obs": ""
    }
]

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Tabela principal dos dias
    c.execute('''
        CREATE TABLE IF NOT EXISTS dias (
            id TEXT PRIMARY KEY,
            dia TEXT,
            data TEXT,
            dow TEXT,
            cidade TEXT,
            atividade TEXT,
            hospedagem TEXT,
            transporte TEXT,
            passeio TEXT,
            hospedagem_val REAL,
            transporte_val REAL,
            alimentacao_val REAL,
            passeio_val REAL,
            hospedagem_pago INTEGER DEFAULT 0,
            transporte_pago INTEGER DEFAULT 0,
            alimentacao_pago INTEGER DEFAULT 0,
            passeio_pago INTEGER DEFAULT 0,
            reservado INTEGER DEFAULT 0,
            obs TEXT
        )
    ''')
    
    # Tabela de configurações globais (ex: Cotação USD -> BRL, Extra Alimentação)
    c.execute('''
        CREATE TABLE IF NOT EXISTS config (
            chave TEXT PRIMARY KEY,
            valor REAL
        )
    ''')
    
    # Popula dados iniciais se vazio
    c.execute("SELECT COUNT(*) FROM dias")
    if c.fetchone()[0] == 0:
        for d in INITIAL_DAYS:
            c.execute('''
                INSERT INTO dias (
                    id, dia, data, dow, cidade, atividade, hospedagem, transporte, passeio,
                    hospedagem_val, transporte_val, alimentacao_val, passeio_val, obs
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                d["id"], d["dia"], d["data"], d["dow"], d["cidade"], d["atividade"],
                d["hospedagem"], d["transporte"], d["passeio"],
                d["hospedagem_val"], d["transporte_val"], d["alimentacao_val"], d["passeio_val"], d["obs"]
            ))
        
        c.execute("INSERT OR REPLACE INTO config (chave, valor) VALUES ('rate', 5.4)")
        c.execute("INSERT OR REPLACE INTO config (chave, valor) VALUES ('extra_food_usd', 1465.0)")
        c.execute("INSERT OR REPLACE INTO config (chave, valor) VALUES ('extra_food_pago', 0)")
        
        conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_NAME)