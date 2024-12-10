import matplotlib.pyplot as plt
import numpy as np
from random import sample


def cria_individuo(config_size: int = 20) -> np.ndarray:
    """Um indivíduo é uma combinação aleatória de números"""
    min, max = 1, config_size
    return np.array(sample(range(min, max + 1), max))


def gerar_custo(x: np.ndarray, y: np.ndarray) -> np.matrix:
    """Matriz de custo de todos para todos, grafo completo"""
    if len(x) != len(y):
        raise ValueError("x e y devem ter o mesmo tamanho!")
    custo = np.empty([len(x), len(y)], np.float64)
    for i in range(len(x)):
        for j in range(len(y)):
            custo[i, j] = np.sqrt((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2)
    return np.matrix(custo)


def calc_aptidao(individuo: np.ndarray, custo: np.matrix) -> float:
    """Retorna a aptidão de um indivíduo"""
    if len(individuo) != len(custo):
        raise ValueError("Ambos devem ter o mesmo tamanho!")
    individuo = np.append(individuo, individuo[0])  # puxadinho
    # np.append cria uma cópia, array original não é alterado
    aptidao = 0
    for i in range(len(individuo) - 1):
        aptidao += custo[individuo[i] - 1, individuo[i + 1] - 1]
    return aptidao


def calc_probabilidade(populacao: list[dict]) -> list:
    """Adiciona o atributo 'probabilidade' aos indivíduos da população"""
    # Usando o método passado na lista de exercício 3
    divisor = 0
    for i in populacao:
        divisor += 1 / i["aptidao"]
    return [((1 / i["aptidao"]) / divisor) for i in populacao]


def selecionar_pais(populacao: list[dict], qtd_pares: int) -> list[list]:
    """Retorna pares de chaves do indivíduos da população"""
    prob = calc_probabilidade(populacao)  # Probabilidade de cada indivíduo
    return [
        list(np.random.choice(len(populacao), 2, False, prob)) for i in range(qtd_pares)
    ]


def crossover(config_pai1: list, config_pai2: list) -> list[list]:
    """Realiza o crossover entre dois pais e gera dois filhos como resultado"""
    rand_index = np.random.randint(len(config_pai1))
    # .copy() garante que os pais não sejam alterados
    filho1, filho2 = config_pai1.copy(), config_pai2.copy()
    filho1[rand_index], filho2[rand_index] = filho2[rand_index], filho1[rand_index]
    index = rand_index + 1
    while len(filho1) != len(set(filho1)):  # Enquanto houver duplicatas
        index = 0 if (index == len(filho1)) else index
        if filho1[rand_index] == filho1[index]:
            filho1[index], filho2[index] = filho2[index], filho1[index]  # troca
            rand_index = index
        index += 1
    return [filho1, filho2]


def mutacao(config: list) -> None:
    """Realiza a mutação do indivíduo"""
    index1 = np.random.randint(len(config))
    index2 = np.random.randint(len(config))
    config[index1], config[index2] = config[index2], config[index1]


def gerar_filhos(populacao: list[dict], pais: list[list]) -> list[np.ndarray]:
    """Gera dois filhos para cada par de pais, realiza mutação antes de retornar os filhos"""
    filhos = []
    for pai in pais:
        config1, config2 = populacao[pai[0]]["config"], populacao[pai[1]]["config"]
        filho1, filho2 = crossover(config1, config2)  # crossover
        mutacao(filho1)  # mutação
        mutacao(filho2)
        filhos.extend((filho1, filho2))
    return filhos


def nova_geracao(populacao: list[dict], custo: np.matrix) -> list[dict]:
    """Gera uma nova geração a partir da população original"""
    pop = populacao.copy()  # Não altera população original
    # Ordena por aptidão e seleciona a melhor metade
    pop = sorted(pop, key=lambda item: item["aptidao"])[: len(pop) // 2]
    # Seleciona os pais
    pais = selecionar_pais(pop, qtd_pares=len(pop) // 2)
    # Gera os filhos a partir dos pais
    filhos = gerar_filhos(pop, pais)
    # Insere os filhos na população
    for filho in filhos:
        aptidao = calc_aptidao(filho, custo)
        pop.append({"config": filho, "aptidao": aptidao})
    return pop


def print_individuos(populacao: list[dict]) -> None:
    """Exibi a configuração dos indivíduos presentes na população"""
    individuos = [list(i["config"]) for i in populacao]
    for i in individuos:
        print(i)


if __name__ == "__main__":
    data = np.loadtxt("cidades.mat")
    x, y = data[0], data[1]

    populacao = []
    custo = gerar_custo(x, y)

    # Gera população inicial de 20 indivíduos
    for _ in range(20):
        individuo = cria_individuo()
        aptidao = calc_aptidao(individuo, custo)
        populacao.append({"config": individuo, "aptidao": aptidao})

    print("Tamanho da população:", len(populacao))
    print("População inicial:")
    print(sorted(populacao, key=lambda item: item["aptidao"]))

    for _ in range(10000):
        populacao = nova_geracao(populacao, custo)

    print("População final:")
    print(sorted(populacao, key=lambda item: item["aptidao"]))

    print("Número de cidades:", len(custo))
    print("Melhor custo:", populacao[0]["aptidao"])
    print("Melhor solução:", populacao[0]["config"])

    # Gráfico do caminho encontrado
    x_copy, y_copy = x.copy(), y.copy()
    for k, v in enumerate(populacao[0]["config"]):
        x[k], y[k] = x_copy[v - 1], y_copy[v - 1]
    x = np.append(x, x[0])  # puxadinho
    y = np.append(y, y[0])  # para completar o ciclo

    plt.plot(x, y)
    plt.plot(x, y, "o")
    plt.plot(x[0], y[0], "X")  # Marca o ponto de partida
    plt.show()
