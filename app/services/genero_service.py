"""Serviço de gerenciamento de gêneros.

Este módulo fornece a camada de serviço para operações relacionadas a gêneros,
incluindo listagem de gêneros com contagem de filmes e filtragem de filmes por gênero.

Classes principais:
    - GeneroService: Serviço principal com métodos para operações de gêneros
    - GeneroServiceError: Exceção customizada para operações do GeneroService
"""
import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from app.infra.modulos import db
from app.models.filme import Filme, Genero
from app.models.juncoes import FilmeGenero


class GeneroServiceError(Exception):
    """Exceção customizada para operações do GeneroService."""
    pass


class GeneroService:
    """Serviço para operações relacionadas a gêneros.

    Centraliza a lógica de negócio relacionada a gêneros, separando-a dos modelos.
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
    def listar_generos_com_contagem(cls, session=None) -> list[dict]:
        """Lista todos os gêneros ativos com contagem de filmes.

        Args:
            session: Sessão SQLAlchemy opcional. Se None, usa a sessão padrão da classe.

        Returns:
            list[dict]: Lista de dicionários com:
                - id: UUID do gênero
                - nome: Nome do gênero
                - count: Número de filmes no gênero

        Raises:
            GeneroServiceError: Quando ocorre erro na operação

        Examples:
            >>> generos = GeneroService.listar_generos_com_contagem()
            >>> for genero in generos:
            ...     print(f"{genero['nome']}: {genero['count']} filmes")
        """
        if session is None:
            session = cls._default_session

        try:
            # Query para contar filmes por gênero
            stmt = (
                select(
                    Genero.id,
                    Genero.nome,
                    func.count(FilmeGenero.filme_id).label('count')
                )
                .outerjoin(FilmeGenero, Genero.id == FilmeGenero.genero_id)
                .where(Genero.ativo == True)
                .group_by(Genero.id, Genero.nome)
                .having(func.count(FilmeGenero.filme_id) > 0)
                .order_by(Genero.nome)
            )

            resultado = session.execute(stmt).all()

            # Converte resultado para lista de dicionários
            generos = [
                {
                    'id': row.id,
                    'nome': row.nome,
                    'count': row.count
                }
                for row in resultado
            ]

            return generos

        except SQLAlchemyError as e:
            raise GeneroServiceError(
                f"Erro de banco de dados em {cls.__name__}.listar_generos_com_contagem: {str(e)}"
            ) from e
        except Exception as e:
            raise GeneroServiceError(
                f"Erro inesperado em {cls.__name__}.listar_generos_com_contagem: {str(e)}"
            ) from e

    @classmethod
    def listar_filmes_por_genero(cls,
                                 genero_id: uuid.UUID,
                                 page: int = 1,
                                 per_page: int = 20,
                                 search: str = None,
                                 session=None):
        """Lista filmes de um gênero específico com paginação e busca.

        Args:
            genero_id: UUID do gênero
            page: Número da página (começa em 1). Default: 1
            per_page: Itens por página. Default: 20
            search: Termo de busca para filtrar por título (opcional)
            session: Sessão SQLAlchemy opcional. Se None, usa a sessão padrão da classe.

        Returns:
            Pagination: Objeto de paginação do Flask-SQLAlchemy contendo:
                - items: Lista de objetos Filme
                - page: Página atual
                - pages: Total de páginas
                - per_page: Registros por página
                - total: Total de registros
                - has_next: Se há próxima página
                - has_prev: Se há página anterior

        Raises:
            GeneroServiceError: Quando ocorre erro na operação

        Examples:
            >>> # Listar primeira página de filmes de ação
            >>> resultado = GeneroService.listar_filmes_por_genero(genero_id)
            >>> filmes = resultado.items

            >>> # Página específica com busca
            >>> resultado = GeneroService.listar_filmes_por_genero(genero_id, page=2, per_page=30, search="matrix")
        """
        if session is None:
            session = cls._default_session

        try:
            # Verifica se o gênero existe
            try:
                genero = Genero.get_by_id(genero_id, raise_if_not_found=True, session=session)
            except Genero.RecordNotFoundError:
                raise GeneroServiceError(f"Gênero não encontrado: {genero_id}")

            # Query para obter filmes do gênero
            stmt = (
                select(Filme)
                .join(FilmeGenero, Filme.id == FilmeGenero.filme_id)
                .where(FilmeGenero.genero_id == genero_id)
            )

            # Adiciona filtro de busca se fornecido
            if search:
                from sqlalchemy import or_
                search_filter = or_(
                    Filme.titulo_portugues.ilike(f'%{search}%'),
                    Filme.titulo_original.ilike(f'%{search}%')
                )
                stmt = stmt.where(search_filter)

            stmt = stmt.order_by(Filme.titulo_portugues, Filme.titulo_original)

            # Aplica paginação
            return db.paginate(
                stmt,
                page=page,
                per_page=per_page,
                error_out=False
            )

        except GeneroServiceError:
            # Re-raise GeneroServiceError sem envolver em outra exceção
            raise
        except SQLAlchemyError as e:
            raise GeneroServiceError(
                f"Erro de banco de dados em {cls.__name__}.listar_filmes_por_genero: {str(e)}"
            ) from e
        except Exception as e:
            raise GeneroServiceError(
                f"Erro inesperado em {cls.__name__}.listar_filmes_por_genero: {str(e)}"
            ) from e
