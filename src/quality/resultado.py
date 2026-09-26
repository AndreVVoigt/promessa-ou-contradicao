from dataclasses import dataclass, field


@dataclass
class ResultadoCheck:
    nome: str                          # identificação do check no relatório
    passou: bool                       # True se nenhuma linha violou a regra
    violacoes: int = 0                 # quantas linhas violaram
    ids: list[str] = field(default_factory=list)   # quais linhas violaram
    detalhe: str = ""                  # mensagem curta opcional

    def __str__(self) -> str:
        status = "PASSOU" if self.passou else "FALHOU"
        if self.passou:
            return f"[{status}] {self.nome}"
        amostra = ", ".join(self.ids[:5])
        if len(self.ids) > 5:
            amostra += f" (+{len(self.ids) - 5})"
        return f"[{status}] {self.nome} — {self.violacoes} violação(ões): {amostra}"
