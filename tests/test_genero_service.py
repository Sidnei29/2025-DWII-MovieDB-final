"""Testes para o GeneroService."""
import uuid
import pytest
from unittest.mock import Mock, MagicMock, patch

from app.services.genero_service import GeneroService, GeneroServiceError
from app.models.filme import Genero, Filme
from app.models.juncoes import FilmeGenero


class TestGeneroService:
    """Testes para a classe GeneroService."""

    def test_listar_generos_com_contagem_retorna_dados_corretos(self):
        """Testa que listar_generos_com_contagem retorna dados corretos."""
        # Arrange
        session = Mock()
        
        # Mock do resultado da query
        mock_row1 = Mock()
        mock_row1.id = uuid.uuid4()
        mock_row1.nome = "Ação"
        mock_row1.count = 5
        
        mock_row2 = Mock()
        mock_row2.id = uuid.uuid4()
        mock_row2.nome = "Drama"
        mock_row2.count = 3
        
        session.execute.return_value.all.return_value = [mock_row1, mock_row2]
        
        # Act
        resultado = GeneroService.listar_generos_com_contagem(session=session)
        
        # Assert
        assert len(resultado) == 2
        assert resultado[0]['nome'] == "Ação"
        assert resultado[0]['count'] == 5
        assert resultado[1]['nome'] == "Drama"
        assert resultado[1]['count'] == 3
        session.execute.assert_called_once()

    def test_listar_generos_com_contagem_filtra_inativos(self):
        """Testa que listar_generos_com_contagem filtra gêneros inativos."""
        # Arrange
        session = Mock()
        
        # Mock do resultado - apenas gêneros ativos devem aparecer
        mock_row = Mock()
        mock_row.id = uuid.uuid4()
        mock_row.nome = "Comédia"
        mock_row.count = 2
        
        session.execute.return_value.all.return_value = [mock_row]
        
        # Act
        resultado = GeneroService.listar_generos_com_contagem(session=session)
        
        # Assert
        assert len(resultado) == 1
        assert resultado[0]['nome'] == "Comédia"
        
        # Verifica que a query inclui filtro de ativo
        call_args = session.execute.call_args
        stmt = call_args[0][0]
        stmt_str = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        assert "ativo" in stmt_str.lower() or "WHERE" in stmt_str

    def test_listar_generos_com_contagem_retorna_lista_vazia_quando_sem_filmes(self):
        """Testa que retorna lista vazia quando não há gêneros com filmes."""
        # Arrange
        session = Mock()
        session.execute.return_value.all.return_value = []
        
        # Act
        resultado = GeneroService.listar_generos_com_contagem(session=session)
        
        # Assert
        assert resultado == []
        assert isinstance(resultado, list)

    def test_listar_generos_com_contagem_levanta_erro_em_falha_db(self):
        """Testa que levanta GeneroServiceError em falha de banco de dados."""
        # Arrange
        from sqlalchemy.exc import SQLAlchemyError
        session = Mock()
        session.execute.side_effect = SQLAlchemyError("Erro de conexão")
        
        # Act & Assert
        with pytest.raises(GeneroServiceError) as exc_info:
            GeneroService.listar_generos_com_contagem(session=session)
        
        assert "Erro de banco de dados" in str(exc_info.value)

    def test_listar_filmes_por_genero_com_genero_valido(self):
        """Testa listar_filmes_por_genero com gênero válido."""
        # Arrange
        genero_id = uuid.uuid4()
        session = Mock()
        
        # Mock do Genero.get_by_id
        mock_genero = Mock(spec=Genero)
        mock_genero.id = genero_id
        mock_genero.nome = "Ficção Científica"
        
        # Patch do método get_by_id
        with patch.object(Genero, 'get_by_id', return_value=mock_genero):
            # Mock da paginação
            from app.infra.modulos import db
            mock_pagination = Mock()
            mock_pagination.items = [Mock(spec=Filme), Mock(spec=Filme)]
            mock_pagination.page = 1
            mock_pagination.pages = 1
            mock_pagination.total = 2
            
            with patch.object(db, 'paginate', return_value=mock_pagination):
                # Act
                resultado = GeneroService.listar_filmes_por_genero(
                    genero_id=genero_id,
                    page=1,
                    per_page=20,
                    session=session
                )
                
                # Assert
                assert resultado is not None
                assert len(resultado.items) == 2
                assert resultado.page == 1

    def test_listar_filmes_por_genero_com_genero_invalido(self):
        """Testa listar_filmes_por_genero com gênero inválido."""
        # Arrange
        genero_id = uuid.uuid4()
        session = Mock()
        
        # Mock do Genero.get_by_id para levantar exceção
        with patch.object(Genero, 'get_by_id', side_effect=Genero.RecordNotFoundError("Gênero não encontrado")):
            # Act & Assert
            with pytest.raises(GeneroServiceError) as exc_info:
                GeneroService.listar_filmes_por_genero(
                    genero_id=genero_id,
                    session=session
                )
            
            assert "Gênero não encontrado" in str(exc_info.value)

    def test_listar_filmes_por_genero_com_genero_vazio(self):
        """Testa listar_filmes_por_genero com gênero sem filmes."""
        # Arrange
        genero_id = uuid.uuid4()
        session = Mock()
        
        # Mock do Genero.get_by_id
        mock_genero = Mock(spec=Genero)
        mock_genero.id = genero_id
        mock_genero.nome = "Terror"
        
        with patch.object(Genero, 'get_by_id', return_value=mock_genero):
            # Mock da paginação vazia
            from app.infra.modulos import db
            mock_pagination = Mock()
            mock_pagination.items = []
            mock_pagination.page = 1
            mock_pagination.pages = 0
            mock_pagination.total = 0
            
            with patch.object(db, 'paginate', return_value=mock_pagination):
                # Act
                resultado = GeneroService.listar_filmes_por_genero(
                    genero_id=genero_id,
                    session=session
                )
                
                # Assert
                assert resultado is not None
                assert len(resultado.items) == 0
                assert resultado.total == 0

    def test_listar_filmes_por_genero_paginacao_funciona(self):
        """Testa que a paginação funciona corretamente."""
        # Arrange
        genero_id = uuid.uuid4()
        session = Mock()
        
        # Mock do Genero.get_by_id
        mock_genero = Mock(spec=Genero)
        mock_genero.id = genero_id
        
        with patch.object(Genero, 'get_by_id', return_value=mock_genero):
            # Mock da paginação
            from app.infra.modulos import db
            mock_pagination = Mock()
            mock_pagination.items = [Mock(spec=Filme) for _ in range(10)]
            mock_pagination.page = 2
            mock_pagination.pages = 5
            mock_pagination.total = 50
            mock_pagination.per_page = 10
            
            with patch.object(db, 'paginate', return_value=mock_pagination) as mock_paginate:
                # Act
                resultado = GeneroService.listar_filmes_por_genero(
                    genero_id=genero_id,
                    page=2,
                    per_page=10,
                    session=session
                )
                
                # Assert
                assert resultado.page == 2
                assert resultado.per_page == 10
                assert resultado.total == 50
                assert len(resultado.items) == 10
                
                # Verifica que paginate foi chamado com os parâmetros corretos
                mock_paginate.assert_called_once()
                call_kwargs = mock_paginate.call_args[1]
                assert call_kwargs['page'] == 2
                assert call_kwargs['per_page'] == 10

    def test_listar_filmes_por_genero_levanta_erro_em_falha_db(self):
        """Testa que levanta GeneroServiceError em falha de banco de dados."""
        # Arrange
        from sqlalchemy.exc import SQLAlchemyError
        genero_id = uuid.uuid4()
        session = Mock()
        
        # Mock do Genero.get_by_id
        mock_genero = Mock(spec=Genero)
        
        with patch.object(Genero, 'get_by_id', return_value=mock_genero):
            # Mock da paginação para levantar erro
            from app.infra.modulos import db
            with patch.object(db, 'paginate', side_effect=SQLAlchemyError("Erro de query")):
                # Act & Assert
                with pytest.raises(GeneroServiceError) as exc_info:
                    GeneroService.listar_filmes_por_genero(
                        genero_id=genero_id,
                        session=session
                    )
                
                assert "Erro de banco de dados" in str(exc_info.value)

    def test_set_default_session(self):
        """Testa que set_default_session configura a sessão padrão."""
        # Arrange
        mock_session = Mock()
        original_session = GeneroService._default_session
        
        try:
            # Act
            GeneroService.set_default_session(mock_session)
            
            # Assert
            assert GeneroService._default_session == mock_session
        finally:
            # Cleanup - restaura sessão original
            GeneroService._default_session = original_session
