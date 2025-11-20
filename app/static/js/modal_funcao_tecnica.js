/**
 * Modal de Função Técnica
 * 
 * Gerencia a exibição de descrições de funções técnicas em um modal.
 * Carrega dados via AJAX da API e exibe em um modal Bootstrap.
 */

class FuncaoTecnicaModal {
    constructor() {
        this.modalElement = null;
        this.modal = null;
        this.loadingElement = null;
        this.contentElement = null;
        this.errorElement = null;
        this.nomeElement = null;
        this.descricaoElement = null;
        this.errorMessageElement = null;
        this.focusableElements = [];
        this.firstFocusableElement = null;
        this.lastFocusableElement = null;
        
        this.init();
    }

    /**
     * Inicializa o modal e seus event listeners
     */
    init() {
        // Aguarda o DOM estar pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    /**
     * Configura o modal e event listeners
     */
    setup() {
        // Obtém referências aos elementos do modal
        this.modalElement = document.getElementById('modalFuncaoTecnica');
        if (!this.modalElement) {
            console.warn('Modal de função técnica não encontrado no DOM');
            return;
        }

        // Inicializa o modal Bootstrap
        this.modal = new bootstrap.Modal(this.modalElement, {
            backdrop: 'static',
            keyboard: true
        });

        // Obtém referências aos elementos internos
        this.loadingElement = document.getElementById('modalFuncaoTecnicaLoading');
        this.contentElement = document.getElementById('modalFuncaoTecnicaContent');
        this.errorElement = document.getElementById('modalFuncaoTecnicaError');
        this.nomeElement = document.getElementById('modalFuncaoTecnicaNome');
        this.descricaoElement = document.getElementById('modalFuncaoTecnicaDescricao');
        this.errorMessageElement = document.getElementById('modalFuncaoTecnicaErrorMessage');

        // Adiciona event listeners
        this.attachEventListeners();
    }

    /**
     * Adiciona event listeners para elementos clicáveis e teclas
     */
    attachEventListeners() {
        // Event listener para elementos clicáveis de função técnica
        document.addEventListener('click', (e) => {
            const clickableElement = e.target.closest('.funcao-clickable');
            if (clickableElement) {
                e.preventDefault();
                const funcaoId = clickableElement.dataset.funcaoId;
                if (funcaoId) {
                    this.open(funcaoId);
                }
            }
        });

        // Event listener para tecla ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modalElement.classList.contains('show')) {
                this.close();
            }
        });

        // Event listener para focus trap quando modal está aberto
        this.modalElement.addEventListener('shown.bs.modal', () => {
            this.setupFocusTrap();
        });

        // Event listener para limpar focus trap quando modal fecha
        this.modalElement.addEventListener('hidden.bs.modal', () => {
            this.clearFocusTrap();
        });
    }

    /**
     * Abre o modal e carrega a descrição da função técnica
     * @param {string} funcaoId - UUID da função técnica
     */
    async open(funcaoId) {
        if (!this.modal) {
            console.error('Modal não inicializado');
            return;
        }

        // Mostra o modal
        this.modal.show();

        // Mostra estado de loading
        this.showLoading();

        try {
            // Faz requisição AJAX para buscar descrição
            const response = await fetch(`/api/funcao-tecnica/${funcaoId}`);
            
            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Função técnica não encontrada.');
                }
                throw new Error('Erro ao carregar a descrição. Tente novamente.');
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message || 'Erro ao carregar a descrição.');
            }

            // Exibe o conteúdo
            this.showContent(data);

        } catch (error) {
            console.error('Erro ao carregar função técnica:', error);
            this.showError(error.message);
        }
    }

    /**
     * Fecha o modal
     */
    close() {
        if (this.modal) {
            this.modal.hide();
        }
    }

    /**
     * Mostra o estado de loading
     */
    showLoading() {
        if (this.loadingElement) {
            this.loadingElement.classList.remove('d-none');
        }
        if (this.contentElement) {
            this.contentElement.classList.add('d-none');
        }
        if (this.errorElement) {
            this.errorElement.classList.add('d-none');
        }
    }

    /**
     * Mostra o conteúdo da função técnica
     * @param {Object} data - Dados da função técnica
     */
    showContent(data) {
        // Esconde loading e erro
        if (this.loadingElement) {
            this.loadingElement.classList.add('d-none');
        }
        if (this.errorElement) {
            this.errorElement.classList.add('d-none');
        }

        // Preenche o conteúdo
        if (this.nomeElement) {
            this.nomeElement.textContent = data.nome || 'Função Técnica';
        }

        if (this.descricaoElement) {
            const descricao = data.descricao || 'Descrição não disponível para esta função.';
            // Preserva quebras de linha convertendo para <br>
            this.descricaoElement.innerHTML = descricao.replace(/\n/g, '<br>');
        }

        // Mostra o conteúdo
        if (this.contentElement) {
            this.contentElement.classList.remove('d-none');
        }
    }

    /**
     * Mostra mensagem de erro
     * @param {string} message - Mensagem de erro
     */
    showError(message) {
        // Esconde loading e conteúdo
        if (this.loadingElement) {
            this.loadingElement.classList.add('d-none');
        }
        if (this.contentElement) {
            this.contentElement.classList.add('d-none');
        }

        // Define mensagem de erro
        if (this.errorMessageElement) {
            this.errorMessageElement.textContent = message || 'Erro ao carregar a descrição. Tente novamente.';
        }

        // Mostra erro
        if (this.errorElement) {
            this.errorElement.classList.remove('d-none');
        }
    }

    /**
     * Configura focus trap para acessibilidade
     */
    setupFocusTrap() {
        // Obtém todos os elementos focáveis dentro do modal
        this.focusableElements = this.modalElement.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (this.focusableElements.length === 0) return;

        this.firstFocusableElement = this.focusableElements[0];
        this.lastFocusableElement = this.focusableElements[this.focusableElements.length - 1];

        // Event listener para trap de foco
        this.modalElement.addEventListener('keydown', this.handleFocusTrap.bind(this));

        // Foca no primeiro elemento
        this.firstFocusableElement.focus();
    }

    /**
     * Gerencia o trap de foco com Tab
     * @param {KeyboardEvent} e - Evento de teclado
     */
    handleFocusTrap(e) {
        if (e.key !== 'Tab') return;

        if (e.shiftKey) {
            // Shift + Tab
            if (document.activeElement === this.firstFocusableElement) {
                e.preventDefault();
                this.lastFocusableElement.focus();
            }
        } else {
            // Tab
            if (document.activeElement === this.lastFocusableElement) {
                e.preventDefault();
                this.firstFocusableElement.focus();
            }
        }
    }

    /**
     * Limpa o focus trap
     */
    clearFocusTrap() {
        this.focusableElements = [];
        this.firstFocusableElement = null;
        this.lastFocusableElement = null;
    }
}

// Inicializa o modal quando o DOM estiver pronto
let funcaoTecnicaModal;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        funcaoTecnicaModal = new FuncaoTecnicaModal();
    });
} else {
    funcaoTecnicaModal = new FuncaoTecnicaModal();
}
