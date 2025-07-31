# Dashboard Excel - Funcionalidade

## 📊 Visão Geral

A nova aba "Excel" no dashboard CEO permite processar e analisar dados de arquivos Excel armazenados na pasta "registros monitorar". A funcionalidade foi desenvolvida para funcionar sem banco de dados, mantendo os dados em memória para otimizar o uso de recursos.

## 🚀 Funcionalidades

### 1. **Carregamento de Pasta**
- Botão "Carregar Pasta" que processa todos os arquivos Excel
- Suporte para arquivos `.xlsx` e `.xls`
- Processamento recursivo de subpastas
- Interface intuitiva com feedback visual

### 2. **Gráficos Interativos**
- **Gráficos de Barras**: Visualização clara dos dados
- **Alternância entre funcionários**: Clique para trocar entre funcionários
- **Dados por semana E por mês**: Duas visualizações temporais
- **Comparativo entre meses**: Análise temporal completa

### 3. **Lógica de Meses Especial**
- **Período**: Do dia 26 ao dia 25 = 1 mês
- **Exemplo**: 26/06 a 25/07 = Julho
- **Processamento**: Todos os meses são processados automaticamente

### 4. **Sem Banco de Dados**
- **Dados em memória**: Processamento rápido
- **Após F5**: Dados somem (não salvos no DB)
- **Ideal para Render**: Limite de 1GB respeitado

### 5. **Estatísticas Gerais**
- Total de funcionários processados
- Total de semanas e meses
- Melhor funcionário identificado
- Médias de desempenho

## 🛠️ Tecnologias Utilizadas

- **Flask**: Framework web
- **Pandas**: Processamento de dados Excel
- **Chart.js**: Gráficos interativos
- **Bootstrap**: Interface responsiva

## 📁 Estrutura de Arquivos

```
registros monitorar/
├── mes 4/
│   ├── Matheus Abril.xlsx
│   ├── Maurício Abril.xlsx
│   └── Rodrigo Abril.xlsx
├── mes 5/
│   ├── Matheus Maio.xlsx
│   └── Maurício Maio.xlsx
└── mes 7/
    ├── Matheus Julho.xlsx
    ├── Maurício Julho.xlsx
    └── Wesley Julho.xlsx
```

## 📋 Formato dos Arquivos Excel

Os arquivos Excel devem seguir este formato:

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| Data | Data da entrada | 2025-03-26 19:00:00 |
| Refinaria | Nome da refinaria | RPBC |
| Pontos | Pontos ganhos | 331 |
| Observações | Comentários | ARNO - chuva forte |

## 🎯 Como Usar

### 1. Acessar a Aba Excel
- Faça login como CEO
- Acesse o dashboard CEO
- Clique na aba "Excel"

### 2. Carregar Dados
- Digite o caminho da pasta (padrão: `./registros monitorar`)
- Clique em "Carregar Pasta"
- Aguarde o processamento

### 3. Visualizar Gráficos
- Selecione um funcionário específico ou "Todos os Funcionários"
- Alternar entre visualização "Semanal" e "Mensal"
- Interaja com os gráficos

### 4. Análise de Dados
- Visualize estatísticas gerais
- Compare desempenho entre funcionários
- Analise tendências temporais

## 🔧 Arquivos Criados/Modificados

### Novos Arquivos
- `routes/excel_dashboard.py`: Lógica do dashboard Excel
- `templates/excel_dashboard.html`: Template standalone (opcional)
- `test_excel.py`: Script de teste
- `README_EXCEL.md`: Esta documentação

### Arquivos Modificados
- `app.py`: Registro do novo blueprint
- `templates/ceo_dashboard_enhanced.html`: Adição da aba Excel

## 🧪 Testes

Execute o script de teste para verificar a funcionalidade:

```bash
python test_excel.py
```

## 📊 APIs Disponíveis

### POST `/api/load_folder`
Carrega e processa arquivos Excel de uma pasta.

**Parâmetros:**
```json
{
  "folder_path": "./registros monitorar"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Processados 45 registros de 3 funcionários"
}
```

### GET `/api/excel_data`
Retorna dados processados em memória.

**Resposta:**
```json
{
  "success": true,
  "data": {
    "processed": true,
    "employees": ["Matheus", "Maurício", "Wesley"],
    "weekly_data": {...},
    "monthly_data": {...},
    "statistics": {...}
  }
}
```

### GET `/api/chart_data`
Retorna dados para gráficos.

**Parâmetros:**
- `type`: "weekly" ou "monthly"
- `employee`: Nome do funcionário (opcional)

## 🎨 Interface

A interface segue o design do dashboard CEO existente:
- **Tema escuro** com gradientes
- **Cards de estatísticas** com animações
- **Gráficos responsivos** com Chart.js
- **Feedback visual** para carregamento

## 🔒 Segurança

- **Acesso restrito**: Apenas usuários CEO
- **Validação de entrada**: Verificação de caminhos de arquivo
- **Tratamento de erros**: Mensagens amigáveis
- **Sanitização**: Dados processados com segurança

## 🚀 Deploy

A funcionalidade é compatível com:
- **Render**: Limite de 1GB respeitado
- **Heroku**: Sem necessidade de banco de dados
- **VPS**: Execução local ou remota

## 📈 Próximas Melhorias

- [ ] Export de dados processados
- [ ] Filtros avançados por período
- [ ] Gráficos de tendência
- [ ] Comparativo entre períodos
- [ ] Relatórios em PDF
- [ ] Cache de dados processados

## 🐛 Solução de Problemas

### Erro: "Nenhum arquivo Excel encontrado"
- Verifique se a pasta existe
- Confirme se há arquivos `.xlsx` ou `.xls`
- Verifique permissões de leitura

### Erro: "Erro ao processar arquivo"
- Verifique o formato das colunas
- Confirme se as datas estão no formato correto
- Verifique se os pontos são números válidos

### Gráficos não aparecem
- Verifique se o Chart.js está carregado
- Confirme se há dados processados
- Verifique o console do navegador

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs da aplicação
2. Execute o script de teste
3. Consulte esta documentação
4. Entre em contato com o desenvolvedor 