# Guia de Teste - Navegação de Pessoas por Função Técnica

## ✅ Status da Implementação

A navegação de pessoas por função técnica está **completamente implementada**:

- ✅ **Rota**: `/funcao_tecnica/<uuid:funcao_id>/pessoas`
- ✅ **Service**: `FuncaoTecnicaService.listar_pessoas_por_funcao()`
- ✅ **Template**: `funcao_tecnica/web/pessoas.jinja2`
- ✅ **Paginação**: Suporte para múltiplas páginas
- ✅ **Contagem de filmes**: Mostra quantos filmes cada pessoa trabalhou na função

---

## 🧪 Como Testar

### Método 1: Através da Lista de Funções Técnicas

#### Passo 1: Acesse a lista de funções técnicas
```
http://localhost:5000/funcao_tecnica/
```

#### Passo 2: Procure por links clicáveis
Na lista de funções técnicas, você deve ver:
- Nome da função (ex: "Director", "Editor", "Cinematographer")
- Número de pessoas que executam essa função
- **Link clicável** para ver as pessoas

#### Passo 3: Clique em uma função
Clique em qualquer função técnica que tenha pessoas associadas.

#### Passo 4: Verifique a página de pessoas
Você deve ver:
- ✅ **Título da página**: "Pessoas - [Nome da Função]"
- ✅ **Lista de pessoas** que executam essa função
- ✅ **Foto de cada pessoa**
- ✅ **Nome da pessoa** (clicável para ver detalhes)
- ✅ **Número de filmes** que a pessoa trabalhou nesta função
- ✅ **Paginação** (se houver mais de 20 pessoas)
- ✅ **Link "Voltar"** para retornar à lista de funções

---

### Método 2: Acesso Direto via URL

Se você souber o UUID de uma função técnica, pode acessar diretamente:

```
http://localhost:5000/funcao_tecnica/<UUID_DA_FUNCAO>/pessoas
```

**Exemplo:**
```
http://localhost:5000/funcao_tecnica/a1b2c3d4-e5f6-7890-abcd-ef1234567890/pessoas
```

---

### Método 3: Através de um Filme

#### Passo 1: Acesse qualquer filme
```
http://localhost:5000/filme/
```

#### Passo 2: Clique em um filme que tenha equipe técnica

#### Passo 3: Na seção "Equipe Técnica"
- Você verá as funções técnicas (ex: "Director", "Editor")
- **Clique no nome da função** para ver o modal com a descrição
- **OU** navegue manualmente para a lista de funções técnicas

---

## 📋 Checklist de Verificação

### Funcionalidades Básicas
- [ ] A página carrega sem erros
- [ ] O título mostra o nome da função técnica
- [ ] A lista de pessoas é exibida
- [ ] Cada pessoa mostra foto, nome e contagem de filmes
- [ ] Os nomes das pessoas são clicáveis
- [ ] Clicar no nome leva para a página de detalhes da pessoa

### Paginação
- [ ] Se houver mais de 20 pessoas, a paginação aparece
- [ ] Botões "Anterior" e "Próximo" funcionam
- [ ] Números de página são clicáveis
- [ ] A página atual está destacada
- [ ] Navegar entre páginas mantém o filtro da função

### Casos Especiais
- [ ] Função sem pessoas mostra mensagem apropriada
- [ ] Função inexistente redireciona para lista de funções
- [ ] Link "Voltar" retorna à lista de funções técnicas

### Responsividade
- [ ] Layout funciona em desktop
- [ ] Layout funciona em tablet
- [ ] Layout funciona em mobile

---

## 🔍 Exemplos de Funções para Testar

Funções técnicas comuns que provavelmente têm pessoas:

1. **Director** (Diretor)
2. **Cinematographer** (Diretor de Fotografia)
3. **Editor** (Editor)
4. **Producer** (Produtor)
5. **Writer** (Roteirista)
6. **Sound Designer** (Designer de Som)
7. **Production Designer** (Designer de Produção)
8. **Costume Designer** (Figurinista)

---

## 🎯 Teste Completo Passo a Passo

### Teste 1: Navegação Completa

1. **Acesse a home**
   ```
   http://localhost:5000
   ```

2. **Navegue para funções técnicas**
   - Procure por um link/menu para "Funções Técnicas"
   - OU acesse diretamente: `http://localhost:5000/funcao_tecnica/`

3. **Escolha uma função**
   - Procure por "Director" ou "Editor"
   - Clique no link para ver as pessoas

4. **Verifique a lista de pessoas**
   - Confirme que mostra pessoas que trabalham como diretores/editores
   - Verifique se a contagem de filmes está correta

5. **Clique em uma pessoa**
   - Deve levar para a página de detalhes da pessoa
   - Na página da pessoa, verifique se mostra os filmes onde trabalhou nesta função

6. **Volte para a lista de funções**
   - Use o botão "Voltar" ou navegação do navegador

---

### Teste 2: Paginação

1. **Encontre uma função com muitas pessoas**
   - Procure por "Director" ou "Producer" (geralmente têm muitas pessoas)

2. **Acesse a lista de pessoas dessa função**

3. **Verifique a paginação**
   - Se houver mais de 20 pessoas, deve aparecer paginação
   - Clique em "Próximo" ou página 2
   - Verifique se carrega a próxima página
   - Clique em "Anterior" ou página 1
   - Verifique se volta para a primeira página

---

### Teste 3: Função Vazia

1. **Crie uma nova função técnica** (se tiver permissão)
   - Acesse: `http://localhost:5000/funcao_tecnica/new`
   - Crie uma função sem associar a nenhuma pessoa

2. **Tente acessar a lista de pessoas dessa função**
   - Deve mostrar mensagem: "Nenhuma pessoa encontrada para esta função"
   - Deve ter link para voltar

---

### Teste 4: Integração com Modal

1. **Acesse um filme com equipe técnica**

2. **Na seção "Equipe Técnica"**
   - Clique no nome de uma função (ex: "Director")
   - O modal deve abrir com a descrição

3. **Feche o modal**

4. **Agora navegue para a lista de funções técnicas**
   - Encontre a mesma função
   - Clique para ver as pessoas
   - Deve mostrar todos os diretores

---

## 🐛 Troubleshooting

### Problema: Página não carrega

**Possíveis causas:**
1. Servidor Flask não está rodando
2. UUID da função inválido
3. Função não existe no banco de dados

**Solução:**
```bash
# Verifique se o servidor está rodando
# Deve mostrar logs no terminal

# Teste com uma função que você sabe que existe
# Acesse primeiro a lista de funções: http://localhost:5000/funcao_tecnica/
# Copie o UUID de uma função existente
```

---

### Problema: Lista vazia mesmo com pessoas no banco

**Possíveis causas:**
1. Pessoas não estão associadas a filmes com essa função
2. Função está inativa (`ativo = False`)

**Solução:**
```sql
-- Verifique no banco de dados
SELECT COUNT(*) 
FROM equipes_tecnicas 
WHERE funcao_tecnica_id = '<UUID_DA_FUNCAO>';

-- Verifique se a função está ativa
SELECT nome, ativo 
FROM funcoes_tecnicas 
WHERE id = '<UUID_DA_FUNCAO>';
```

---

### Problema: Contagem de filmes incorreta

**Possíveis causas:**
1. Pessoa trabalhou em múltiplos filmes mas a contagem não reflete
2. Dados duplicados na tabela de junção

**Solução:**
```sql
-- Verifique a contagem manualmente
SELECT p.nome, COUNT(DISTINCT et.filme_id) as film_count
FROM pessoas p
JOIN equipes_tecnicas et ON p.id = et.pessoa_id
WHERE et.funcao_tecnica_id = '<UUID_DA_FUNCAO>'
GROUP BY p.id, p.nome;
```

---

### Problema: Paginação não aparece

**Possíveis causas:**
1. Menos de 20 pessoas na função
2. Template não está renderizando a paginação

**Solução:**
- A paginação só aparece se houver mais de 20 pessoas
- Teste com uma função que tenha muitas pessoas (ex: "Director")

---

## 📊 Dados de Teste Sugeridos

Para testar adequadamente, certifique-se de ter:

- ✅ Pelo menos 3 funções técnicas diferentes
- ✅ Pelo menos 5 pessoas em cada função
- ✅ Pelo menos uma função com mais de 20 pessoas (para testar paginação)
- ✅ Pelo menos uma função vazia (para testar estado vazio)
- ✅ Pessoas que trabalham em múltiplas funções

---

## ✅ Checklist Final

Antes de considerar o teste completo, verifique:

- [ ] Navegação funciona da lista de funções para lista de pessoas
- [ ] Navegação funciona da lista de pessoas para detalhes da pessoa
- [ ] Navegação funciona dos detalhes da pessoa de volta
- [ ] Paginação funciona corretamente
- [ ] Contagem de filmes está correta
- [ ] Função vazia mostra mensagem apropriada
- [ ] Função inexistente redireciona corretamente
- [ ] Layout é responsivo em diferentes tamanhos de tela
- [ ] Não há erros no console do navegador
- [ ] Não há erros nos logs do servidor Flask

---

## 🎉 Resultado Esperado

Quando tudo estiver funcionando:

1. ✅ Você pode navegar de funções técnicas → pessoas → detalhes da pessoa
2. ✅ A contagem de filmes está correta para cada pessoa
3. ✅ A paginação funciona suavemente
4. ✅ Estados vazios são tratados graciosamente
5. ✅ A experiência do usuário é fluida e intuitiva

---

## 📞 Próximos Passos

Após testar a navegação de pessoas por função técnica, você pode:

1. **Testar a navegação de filmes por gênero** (Feature 1)
2. **Implementar melhorias** baseadas no feedback dos testes
3. **Adicionar testes automatizados** para garantir que tudo continue funcionando

Consulte o arquivo `tasks.md` para ver as próximas tarefas!
