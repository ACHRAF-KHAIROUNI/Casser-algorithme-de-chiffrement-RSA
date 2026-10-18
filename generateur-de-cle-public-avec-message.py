# projet_rsa.py - RSA + Fermat + GUI (Python 3.14, tkinter) - chiffre affiche en LETTRES
import random, time, json, threading
from math import isqrt, gcd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ---------- 1. Outils mathématiques ----------
def est_premier(n):
    """Miller-Rabin deterministe (n < 3.3e24)"""
    if n < 2: return False
    pts = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for x in pts:
        if n % x == 0: return n == x
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in pts:
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else:
            return False
    return True

def premier_suivant(x):
    x |= 1
    while not est_premier(x): x += 2
    return x

def fermat(n):
    """Fermat : n = a^2 - b^2 = (a-b)(a+b)"""
    a = isqrt(n)
    if a * a < n: a += 1                    # a = ceil(sqrt(n))
    while True:
        b2 = a * a - n
        b = isqrt(b2)
        if b * b == b2:                     # b^2 carre parfait ?
            return a - b, a + b             # p, q
        a += 1

# ---------- 2. Generation de cles ----------
def generer_cles(bits):
    """n de 'bits' bits, p et q PROCHES (sinon Fermat est trop lent)"""
    k = bits // 2
    while True:
        p = premier_suivant(random.randrange(3 << (k - 2), 1 << k))   # 2 bits de poids fort a 1
        q = premier_suivant(p + random.randrange(2, 1 << max(2, k - 8)))  # ecart controle
        n = p * q
        if p == q or n.bit_length() != bits: continue
        phi = (p - 1) * (q - 1)
        for e in (65537, 17, 5, 3):                                   # e premier avec phi
            if e < phi and gcd(e, phi) == 1:
                return {"n": n, "e": e, "p": p, "q": q, "phi": phi, "d": pow(e, -1, phi)}

# ---------- 3. Chiffrement / dechiffrement (sortie en lettres A-Z) ----------
def taille_bloc(n):
    return (n.bit_length() - 1) // 8        # octets par bloc -> garantit M < n

def largeur(n):
    L = 1                                   # nb de lettres par bloc : 26^L > n
    while 26 ** L <= n: L += 1
    return L

def nb_en_lettres(c, L):                    # entier -> L lettres (base 26)
    s = ""
    for _ in range(L):
        c, r = divmod(c, 26); s = chr(65 + r) + s
    return s

def lettres_en_nb(s):                       # lettres -> entier
    c = 0
    for ch in s: c = c * 26 + (ord(ch) - 65)
    return c

def chiffrer(texte, e, n):
    data, t, L = texte.encode("utf-8"), taille_bloc(n), largeur(n)
    blocs = [pow(int.from_bytes(data[i:i+t], "big"), e, n) for i in range(0, len(data), t)]  # C = M^e mod n
    return " ".join(nb_en_lettres(c, L) for c in blocs)              # 1 mot = 1 bloc

def dechiffrer(chiffre, d, n):
    t, L = taille_bloc(n), largeur(n)
    s = "".join(ch for ch in chiffre.upper() if "A" <= ch <= "Z")    # ignore espaces / retours
    blocs = [lettres_en_nb(s[i:i+L]) for i in range(0, len(s), L)]
    data = b"".join(pow(c, d, n).to_bytes(t, "big").lstrip(b"\x00") for c in blocs)   # M = C^d mod n
    return data.decode("utf-8", errors="replace")

# ---------- 4. Attaque complete avec temps ----------
def attaque(n, e, chiffre):
    t0 = time.perf_counter(); p, q = fermat(n);            t1 = time.perf_counter()
    phi = (p - 1) * (q - 1); d = pow(e, -1, phi);          t2 = time.perf_counter()
    msg = dechiffrer(chiffre, d, n);                       t3 = time.perf_counter()
    return dict(p=p, q=q, phi=phi, d=d, msg=msg, t_fact=t1-t0, t_d=t2-t1, t_dec=t3-t2)

# ---------- 5. Interface graphique ----------
NIVEAUX = {"Niveau 1 - 32 bits (5 pts)": 32, "Niveau 2 - 40 bits (10 pts)": 40,
           "Niveau 3 - 48 bits (15 pts)": 48, "Niveau 4 - 56 bits (20 pts)": 56,
           "Niveau 5 - 64 bits (25 pts)": 64}

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Projet RSA - Fermat"); self.geometry("820x640")
        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True, padx=6, pady=6)
        self.f1, self.f2 = ttk.Frame(nb), ttk.Frame(nb)
        nb.add(self.f1, text="Chiffrer (envoyer)"); nb.add(self.f2, text="Dechiffrer (Fermat)")
        self.pack_chiffrer(); self.pack_dechiffrer()
        self.paquet = None

    def pack_chiffrer(self):
        f = self.f1
        ttk.Label(f, text="Message clair :").pack(anchor="w", padx=8, pady=(8, 0))
        self.e_msg = tk.Text(f, height=4); self.e_msg.pack(fill="x", padx=8)
        ligne = ttk.Frame(f); ligne.pack(fill="x", padx=8, pady=6)
        self.cb = ttk.Combobox(ligne, values=list(NIVEAUX), state="readonly", width=30)
        self.cb.current(0); self.cb.pack(side="left")
        ttk.Button(ligne, text="Generer cles + chiffrer", command=self.on_chiffrer).pack(side="left", padx=8)
        ttk.Button(ligne, text="Enregistrer (.json)", command=self.on_save).pack(side="left")
        self.out1 = tk.Text(f, height=22, wrap="word"); self.out1.pack(fill="both", expand=True, padx=8, pady=6)

    def on_chiffrer(self):
        msg = self.e_msg.get("1.0", "end").strip()
        if not msg: return messagebox.showwarning("Erreur", "Ecris un message.")
        k = generer_cles(NIVEAUX[self.cb.get()])
        chiffre = chiffrer(msg, k["e"], k["n"])
        self.paquet = {"n": k["n"], "e": k["e"], "chiffre": chiffre}     # PUBLIC : a envoyer au binome
        self.out1.delete("1.0", "end")
        self.out1.insert("end",
            f"n ({k['n'].bit_length()} bits) = {k['n']}\ne = {k['e']}\n"
            f"p = {k['p']}\nq = {k['q']}\nphi(n) = {k['phi']}\nd = {k['d']}   (PRIVE)\n\n"
            f"Message chiffre (lettres) :\n{chiffre}\n\nVerif : {dechiffrer(chiffre, k['d'], k['n'])}")

    def on_save(self):
        if not self.paquet: return messagebox.showwarning("Erreur", "Rien a enregistrer.")
        fn = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if fn:
            with open(fn, "w") as fh: json.dump(self.paquet, fh)

    def pack_dechiffrer(self):
        f = self.f2
        ligne = ttk.Frame(f); ligne.pack(fill="x", padx=8, pady=8)
        ttk.Button(ligne, text="Ouvrir fichier .json", command=self.on_open).pack(side="left")
        ttk.Button(ligne, text="Casser avec Fermat", command=self.on_casser).pack(side="left", padx=8)
        ttk.Label(f, text="Recu (JSON : n, e, chiffre) :").pack(anchor="w", padx=8)
        self.e_json = tk.Text(f, height=7, wrap="word"); self.e_json.pack(fill="x", padx=8)
        self.out2 = tk.Text(f, height=20); self.out2.pack(fill="both", expand=True, padx=8, pady=6)

    def on_open(self):
        fn = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if fn:
            self.e_json.delete("1.0", "end"); self.e_json.insert("end", open(fn).read())

    def on_casser(self):
        try:
            j = json.loads(self.e_json.get("1.0", "end"))
            n, e, chiffre = int(j["n"]), int(j["e"]), j["chiffre"]
        except Exception:
            return messagebox.showerror("Erreur", "JSON invalide.")
        self.out2.delete("1.0", "end"); self.out2.insert("end", "Fermat en cours...\n")
        def travail():                                   # thread : la fenetre ne gele pas
            r = attaque(n, e, chiffre)
            self.after(0, lambda: self.afficher(n, e, r))
        threading.Thread(target=travail, daemon=True).start()

    def afficher(self, n, e, r):
        self.out2.delete("1.0", "end")
        self.out2.insert("end",
            f"n = {n} ({n.bit_length()} bits)\ne = {e}\np = {r['p']}\nq = {r['q']}\n"
            f"phi(n) = {r['phi']}\nd = {r['d']}\n\n"
            f"Temps factorisation (p,q) : {r['t_fact']:.6f} s\n"
            f"Temps calcul de d         : {r['t_d']:.6f} s\n"
            f"Temps dechiffrement       : {r['t_dec']:.6f} s\n\n"
            f"MESSAGE DECHIFFRE :\n{r['msg']}")

if __name__ == "__main__":
    App().mainloop()
