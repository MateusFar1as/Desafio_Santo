# FUNÇÕES
def asteristico(n):
    lista = []
    aste = ""

    for i in range(n):
        aste = aste + "*"
        lista.append(aste)

    print(lista)


def diferenca(n = []):
    dif = abs(n[0] - n[1])
    menorDiferenca = []
    
    for i in range(len(n)):
        for j in range(len(n)):
            if i != j:
                if n[i] - n[j] <= dif and n[i] - n[j] >= 0:
                    if n[i] - n[j] < dif:
                        dif = abs(n[i] - n[j])
                        menorDiferenca = [[n[i],n[j]]]
                    else:
                        if [n[i],n[j]] not in menorDiferenca: menorDiferenca.append([n[i],n[j]]) 
    print(menorDiferenca)


def subConjuntos(n = []):
    subConj = []

    def voltar(comb, inicio):
        subConj.append(list(comb))

        for i in range(inicio, len(n)):
            comb.append(n[i])
            voltar(comb, i + 1)
            comb.pop()

    voltar([], 0)
    print(subConj)


# EXECUÇÕES DAS FUNÇÕES
asteristico(8)

print()

n = [3, 8, 50, 5, 1, 18, 12]
diferenca(n)

print()

subConjuntos([1,2])