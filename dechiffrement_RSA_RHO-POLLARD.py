from math import gcd
import time


def rho_pollard(n):
    def f(x):
        return x*x+1

    start_time = time.perf_counter()

    x, y, d = 2, 2, 1

    while d==1:
        x = f(x) % n
        y = f(f(y)) % n
        #print (x,y)
        d = gcd(x-y, n)

    elapsed_time = time.perf_counter() - start_time

    if d == n:
        raise ValueError("Échec de la factorisation : facteur trivial trouvé.")
    
    return d , elapsed_time

#print(rho_pollard(978190915167475073737))


def dechiffrement_RSA(n,e):
    p, temps_facto = rho_pollard(n)
    q = n // p

    # 2. Calcul de l'indicatrice d'Euler phi(n)
    phi_n = (p - 1) * (q - 1)

    # 3. Calcul de la clé privée d (inverse modulaire de e modulo phi(n))
    d = pow(e, -1, phi_n)

    print(f"Temps de factorisation : {temps_facto:.6f} s")
    print(f"p = {p}")
    print(f"q = {q}")
    print(f"phi(n) = {phi_n}")
    print(f"d = {d}")
    return n , d


l=[(7599016027,65537),
   (7599016027,17),
   (1002682255717,65537),
   (1002682255717,5),
   (9782620167021197,65537),
   (9782620167021197,17),
   (9782620167021197,2237),
   (3824926627,65537),
   #(978190915167475073737,65537)
   ]

for i  in l:
    print(f"pour N={i[0]} et e={i[1]}")
    dechiffrement_RSA(i[0],i[1])
    print("----------------------------------")