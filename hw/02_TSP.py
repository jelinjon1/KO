# traveling salesman problem

# 1
# naivní řešení je přes ten součet po řádcích a sloupcích, čím zajistíme že do vertexu vejdeme a z něj následně odejdeme
# jen jednou, ale neřeší to problém s tím když nám tam vzniknou nějaký disjunktní kružnice jako řešení

# approach je přes čas navštívení vertexu Si, kde chceme aby pro i,j kde vede hrana z i->j kterou jsme vzali, tak
# Si + cij <= Sj + M(1 - xij)
# pro všechna i z V a j z V \ {1}



# 2
# Alternativní formulace s časem ne pro vrcholy, ale pro hrany
# yij \in Z+0
# for all i,j in E
# yij pujde pro hrany od n-1 do 1
# pokud hrana není vybraná, hodnota je 0

# yij <= (n - 1) xij    for all ij in E

# pro všechny hrany pak chceme
# součet yij všech hran které vedou do uzlu j bez 1 
# se rovná součet yjk všech hran které vedou ven z uzlu j
# podmínka neplatí pro jeden uzel (začátek/konec) pro kterej uděláme vyjímku

# extra podmnka pro start
# součet hran vedoucích do start + (n - 1) se musí rovnat součtu všcech který vedou ze startu ven



# 3
# lazy constraints
# zadáme jen základní část podmínek, necháme si udělat řešení
# zkontrolujeme jestli je feasible
# pokud ne upravíme model tak aby se tam nevyskytlo to nalezené řešení a opakujeme

# pokud nalezneme v tomhle alg více kružnic naivní implementací
# vezmeme jen seznam vrcholů, který jí tvoří a na další run přidáme pravidlo který
# zakáže konkrétně její existenci


# image shredding

# budeme brát pásky obrázku jako vrcholy v grafu a hledáme cestu mezi vrcholy, jako posloupnost pásků obrázku

# prevedeme shortest hamiltonian path problem na tsp
# uděláme asi pomocí arbitrárního vertexu, který spojíme s každým ostatním vertexem a dáme hranám cenu 0
# řešení tak nemusí bejt zacyklenej obrázek kde levej a pravej edge sedí, ale rozloží se nám to jakoby

# vzdálenost počítat přes numpy jinak na brute neprojde
