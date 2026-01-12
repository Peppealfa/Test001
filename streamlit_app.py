import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Configurazione della pagina
st.set_page_config(page_title="Sistema Domande", page_icon="❓", layout="wide")

# Funzione per inizializzare il database
def init_database():
    conn = sqlite3.connect('domande.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS domande (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domanda TEXT NOT NULL,
            risposta TEXT,
            data_ora_domanda TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_ora_risposta TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Funzione per salvare una domanda
def salva_domanda(domanda):
    conn = sqlite3.connect('domande.db')
    c = conn.cursor()
    c.execute('INSERT INTO domande (domanda, data_ora_domanda) VALUES (?, ?)', 
              (domanda, datetime.now()))
    conn.commit()
    conn.close()

# Funzione per salvare una risposta
def salva_risposta(id_domanda, risposta):
    conn = sqlite3.connect('domande.db')
    c = conn.cursor()
    c.execute('UPDATE domande SET risposta = ?, data_ora_risposta = ? WHERE id = ?', 
              (risposta, datetime.now(), id_domanda))
    conn.commit()
    conn.close()

# Funzione per recuperare tutte le domande
def get_tutte_domande():
    conn = sqlite3.connect('domande.db')
    df = pd.read_sql_query('SELECT * FROM domande ORDER BY data_ora_domanda DESC', conn)
    conn.close()
    return df

# Funzione per eliminare una domanda
def elimina_domanda(id_domanda):
    conn = sqlite3.connect('domande.db')
    c = conn.cursor()
    c.execute('DELETE FROM domande WHERE id = ?', (id_domanda,))
    conn.commit()
    conn.close()

# Inizializza il database
init_database()

# Inizializza lo stato della sessione per gestire i form di risposta
if 'risposta_aperta' not in st.session_state:
    st.session_state.risposta_aperta = {}

# Titolo dell'applicazione
st.title("❓ Sistema di Gestione Domande e Risposte")
st.markdown("---")

# Sezione per inserire una nuova domanda
st.header("📝 Fai una domanda")
col1, col2 = st.columns([4, 1])

with col1:
    nuova_domanda = st.text_input("Scrivi la tua domanda:", 
                                   placeholder="Inserisci qui la tua domanda...")

with col2:
    st.write("")  # Spazio per allineamento
    st.write("")  # Spazio per allineamento
    if st.button("Invia", type="primary", use_container_width=True):
        if nuova_domanda.strip():
            salva_domanda(nuova_domanda)
            st.success("✅ Domanda salvata con successo!")
            st.rerun()
        else:
            st.error("⚠️ Per favore, inserisci una domanda valida!")

st.markdown("---")

# Sezione per visualizzare lo storico
st.header("📚 Storico delle Domande e Risposte")

# Recupera tutte le domande
domande_df = get_tutte_domande()

if not domande_df.empty:
    # Mostra statistiche
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Totale Domande", len(domande_df))
    with col2:
        risposte_date = domande_df['risposta'].notna().sum()
        st.metric("Risposte Date", risposte_date)
    with col3:
        st.metric("In Attesa", len(domande_df) - risposte_date)
    
    st.markdown("---")
    
    # Filtro per visualizzare solo domande senza risposta
    mostra_solo_senza_risposta = st.checkbox("🔍 Mostra solo domande senza risposta")
    
    # Filtra il dataframe se necessario
    if mostra_solo_senza_risposta:
        domande_filtrate = domande_df[domande_df['risposta'].isna()]
    else:
        domande_filtrate = domande_df
    
    if domande_filtrate.empty:
        st.info("📭 Nessuna domanda trovata con i filtri selezionati.")
    else:
        # Mostra le domande in card con layout a due colonne
        for index, row in domande_filtrate.iterrows():
            with st.container():
                # Header con ID e bottone elimina
                col_header1, col_header2, col_header3 = st.columns([0.5, 8, 1.5])
                
                with col_header1:
                    # Icona stato
                    if pd.notna(row['risposta']):
                        st.write("✅")
                    else:
                        st.write("⏳")
                
                with col_header2:
                    st.write(f"**Domanda #{row['id']}**")
                
                with col_header3:
                    if st.button("🗑️ Elimina", key=f"delete_{row['id']}", use_container_width=True):
                        elimina_domanda(row['id'])
                        st.success("Domanda eliminata!")
                        st.rerun()
                
                # Layout a due colonne: Domanda | Risposta
                col_domanda, col_risposta = st.columns(2)
                
                # COLONNA SINISTRA: DOMANDA
                with col_domanda:
                    st.markdown("### ❓ Domanda")
                    st.info(row['domanda'])
                    st.caption(f"📅 {pd.to_datetime(row['data_ora_domanda']).strftime('%d/%m/%Y alle %H:%M:%S')}")
                
                # COLONNA DESTRA: RISPOSTA
                with col_risposta:
                    st.markdown("### 💬 Risposta")
                    
                    # Se c'è già una risposta e non è in modalità modifica
                    if pd.notna(row['risposta']) and not st.session_state.risposta_aperta.get(row['id'], False):
                        st.success(row['risposta'])
                        st.caption(f"📅 {pd.to_datetime(row['data_ora_risposta']).strftime('%d/%m/%Y alle %H:%M:%S')}")
                        
                        if st.button("✏️ Modifica", key=f"edit_{row['id']}", use_container_width=True):
                            st.session_state.risposta_aperta[row['id']] = True
                            st.rerun()
                    
                    # Form per inserire/modificare la risposta
                    elif pd.isna(row['risposta']) or st.session_state.risposta_aperta.get(row['id'], False):
                        with st.form(key=f"form_risposta_{row['id']}"):
                            risposta_testo = st.text_area(
                                "Scrivi la risposta:",
                                value=row['risposta'] if pd.notna(row['risposta']) else "",
                                placeholder="Inserisci qui la tua risposta...",
                                height=150,
                                key=f"textarea_{row['id']}",
                                label_visibility="collapsed"
                            )
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                submit = st.form_submit_button("💾 Salva", type="primary", use_container_width=True)
                            with col_btn2:
                                if pd.notna(row['risposta']):
                                    cancel = st.form_submit_button("❌ Annulla", use_container_width=True)
                                else:
                                    cancel = False
                            
                            if submit:
                                if risposta_testo.strip():
                                    salva_risposta(row['id'], risposta_testo)
                                    st.success("✅ Risposta salvata!")
                                    if row['id'] in st.session_state.risposta_aperta:
                                        del st.session_state.risposta_aperta[row['id']]
                                    st.rerun()
                                else:
                                    st.error("⚠️ La risposta non può essere vuota!")
                            
                            if cancel:
                                if row['id'] in st.session_state.risposta_aperta:
                                    del st.session_state.risposta_aperta[row['id']]
                                st.rerun()
                
                st.markdown("---")
    
    # Opzione per scaricare lo storico
    st.download_button(
        label="📥 Scarica Storico Completo (CSV)",
        data=domande_df.to_csv(index=False).encode('utf-8'),
        file_name=f'storico_domande_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv',
    )
else:
    st.info("📭 Nessuna domanda ancora presente. Inizia facendo la tua prima domanda!")

# Footer
st.markdown("---")
st.caption("💡 Suggerimento: Tutte le domande e risposte vengono salvate automaticamente nel database locale.")