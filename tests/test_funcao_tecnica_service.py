"""Testes para o FuncaoTecnicaService."""
import uuid
import pytest
from unittest.mock import Mock, patch

from app.services.funcao_tecnica_service import FuncaoTecnicaService, FuncaoTecnicaServiceError
from app.models.filme import FuncaoTecnica
from app.models.pessoa import Pessoa
from app.models.juncoes import EquipeTecnica


class TestFuncaoTecnicaService:
    """Testes para a classe FuncaoTecnicaService."""

    def test_listar_funcoes_com_contagem_retorna_dados_corretos(self):
        """Testa que listar_funcoes_com_contagem retorna dados corretos."""
        # Arrange
        session = Mock()
        
        # Mock do resultado da query
        mock_row1 = Mock()
        mock_row1.id = uuid.uuid4()
        mock_row1.nome = "Diretor"
        mock_row1.count = 10
        
        mock_row2 = Mock()
        mock_row2.id = uuid.uuid4()
        mock_row2.nome = "Roteirista"
        mock_row2.count = 8
        
        session.execute.return_value.all.return_value = [mock_row1, mock_row2]
        
        # Act
        resultado = FuncaoTecnicaService.listar_funcoes_com_contagem(session=session)
        
        # Assert
        assert len(resultado) == 2
        assert resultado[0]['nome'] == "Diretor"
        assert resultado[0]['count'] == 10
        assert resultado[1]['nome'] == "Roteirista"
        assert resultado[1]['count'] == 8
        session.execute.assert_called_once()

    def test_listar_funcoes_com_contagem_filtra_inativas(self):
        """Testa que listar_funcoes_com_contagem filtra funções inativas."""
        # Arrange
        session = Mock()
        
        # Mock do resultado - apenas funções ativas devem aparecer
        mock_row = Mock()
        mock_row.id = uuid.uuid4()
        mock_row.nome = "Cinematógrafo"
        mock_row.count = 5
        
        session.execute.return_value.all.return_value = [mock_row]
        
        # Act
        resultado = FuncaoTecnicaService.listar_funcoes_com_contagem(session=session)
        
        # Assert
        assert len(resultado) == 1
        assert resultado[0]['nome'] == "Cinematógrafo"
        
        # Verifica que a query inclui filtro de ativo
        call_args = session.execute.call_args
        stmt = call_args[0][0]
        stmt_str = str(stmt.compile(compile_kwargs={"literal_binds": True}))
        assert "ativo" in stmt_str.lower() or "WHERE" in stmt_str

    def test_listar_funcoes_com_contagem_retorna_lista_vazia_quando_sem_pessoas(self):
        """Testa que retorna lista vazia quando não há funções com pessoas."""
        # Arrange
        session = Mock()
        session.execute.return_value.all.return_value = []
        
        # Act
        resultado = FuncaoTecnicaService.listar_funcoes_com_contagem(session=session)
        
        # Assert
        assert resultado == []
        assert isinstance(resultado, list)

    def test_listar_funcoes_com_contagem_levanta_erro_em_falha_db(self):
        """Testa que levanta FuncaoTecnicaServiceError em falha de banco de dados."""
        # Arrange
        from sqlalchemy.exc import SQLAlchemyError
        session = Mock()
        session.execute.side_effect = SQLAlchemyError("Erro de conexão")
        
        # Act & Assert
        with pytest.raises(FuncaoTecnicaServiceError) as exc_info:
            FuncaoTecnicaService.listar_funcoes_com_contagem(session=session)
        
        assert "Erro de banco de dados" in str(exc_info.value)

    def test_listar_pessoas_por_funcao_com_funcao_valida(self):
        """Testa listar_pessoas_por_funcao com função válida."""
        # Arrange
        funcao_id = uuid.uuid4()
        session = Mock()
        
        # Mock do FuncaoTecnica.get_by_id
        mock_funcao = Mock(spec=FuncaoTecnica)
        mock_funcao.id = funcao_id
        mock_funcao.nome = "Diretor"
        
        # Patch do método get_by_id
        with patch.object(FuncaoTecnica, 'get_by_id', return_value=mock_funcao):
            # Mock da paginação
            from app.infra.modulos import db
            mock_pagination = Mock()
            mock_pessoa1 = Mock(spec=Pessoa)
            mock_pessoa2 = Mock(spec=Pessoa)
            mock_pagination.items = [(mock_pessoa1, 3), (mock_pessoa2, 5)]
            mock_pagination.page = 1
            mock_pagination.pages = 1
            mock_pagination.total = 2
            
            with patch.object(db, 'paginate', return_value=mock_pagination):
                # Act
                resultado = FuncaoTecnicaService.listar_pessoas_por_funcao(
                    funcao_id=funcao_id,
                    page=1,
                    per_page=20,
                    session=session
                )
                
                # Assert
                assert resultado is not None
                assert len(resultado.items) == 2
                assert resultado.page == 1

    def test_listar_pessoas_por_funcao_com_funcao_invalida(self):
        """Testa listar_pessoas_por_funcao com função inválida."""
        # Arrange
        funcao_id = uuid.uuid4()
        session = Mock()
        
        # Mock do FuncaoTecnica.get_by_id para levantar exceção
        with patch.object(FuncaoTecnica, 'get_by_id', 
                         side_effect=FuncaoTecnica.RecordNotFoundError("Função não encontrada")):
            # Act & Assert
            with pytest.raises(FuncaoTecnicaServiceError) as exc_info:
                FuncaoTecnicaService.listar_pessoas_por_funcao(
                    funcao_id=funcao_id,
                    session=session
                )
            
            assert "Função técnica não encontrada" in str(exc_info.value)

    def test_listar_pessoas_por_funcao_com_funcao_vazia(self):
        """Testa listar_pessoas_por_funcao com função sem pessoas."""
        # Arrange
        funcao_id = uuid.uuid4()
        session = Mock()
        
        # Mock do FuncaoTecnica.get_by_id
        mock_funcao = Mock(spec=FuncaoTecnica)
        mock_funcao.id = funcao_id
        mock_funcao.nome = "Editor"
        
        with patch.object(FuncaoTecnica, 'get_by_id', return_value=mock_funcao):
            # Mock da paginação vazia
            from app.infra.modulos import db
            mock_pagination = Mock()
            mock_pagination.items = []
            mock_pagination.page = 1
            mock_pagination.pages = 0
            mock_pagination.total = 0
            
            with patch.object(db, 'paginate', return_value=mock_pagination):
                # Act
                resultado = FuncaoTecnicaService.listar_pessoas_por_funcao(
                    funcao_id=funcao_id,
                    session=session
                )
                
                # Assert
                assert resultado is not None
                assert len(resultado.items) == 0
                assert resultado.total == 0

    def test_listar_pessoas_por_funcao_paginacao_funciona(self):
        """Testa que a paginação funciona corretamente."""
        # Arrange
        funcao_id = uuid.uuid4()
        session = Mock()
        
        # Mock do FuncaoTecnica.get_by_id
        mock_funcao = Mock(spec=FuncaoTecnica)
        mock_funcao.id = funcao_id
        
        with patch.object(FuncaoTecnica, 'get_by_id', return_value=mock_funcao):
            # Mock da paginação
            from app.infra.modulos import db
            mock_pagination = Mock()
            mock_pagination.items = [(Mock(spec=Pessoa), i) for i in range(10)]
            mock_pagination.page = 2
            mock_pagination.pages = 5
            mock_pagination.total = 50
            mock_pagination.per_page = 10
            
            with patch.object(db, 'paginate', return_value=mock_pagination) as mock_paginate:
                # Act
                resultado = FuncaoTecnicaService.listar_pessoas_por_funcao(
                    funcao_id=funcao_id,
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

    def test_listar_pessoas_por_funcao_levanta_erro_em_falha_db(self):
        """Testa que levanta FuncaoTecnicaServiceError em falha de banco de dados."""
        # Arrange
        from sqlalchemy.exc import SQLAlchemyError
        funcao_id = uuid.uuid4()
        session = Mock()
        
        # Mock do FuncaoTecnica.get_by_id
        mock_funcao = Mock(spec=FuncaoTecnica)
        
        with patch.object(FuncaoTecnica, 'get_by_id', return_value=mock_funcao):
            # Mock da paginação para levantar erro
            from app.infra.modulos import db
            with patch.object(db, 'paginate', side_effect=SQLAlchemyError("Erro de query")):
                # Act & Assert
                with pytest.raises(FuncaoTecnicaServiceError) as exc_info:
                    FuncaoTecnicaService.listar_pessoas_por_funcao(
                        funcao_id=funcao_id,
                        session=session
                    )
                
                assert "Erro de banco de dados" in str(exc_info.value)

    def test_obter_descricao_com_funcao_valida(self):
        """Testa obter_descricao com função válida."""
        # Arrange
        funcao_id = uuid.uuid4()
        session = Mock()
        
        # Mock do FuncaoTecnica.get_by_id
        mock_funcao = Mock(spec=FuncaoTecnica)
        mock_funcao.id = funcao_id
        mock_funcao.nome = "Diretor"
        mock_funcao.descricao = "Responsável pela direção artística do filme"
        
        with patch.object(FuncaoTecnica, 'get_by_id', return_value=mock_funcao):
            # Act
            resultado = FuncaoTecnicaService.obter_descricao(
                funcao_id=funcao_id,
                session=session
            )
            
            # Assert
            assert resultado is not None
            assert resultado['id'] == funcao_id
            assert resultado['nome'] == "Diretor"
            assert resultado['descricao'] == "Responsável pela direção artística do filme"

    def test_obter_descricao_com_descricao_ausente(self):
        """Testa obter_descricao com função sem descrição."""
        # Arrange
        funcao_id = uuid.uuid4()
        session = Mock()
        
        # Mock do FuncaoTecnica.get_by_id
        mock_funcao = Mock(spec=FuncaoTecnica)
        mock_funcao.id = funcao_id
        mock_funcao.nome = "Produtor"
        mock_funcao.descricao = None
        
        with patch.object(FuncaoTecnica, 'get_by_id', return_value=mock_funcao):
            # Act
            resultado = FuncaoTecnicaService.obter_descricao(
                funcao_id=funcao_id,
                session=session
            )
            
            # Assert
            assert resultado is not None
            assert resultado['id'] == funcao_id
            assert resultado['nome'] == "Produtor"
            assert resultado['descricao'] is None

    def test_obter_descricao_com_funcao_invalida(self):
        """Testa obter_descricao com função inválida."""
        # Arrange
        funcao_id = uuid.uuid4()
        session = Mock()
        
        # Mock do FuncaoTecnica.get_by_id para levantar exceção
        with patch.object(FuncaoTecnica, 'get_by_id',
                         side_effect=FuncaoTecnica.RecordNotFoundError("Função não encontrada")):
            # Act & Assert
            with pytest.raises(FuncaoTecnicaServiceError) as exc_info:
                FuncaoTecnicaService.obter_descricao(
                    funcao_id=funcao_id,
                    session=session
                )
            
            assert "Função técnica não encontrada" in str(exc_info.value)

    def test_obter_descricao_levanta_erro_em_falha_db(self):
        """Testa que levanta FuncaoTecnicaServiceError em falha de banco de dados."""
        # Arrange
        from sqlalchemy.exc import SQLAlchemyError
        funcao_id = uuid.uuid4()
        session = Mock()
        
        # Mock do FuncaoTecnica.get_by_id para levantar erro de banco
        with patch.object(FuncaoTecnica, 'get_by_id', 
                         side_effect=SQLAlchemyError("Erro de conexão")):
            # Act & Assert
            with pytest.raises(FuncaoTecnicaServiceError) as exc_info:
                FuncaoTecnicaService.obter_descricao(
                    funcao_id=funcao_id,
                    session=session
                )
            
            assert "Erro de banco de dados" in str(exc_info.value)

    def test_set_default_session(self):
        """Testa que set_default_session configura a sessão padrão."""
        # Arrange
        mock_session = Mock()
        original_session = FuncaoTecnicaService._default_session
        
        try:
            # Act
            FuncaoTecnicaService.set_default_session(mock_session)
            
            # Assert
            assert FuncaoTecnicaService._default_session == mock_session
        finally:
            # Cleanup - restaura sessão original
            FuncaoTecnicaService._default_session = original_session
