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
            data_ora TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Funzione per salvare una domanda
def salva_domanda(domanda):
    conn = sqlite3.connect('domande.db')
    c = conn.cursor()
    c.execute('INSERT INTO domande (domanda, data_ora) VALUES (?, ?)', 
              (domanda, datetime.now()))
    conn.commit()
    conn.close()

# Funzione per recuperare tutte le domande
def get_tutte_domande():
    conn = sqlite3.connect('domande.db')
    df = pd.read_sql_query('SELECT * FROM domande ORDER BY data_ora DESC', conn)
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

# Titolo dell'applicazione
st.title("❓ Sistema di Gestione Domande")
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
st.header("📚 Storico delle Domande")

# Recupera tutte le domande
domande_df = get_tutte_domande()

if not domande_df.empty:
    # Mostra statistiche
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Totale Domande", len(domande_df))
    with col2:
        st.metric("Ultima Domanda", 
                  pd.to_datetime(domande_df['data_ora'].iloc[0]).strftime('%d/%m/%Y %H:%M'))
    
    st.markdown("---")
    
    # Mostra le domande in card
    for index, row in domande_df.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([0.5, 8, 1.5])
            
            with col1:
                st.write(f"**#{row['id']}**")
            
            with col2:
                st.write(f"**{row['domanda']}**")
                st.caption(f"📅 {pd.to_datetime(row['data_ora']).strftime('%d/%m/%Y alle %H:%M:%S')}")
            
            with col3:
                if st.button("🗑️ Elimina", key=f"delete_{row['id']}", use_container_width=True):
                    elimina_domanda(row['id'])
                    st.success("Domanda eliminata!")
                    st.rerun()
            
            st.markdown("---")
    
    # Opzione per scaricare lo storico
    st.download_button(
        label="📥 Scarica Storico (CSV)",
        data=domande_df.to_csv(index=False).encode('utf-8'),
        file_name=f'storico_domande_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        mime='text/csv',
    )
else:
    st.info("📭 Nessuna domanda ancora presente. Inizia facendo la tua prima domanda!")

# Footer
st.markdown("---")
st.caption("💡 Suggerimento: Tutte le domande vengono salvate automaticamente nel database locale.")