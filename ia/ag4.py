"""Algoritmo genético didático para montar horários de turmas escolares.

Cada gene representa uma aula e guarda o horário e o professor escolhido.
"""

from collections.abc import Callable
from random import Random as GeradorAleatorio
from typing import TypedDict

Gene = tuple[int, str]
Individuo = list[Gene]
Populacao = list[Individuo]


class Aula(TypedDict):
    turma: str
    disciplina: str
    professores: tuple[str, ...]


class AlgoritmoGenetico:
    DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
    PERIODOS_POR_DIA = 4
    TOTAL_HORARIOS = len(DIAS) * PERIODOS_POR_DIA
    TURMAS = ("6º A", "6º B", "6º C")

    def __init__(
        self,
        aleatorio: GeradorAleatorio | None = None,
        tamanho_populacao: int = 60,
        taxa_elitismo: float = 0.10,
        taxa_selecao: float = 0.50,
        taxa_cruzamento: float = 0.80,
        taxa_mutacao: float = 0.08,
    ) -> None:
        self._gerador_aleatorio = aleatorio or GeradorAleatorio()
        self._taxa_elitismo = taxa_elitismo
        self._taxa_selecao = taxa_selecao
        self._taxa_cruzamento = taxa_cruzamento
        self._taxa_mutacao = taxa_mutacao

        # Cada turma tem 20 aulas semanais, uma para cada período.
        # Matemática e Português podem ser atribuídas a qualquer um dos dois
        # professores da disciplina. As demais disciplinas têm um professor.
        grade_curricular = [
            ("Matemática", ("Ana", "Helena"), 5),
            ("Português", ("Bruno", "Marcos"), 5),
            ("História", ("Carla",), 2),
            ("Geografia", ("Diego",), 2),
            ("Ciências", ("Elisa",), 2),
            ("Ed. Física", ("Fabio",), 2),
            ("Inglês", ("Gabriela",), 2),
        ]
        self._aulas: list[Aula] = []
        for turma in self.TURMAS:
            for disciplina, professores, aulas_semanais in grade_curricular:
                for _ in range(aulas_semanais):
                    self._aulas.append(
                        {
                            "turma": turma,
                            "disciplina": disciplina,
                            "professores": professores,
                        }
                    )

        self._grupos_de_aulas: dict[tuple[str, str], list[int]] = {}
        for indice, aula in enumerate(self._aulas):
            chave = (aula["turma"], aula["disciplina"])
            if chave not in self._grupos_de_aulas:
                self._grupos_de_aulas[chave] = []
            self._grupos_de_aulas[chave].append(indice)

        self._populacao = self._criar_populacao(tamanho_populacao)
        self._ordenar_populacao()

    def _sortear_probabilidade(self) -> float:
        return self._gerador_aleatorio.random()

    def _sortear_horario(self) -> int:
        return self._gerador_aleatorio.randrange(self.TOTAL_HORARIOS)

    def _criar_populacao(self, tamanho_populacao: int) -> Populacao:
        populacao: Populacao = []
        for _ in range(tamanho_populacao):
            professor_por_grupo = {
                chave: self._gerador_aleatorio.choice(self._aulas[indices[0]]["professores"])
                for chave, indices in self._grupos_de_aulas.items()
            }
            individuo = [
                (
                    self._sortear_horario(),
                    professor_por_grupo[(aula["turma"], aula["disciplina"])],
                )
                for aula in self._aulas
            ]
            populacao.append(individuo)
        return populacao

    def _calcular_conflitos(self, individuo: Individuo) -> int:
        """Conta choques de horário e violações das regras das disciplinas."""
        conflitos = 0
        professor_por_disciplina: dict[tuple[str, str], str] = {}

        for indice, aula in enumerate(self._aulas):
            _, professor = individuo[indice]
            chave_disciplina = (aula["turma"], aula["disciplina"])
            professor_anterior = professor_por_disciplina.get(chave_disciplina)
            if professor_anterior is not None and professor_anterior != professor:
                # Hard constraint: a mesma turma e disciplina usam um professor só.
                conflitos += 1
            else:
                professor_por_disciplina[chave_disciplina] = professor

            horario, _ = individuo[indice]
            for outro_indice in range(indice + 1, len(self._aulas)):
                outro_horario, outro_professor = individuo[outro_indice]
                if horario != outro_horario:
                    continue
                outra_aula = self._aulas[outro_indice]
                # Uma turma ou professor não pode ter duas aulas simultâneas.
                if aula["turma"] == outra_aula["turma"] or professor == outro_professor:
                    conflitos += 1

        return conflitos

    def _ordenar_populacao(self) -> None:
        self._populacao.sort(key=self._calcular_conflitos)

    def _selecionar_elite(self) -> Populacao:
        quantidade = max(1, round(len(self._populacao) * self._taxa_elitismo))
        return [individuo.copy() for individuo in self._populacao[:quantidade]]

    def _selecionar_pais(self) -> Populacao:
        """Escolhe o melhor de três indivíduos sorteados em cada torneio."""
        quantidade = max(2, round(len(self._populacao) * self._taxa_selecao))
        pais: Populacao = []
        for _ in range(quantidade):
            candidatos = [self._gerador_aleatorio.choice(self._populacao) for _ in range(3)]
            pais.append(min(candidatos, key=self._calcular_conflitos))
        return pais

    def _cruzar_individuos(
        self, primeiro_pai: Individuo, segundo_pai: Individuo
    ) -> tuple[Individuo, Individuo]:
        if self._sortear_probabilidade() >= self._taxa_cruzamento:
            return primeiro_pai.copy(), segundo_pai.copy()

        # Cruzamento de um ponto: os filhos combinam trechos dos dois pais.
        ponto = self._gerador_aleatorio.randint(1, len(primeiro_pai) - 1)
        primeiro_filho = primeiro_pai[:ponto] + segundo_pai[ponto:]
        segundo_filho = segundo_pai[:ponto] + primeiro_pai[ponto:]
        self._normalizar_professores(primeiro_filho)
        self._normalizar_professores(segundo_filho)
        return primeiro_filho, segundo_filho

    def _normalizar_professores(self, individuo: Individuo) -> None:
        """Mantém um único professor por turma e disciplina após o cruzamento."""
        for indices in self._grupos_de_aulas.values():
            contagem_professores: dict[str, int] = {}
            for indice in indices:
                professor = individuo[indice][1]
                contagem_professores[professor] = contagem_professores.get(professor, 0) + 1
            professor_escolhido = max(
                contagem_professores, key=lambda professor: contagem_professores[professor]
            )
            for indice in indices:
                horario, _ = individuo[indice]
                individuo[indice] = (horario, professor_escolhido)

    def _cruzar_pais(self, pais: Populacao, quantidade_filhos: int) -> Populacao:
        filhos: Populacao = []
        while len(filhos) < quantidade_filhos:
            primeiro_pai = self._gerador_aleatorio.choice(pais)
            segundo_pai = self._gerador_aleatorio.choice(pais)
            primeiro_filho, segundo_filho = self._cruzar_individuos(
                primeiro_pai, segundo_pai
            )
            filhos.append(primeiro_filho)
            if len(filhos) < quantidade_filhos:
                filhos.append(segundo_filho)
        return filhos

    def _mutar_filhos(self, filhos: Populacao) -> None:
        for individuo in filhos:
            for indice_gene, aula in enumerate(self._aulas):
                if self._sortear_probabilidade() >= self._taxa_mutacao:
                    continue

                horario, professor = individuo[indice_gene]
                if self._sortear_probabilidade() < 0.5:
                    horario = self._sortear_horario()
                else:
                    chave = (aula["turma"], aula["disciplina"])
                    professor = self._gerador_aleatorio.choice(aula["professores"])
                    for indice_aula in self._grupos_de_aulas[chave]:
                        horario_aula, _ = individuo[indice_aula]
                        individuo[indice_aula] = (horario_aula, professor)
                individuo[indice_gene] = (horario, professor)

    def _consolidar_populacao(self, filhos: Populacao, elite: Populacao) -> None:
        self._populacao = filhos + elite
        self._ordenar_populacao()

    def _iterar(self) -> None:
        elite = self._selecionar_elite()
        pais = self._selecionar_pais()
        filhos = self._cruzar_pais(pais, len(self._populacao) - len(elite))
        self._mutar_filhos(filhos)
        self._consolidar_populacao(filhos, elite)

    def obter_individuo(self, posicao_relativa: float) -> tuple[Individuo, int]:
        posicao = round((len(self._populacao) - 1) * posicao_relativa)
        individuo = self._populacao[posicao]
        return individuo.copy(), self._calcular_conflitos(individuo)

    def executar(
        self,
        geracoes: int,
        ao_final_da_geracao: Callable[[int, "AlgoritmoGenetico"], None] | None = None,
    ) -> None:
        for geracao in range(1, geracoes + 1):
            self._iterar()
            if ao_final_da_geracao is not None:
                ao_final_da_geracao(geracao, self)
            if self._calcular_conflitos(self._populacao[0]) == 0:
                break

    def imprimir_horario(self, individuo: Individuo) -> None:
        for turma in self.TURMAS:
            print(f"\nHorário da turma {turma}")
            for indice_dia, dia in enumerate(self.DIAS):
                print(f"\n{dia}")
                for periodo in range(self.PERIODOS_POR_DIA):
                    horario = indice_dia * self.PERIODOS_POR_DIA + periodo
                    aulas_no_periodo = [
                        (aula, individuo[indice][1])
                        for indice, aula in enumerate(self._aulas)
                        if individuo[indice][0] == horario and aula["turma"] == turma
                    ]
                    descricoes = "; ".join(
                        f"{aula['disciplina']} ({professor})"
                        for aula, professor in aulas_no_periodo
                    )
                    print(
                        f"  {periodo + 1}º período: "
                        f"{descricoes if descricoes else 'Livre'}"
                    )


def principal() -> None:
    algoritmo = AlgoritmoGenetico(aleatorio=GeradorAleatorio(67))
    algoritmo.executar(geracoes=500)
    horario, conflitos = algoritmo.obter_individuo(0)
    print(f"\nMelhor horário encontrado: {conflitos} conflitos")
    algoritmo.imprimir_horario(horario)


if __name__ == "__main__":
    principal()
