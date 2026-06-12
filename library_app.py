import json
import random
import string
from pathlib import Path
from datetime import datetime
import streamlit as st

# ─── Config ───────────────────────────────────────────────────────────────────
DATABASE = "database.json"

st.set_page_config(
    page_title="LibraryOS",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f1117;
    border-right: 1px solid #1e2130;
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.95rem !important;
    padding: 6px 0;
}

/* Main bg */
.stApp { background: #13151f; }

/* Headers */
h1, h2, h3 { color: #f0f4ff !important; }
p, label, .stMarkdown { color: #94a3b8 !important; }

/* Cards */
.card {
    background: #1a1d2e;
    border: 1px solid #252840;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.card:hover { border-color: #6366f1; }

.book-id, .member-id {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #6366f1 !important;
    background: #1e1f3a;
    padding: 2px 8px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 6px;
}

.book-title { font-size: 1.1rem; font-weight: 600; color: #f0f4ff !important; }
.book-meta  { font-size: 0.85rem; color: #64748b !important; margin-top: 2px; }

.badge-ok   { background:#14532d; color:#86efac !important; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-warn { background:#422006; color:#fdba74 !important; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-none { background:#3b0764; color:#e879f9 !important; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }

.stat-box {
    background: linear-gradient(135deg, #1a1d2e, #1e2040);
    border: 1px solid #252840;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}
.stat-number { font-size: 2rem; font-weight: 700; color: #6366f1 !important; font-family: 'DM Mono', monospace; }
.stat-label  { font-size: 0.8rem; color: #64748b !important; text-transform: uppercase; letter-spacing: 0.08em; }

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox > div > div {
    background: #1a1d2e !important;
    border: 1px solid #252840 !important;
    color: #f0f4ff !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
}

/* Buttons */
.stButton > button {
    background: #6366f1 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Dividers */
hr { border-color: #1e2130 !important; }

/* Success / error */
.stSuccess { background: #14532d !important; color: #86efac !important; border: none !important; border-radius: 8px !important; }
.stError   { background: #450a0a !important; color: #fca5a5 !important; border: none !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)


# ─── Database helpers ─────────────────────────────────────────────────────────
def load_data() -> dict:
    path = Path(DATABASE)
    if path.exists():
        content = path.read_text().strip()
        if content:
            return json.loads(content)
    return {"book": [], "member": []}


def save_data(data: dict):
    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=4, default=str)


def gen_id(prefix: str = "B") -> str:
    """Generate a short random ID like B-aX3kR"""
    chars = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    return f"{prefix}-{chars}"


# ─── Session state bootstrap ──────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data   # shorthand


# ─── Sidebar nav ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 LibraryOS")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["Dashboard", "Books", "Members", "Borrow / Return"],
        label_visibility="collapsed",
    )
    st.markdown("---")

    total_books   = len(data["book"])
    total_members = len(data["member"])
    total_borrows = sum(len(m["borrowed"]) for m in data["member"])

    st.markdown(f"**{total_books}** books · **{total_members}** members")
    st.markdown(f"**{total_borrows}** active borrows")


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown("# Library Dashboard")
    st.markdown("An overview of everything in the system.")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns(4)
    avail = sum(b["available_copies"] for b in data["book"])

    for col, num, label in [
        (c1, total_books,   "Total Books"),
        (c2, avail,         "Copies Available"),
        (c3, total_members, "Members"),
        (c4, total_borrows, "Active Borrows"),
    ]:
        col.markdown(
            f'<div class="stat-box"><div class="stat-number">{num}</div>'
            f'<div class="stat-label">{label}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### Recently Added Books")

    recent = sorted(data["book"], key=lambda b: b.get("added_on", ""), reverse=True)[:5]
    if not recent:
        st.info("No books added yet.")
    for b in recent:
        avail_copies = b["available_copies"]
        badge_cls  = "badge-ok" if avail_copies > 2 else ("badge-warn" if avail_copies > 0 else "badge-none")
        badge_text = f"{avail_copies} available"
        st.markdown(
            f'<div class="card">'
            f'<span class="book-id">{b["id"]}</span>&nbsp;&nbsp;'
            f'<span class="badge {badge_cls}">{badge_text}</span>'
            f'<div class="book-title">{b["title"]}</div>'
            f'<div class="book-meta">by {b["author"]} · {b["total_copies"]} total copies</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
#  BOOKS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Books":
    st.markdown("# Books")

    tab_list, tab_add = st.tabs(["📋  All Books", "➕  Add Book"])

    # ── List ──────────────────────────────────────────────────────────────────
    with tab_list:
        if not data["book"]:
            st.info("No books in the library yet.")
        else:
            search = st.text_input("Search by title or author", placeholder="e.g. Harry Potter")
            filtered = [
                b for b in data["book"]
                if search.lower() in b["title"].lower() or search.lower() in b["author"].lower()
            ] if search else data["book"]

            st.markdown(f"Showing **{len(filtered)}** book(s)")
            for b in filtered:
                avail_copies = b["available_copies"]
                badge_cls  = "badge-ok" if avail_copies > 2 else ("badge-warn" if avail_copies > 0 else "badge-none")
                st.markdown(
                    f'<div class="card">'
                    f'<span class="book-id">{b["id"]}</span>&nbsp;&nbsp;'
                    f'<span class="{badge_cls}">{avail_copies} / {b["total_copies"]} available</span>'
                    f'<div class="book-title">{b["title"]}</div>'
                    f'<div class="book-meta">by {b["author"]}</div>'
                    f'<div class="book-meta">Added: {b.get("added_on", "—")}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # ── Add ───────────────────────────────────────────────────────────────────
    with tab_add:
        with st.form("add_book_form"):
            st.markdown("#### New Book Details")
            title   = st.text_input("Title")
            author  = st.text_input("Author")
            copies  = st.number_input("Number of Copies", min_value=1, step=1, value=1)
            submit  = st.form_submit_button("Add Book")

        if submit:
            if not title.strip() or not author.strip():
                st.error("Title and Author cannot be empty.")
            else:
                book = {
                    "id":               gen_id("B"),
                    "title":            title.strip(),
                    "author":           author.strip(),
                    "total_copies":     int(copies),
                    "available_copies": int(copies),
                    "added_on":         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                data["book"].append(book)
                save_data(data)
                st.success(f'✅ "{title}" added with ID `{book["id"]}`')


# ══════════════════════════════════════════════════════════════════════════════
#  MEMBERS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Members":
    st.markdown("# Members")

    tab_list, tab_add = st.tabs(["📋  All Members", "➕  Add Member"])

    # ── List ──────────────────────────────────────────────────────────────────
    with tab_list:
        if not data["member"]:
            st.info("No members registered yet.")
        else:
            for m in data["member"]:
                borrow_count = len(m["borrowed"])
                st.markdown(
                    f'<div class="card">'
                    f'<span class="member-id">{m["id"]}</span>'
                    f'<div class="book-title">{m["name"]}</div>'
                    f'<div class="book-meta">{m["email"]}</div>'
                    f'<div class="book-meta" style="margin-top:6px">'
                    f'<span class="{"badge-warn" if borrow_count else "badge-ok"}">'
                    f'{borrow_count} book(s) currently borrowed</span></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if borrow_count:
                    with st.expander(f"View borrows for {m['name']}"):
                        for bk in m["borrowed"]:
                            st.markdown(
                                f'- **{bk["title"]}** `{bk["book_id"]}` — borrowed on {bk["borrow_on"]}'
                            )

    # ── Add ───────────────────────────────────────────────────────────────────
    with tab_add:
        with st.form("add_member_form"):
            st.markdown("#### New Member Details")
            name  = st.text_input("Full Name")
            email = st.text_input("Email")
            submit = st.form_submit_button("Register Member")

        if submit:
            if not name.strip() or not email.strip():
                st.error("Name and Email cannot be empty.")
            else:
                member = {
                    "id":       gen_id("M"),
                    "name":     name.strip(),
                    "email":    email.strip(),
                    "borrowed": [],
                }
                data["member"].append(member)
                save_data(data)
                st.success(f'✅ {name} registered with ID `{member["id"]}`')


# ══════════════════════════════════════════════════════════════════════════════
#  BORROW / RETURN
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Borrow / Return":
    st.markdown("# Borrow & Return")

    tab_borrow, tab_return = st.tabs(["📤  Borrow a Book", "📥  Return a Book"])

    # ── Borrow ────────────────────────────────────────────────────────────────
    with tab_borrow:
        if not data["member"]:
            st.warning("No members registered. Add a member first.")
        elif not data["book"]:
            st.warning("No books in the library. Add a book first.")
        else:
            member_opts = {f'{m["id"]} — {m["name"]}': m for m in data["member"]}
            available_books = [b for b in data["book"] if b["available_copies"] > 0]
            book_opts = {f'{b["id"]} — {b["title"]} ({b["available_copies"]} left)': b for b in available_books}

            with st.form("borrow_form"):
                selected_member = st.selectbox("Select Member", list(member_opts.keys()))
                if book_opts:
                    selected_book = st.selectbox("Select Book", list(book_opts.keys()))
                    submit = st.form_submit_button("Borrow Book")
                else:
                    st.warning("No copies available to borrow right now.")
                    submit = st.form_submit_button("Borrow Book", disabled=True)

            if submit and book_opts:
                member = member_opts[selected_member]
                book   = book_opts[selected_book]
                entry  = {
                    "book_id":   book["id"],
                    "title":     book["title"],
                    "borrow_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                member["borrowed"].append(entry)
                book["available_copies"] -= 1
                save_data(data)
                st.success(f'✅ **{member["name"]}** borrowed **{book["title"]}** successfully!')

    # ── Return ────────────────────────────────────────────────────────────────
    with tab_return:
        members_with_borrows = [m for m in data["member"] if m["borrowed"]]

        if not members_with_borrows:
            st.info("No active borrows in the system.")
        else:
            member_opts = {f'{m["id"]} — {m["name"]}': m for m in members_with_borrows}

            with st.form("return_form"):
                selected_member = st.selectbox("Select Member", list(member_opts.keys()))
                member = member_opts[selected_member]

                borrow_opts = {
                    f'{b["title"]} (borrowed {b["borrow_on"]})': i
                    for i, b in enumerate(member["borrowed"])
                }
                selected_borrow = st.selectbox("Select Book to Return", list(borrow_opts.keys()))
                submit = st.form_submit_button("Return Book")

            if submit:
                idx     = borrow_opts[selected_borrow]
                entry   = member["borrowed"].pop(idx)

                # Restore available copy
                for bk in data["book"]:
                    if bk["id"] == entry["book_id"]:
                        bk["available_copies"] += 1
                        break

                save_data(data)
                st.success(f'✅ **{entry["title"]}** returned successfully by **{member["name"]}**!')
