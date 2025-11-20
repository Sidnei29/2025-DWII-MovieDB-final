# Design Document

## Overview

This design document outlines the implementation of navigation and filtering features for the MyMovieDB application. The system will provide three main capabilities:

1. **Genre-based film navigation** - Allow users to browse films filtered by genre
2. **Technical function-based people navigation** - Allow users to browse people filtered by their technical roles
3. **Technical function description modals** - Display detailed information about technical roles through interactive modals

These features enhance content discovery and provide educational context about film production roles. The implementation follows the existing Flask application architecture with blueprints, service layer pattern, and Jinja2 templates.

## Architecture

### High-Level Architecture

The implementation follows the existing MyMovieDB architecture:

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP Requests
       ▼
┌─────────────────────────────────────┐
│      Flask Application              │
│  ┌───────────────────────────────┐  │
│  │   Route Handlers (Blueprints) │  │
│  │  - filme_bp                   │  │
│  │  - pessoa_bp                  │  │
│  │  - genero_bp (enhanced)       │  │
│  │  - funcao_tecnica_bp (enhanced)│ │
│  │  - api_bp (new)               │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │   Service Layer               │  │
│  │  - FilmeService               │  │
│  │  - PessoaService              │  │
│  │  - GeneroService (new)        │  │
│  │  - FuncaoTecnicaService (new) │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │   Models (SQLAlchemy)         │  │
│  │  - Filme                      │  │
│  │  - Genero                     │  │
│  │  - Pessoa                     │  │
│  │  - FuncaoTecnica              │  │
│  │  - FilmeGenero                │  │
│  │  - EquipeTecnica              │  │
│  └───────────┬───────────────────┘  │
│              │                       │
└──────────────┼───────────────────────┘
               │
        ┌──────▼──────┐
        │   Database  │
        │  (SQLite)   │
        └─────────────┘
```

### Component Interaction Flow

#### Genre Navigation Flow
```
User clicks genre → genero_bp.filmes_por_genero() → GeneroService.listar_filmes_por_genero() 
→ Query Filme via FilmeGenero → Return paginated results → Render template
```

#### Technical Function Navigation Flow
```
User clicks function → funcao_tecnica_bp.pessoas_por_funcao() → FuncaoTecnicaService.listar_pessoas_por_funcao()
→ Query Pessoa via EquipeTecnica → Return paginated results → Render template
```

#### Modal Description Flow
```
User clicks function name → JavaScript AJAX request → api_bp.funcao_tecnica_descricao()
→ FuncaoTecnica.get_by_id() → Return JSON → JavaScript displays modal
```

## Components and Interfaces

### 1. Database Models (Existing - No Changes Required)

The existing models already support all required relationships:

**Genero Model** (`app/models/filme.py`)
- Already has `filmes` relationship via `FilmeGenero` junction table
- Has `descricao` field for genre descriptions
- Has `ativo` field for filtering active genres

**FuncaoTecnica Model** (`app/models/filme.py`)
- Already has `pessoas` relationship via `EquipeTecnica` junction table
- Has `descricao` field (1024 chars) for function descriptions
- Has `ativo` field for filtering active functions

**FilmeGenero Junction Table** (`app/models/juncoes.py`)
- Links Filme and Genero with many-to-many relationship

**EquipeTecnica Junction Table** (`app/models/juncoes.py`)
- Links Filme, Pessoa, and FuncaoTecnica

### 2. Service Layer (New Services)

#### GeneroService

```python
class GeneroService:
    """Service for genre-related operations."""
    
    @classmethod
    def listar_generos_com_contagem(cls, session=None) -> list[dict]:
        """Lista todos os gêneros ativos com contagem de filmes.
        
        Returns:
            list[dict]: Lista de dicionários com:
                - id: UUID do gênero
                - nome: Nome do gênero
                - count: Número de filmes no gênero
        """
        
    @classmethod
    def listar_filmes_por_genero(cls, genero_id: uuid.UUID, page: int = 1, 
                                 per_page: int = 20, search: str = None, session=None):
        """Lista filmes de um gênero específico com paginação e busca.
        
        Args:
            genero_id: UUID do gênero
            page: Número da página
            per_page: Itens por página
            search: Termo de busca para filtrar por título (opcional)
            session: Sessão SQLAlchemy opcional
            
        Returns:
            Pagination: Objeto de paginação do Flask-SQLAlchemy
        """
```

#### FuncaoTecnicaService

```python
class FuncaoTecnicaService:
    """Service for technical function-related operations."""
    
    @classmethod
    def listar_funcoes_com_contagem(cls, session=None) -> list[dict]:
        """Lista todas as funções técnicas ativas com contagem de pessoas.
        
        Returns:
            list[dict]: Lista de dicionários com:
                - id: UUID da função
                - nome: Nome da função
                - count: Número de pessoas com esta função
        """
        
    @classmethod
    def listar_pessoas_por_funcao(cls, funcao_id: uuid.UUID, page: int = 1,
                                  per_page: int = 20, session=None):
        """Lista pessoas que executam uma função técnica específica.
        
        Args:
            funcao_id: UUID da função técnica
            page: Número da página
            per_page: Itens por página
            session: Sessão SQLAlchemy opcional
            
        Returns:
            Pagination: Objeto de paginação do Flask-SQLAlchemy
        """
        
    @classmethod
    def obter_descricao(cls, funcao_id: uuid.UUID, session=None) -> dict:
        """Obtém informações detalhadas de uma função técnica.
        
        Args:
            funcao_id: UUID da função técnica
            session: Sessão SQLAlchemy opcional
            
        Returns:
            dict: Dicionário com nome e descrição da função
        """
```

### 3. Route Handlers (Enhanced Blueprints)

#### Enhanced genero_bp Routes

**New Route: `/genero/<uuid:genero_id>/filmes`**
- Method: GET
- Handler: `filmes_por_genero(genero_id)`
- Purpose: Display films filtered by genre with search and pagination
- Query params: `page`, `per_page`, `search`
- Template: `genero/web/filmes.jinja2`

#### Enhanced funcao_tecnica_bp Routes

**New Route: `/funcao_tecnica/<uuid:funcao_id>/pessoas`**
- Method: GET
- Handler: `pessoas_por_funcao(funcao_id)`
- Purpose: Display people filtered by technical function
- Query params: `page`, `per_page`
- Template: `funcao_tecnica/web/pessoas.jinja2`

#### New API Blueprint

**New Route: `/api/funcao-tecnica/<uuid:funcao_id>`**
- Method: GET
- Handler: `funcao_tecnica_descricao(funcao_id)`
- Purpose: Return technical function description as JSON
- Response format:
```json
{
  "id": "uuid-string",
  "nome": "Director",
  "descricao": "Detailed description...",
  "success": true
}
```

### 4. Templates

#### Genre Navigation Templates

**`app/templates/genero/web/lista.jinja2` (Enhanced)**
- Add genre navigation component showing all genres with counts
- Each genre is clickable and links to filtered view

**`app/templates/genero/web/filmes.jinja2` (New)**
- Display genre name as page title
- Add search form with title input field
- Add items per page dropdown (12, 24, 48, 96 options)
- Add "Buscar" button to submit search
- Show filtered list of films in grid layout
- Include pagination controls that maintain search and per_page parameters
- Provide "Back to All Films" link
- Handle empty state with appropriate message
- Display search term in empty state when applicable

#### Technical Function Navigation Templates

**`app/templates/funcao_tecnica/web/lista.jinja2` (Enhanced)**
- Add function navigation component showing all functions with counts
- Each function is clickable and links to filtered view

**`app/templates/funcao_tecnica/web/pessoas.jinja2` (New)**
- Display function name as page title
- Show filtered list of people in grid layout
- Include pagination controls
- Provide "Back to All People" link
- Handle empty state with appropriate message

#### Modal Templates

**`app/templates/components/modal_funcao_tecnica.jinja2` (New)**
- Reusable modal component for displaying function descriptions
- Structure:
  - Modal backdrop (dimmed background)
  - Modal dialog (centered)
  - Modal header with title and close button (X)
  - Modal body with description content
  - Modal footer with Close button

**Enhanced Film Detail Template** (`app/templates/filme/web/details.jinja2`)
- Add `data-funcao-id` attribute to technical function names
- Add CSS class to make function names clickable
- Include modal template

**Enhanced Person Detail Template** (`app/templates/pessoa/web/details.jinja2`)
- Add `data-funcao-id` attribute to technical function names in filmography
- Add CSS class to make function names clickable
- Include modal template

### 5. Frontend Components

#### JavaScript Module: `modal_funcao_tecnica.js`

```javascript
// Modal management for technical function descriptions
class FuncaoTecnicaModal {
    constructor() {
        this.modal = null;
        this.backdrop = null;
        this.init();
    }
    
    init() {
        // Attach click handlers to all function names
        // Handle ESC key press
        // Handle backdrop click
    }
    
    async open(funcaoId) {
        // Fetch function description via AJAX
        // Display modal with content
        // Handle loading state
    }
    
    close() {
        // Hide modal
        // Remove backdrop
    }
    
    handleError(message) {
        // Display error message in modal
    }
}
```

#### CSS Styling: `modal.css`

```css
/* Modal backdrop - full screen overlay */
.modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 1040;
}

/* Modal dialog - centered container */
.modal-dialog {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    max-width: 600px;
    width: 90%;
    z-index: 1050;
}

/* Responsive design for mobile */
@media (max-width: 768px) {
    .modal-dialog {
        width: 95%;
        max-height: 90vh;
        overflow-y: auto;
    }
}
```

## Data Models

### Existing Models (No Changes)

All required data structures already exist:

**Genero**
- `id`: UUID (PK)
- `nome`: String(40), unique
- `descricao`: String(1024), optional
- `ativo`: Boolean
- Relationships: `filmes` (many-to-many via FilmeGenero)

**FuncaoTecnica**
- `id`: UUID (PK)
- `nome`: String(100), unique
- `descricao`: String(1024), optional
- `ativo`: Boolean
- Relationships: `pessoas` (many-to-many via EquipeTecnica)

### Query Patterns

#### Genre Film Count Query
```python
from sqlalchemy import func, select
from app.models.filme import Genero, Filme
from app.models.juncoes import FilmeGenero

# Count films per genre
query = (
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
```

#### Films by Genre Query (with pagination and search)
```python
from sqlalchemy import select, or_
from app.models.filme import Filme, Genero
from app.models.juncoes import FilmeGenero

# Get films for a specific genre with optional search
query = (
    select(Filme)
    .join(FilmeGenero, Filme.id == FilmeGenero.filme_id)
    .where(FilmeGenero.genero_id == genero_id)
)

# Add search filter if provided
if search:
    search_filter = or_(
        Filme.titulo_portugues.ilike(f'%{search}%'),
        Filme.titulo_original.ilike(f'%{search}%')
    )
    query = query.where(search_filter)

query = query.order_by(Filme.titulo_portugues)

pagination = db.paginate(query, page=page, per_page=per_page)
```

#### Technical Function Person Count Query
```python
from sqlalchemy import func, select
from app.models.filme import FuncaoTecnica
from app.models.pessoa import Pessoa
from app.models.juncoes import EquipeTecnica

# Count people per technical function
query = (
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
```

#### People by Technical Function Query (with pagination)
```python
from sqlalchemy import select, func
from app.models.pessoa import Pessoa
from app.models.filme import FuncaoTecnica
from app.models.juncoes import EquipeTecnica

# Get people for a specific technical function with film count
query = (
    select(
        Pessoa,
        func.count(EquipeTecnica.filme_id).label('film_count')
    )
    .join(EquipeTecnica, Pessoa.id == EquipeTecnica.pessoa_id)
    .where(EquipeTecnica.funcao_tecnica_id == funcao_id)
    .group_by(Pessoa.id)
    .order_by(Pessoa.nome)
)

pagination = db.paginate(query, page=page, per_page=per_page)
```

## Error Handling

### Service Layer Error Handling

Following the existing service pattern, all new services will implement:

```python
class GeneroServiceError(Exception):
    """Custom exception for GeneroService operations."""
    pass

class FuncaoTecnicaServiceError(Exception):
    """Custom exception for FuncaoTecnicaService operations."""
    pass
```

### Error Scenarios

1. **Genre/Function Not Found**
   - Service: Raise custom exception
   - Route: Flash error message, redirect to list page
   - HTTP Status: 404

2. **Empty Results**
   - Service: Return empty pagination object
   - Route: Render template with empty state message
   - HTTP Status: 200

3. **Invalid Page Number**
   - Service: Return first page
   - Route: Flash info message about page adjustment
   - HTTP Status: 200

4. **Database Error**
   - Service: Rollback transaction, raise custom exception
   - Route: Flash error message, log error, redirect to safe page
   - HTTP Status: 500

5. **AJAX Request Failure (Modal)**
   - JavaScript: Display error message in modal
   - Fallback: Show generic "Description not available" message

### Error Messages (Portuguese)

```python
ERROR_MESSAGES = {
    'genero_not_found': 'Gênero não encontrado.',
    'funcao_not_found': 'Função técnica não encontrada.',
    'no_films_in_genre': 'Nenhum filme encontrado neste gênero.',
    'no_people_in_function': 'Nenhuma pessoa encontrada para esta função.',
    'database_error': 'Erro ao acessar o banco de dados. Tente novamente.',
    'description_not_available': 'Descrição não disponível para esta função.',
}
```

## Testing Strategy

### Unit Tests

#### Service Layer Tests

**GeneroService Tests** (`tests/test_genero_service.py`)
- Test `listar_generos_com_contagem()` returns correct counts
- Test `listar_generos_com_contagem()` filters inactive genres
- Test `listar_filmes_por_genero()` returns correct films
- Test `listar_filmes_por_genero()` handles pagination correctly
- Test `listar_filmes_por_genero()` with non-existent genre
- Test `listar_filmes_por_genero()` with empty genre

**FuncaoTecnicaService Tests** (`tests/test_funcao_tecnica_service.py`)
- Test `listar_funcoes_com_contagem()` returns correct counts
- Test `listar_funcoes_com_contagem()` filters inactive functions
- Test `listar_pessoas_por_funcao()` returns correct people
- Test `listar_pessoas_por_funcao()` handles pagination correctly
- Test `listar_pessoas_por_funcao()` with non-existent function
- Test `listar_pessoas_por_funcao()` with empty function
- Test `obter_descricao()` returns correct data
- Test `obter_descricao()` with non-existent function

#### Route Handler Tests

**Genre Routes Tests** (`tests/test_genero_routes.py`)
- Test GET `/genero/<id>/filmes` returns 200 for valid genre
- Test GET `/genero/<id>/filmes` returns 404 for invalid genre
- Test GET `/genero/<id>/filmes` with pagination parameters
- Test GET `/genero/<id>/filmes` displays correct films

**Technical Function Routes Tests** (`tests/test_funcao_tecnica_routes.py`)
- Test GET `/funcao_tecnica/<id>/pessoas` returns 200 for valid function
- Test GET `/funcao_tecnica/<id>/pessoas` returns 404 for invalid function
- Test GET `/funcao_tecnica/<id>/pessoas` with pagination parameters
- Test GET `/funcao_tecnica/<id>/pessoas` displays correct people

**API Routes Tests** (`tests/test_api_routes.py`)
- Test GET `/api/funcao-tecnica/<id>` returns JSON with description
- Test GET `/api/funcao-tecnica/<id>` returns 404 for invalid function
- Test GET `/api/funcao-tecnica/<id>` handles missing description

### Integration Tests

**End-to-End Navigation Tests** (`tests/test_navigation_integration.py`)
- Test complete genre navigation flow (list → filter → detail)
- Test complete technical function navigation flow (list → filter → detail)
- Test pagination across multiple pages
- Test "back to list" navigation

### Manual Testing Checklist

**Genre Navigation**
- [ ] Genre list displays all active genres with correct counts
- [ ] Clicking genre filters films correctly
- [ ] Pagination works on filtered results
- [ ] Empty genre shows appropriate message
- [ ] "Back to catalog" link works

**Technical Function Navigation**
- [ ] Function list displays all active functions with correct counts
- [ ] Clicking function filters people correctly
- [ ] Pagination works on filtered results
- [ ] Empty function shows appropriate message
- [ ] "Back to people list" link works

**Modal Functionality**
- [ ] Modal opens when clicking function name on film detail page
- [ ] Modal opens when clicking function name on person detail page
- [ ] Modal displays correct description
- [ ] Modal closes via X button
- [ ] Modal closes via Close button
- [ ] Modal closes via backdrop click
- [ ] Modal closes via ESC key
- [ ] Modal is responsive on mobile devices
- [ ] Modal handles missing descriptions gracefully

**Cross-Browser Testing**
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

**Accessibility Testing**
- [ ] Keyboard navigation works for all interactive elements
- [ ] Screen reader can access all content
- [ ] Focus indicators are visible
- [ ] ARIA labels are appropriate

## Implementation Notes

### Pagination Configuration

Use consistent pagination settings across all filtered views:
- Default items per page: 20
- Maximum items per page: 100
- Show page numbers: 5 visible at a time
- Include "Previous" and "Next" buttons

### Performance Considerations

1. **Database Queries**
   - Use `func.count()` for counting instead of loading all records
   - Use `outerjoin` for count queries to include zero counts
   - Add indexes on foreign key columns (already exist)

2. **Caching Strategy**
   - Genre/function counts can be cached (low change frequency)
   - Cache invalidation on genre/function updates
   - Consider Redis for production caching

3. **AJAX Requests**
   - Implement request debouncing if needed
   - Cache function descriptions in browser localStorage
   - Set appropriate HTTP cache headers

### Security Considerations

1. **CSRF Protection**
   - Not required for GET requests (genre/function filtering)
   - Not required for API GET requests (read-only)

2. **Input Validation**
   - Validate UUID format for genre_id and funcao_id
   - Validate pagination parameters (positive integers)
   - Sanitize search queries (already handled by SQLAlchemy)

3. **Authorization**
   - All navigation features are public (no login required)
   - Modal API endpoint is public (read-only data)

### Internationalization

All user-facing text is in Portuguese (pt-BR):
- Flash messages
- Template text
- Error messages
- Button labels
- Modal content

### Accessibility Requirements

1. **Semantic HTML**
   - Use `<nav>` for navigation components
   - Use `<button>` for clickable elements
   - Use proper heading hierarchy

2. **ARIA Attributes**
   - `aria-label` for icon buttons
   - `role="dialog"` for modal
   - `aria-modal="true"` for modal
   - `aria-labelledby` for modal title

3. **Keyboard Navigation**
   - Tab order follows logical flow
   - ESC key closes modal
   - Enter/Space activates buttons
   - Focus trap within modal when open

4. **Screen Reader Support**
   - Announce modal open/close
   - Announce page changes
   - Provide text alternatives for icons

## Design Decisions and Rationales

### Decision 1: No Database Schema Changes

**Rationale**: The existing models already have all required fields and relationships. The `descricao` field exists in both `Genero` and `FuncaoTecnica` models, and the junction tables properly support many-to-many relationships.

**Alternative Considered**: Adding a `categoria` field to `FuncaoTecnica` for grouping functions (Pre-Production, Production, Post-Production).

**Decision**: Defer this enhancement to a future iteration. The current design supports all requirements without it.

### Decision 2: Separate Service Classes

**Rationale**: Create dedicated `GeneroService` and `FuncaoTecnicaService` classes following the existing service pattern. This maintains consistency with the codebase and provides clear separation of concerns.

**Alternative Considered**: Extending existing `FilmeService` and `PessoaService` with genre/function methods.

**Decision**: Separate services are cleaner and more maintainable.

### Decision 3: AJAX for Modal Content

**Rationale**: Fetch function descriptions via AJAX to avoid loading all descriptions on page load. This improves initial page load performance and allows for dynamic content updates.

**Alternative Considered**: Embed all function descriptions in page data attributes.

**Decision**: AJAX approach is more scalable and performant.

### Decision 4: Reusable Modal Component

**Rationale**: Create a single modal template that can be reused on both film and person detail pages. This reduces code duplication and ensures consistent behavior.

**Alternative Considered**: Separate modal implementations for each page.

**Decision**: Reusable component is more maintainable.

### Decision 5: Pagination Defaults

**Rationale**: Use 20 items per page for filtered views (vs 12 for main catalog). This balances usability with performance for filtered results which tend to be smaller datasets.

**Alternative Considered**: Same pagination settings as main catalog (12 items).

**Decision**: 20 items provides better user experience for filtered views.

## Future Enhancements

1. **Genre Description Modal**: Similar to technical function modals, add clickable genre names with description modals

2. **Multi-Filter Support**: Allow filtering by multiple genres or functions simultaneously

3. **Sort Options**: Add sorting options (alphabetical, by rating, by year) to filtered views

4. **Filter Persistence**: Remember user's last filter selection using browser storage

5. **Function Categories**: Group technical functions by production phase (Pre/Production/Post)

6. **Search Within Filters**: Add search capability within filtered results

7. **Export Functionality**: Allow exporting filtered lists to CSV or PDF

8. **Analytics**: Track which genres/functions are most viewed to inform content strategy
