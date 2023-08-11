class CodeParser:
    """Parse le code d'une classe ou d'une unité d'enseignement"""

    @staticmethod
    def est_code_classe(code: str) -> bool:
        separation_classe_magistrale = '-'
        separation_classe_pratique = '_'
        return separation_classe_magistrale in code or separation_classe_pratique in code

    @staticmethod
    def get_code_classe(code: str) -> str:
        return code[-1] if CodeParser.est_code_classe(code) else ""

    @staticmethod
    def get_code_unite_enseignement(code: str) -> str:
        return code[:-2] if CodeParser.est_code_classe(code) else code
