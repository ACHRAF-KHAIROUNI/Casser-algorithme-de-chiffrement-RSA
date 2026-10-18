import math
import numpy as np
from numba import cuda

# -------------------------------------------------------------------------
# 1. KERNEL CUDA : Test parallèle des candidats 'a' pour Fermat
# -------------------------------------------------------------------------
@cuda.jit
def fermat_kernel(n, a_base, chunk_size, out_found, out_pq):
    """
    Chaque thread prend en charge un candidat :
    a = a_base + thread_idx
    """
    idx = cuda.grid(1)
    if idx >= chunk_size:
        return

    # Si un autre thread a déjà trouvé la solution, on s'arrête immédiatement
    if out_found[0] != 0:
        return

    a = a_base + idx
    b2 = a * a - n

    if b2 >= 0:
        b = int(math.isqrt(b2))
        if b * b == b2:
            # Carré parfait détecté !
            if cuda.atomic.cas(out_found, 0, 1) == 0:
                out_pq[0] = a - b  # p
                out_pq[1] = a + b  # q


# -------------------------------------------------------------------------
# 2. Factorisation hybride GPU (avec fallback CPU pour > 64 bits)
# -------------------------------------------------------------------------
def fermat_factorization_gpu(n, chunk_size=2_000_000):
    # Si le nombre dépasse la capacité uint64 du GPU, fallback propre sur CPU
    if n > np.iinfo(np.uint64).max or (math.isqrt(n) + chunk_size) > np.iinfo(np.uint64).max:
        return fermat_factorization_cpu(n)

    a_curr = math.isqrt(n)
    if a_curr * a_curr < n:
        a_curr += 1

    threads_per_block = 256
    blocks = (chunk_size + threads_per_block - 1) // threads_per_block

    # Tableaux de communication Host/Device
    d_found = cuda.to_device(np.zeros(1, dtype=np.int32))
    d_pq = cuda.to_device(np.zeros(2, dtype=np.uint64))

    total_steps = 0

    while True:
        # Exécution du kernel sur GPU par blocs de candidats
        fermat_kernel[blocks, threads_per_block](
            np.uint64(n), np.uint64(a_curr), chunk_size, d_found, d_pq
        )
        cuda.synchronize()

        found = d_found.copy_to_host()[0]
        if found:
            pq = d_pq.copy_to_host()
            p, q = int(pq[0]), int(pq[1])
            total_steps += int((p + q) // 2 - (math.isqrt(n) + 1))
            return p, q, max(0, total_steps)

        # Passer au lot suivant de candidats
        a_curr += chunk_size
        total_steps += chunk_size


def fermat_factorization_cpu(n):
    """Algorithme standard pour les entiers arbitrairement grands (> 64 bits)."""
    a = math.isqrt(n)
    if a * a < n:
        a += 1
    i = 0
    while True:
        b2 = a * a - n
        b = math.isqrt(b2)
        if b * b == b2:
            return a - b, a + b, i
        a += 1
        i += 1


# -------------------------------------------------------------------------
# 3. Déchiffrement RSA
# -------------------------------------------------------------------------
def dechiffrement_RSA(n, e):
    # Choisir la factorisation GPU si compatible
    if cuda.is_available() and n <= np.iinfo(np.uint64).max:
        p, q, i = fermat_factorization_gpu(n)
    else:
        p, q, i = fermat_factorization_cpu(n)

    phi_n = (p - 1) * (q - 1)
    d = pow(e, -1, phi_n)

    print(f"nombre d'etapes : {i}")
    print(f"p = {p}")
    print(f"q = {q}")
    print(f"phi(n) = {phi_n}")
    print(f"d = {d}")


# -------------------------------------------------------------------------
# 4. Exécution sur votre liste de tests
# -------------------------------------------------------------------------
if __name__ == "__main__":
    l = [
        (7599016027, 65537),
        (7599016027, 17),
        (1002682255717, 65537),
        (1002682255717, 5),
        (9782620167021197, 65537),
        (9782620167021197, 17),
        (9782620167021197, 2237),
        (978190915167475073737, 65537),  # > 64-bit : bascule automatiquement sur CPU
    ]

    for n_val, e_val in l:
        print(f"Pour N = {n_val} et e = {e_val}")
        dechiffrement_RSA(n_val, e_val)
        print("-" * 40)