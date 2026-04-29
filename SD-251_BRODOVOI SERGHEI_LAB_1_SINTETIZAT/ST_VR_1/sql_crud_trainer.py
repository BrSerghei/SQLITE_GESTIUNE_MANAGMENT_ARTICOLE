import sqlite3
import streamlit as st
import os
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LAB1.db")
def get_conn():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
st.set_page_config(page_title="SQL CRUD Trainer", layout="wide")
st.title("SQL CRUD Trainer — LAB1.db")
st.caption("Tabele: Categorii | Autori | Articole | Comentarii")
tab1, tab2, tab3 = st.tabs(["Editor SQL", "CRUD", "JOIN-uri"])
with tab1:
    st.subheader("Editor SQL")
    sql = st.text_area("Scrie orice comanda SQL:", height=150,
                       value="SELECT * FROM Articole LIMIT 10;")
    if st.button("Executa", key="run"):
        conn = get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            if sql.strip().upper().startswith("SELECT"):
                rezultate = cursor.fetchall()
                cols = [d[0] for d in cursor.description]
                st.write("**Rezultat:**")
                st.write([cols] + list(rezultate))
                st.success(f"{len(rezultate)} randuri returnate.")
            else:
                conn.commit()
                st.success("Comanda executata cu succes.")
        except Exception as e:
            st.error(f"Eroare: {e}")
        conn.close()
with tab2:
    st.subheader("Operatii CRUD")
    tabel = st.selectbox("Alege tabelul:", ["Articole", "Autori", "Categorii", "Comentarii"])
    operatie = st.radio("Operatie:", ["SELECT (Read)", "INSERT", "UPDATE", "DELETE"], horizontal=True)
    if operatie == "SELECT (Read)":
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {tabel}")
        rezultate = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        conn.close()
        st.write("**Coloane:**", cols)
        for rand in rezultate:
            st.write(rand)
        st.info(f"Total: {len(rezultate)} randuri in {tabel}.")
    elif operatie == "INSERT":
        st.write("**INSERT in Articole** (exemplu):")
        titlu = st.text_input("Titlu articol nou:")
        id_autor = st.number_input("ID Autor:", min_value=1, step=1)
        id_cat = st.number_input("ID Categorie:", min_value=1, step=1)
        status = st.selectbox("Status:", ["publicat", "draft", "arhivat"])
        if st.button("Adauga articol"):
            conn = get_conn()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO Articole (titlu, continut, data_publicarii, id_autor, id_categorie, numar_vizualizari, status) VALUES (?, ?, date('now'), ?, ?, 0, ?)",
                    (titlu, "Continut implicit.", id_autor, id_cat, status)
                )
                conn.commit()
                st.success("Articol adaugat!")
            except Exception as e:
                st.error(f"Eroare: {e}")
            conn.close()
    elif operatie == "UPDATE":
        st.write("**UPDATE vizualizari articol:**")
        id_art = st.number_input("ID Articol:", min_value=1, step=1)
        viz_nou = st.number_input("Numar vizualizari nou:", min_value=0, step=1)
        if st.button("Actualizeaza"):
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("UPDATE Articole SET numar_vizualizari = ? WHERE id_articol = ?",
                           (viz_nou, id_art))
            conn.commit()
            conn.close()
            st.success(f"Articolul {id_art} actualizat.")
    elif operatie == "DELETE":
        st.write("**DELETE articol dupa ID:**")
        id_del = st.number_input("ID Articol de sters:", min_value=1, step=1)
        if st.button("Sterge", type="primary"):
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Articole WHERE id_articol = ?", (id_del,))
            conn.commit()
            conn.close()
            st.success(f"Articolul {id_del} sters.")
with tab3:
    st.subheader("JOIN-uri")
    join_ales = st.selectbox("Alege JOIN-ul:", [
        "1. INNER JOIN — Articole cu autor si categorie",
        "2. LEFT JOIN — Toate articolele, inclusiv fara comentarii",
        "3. GROUP BY — Numar articole pe categorie",
        "4. JOIN + agregare — Vizualizari totale pe autor",
        "5. JOIN cu filtru — Articole dintr-o categorie specifica",
    ])
    queries = {
        "1. INNER JOIN — Articole cu autor si categorie": """
SELECT a.id_articol, a.titlu,
       au.prenume || ' ' || au.nume AS autor,
       c.nume_categorie AS categorie,
       a.numar_vizualizari, a.status
FROM Articole a
INNER JOIN Autori au ON a.id_autor = au.id_autor
INNER JOIN Categorii c ON a.id_categorie = c.id_categorie
ORDER BY a.numar_vizualizari DESC;""",
        "2. LEFT JOIN — Toate articolele, inclusiv fara comentarii": """
SELECT a.titlu, co.autor_comentariu, co.evaluare
FROM Articole a
LEFT JOIN Comentarii co ON a.id_articol = co.id_articol
ORDER BY a.id_articol;""",
        "3. GROUP BY — Numar articole pe categorie": """
SELECT c.nume_categorie, COUNT(a.id_articol) AS nr_articole
FROM Categorii c
LEFT JOIN Articole a ON c.id_categorie = a.id_categorie
GROUP BY c.id_categorie
ORDER BY nr_articole DESC;""",
        "4. JOIN + agregare — Vizualizari totale pe autor": """
SELECT au.prenume || ' ' || au.nume AS autor,
       COUNT(a.id_articol) AS nr_articole,
       SUM(a.numar_vizualizari) AS total_vizualizari
FROM Autori au
LEFT JOIN Articole a ON au.id_autor = a.id_autor
GROUP BY au.id_autor
ORDER BY total_vizualizari DESC;""",
        "5. JOIN cu filtru — Articole dintr-o categorie specifica": """
SELECT a.titlu, a.data_publicarii, a.numar_vizualizari
FROM Articole a
INNER JOIN Categorii c ON a.id_categorie = c.id_categorie
WHERE c.nume_categorie = 'Tehnologie'
  AND a.status = 'publicat'
ORDER BY a.data_publicarii DESC;""",
    }
    sql_join = queries[join_ales]
    st.code(sql_join.strip(), language="sql")
    if st.button("Ruleaza JOIN"):
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(sql_join)
        rezultate = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        conn.close()
        st.write("**Coloane:**", cols)
        for rand in rezultate:
            st.write(rand)
        st.success(f"{len(rezultate)} randuri returnate.")