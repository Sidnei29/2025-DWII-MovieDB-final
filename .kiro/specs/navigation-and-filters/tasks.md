# Implementation Plan

- [x] 1. Create GeneroService for genre-based navigation







  - Implement `GeneroService` class in `app/services/genero_service.py`
  - Add `listar_generos_com_contagem()` method to return active genres with film counts
  - Add `listar_filmes_por_genero()` method with pagination support
  - Implement custom `GeneroServiceError` exception class
  - Follow service layer pattern with session management and error handling
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Enhance genero_bp with film filtering route






  - Add new route `/genero/<uuid:genero_id>/filmes` in `app/routes/generos/__init__.py`
  - Implement `filmes_por_genero(genero_id)` handler with GET method
  - Handle pagination query parameters (page, per_page)
  - Handle search query parameter (search)
  - Use `GeneroService.listar_filmes_por_genero()` to fetch data with search support
  - Handle 404 for non-existent genres
  - Flash appropriate messages for empty results
  - Pass search and per_page parameters to template
  - _Requirements: 1.2, 1.3, 1.4, 3.5, 3.6, 3.7, 3.8_

- [x] 3. Create genre navigation templates









  - Enhance `app/templates/genero/web/lista.jinja2` to display genre counts with clickable links
  - Create `app/templates/genero/web/filmes.jinja2` for filtered film display
  - Display genre name as page title in filtered view
  - Add search form with title input field and "Buscar" button
  - Add items per page dropdown with options (12, 24, 48, 96)
  - Show films in grid layout with poster, title, year, rating, synopsis
  - Add pagination controls that maintain search and per_page parameters
  - Include "Voltar ao Catálogo" link
  - Handle empty state with message "Nenhum filme encontrado neste gênero"
  - Display search term in empty state when search is active
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10_

- [x] 4. Create FuncaoTecnicaService for technical function navigation





  - Implement `FuncaoTecnicaService` class in `app/services/funcao_tecnica_service.py`
  - Add `listar_funcoes_com_contagem()` method to return active functions with people counts
  - Add `listar_pessoas_por_funcao()` method with pagination support
  - Add `obter_descricao()` method to fetch function details for API
  - Implement custom `FuncaoTecnicaServiceError` exception class
  - Follow service layer pattern with session management and error handling
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_

- [x] 5. Enhance funcao_tecnica_bp with people filtering route




  - Add new route `/funcao_tecnica/<uuid:funcao_id>/pessoas` in `app/routes/funcoes_tecnicas/__init__.py`
  - Implement `pessoas_por_funcao(funcao_id)` handler with GET method
  - Handle pagination query parameters (page, per_page)
  - Use `FuncaoTecnicaService.listar_pessoas_por_funcao()` to fetch data
  - Handle 404 for non-existent functions
  - Flash appropriate messages for empty results
  - _Requirements: 5.2, 5.3, 5.4_

- [x] 6. Create technical function navigation templates





  - Enhance `app/templates/funcao_tecnica/web/lista.jinja2` to display function counts with clickable links
  - Create `app/templates/funcao_tecnica/web/pessoas.jinja2` for filtered people display
  - Display function name as page title in filtered view
  - Show people in grid layout with photo, name, nationality, film count
  - Add pagination controls using existing pagination component
  - Include "Voltar à Lista de Pessoas" link
  - Handle empty state with message "Nenhuma pessoa encontrada para esta função"
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 7. Create API blueprint for function descriptions





  - Create new API blueprint in `app/routes/api/__init__.py`
  - Add route `/api/funcao-tecnica/<uuid:funcao_id>` with GET method
  - Implement `funcao_tecnica_descricao(funcao_id)` handler
  - Use `FuncaoTecnicaService.obter_descricao()` to fetch data
  - Return JSON response with id, nome, descricao, success fields
  - Handle 404 for non-existent functions with JSON error response
  - Handle missing descriptions with fallback message
  - Register API blueprint in `app/__init__.py`
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 10.1, 10.2, 10.3, 10.4, 12.4_
-

- [x] 8. Create reusable modal component template




  - Create `app/templates/components/modal_funcao_tecnica.jinja2`
  - Implement modal structure with backdrop, dialog, header, body, footer
  - Add close button (X) in header
  - Add "Fechar" button in footer
  - Include placeholder content area for dynamic loading
  - Add loading spinner for AJAX requests
  - Add error message area for failed requests
  - Style modal to be centered and responsive
  - _Requirements: 9.3, 10.3, 11.1, 11.6_

- [x] 9. Enhance film detail template with clickable function names





  - Modify `app/templates/filme/web/details.jinja2`
  - Add `data-funcao-id` attribute to technical function names in crew list
  - Add CSS class `funcao-clickable` to function names
  - Include modal component template
  - Add visual indicator (cursor pointer, underline on hover) for clickable functions
  - _Requirements: 9.1, 9.2_

- [x] 10. Enhance person detail template with clickable function names





  - Modify `app/templates/pessoa/web/details.jinja2`
  - Add `data-funcao-id` attribute to technical function names in filmography
  - Add CSS class `funcao-clickable` to function names
  - Include modal component template
  - Add visual indicator (cursor pointer, underline on hover) for clickable functions
  - _Requirements: 10.1, 10.2_

- [x] 11. Implement modal JavaScript functionality





  - Create `app/static/js/modal_funcao_tecnica.js`
  - Implement `FuncaoTecnicaModal` class with init, open, close methods
  - Attach click event handlers to all `.funcao-clickable` elements
  - Implement AJAX request to fetch function description from API
  - Display loading state while fetching data
  - Populate modal with fetched description
  - Handle ESC key press to close modal
  - Handle backdrop click to close modal
  - Handle close button clicks
  - Implement error handling for failed AJAX requests
  - Add focus trap to keep keyboard navigation within modal
  - _Requirements: 9.2, 10.2, 11.2, 11.3, 11.4, 11.5, 11.7_

- [x] 12. Create modal CSS styling





  - Create `app/static/css/modal.css`
  - Style modal backdrop with semi-transparent overlay
  - Style modal dialog as centered, responsive container
  - Add animations for modal open/close (fade in/out)
  - Style modal header, body, and footer sections
  - Style close buttons with hover effects
  - Add responsive styles for mobile devices (max-width: 768px)
  - Ensure modal is scrollable on small screens
  - Style loading spinner
  - Style error message display
  - _Requirements: 11.1, 11.6_

- [x] 13. Add clickable function name styling





  - Create or update `app/static/css/main.css` or appropriate stylesheet
  - Add `.funcao-clickable` class with cursor pointer
  - Add hover effect (underline, color change)
  - Add focus styles for keyboard navigation
  - Ensure sufficient color contrast for accessibility
  - _Requirements: 9.1, 10.1, 11.7_

- [x] 14. Include JavaScript and CSS in base template





  - Modify base template to include `modal_funcao_tecnica.js`
  - Modify base template to include `modal.css`
  - Ensure scripts load after DOM is ready
  - Initialize modal functionality on page load
  - _Requirements: 9.2, 10.2, 11.1_

- [x] 15. Write unit tests for GeneroService






  - Create `tests/test_genero_service.py`
  - Test `listar_generos_com_contagem()` returns correct data
  - Test filtering of inactive genres
  - Test `listar_filmes_por_genero()` with valid genre
  - Test `listar_filmes_por_genero()` with invalid genre
  - Test `listar_filmes_por_genero()` with empty genre
  - Test pagination functionality
  - Test error handling and exception raising
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 16. Write unit tests for FuncaoTecnicaService







  - Create `tests/test_funcao_tecnica_service.py`
  - Test `listar_funcoes_com_contagem()` returns correct data
  - Test filtering of inactive functions
  - Test `listar_pessoas_por_funcao()` with valid function
  - Test `listar_pessoas_por_funcao()` with invalid function
  - Test `listar_pessoas_por_funcao()` with empty function
  - Test `obter_descricao()` with valid function
  - Test `obter_descricao()` with missing description
  - Test pagination functionality
  - Test error handling and exception raising
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 12.1, 12.2, 12.4_

- [x] 17. Implement search and filters for genre film listing











  - Update `GeneroService.listar_filmes_por_genero()` to accept search parameter
  - Add search filter using `or_()` to match titulo_portugues or titulo_original with `ilike`
  - Update `genero_bp.filmes_por_genero()` route to handle search query parameter
  - Update `genero/web/filmes.jinja2` template to include search form
  - Add search input field with label "Buscar por título"
  - Add items per page dropdown with options 12, 24, 48, 96
  - Update pagination component to maintain search and per_page parameters
  - Update empty state message to show search term when applicable
  - _Requirements: 3.5, 3.6, 3.7, 3.8, 3.9, 3.10_

- [ ] 18. Write route handler tests for genre filtering

  - Create or update `tests/test_genero_routes.py`
  - Test GET `/genero/<id>/filmes` returns 200 for valid genre
  - Test GET `/genero/<id>/filmes` returns 404 for invalid genre
  - Test pagination parameters are handled correctly
  - Test search parameter filters films correctly
  - Test per_page parameter changes items per page
  - Test empty genre displays appropriate message
  - Test empty search results display appropriate message
  - Test "back to catalog" link is present
  - _Requirements: 1.2, 1.3, 1.4, 3.5, 3.6, 3.7, 3.8_

- [ ] 19. Write route handler tests for function filtering

  - Create or update `tests/test_funcao_tecnica_routes.py`
  - Test GET `/funcao_tecnica/<id>/pessoas` returns 200 for valid function
  - Test GET `/funcao_tecnica/<id>/pessoas` returns 404 for invalid function
  - Test pagination parameters are handled correctly
  - Test empty function displays appropriate message
  - Test "back to people list" link is present
  - _Requirements: 5.2, 5.3, 5.4_

- [ ]* 20. Write API endpoint tests
  - Create `tests/test_api_routes.py`
  - Test GET `/api/funcao-tecnica/<id>` returns JSON with correct structure
  - Test GET `/api/funcao-tecnica/<id>` returns 404 for invalid function
  - Test response includes all required fields (id, nome, descricao, success)
  - Test handling of missing descriptions
  - Test JSON content-type header
  - _Requirements: 12.4_

- [ ]* 21. Write integration tests for navigation flows
  - Create `tests/test_navigation_integration.py`
  - Test complete genre navigation flow (list → filter → search → film detail)
  - Test complete function navigation flow (list → filter → person detail)
  - Test pagination across multiple pages with search parameters
  - Test "back to list" navigation works correctly
  - Test modal opens and displays correct content
  - Test search within genre maintains genre filter
  - _Requirements: 1.1, 1.2, 1.3, 3.5, 3.6, 5.1, 5.2, 5.3, 9.2, 10.2_
