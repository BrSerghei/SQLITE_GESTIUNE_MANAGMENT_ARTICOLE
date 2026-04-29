import sqlite3
import streamlit as st
import os
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LAB1.db")
def conn():
    c = sqlite3.connect(DB)
    c.execute("PRAGMA foreign_keys = ON")
    return c
def q(sql, params=()):
    c = conn()
    cur = c.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description] if cur.description else []
    c.close()
    return cols, rows
def run(sql, params=()):
    c = conn()
    cur = c.cursor()
    cur.execute(sql, params)
    c.commit()
    c.close()
def tabel(cols, rows):
    if not rows:
        st.info("Niciun rezultat.")
        return
    header = "| " + " | ".join(str(c) for c in cols) + " |"
    sep    = "| " + " | ".join("---" for _ in cols) + " |"
    lines  = [header, sep]
    for r in rows:
        lines.append("| " + " | ".join(str(v) if v is not None else "—" for v in r) + " |")
    st.markdown("\n".join(lines))
st.set_page_config(page_title="Portal Articole", layout="wide", )
with st.sidebar:
    st.markdown("## PORTAL ARTICOLE")
    st.divider()
    sectiune = st.radio("Navigare:", [
        "[ 1 ] Back-End (CRUD)",
        "[ 2 ] Front-End (10 Obiective)",
        "[ 3 ] Vedere Combinată + KPI"
    ])
    st.divider()
    _, r = q("SELECT COUNT(*) FROM Articole WHERE status='publicat'")
    _, r2 = q("SELECT ROUND(AVG(evaluare),1) FROM Comentarii")
    _, r3 = q("SELECT COUNT(*) FROM Comentarii")
    st.metric("Articole publicate", r[0][0] if r else 0)
    st.metric("Rating mediu", r2[0][0] if r2 else "—")
    st.metric("Total comentarii", r3[0][0] if r3 else 0)
if sectiune == "[ 1 ] Back-End (CRUD)":
    st.title("Back-End — Administrarea Bazei de Date")
    st.caption("Operații CRUD: CREATE · READ · UPDATE · DELETE")
    st.divider()
    col_t, col_o = st.columns([1, 2])
    with col_t:
        tbl = st.selectbox("Tabel:", ["Articole", "Autori", "Categorii", "Comentarii"])
    with col_o:
        op = st.radio("Operatie:", ["READ", "CREATE", "UPDATE", "DELETE"], horizontal=True)
    st.divider()
    if op == "READ":
        st.subheader(f"READ — {tbl}")
        cols, rows = q(f"SELECT * FROM {tbl}")
        st.caption(f"Total: {len(rows)} inregistrari")
        tabel(cols, rows)
    elif op == "CREATE":
        st.subheader(f"CREATE — Adauga in {tbl}")
        if tbl == "Articole":
            with st.form("f_create_art"):
                titlu    = st.text_input("Titlu *")
                continut = st.text_area("Continut", height=100)
                _, ar = q("SELECT id_autor, prenume||' '||nume FROM Autori")
                _, cr = q("SELECT id_categorie, nume_categorie FROM Categorii")
                ad = {f"{r[1]} (id={r[0]})": r[0] for r in ar}
                cd = {f"{r[1]} (id={r[0]})": r[0] for r in cr}
                col1, col2, col3 = st.columns(3)
                autor_sel = col1.selectbox("Autor *", list(ad.keys()))
                cat_sel   = col2.selectbox("Categorie *", list(cd.keys()))
                status    = col3.selectbox("Status", ["publicat", "draft", "arhivat"])
                if st.form_submit_button("Adaugă articol", type="primary"):
                    if titlu:
                        run("""INSERT INTO Articole
                               (titlu, continut, data_publicarii, id_autor, id_categorie, numar_vizualizari, status)
                               VALUES (?, ?, date('now'), ?, ?, 0, ?)""",
                            (titlu, continut, ad[autor_sel], cd[cat_sel], status))
                        st.success(f"Articolul '{titlu}' a fost adaugat cu succes!")
                    else:
                        st.warning("Titlul este obligatoriu.")
        elif tbl == "Autori":
            with st.form("f_create_aut"):
                col1, col2, col3 = st.columns(3)
                nume    = col1.text_input("Nume *")
                prenume = col2.text_input("Prenume *")
                email   = col3.text_input("Email *")
                if st.form_submit_button("Adaugă autor", type="primary"):
                    if nume and email:
                        run("INSERT INTO Autori (nume, prenume, email, data_inregistrare) VALUES (?, ?, ?, date('now'))",
                            (nume, prenume, email))
                        st.success(f"Autorul '{prenume} {nume}' adaugat!")
                    else:
                        st.warning("Numele și emailul sunt obligatorii.")
        elif tbl == "Comentarii":
            with st.form("f_create_com"):
                _, ar = q("SELECT id_articol, titlu FROM Articole WHERE status='publicat'")
                ad = {f"{r[1][:50]} (id={r[0]})": r[0] for r in ar}
                art_sel   = st.selectbox("Articol *", list(ad.keys()))
                col1, col2 = st.columns([2, 1])
                autor_com = col1.text_input("Autorul comentariului *")
                evaluare  = col2.slider("Evaluare", 1, 5, 5)
                text_com  = st.text_area("Text comentariu *")
                if st.form_submit_button("Adaugă comentariu", type="primary"):
                    if autor_com and text_com:
                        run("""INSERT INTO Comentarii
                               (id_articol, autor_comentariu, text_comentariu, data_comentariu, evaluare)
                               VALUES (?, ?, ?, datetime('now'), ?)""",
                            (ad[art_sel], autor_com, text_com, evaluare))
                        st.success("Comentariu adăugat!")
                    else:
                        st.warning("Completați toate câmpurile obligatorii.")
        elif tbl == "Categorii":
            with st.form("f_create_cat"):
                col1, col2 = st.columns([1, 2])
                nume_cat = col1.text_input("Nume categorie *")
                desc_cat = col2.text_input("Descriere")
                if st.form_submit_button("Adaugă categorie", type="primary"):
                    if nume_cat:
                        run("INSERT INTO Categorii (nume_categorie, descriere) VALUES (?, ?)", (nume_cat, desc_cat))
                        st.success(f"Categoria '{nume_cat}' adaugata!")
    elif op == "UPDATE":
        st.subheader(f"UPDATE — Modifica in {tbl}")
        if tbl == "Articole":
            _, ar = q("SELECT id_articol, titlu, status, numar_vizualizari FROM Articole")
            ad = {f"[{r[0]}] {r[1][:50]}": r[0] for r in ar}
            art_sel = st.selectbox("Alege articolul:", list(ad.keys()))
            id_art  = ad[art_sel]
            _, cr   = q("SELECT titlu, status, numar_vizualizari FROM Articole WHERE id_articol=?", (id_art,))
            if cr:
                with st.form("f_upd_art"):
                    col1, col2, col3 = st.columns(3)
                    titlu_nou  = col1.text_input("Titlu:", value=cr[0][0])
                    status_nou = col2.selectbox("Status:", ["publicat", "draft", "arhivat"],
                                                index=["publicat","draft","arhivat"].index(cr[0][1]))
                    viz_noi    = col3.number_input("Vizualizari:", min_value=0, value=int(cr[0][2]))
                    if st.form_submit_button("Salvează", type="primary"):
                        run("UPDATE Articole SET titlu=?, status=?, numar_vizualizari=? WHERE id_articol=?",
                            (titlu_nou, status_nou, viz_noi, id_art))
                        st.success("Articol actualizat!")
                st.caption("Stare curentă:")
                tabel(["titlu","status","numar_vizualizari"], [cr[0]])
        elif tbl == "Autori":
            _, ar = q("SELECT id_autor, prenume||' '||nume, email FROM Autori")
            ad = {f"[{r[0]}] {r[1]}": r[0] for r in ar}
            aut_sel = st.selectbox("Alege autorul:", list(ad.keys()))
            id_aut  = ad[aut_sel]
            _, cr   = q("SELECT email FROM Autori WHERE id_autor=?", (id_aut,))
            if cr:
                with st.form("f_upd_aut"):
                    email_nou = st.text_input("Email nou:", value=cr[0][0])
                    if st.form_submit_button("Salvează", type="primary"):
                        run("UPDATE Autori SET email=? WHERE id_autor=?", (email_nou, id_aut))
                        st.success("Email actualizat!")
    elif op == "DELETE":
        st.subheader(f"DELETE — Sterge din {tbl}")
        st.warning("⚠️ Stergerea articolelor elimina si comentariile asociate (CASCADE DELETE).")
        if tbl == "Articole":
            _, ar = q("SELECT id_articol, titlu, status, numar_vizualizari FROM Articole")
            ad = {f"[{r[0]}] {r[1][:50]} — {r[2]}, {r[3]} viz.": r[0] for r in ar}
            art_sel = st.selectbox("Alege articolul:", list(ad.keys()))
            st.caption("Înainte de ștergere:")
            _, prev = q("SELECT * FROM Articole WHERE id_articol=?", (ad[art_sel],))
            _, pc   = q("SELECT * FROM Articole")
            tabel(["id_articol","titlu","data_publicarii","id_autor","id_categorie","numar_vizualizari","status"], prev)
            col1, col2 = st.columns([1,4])
            if col1.button("STERGE", type="primary"):
                run("DELETE FROM Articole WHERE id_articol=?", (ad[art_sel],))
                _, ac = q("SELECT * FROM Articole")
                st.success(f"Sters! Inainte: {len(pc)} articole → Dupa: {len(ac)} articole.")
        elif tbl == "Comentarii":
            _, cr = q("""SELECT co.id_comentariu, a.titlu, co.autor_comentariu, co.evaluare
                         FROM Comentarii co JOIN Articole a ON co.id_articol=a.id_articol""")
            if cr:
                cd = {f"[{r[0]}] {r[1][:35]} — {r[2]} (★{r[3]})": r[0] for r in cr}
                com_sel = st.selectbox("Alege comentariul:", list(cd.keys()))
                if st.button("STERGE comentariu", type="primary"):
                    run("DELETE FROM Comentarii WHERE id_comentariu=?", (cd[com_sel],))
                    st.success("Comentariu șters!")
            else:
                st.info("Nu există comentarii.")
elif sectiune == "[ 2 ] Front-End (10 Obiective)":
    st.title("Front-End — Cele 10 Obiective")
    st.caption("SQL → Tabel formatat → Grafic → Interpretare")
    st.divider()
    with st.expander("O1 — Articole publicate cu autor și categorie", expanded=True):
        st.code("""SELECT a.titlu, au.prenume||' '||au.nume AS autor,
       c.nume_categorie, a.numar_vizualizari, a.status
FROM Articole a
JOIN Autori au ON a.id_autor=au.id_autor
JOIN Categorii c ON a.id_categorie=c.id_categorie
ORDER BY a.numar_vizualizari DESC""", language="sql")
        cols, rows = q("""
            SELECT a.titlu, au.prenume||' '||au.nume AS autor,
                   c.nume_categorie AS categorie, a.numar_vizualizari, a.status
            FROM Articole a
            JOIN Autori au ON a.id_autor=au.id_autor
            JOIN Categorii c ON a.id_categorie=c.id_categorie
            ORDER BY a.numar_vizualizari DESC""")
        tabel(cols, rows)
        st.bar_chart({r[0][:28]: r[3] for r in rows})
        st.info(f"**Rezultat:** {len(rows)} articole. Lider: '{rows[0][0][:45]}' — {rows[0][3]} vizualizări." if rows else "")
    with st.expander("O2 — Număr articole pe categorii"):
        st.code("""SELECT c.nume_categorie, COUNT(a.id_articol) AS nr_articole
FROM Categorii c
LEFT JOIN Articole a ON c.id_categorie=a.id_categorie
GROUP BY c.id_categorie
ORDER BY nr_articole DESC""", language="sql")
        cols, rows = q("""
            SELECT c.nume_categorie, COUNT(a.id_articol) AS nr_articole
            FROM Categorii c
            LEFT JOIN Articole a ON c.id_categorie=a.id_categorie
            GROUP BY c.id_categorie ORDER BY nr_articole DESC""")
        tabel(cols, rows)
        st.bar_chart({r[0]: r[1] for r in rows})
        st.info("**Interpretare:** Categorii cu 0 articole = zone editoriale neacoperite.")
    with st.expander("O3 — Top autori după vizualizări totale"):
        st.code("""SELECT au.prenume||' '||au.nume AS autor,
       COUNT(a.id_articol) AS nr_articole,
       COALESCE(SUM(a.numar_vizualizari),0) AS total_vizualizari
FROM Autori au
LEFT JOIN Articole a ON au.id_autor=a.id_autor
GROUP BY au.id_autor
ORDER BY total_vizualizari DESC""", language="sql")
        cols, rows = q("""
            SELECT au.prenume||' '||au.nume AS autor,
                   COUNT(a.id_articol) AS nr_articole,
                   COALESCE(SUM(a.numar_vizualizari),0) AS total_viz
            FROM Autori au
            LEFT JOIN Articole a ON au.id_autor=a.id_autor
            GROUP BY au.id_autor ORDER BY total_viz DESC""")
        tabel(cols, rows)
        st.bar_chart({r[0]: r[2] for r in rows})
        st.info("**Interpretare:** Autori cu 0 articole = potential editorial nevalorificat.")
    with st.expander("O4 — Rating mediu pe categorii"):
        st.code("""SELECT c.nume_categorie,
       ROUND(AVG(co.evaluare),2) AS rating_mediu,
       COUNT(co.id_comentariu) AS nr_comentarii
FROM Categorii c
LEFT JOIN Articole a ON c.id_categorie=a.id_categorie
LEFT JOIN Comentarii co ON a.id_articol=co.id_articol
GROUP BY c.id_categorie
ORDER BY rating_mediu DESC""", language="sql")
        cols, rows = q("""
            SELECT c.nume_categorie,
                   ROUND(AVG(co.evaluare),2) AS rating_mediu,
                   COUNT(co.id_comentariu) AS nr_comentarii
            FROM Categorii c
            LEFT JOIN Articole a ON c.id_categorie=a.id_categorie
            LEFT JOIN Comentarii co ON a.id_articol=co.id_articol
            GROUP BY c.id_categorie ORDER BY rating_mediu DESC NULLS LAST""")
        tabel(cols, rows)
        st.bar_chart({r[0]: r[1] if r[1] else 0 for r in rows})
        st.info("**Interpretare:** Rating bazat pe un singur comentariu e mai puțin fiabil statistic.")
    with st.expander("O5 — Articole fără comentarii"):
        st.code("""SELECT a.titlu, c.nume_categorie, a.numar_vizualizari, a.status
FROM Articole a
LEFT JOIN Comentarii co ON a.id_articol=co.id_articol
JOIN Categorii c ON a.id_categorie=c.id_categorie
WHERE co.id_comentariu IS NULL""", language="sql")
        cols, rows = q("""
            SELECT a.titlu, c.nume_categorie, a.numar_vizualizari, a.status
            FROM Articole a
            LEFT JOIN Comentarii co ON a.id_articol=co.id_articol
            JOIN Categorii c ON a.id_categorie=c.id_categorie
            WHERE co.id_comentariu IS NULL""")
        tabel(cols, rows)
        st.warning(f"**{len(rows)} articole** fara niciun comentariu — necesita promovare activa.")
    with st.expander("O6 — Top 5 articole după vizualizări"):
        st.code("""SELECT a.titlu, c.nume_categorie, a.numar_vizualizari
FROM Articole a
JOIN Categorii c ON a.id_categorie=c.id_categorie
WHERE a.status='publicat'
ORDER BY a.numar_vizualizari DESC
LIMIT 5""", language="sql")
        cols, rows = q("""
            SELECT a.titlu, c.nume_categorie, a.numar_vizualizari
            FROM Articole a JOIN Categorii c ON a.id_categorie=c.id_categorie
            WHERE a.status='publicat'
            ORDER BY a.numar_vizualizari DESC LIMIT 5""")
        tabel(cols, rows)
        st.bar_chart({r[0][:28]: r[2] for r in rows})
        st.info("**Interpretare:** Aceste articole generează cel mai mare reach — teme de replicat editorial.")
    with st.expander("O7 — Rata de publicare — distribuția statusurilor"):
        st.code("""SELECT status, COUNT(*) AS nr
FROM Articole
GROUP BY status
ORDER BY nr DESC""", language="sql")
        _, rows = q("SELECT status, COUNT(*) AS nr FROM Articole GROUP BY status ORDER BY nr DESC")
        tabel(["status","nr"], rows)
        st.bar_chart({r[0]: r[1] for r in rows})
        total = sum(r[1] for r in rows)
        pub   = next((r[1] for r in rows if r[0]=="publicat"), 0)
        rata  = round(pub/total*100,1) if total else 0
        st.info(f"**Rată publicare:** {pub}/{total} articole = **{rata}%**. Țintă recomandată: peste 80%.")
    with st.expander("O8 — Articole sub prag critic (sub 50 vizualizări)"):
        st.code("""SELECT a.titlu, a.status, a.numar_vizualizari, c.nume_categorie
FROM Articole a
JOIN Categorii c ON a.id_categorie=c.id_categorie
WHERE a.numar_vizualizari < 50
ORDER BY a.numar_vizualizari""", language="sql")
        cols, rows = q("""
            SELECT a.titlu, a.status, a.numar_vizualizari, c.nume_categorie
            FROM Articole a JOIN Categorii c ON a.id_categorie=c.id_categorie
            WHERE a.numar_vizualizari < 50 ORDER BY a.numar_vizualizari""")
        tabel(cols, rows)
        if rows:
            st.bar_chart({r[0][:28]: r[2] for r in rows})
        st.warning(f"**{len(rows)} articole** sub pragul critic de 50 vizualizari — actiune necesara.")
    with st.expander("O9 — Media vizualizări și comentarii per articol"):
        st.code("""SELECT ROUND(AVG(numar_vizualizari),1) AS medie_viz
FROM Articole WHERE status='publicat'""", language="sql")
        _, rv = q("SELECT ROUND(AVG(numar_vizualizari),1) FROM Articole WHERE status='publicat'")
        _, rc = q("""SELECT ROUND(AVG(nr),2) FROM
                     (SELECT COUNT(co.id_comentariu) AS nr FROM Articole a
                      LEFT JOIN Comentarii co ON a.id_articol=co.id_articol
                      WHERE a.status='publicat' GROUP BY a.id_articol)""")
        mv = rv[0][0] if rv else 0
        mc = rc[0][0] if rc else 0
        tabel(["Indicator","Valoare"],[("Medie vizualizari / articol", mv),("Medie comentarii / articol", mc)])
        col1, col2 = st.columns(2)
        col1.metric("Medie vizualizari / articol", mv)
        col2.metric("Medie comentarii / articol", mc)
        st.bar_chart({"Medie viz": mv, "Medie com ×10": round((mc or 0)*10,1)})
        st.info("**Interpretare:** Medie sub 100 viz. = conținut subdistribuit sau subiect nepotrivit audienței.")
    with st.expander("O10 — Tablou de Bord General al Portalului"):
        st.code("""SELECT a.titlu, au.prenume||' '||au.nume AS autor,
       c.nume_categorie AS categorie,
       a.numar_vizualizari,
       COUNT(co.id_comentariu) AS nr_comentarii,
       ROUND(AVG(co.evaluare),1) AS rating,
       a.status
FROM Articole a
JOIN Autori au ON a.id_autor=au.id_autor
JOIN Categorii c ON a.id_categorie=c.id_categorie
LEFT JOIN Comentarii co ON a.id_articol=co.id_articol
GROUP BY a.id_articol
ORDER BY a.numar_vizualizari DESC""", language="sql")
        cols, rows = q("""
            SELECT a.titlu, au.prenume||' '||au.nume AS autor,
                   c.nume_categorie, a.numar_vizualizari,
                   COUNT(co.id_comentariu) AS nr_com,
                   ROUND(AVG(co.evaluare),1) AS rating, a.status
            FROM Articole a
            JOIN Autori au ON a.id_autor=au.id_autor
            JOIN Categorii c ON a.id_categorie=c.id_categorie
            LEFT JOIN Comentarii co ON a.id_articol=co.id_articol
            GROUP BY a.id_articol ORDER BY a.numar_vizualizari DESC""")
        tabel(cols, rows)
        st.info("**Raport complet:** combina reach, engagement si calitate perceputa per articol — baza pentru decizie.")
elif sectiune == "[ 3 ] Vedere Combinată + KPI":
    st.title("Vedere Combinată — CRUD + Obiective + Recomandări")
    st.caption("Modificările din CRUD se reflectă instantaneu asupra obiectivelor și scorului de mai jos.")
    st.divider()
    st.subheader("1. Modifică rapid date (CRUD)")
    with st.form("crud_rapid"):
        col1, col2, col3 = st.columns(3)
        _, ar = q("SELECT id_articol, titlu, status, numar_vizualizari FROM Articole")
        ad = {f"[{r[0]}] {r[1][:35]} ({r[2]}, {r[3]} viz.)": r[0] for r in ar}
        art_sel = col1.selectbox("Articol:", list(ad.keys()))
        viz_noi = col2.number_input("Vizualizari noi:", min_value=0, step=10)
        st_nou  = col3.selectbox("Status nou:", ["publicat", "draft", "arhivat"])
        if st.form_submit_button("Aplică modificarea", type="primary"):
            run("UPDATE Articole SET numar_vizualizari=?, status=? WHERE id_articol=?",
                (viz_noi, st_nou, ad[art_sel]))
            st.success("Modificare aplicată! Impactul se vede imediat în graficele de mai jos.")
    st.divider()
    st.subheader("2. Tablou de Bord — Metrici Live")
    _, r1 = q("SELECT COUNT(*) FROM Articole WHERE status='publicat'")
    _, r2 = q("SELECT COUNT(*) FROM Articole")
    _, r3 = q("SELECT ROUND(AVG(numar_vizualizari),1) FROM Articole WHERE status='publicat'")
    _, r4 = q("SELECT ROUND(AVG(evaluare),2) FROM Comentarii")
    _, r5 = q("""SELECT COUNT(*) FROM Articole a
                 LEFT JOIN Comentarii co ON a.id_articol=co.id_articol
                 WHERE co.id_comentariu IS NULL""")
    _, r6 = q("SELECT COUNT(*) FROM Articole WHERE numar_vizualizari < 50")
    pub      = r1[0][0] if r1 else 0
    total    = r2[0][0] if r2 else 1
    medie_v  = r3[0][0] if r3 else 0
    rating   = r4[0][0] if r4 else 0
    fara_com = r5[0][0] if r5 else 0
    sub_prag = r6[0][0] if r6 else 0
    rata_pub = round(pub/total*100,1) if total else 0
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    c1.metric("Articole publicate", pub,      help="Articole cu status='publicat'")
    c2.metric("Rată publicare",     f"{rata_pub}%", help="Publicate / Total × 100")
    c3.metric("Medie viz./articol",  medie_v,  help="AVG(numar_vizualizari)")
    c4.metric("Rating mediu",       rating,   help="AVG(evaluare) din Comentarii")
    c5.metric("Fără comentarii",    fara_com, help="LEFT JOIN + IS NULL")
    c6.metric("Sub 50 vizualizări", sub_prag, help="COUNT WHERE viz < 50")
    st.divider()
    st.subheader("3. IPE — Indicatorul de Performanță Editorial")
    st.caption("KPI compus: 5 ținte verificate automat pe datele curente din LAB1.db")
    TINTE = {
        "Rată publicare ≥ 80%":     rata_pub >= 80,
        "Medie vizualizări ≥ 100":  (medie_v or 0) >= 100,
        "Rating mediu ≥ 4.0":       (rating or 0) >= 4.0,
        "Art. fără com. ≤ 25%":      fara_com <= total * 0.25,
        "Sub prag critic ≤ 2 art.":  sub_prag <= 2,
    }
    indeplinite = sum(1 for v in TINTE.values() if v)
    scor = round(indeplinite / len(TINTE) * 100)
    col_s, col_t = st.columns([1, 2])
    with col_s:
        if scor >= 80:
            st.success(f"### IPE: {scor} / 100")
            culoare = "VERDE"
        elif scor >= 60:
            st.warning(f"### IPE: {scor} / 100")
            culoare = "GALBEN"
        else:
            st.error(f"### IPE: {scor} / 100")
            culoare = "ROSU"
        st.bar_chart({"IPE actual": scor, "Tinta": 100})
    with col_t:
        st.write("**Ținte individuale:**")
        tabel(["Tinta", "Status"],
              [(t, "Îndeplinită" if v else "Neîndeplinită") for t, v in TINTE.items()])
    st.divider()
    st.subheader("4. Impact CRUD → Obiective (live)")
    col_a, col_b = st.columns(2)
    with col_a:
        st.caption("Distribuția statusurilor (O7)")
        _, rs = q("SELECT status, COUNT(*) FROM Articole GROUP BY status")
        st.bar_chart({r[0]: r[1] for r in rs})
    with col_b:
        st.caption("Articole sub prag critic — sub 50 viz. (O8)")
        _, rp = q("SELECT titlu, numar_vizualizari FROM Articole WHERE numar_vizualizari < 50 ORDER BY numar_vizualizari")
        st.bar_chart({r[0][:25]: r[1] for r in rp} if rp else {"(niciun articol sub prag)": 0})
    _, rc = q("""SELECT c.nume_categorie, COALESCE(SUM(a.numar_vizualizari),0)
                 FROM Categorii c
                 LEFT JOIN Articole a ON c.id_categorie=a.id_categorie AND a.status='publicat'
                 GROUP BY c.id_categorie ORDER BY 2 DESC""")
    st.caption("Vizualizări totale pe categorie — impact combinat O2 + O3")
    st.bar_chart({r[0]: r[1] for r in rc})
    st.divider()
    st.subheader("5. Recomandări Editoriale")
    if scor >= 80:
        st.success("Articolele, autorii și comentariile sunt în stare bună — vizualizările și rating-urile ating nivelul așteptat. Se recomandă continuarea publicării regulate și completarea categoriilor cu puține articole.")
    elif scor >= 60:
        st.warning("Baza de date conține articole, însă unele nu primesc suficiente vizualizări sau comentarii. Acțiunile de mai jos pot îmbunătăți situația fără modificări majore.")
        if (medie_v or 0) < 100:
            st.write("-> Articolele publicate au în medie sub 100 de vizualizări — titlurile pot fi reformulate mai atrăgător, iar articolele distribuite pe rețele sociale.")
        if fara_com > total * 0.25:
            st.write("-> Peste un sfert din articolele publicate nu au primit niciun comentariu — adaugă la finalul fiecărui articol o întrebare sau un îndemn către cititori.")
        if sub_prag > 2:
            st.write(f"-> {sub_prag} articole au sub 50 de vizualizări — acestea necesită promovare activă sau revizuirea conținutului.")
    else:
        st.error("Majoritatea articolelor din baza de date nu ating nivelul minim de vizualizări sau nu au primit feedback. Verificați punctele de mai jos și acționați imediat.")
        for tinta, ok in TINTE.items():
            if not ok:
                st.write(f"Țintă neîndeplinită: {tinta}")
    st.caption(f"Această concluzie se bazează pe {indeplinite} din {len(TINTE)} criterii de performanță atinse.")