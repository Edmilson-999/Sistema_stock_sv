# Manual do Utilizador - Sistema de Gestão de Stock São Vicente

## Introdução

O Sistema de Gestão de Stock São Vicente foi desenvolvido especificamente para coordenar o apoio às vítimas do enchente ocorrido no dia 11 de agosto. Este sistema permite que múltiplas instituições de apoio trabalhem de forma coordenada, mantendo um stock centralizado enquanto preserva a autonomia de cada organização.

## Conceitos Fundamentais

### Stock Centralizado com Gestão Independente

O sistema implementa um modelo único onde existe um stock central partilhado por todas as instituições, mas cada organização apenas pode visualizar e gerir os seus próprios movimentos. Esta abordagem garante transparência na gestão global dos recursos enquanto mantém a privacidade operacional de cada instituição.

### Base de Dados Unificada de Beneficiários

Todos os beneficiários estão registados numa base de dados central acessível por todas as instituições. Cada pessoa é identificada de forma única pelo seu NIF (Número de Identificação Fiscal), permitindo que qualquer instituição consulte o histórico completo de ajuda recebida por um beneficiário, independentemente de qual organização forneceu essa ajuda.

## Acesso ao Sistema

### Credenciais de Login

O sistema está configurado com cinco instituições principais que prestam apoio em São Vicente. Cada instituição possui credenciais específicas para acesso seguro ao sistema.

**Instituições Configuradas:**
- Cáritas São Vicente (username: caritas)
- Cruz Vermelha Cabo Verde (username: cruz_vermelha)  
- ADRA São Vicente (username: adra)
- Bombeiros Voluntários (username: bombeiros)
- Câmara Municipal de São Vicente (username: camara)

Todas as instituições utilizam o código de acesso padrão "sv2024". Este código pode ser alterado individualmente para cada instituição através da administração do sistema.

### Processo de Login

Ao aceder ao sistema através do navegador web, será apresentado um ecrã de login onde deve selecionar a sua instituição na lista disponível e inserir o código de acesso correspondente. Após autenticação bem-sucedida, será redirecionado para o dashboard principal da aplicação.

## Dashboard Principal

### Visão Geral das Estatísticas

O dashboard apresenta quatro indicadores principais que fornecem uma visão imediata do estado atual das operações. O primeiro indicador mostra o número total de beneficiários registados no sistema, representando todas as pessoas que podem receber apoio de qualquer instituição. O segundo indicador apresenta o total de movimentos de stock realizados pela sua instituição, incluindo tanto entradas quanto saídas.

Os terceiro e quarto indicadores detalham especificamente as entradas e saídas de stock da sua instituição, permitindo uma análise rápida do volume de atividade. Estes números são atualizados em tempo real sempre que novos movimentos são registados.

### Navegação Principal

O dashboard oferece três áreas principais de funcionalidade através de cartões interativos claramente identificados. O cartão de Gestão de Beneficiários permite consultar informações sobre as pessoas que recebem apoio, incluindo o seu histórico completo de ajuda. O cartão de Gestão de Stock fornece acesso às funcionalidades de registo de entradas e saídas de materiais. O cartão de Relatórios e Estatísticas apresenta análises detalhadas da atividade da instituição.

## Gestão de Beneficiários

### Consulta de Beneficiários

A secção de beneficiários apresenta uma lista completa de todas as pessoas registadas no sistema. A tabela mostra informações essenciais como o NIF, nome, zona de residência, contacto e número total de ajudas recebidas. Esta informação está disponível para todas as instituições, promovendo transparência e coordenação.

### Pesquisa e Filtros

O sistema inclui uma funcionalidade de pesquisa que permite localizar beneficiários específicos através de diferentes critérios. Pode pesquisar por nome, NIF ou zona de residência, facilitando a identificação rápida de pessoas específicas durante as operações de distribuição.

### Visualização Detalhada

Ao clicar no botão "Ver" junto a qualquer beneficiário, é apresentada uma janela modal com informações completas sobre essa pessoa. Esta vista inclui dados pessoais como idade, contacto e composição do agregado familiar, bem como informações específicas sobre necessidades e observações relevantes.

**Histórico de Ajuda Completo**

A funcionalidade mais importante desta secção é o histórico completo de ajuda recebida. Esta tabela mostra cronologicamente todos os itens que o beneficiário recebeu, incluindo a data, tipo de item, quantidade, instituição que forneceu a ajuda e o motivo da distribuição. Esta informação é crucial para evitar duplicação de esforços e garantir distribuição equitativa.

### Registo de Novos Beneficiários

Qualquer instituição pode registar novos beneficiários no sistema através do botão "Novo Beneficiário". O formulário de registo inclui campos obrigatórios como NIF e nome, bem como informações opcionais como idade, contacto, zona de residência, número de pessoas no agregado familiar, necessidades específicas e observações gerais.

## Gestão de Stock

### Registo de Entradas

O registo de entradas permite documentar todas as doações recebidas pela instituição. Ao clicar em "Registar Entrada", é apresentado um formulário onde deve selecionar o item recebido, especificar a quantidade, indicar a origem da doação e adicionar observações sobre o motivo da entrada.

O sistema inclui um catálogo pré-configurado de itens organizados por categorias como alimentação, vestuário, higiene, casa e medicamentos. Cada item tem uma unidade de medida específica (quilogramas, litros, unidades, pares) que é automaticamente apresentada durante o registo.

### Registo de Saídas

O registo de saídas documenta a distribuição de itens para beneficiários específicos. Este processo requer a seleção do item a distribuir, a quantidade, o beneficiário que receberá a ajuda, o local de entrega e o motivo da distribuição.

**Controlo de Stock Disponível**

O sistema apenas permite registar saídas de itens que tenham stock disponível. Durante a seleção do item, é apresentada a quantidade atual disponível, evitando registos de distribuições impossíveis. Esta funcionalidade garante a integridade dos dados de stock.

### Resumo de Stock

A funcionalidade de resumo apresenta uma visão consolidada do stock atual e da atividade da instituição. São apresentadas estatísticas gerais como total de entradas, saídas e movimentos, bem como uma análise dos movimentos recentes.

A tabela de resumo mostra todos os itens que tiveram movimento pela instituição, indicando o stock total atual (soma de todas as instituições), as entradas específicas da instituição e as saídas específicas da instituição. Esta vista permite compreender a contribuição da instituição para o stock global.

## Relatórios e Estatísticas

### Atividade Recente

A secção de relatórios apresenta um histórico detalhado da atividade recente da instituição. Esta tabela cronológica mostra todos os movimentos de stock realizados, incluindo data, tipo de movimento (entrada ou saída), item, quantidade e detalhes específicos como origem da doação ou beneficiário que recebeu a ajuda.

### Análise de Tendências

Os relatórios permitem identificar padrões na atividade da instituição, como quais itens são mais frequentemente distribuídos, períodos de maior atividade e eficácia das operações de distribuição. Esta informação é valiosa para planeamento futuro e otimização dos processos.

## Funcionalidades Avançadas

### Histórico Completo e Auditoria

O sistema mantém um registo completo de todas as ações realizadas, permitindo auditoria total das operações. Cada movimento de stock é permanentemente registado com informação sobre quem o realizou, quando foi feito e todos os detalhes relevantes.

### Integridade dos Dados

O sistema implementa várias verificações para garantir a integridade dos dados. Não é possível registar saídas superiores ao stock disponível, todos os campos obrigatórios devem ser preenchidos, e os NIFs dos beneficiários devem ser únicos no sistema.

### Segurança e Privacidade

Cada instituição apenas pode visualizar e modificar os seus próprios movimentos de stock. Os dados dos beneficiários são partilhados para coordenação, mas as operações específicas de cada instituição permanecem privadas. O sistema implementa autenticação segura e gestão de sessões para proteger o acesso.

## Resolução de Problemas Comuns

### Problemas de Login

Se não conseguir fazer login, verifique se está a utilizar o username correto da sua instituição e o código de acesso "sv2024". Certifique-se de que seleccionou a instituição correcta na lista antes de inserir o código.

### Problemas com Registo de Movimentos

Se não conseguir registar um movimento de stock, verifique se todos os campos obrigatórios estão preenchidos. Para saídas, confirme se existe stock suficiente do item seleccionado. Se o problema persistir, tente actualizar a página e repetir a operação.

### Problemas de Visualização

Se as informações não estão a carregar correctamente, verifique a sua ligação à internet e tente actualizar a página. O sistema requer uma ligação estável para funcionar adequadamente.

## Boas Práticas de Utilização

### Registo Atempado

Registe todos os movimentos de stock o mais rapidamente possível após ocorrerem. Isto garante que a informação no sistema está sempre actualizada e permite melhor coordenação entre instituições.

### Informação Completa

Preencha sempre todos os campos disponíveis, especialmente os motivos e observações. Esta informação adicional é valiosa para análise posterior e pode ser importante para relatórios e prestação de contas.

### Verificação de Beneficiários

Antes de registar uma saída para um beneficiário, consulte sempre o seu histórico para compreender que ajuda já recebeu. Isto ajuda a garantir distribuição equitativa e evita duplicação desnecessária.

### Coordenação Inter-Institucional

Utilize a informação partilhada sobre beneficiários para coordenar com outras instituições. Se um beneficiário recebeu recentemente ajuda similar de outra organização, considere priorizar outras pessoas ou tipos de ajuda diferentes.

## Suporte Técnico

### Contactos de Emergência

Em caso de problemas técnicos graves que impeçam o funcionamento normal do sistema, contacte imediatamente o administrador técnico. Mantenha sempre uma lista de contactos de emergência actualizada.

### Backup e Recuperação

O sistema mantém automaticamente cópias de segurança de todos os dados. Em caso de perda de informação, é possível recuperar dados de períodos anteriores. No entanto, é importante reportar qualquer problema o mais rapidamente possível.

### Actualizações do Sistema

O sistema pode receber actualizações periódicas para melhorar funcionalidades ou corrigir problemas. Estas actualizações são normalmente realizadas durante períodos de menor atividade e são comunicadas antecipadamente a todas as instituições.

## Conclusão

O Sistema de Gestão de Stock São Vicente representa uma ferramenta fundamental para coordenar eficazmente o apoio às vítimas do enchente. A sua utilização adequada por todas as instituições envolvidas garante transparência, eficiência e equidade na distribuição de ajuda.

A chave para o sucesso do sistema reside na participação ativa de todas as instituições, no registo completo e atempado de todas as operações, e na utilização da informação partilhada para melhorar a coordenação e evitar duplicação de esforços.

Este manual deve ser consultado regularmente, especialmente durante as fases iniciais de utilização do sistema. À medida que se familiariza com as funcionalidades, a utilização torna-se mais intuitiva e eficiente, contribuindo significativamente para o sucesso das operações de apoio humanitário em São Vicente.
