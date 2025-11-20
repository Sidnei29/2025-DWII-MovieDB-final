"""Serviço de gerenciamento de funções técnicas.

Este módulo fornece a camada de serviço para operações relacionadas a funções técnicas,
incluindo listagem de funções com contagem de pessoas, filtragem de pessoas por função
e obtenção de descrições de funções.

Classes principais:
    - FuncaoTecnicaService: Serviço principal com métodos para operações de funções técnicas
    - FuncaoTecnicaServiceError: Exceção customizada para operações do FuncaoTecnicaService
"""
import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.infra.modulos import db
from app.models.filme import FuncaoTecnica
from app.models.pessoa import Pessoa
from app.models.juncoes import EquipeTecnica


class FuncaoTecnicaServiceError(Exception):
    """Exceção customizada para operações do FuncaoTecnicaService."""
    pass


class FuncaoTecnicaService:
    """Serviço para operações relacionadas a funções técnicas.

    Centraliza a lógica de negócio relacionada a funções técnicas, separando-a dos modelos.
    Utiliza uma sessão SQLAlchemy configurável para permitir uso em diferentes contextos,
    como testes ou transações customizadas.
    """

    # Sessão padrão a ser utilizada quando nenhuma sessão é fornecida
    _default_session = db.session

    @classmethod
    def set_default_session(cls, session):
        """Define a sessão padrão a ser utilizada pelo serviço.

        Args:
            session: Sessão SQLAlchemy a ser utilizada como padrão
        """
        cls._default_session = session

    @classmethod
    def listar_funcoes_com_contagem(cls, session=None) -> list[dict]:
        """Lista todas as funções técnicas ativas com contagem de pessoas.

        Args:
            session: Sessão SQLAlchemy opcional. Se None, usa a sessão padrão da classe.

        Returns:
            list[dict]: Lista de dicionários com:
                - id: UUID da função técnica
                - nome: Nome da função técnica
                - count: Número de pessoas que executam esta função

        Raises:
            FuncaoTecnicaServiceError: Quando ocorre erro na operação

        Examples:
            >>> funcoes = FuncaoTecnicaService.listar_funcoes_com_contagem()
            >>> for funcao in funcoes:
            ...     print(f"{funcao['nome']}: {funcao['count']} pessoas")
        """
        if session is None:
            session = cls._default_session

        try:
            # Query para contar pessoas distintas por função técnica
            stmt = (
                select(
                    FuncaoTecnica.id,
                    FuncaoTecnica.nome,
                    func.count(func.distinct(EquipeTecnica.pessoa_id)).label('count')
                )
                .outerjoin(EquipeTecnica, FuncaoTecnica.id == EquipeTecnica.funcao_tecnica_id)
                .where(FuncaoTecnica.ativo == True)
                .group_by(FuncaoTecnica.id, FuncaoTecnica.nome)
                .having(func.count(func.distinct(EquipeTecnica.pessoa_id)) > 0)
                .order_by(FuncaoTecnica.nome)
            )

            resultado = session.execute(stmt).all()

            # Converte resultado para lista de dicionários
            funcoes = [
                {
                    'id': row.id,
                    'nome': row.nome,
                    'count': row.count
                }
                for row in resultado
            ]

            return funcoes

        except SQLAlchemyError as e:
            raise FuncaoTecnicaServiceError(
                f"Erro de banco de dados em {cls.__name__}.listar_funcoes_com_contagem: {str(e)}"
            ) from e
        except Exception as e:
            raise FuncaoTecnicaServiceError(
                f"Erro inesperado em {cls.__name__}.listar_funcoes_com_contagem: {str(e)}"
            ) from e

    @classmethod
    def listar_pessoas_por_funcao(cls,
                                  funcao_id: uuid.UUID,
                                  page: int = 1,
                                  per_page: int = 20,
                                  session=None):
        """Lista pessoas que executam uma função técnica específica com paginação.

        Args:
            funcao_id: UUID da função técnica
            page: Número da página (começa em 1). Default: 1
            per_page: Itens por página. Default: 20
            session: Sessão SQLAlchemy opcional. Se None, usa a sessão padrão da classe.

        Returns:
            Pagination: Objeto de paginação do Flask-SQLAlchemy contendo:
                - items: Lista de tuplas (Pessoa, film_count)
                - page: Página atual
                - pages: Total de páginas
                - per_page: Registros por página
                - total: Total de registros
                - has_next: Se há próxima página
                - has_prev: Se há página anterior

        Raises:
            FuncaoTecnicaServiceError: Quando ocorre erro na operação

        Examples:
            >>> # Listar primeira página de diretores
            >>> resultado = FuncaoTecnicaService.listar_pessoas_por_funcao(funcao_id)
            >>> for pessoa, film_count in resultado.items:
            ...     print(f"{pessoa.nome}: {film_count} filmes")

            >>> # Página específica
            >>> resultado = FuncaoTecnicaService.listar_pessoas_por_funcao(funcao_id, page=2, per_page=30)
        """
        if session is None:
            session = cls._default_session

        try:
            # Verifica se a função técnica existe
            try:
                funcao = FuncaoTecnica.get_by_id(funcao_id, raise_if_not_found=True, session=session)
            except FuncaoTecnica.RecordNotFoundError:
                raise FuncaoTecnicaServiceError(f"Função técnica não encontrada: {funcao_id}")

            # Query simplificada: buscar apenas Pessoa objects
            # Depois calcularemos a contagem de filmes separadamente
            stmt = (
                select(Pessoa)
                .join(EquipeTecnica, Pessoa.id == EquipeTecnica.pessoa_id)
                .where(EquipeTecnica.funcao_tecnica_id == funcao_id)
                .group_by(Pessoa.id)
                .order_by(Pessoa.nome)
            )

            # Aplica paginação
            pagination = db.paginate(
                stmt,
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # Para cada pessoa, calcula a contagem de filmes nesta função
            if pagination.items:
                new_items = []
                for pessoa in pagination.items:
                    # Conta quantos filmes esta pessoa tem nesta função
                    film_count = session.query(func.count(EquipeTecnica.filme_id))\
                        .filter(EquipeTecnica.pessoa_id == pessoa.id)\
                        .filter(EquipeTecnica.funcao_tecnica_id == funcao_id)\
                        .scalar()
                    
                    new_items.append((pessoa, film_count))
                
                pagination.items = new_items
            
            return pagination

        except FuncaoTecnicaServiceError:
            # Re-raise FuncaoTecnicaServiceError sem envolver em outra exceção
            raise
        except SQLAlchemyError as e:
            raise FuncaoTecnicaServiceError(
                f"Erro de banco de dados em {cls.__name__}.listar_pessoas_por_funcao: {str(e)}"
            ) from e
        except Exception as e:
            raise FuncaoTecnicaServiceError(
                f"Erro inesperado em {cls.__name__}.listar_pessoas_por_funcao: {str(e)}"
            ) from e

    @classmethod
    def obter_descricao(cls, funcao_id: uuid.UUID, session=None) -> dict:
        """Obtém informações detalhadas de uma função técnica.

        Args:
            funcao_id: UUID da função técnica
            session: Sessão SQLAlchemy opcional. Se None, usa a sessão padrão da classe.

        Returns:
            dict: Dicionário com:
                - id: UUID da função técnica
                - nome: Nome da função técnica
                - descricao: Descrição da função (ou None se não disponível)

        Raises:
            FuncaoTecnicaServiceError: Quando ocorre erro na operação

        Examples:
            >>> info = FuncaoTecnicaService.obter_descricao(funcao_id)
            >>> print(f"{info['nome']}: {info['descricao']}")
        """
        if session is None:
            session = cls._default_session

        try:
            # Busca a função técnica
            try:
                funcao = FuncaoTecnica.get_by_id(funcao_id, raise_if_not_found=True, session=session)
            except FuncaoTecnica.RecordNotFoundError:
                raise FuncaoTecnicaServiceError(f"Função técnica não encontrada: {funcao_id}")

            return {
                'id': funcao.id,
                'nome': funcao.nome,
                'descricao': funcao.descricao
            }

        except FuncaoTecnicaServiceError:
            # Re-raise FuncaoTecnicaServiceError sem envolver em outra exceção
            raise
        except SQLAlchemyError as e:
            raise FuncaoTecnicaServiceError(
                f"Erro de banco de dados em {cls.__name__}.obter_descricao: {str(e)}"
            ) from e
        except Exception as e:
            raise FuncaoTecnicaServiceError(
                f"Erro inesperado em {cls.__name__}.obter_descricao: {str(e)}"
            ) from e
