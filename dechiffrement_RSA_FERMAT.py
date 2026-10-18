import math


def fermat_factorization(n):
    a = math.isqrt(n)+1 # E(sqrt(n)) + 1 
    
    i=0
    while True:
        b2 = a**2 - n
        b = math.isqrt(b2)
        if b * b == b2:
            p = a - b
            q = a + b
            return p, q , i
        a += 1
        i+=1





def dechiffrement_RSA(n,e):
    p, q , i = fermat_factorization(n)

    # 2. Calcul de l'indicatrice d'Euler phi(n)
    phi_n = (p - 1) * (q - 1)

    # 3. Calcul de la clé privée d (inverse modulaire de e modulo phi(n))
    d = pow(e, -1, phi_n)

    print(f"nombre d'etape : {i}")
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

print("pour N=978190915167475073737 et e=65537")
print("impossible avec notre machine actuel plusieur heur sans resultat")
print("----------------------------------")






# fonction de base pour le chiffrement et dechifremment 

#---------------------------------------------------------------------------------------------------------------------

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

#-------------------------------------------------------------------------------------------------------------------

liste_a_dechiffre = [
    {
        "n": 3151465243,
        "e": 65537, 
        "chiffre": "EFGNCZS BBNKKEN KFDIPZJ AAXXVYU HHZDLSH HPMTKYO KBHZXPG HDYAZHF DCBUURJ HRJTJNK BXJHBLG EYXPAGC EVQJCFE"
        },
    {
        "n": 854020749013,
        "e": 65537, 
        "chiffre": "CEJFXEDPW EAEGZIIFO EBGRSQIBU BMKFIICWY DNYTHKIZG CIFOTGUTY BLCNXXMVG ARNMIUBCT AFICKUFJX BSYGNXLPL AENKAGRJQ DZRPKWIXN AXSWXMAON DLLPXBGZH CLWZTGZPJ CSUBWPHIR BGUKRYYWM ABAGUTBJH BPKWIVLSG"
        },
    {
        "n": 219836442089027,
        "e": 65537,
        "chiffre": "ADTLHDDUCUT ACKPIHCMUYX AASFFFLBEGH AWQSJVAVAQZ BDJCYHJDFYS BKZJZZEMGIA BMOJWIMOBFH AJMRBYUWAPD BMLTWVTASTA ABGVVZGIONU BGLUNOVBAZM BKNPPVMRYUC"
        },
    {
        "n": 67893477472934171, 
        "e": 65537, 
        "chiffre": "GPTAZNJAFBVA RNVXFHNLMYBQ RTSIFJUJWYWJ KMBSOILJPBQM OYNKTARYZMXX OBAMONNGJUMJ FGXTBOFZWPPA RIJNYYCPCPEC ESBPKIPPQVMY NDYEESXRLWKS FJPLQGCVBTUO AIBLFGRECJWT QPDPYTOUUWUQ DFADBVHLJTIR BKRHLPPPKXKR"
        },
    {
        "n": 17627427682441225681, 
        "e": 65537, 
        "chiffre": "BUOZXKCVBULGDZ AKWOCLVOIAUEYF CRXHZQIGEHOXHV DKYRGKZJZMVCQH GAOVSOXJJYEGKD GKYCNOSKFHSJQT CZXJGPXZFXARJU DEOAXHDXDLSWBU FLKHEIBENUMGPE DMNDCXXIZECHWR GNCEONLOTYWBFK BTBUAISRZBKFJW AWXVXDLDFEFGLC GIEUWRYSYKICYB BBIVNYBRIGTBLR CAHPQXZBBNEJAS"
        }

]



#test
#chiffre = "LHVNSRR EVMEZPA IRNUACM KIIWFSB CQBBVIE KYYFCOG ESSESRD DHDXDHI IFSQCDC FITRAIB EECBIPE MJEQLTU FZWPBMR GXHXIJD HCVDCDJ BLVOMLX KTDQSYU"
#n , d = dechiffrement_RSA(3824926627,65537)
#print(dechiffrer(chiffre,d , n))
print("-------------------------------------")

j=0
for i in liste_a_dechiffre:
    j+=1
    print(f"niveau : {j}")
    print(f"pour N={i["n"]} et e={i["e"]}")
    n , d = dechiffrement_RSA(i["n"],i["e"])
    print(dechiffrer(i["chiffre"],d , n))
    print("-----------------------------------")