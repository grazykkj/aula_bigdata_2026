# Relatório Final do Projeto de Big Data

## Integrantes do Grupo

- Grazielli Monteiro — RA 6325165
- Andrey Rodrigues — RA 6325231
- Lucas José — RA 6325123
- Fabio — RA 6325250

## Resumo dos Resultados

A análise local da base tratada encontrou 10.000 itens: 9.244 entregues, 408 devolvidos e 348 cancelados. Os itens entregues somam R$ 3.297.891,59 em receita e representam 6.706 pedidos distintos. Entre os itens entregues, 16,27% tiveram atraso; a nota média dos itens avaliados foi 4,11.

O atraso está associado a avaliações piores: a nota média é 4,39 para entregas no prazo, 3,59 para atrasos de 1 a 3 dias, 2,35 para atrasos de 4 a 7 dias e 1,24 para atrasos de 8 dias ou mais. Na série mensal, novembro teve R$ 398.823,07 em receita e dezembro R$ 417.595,73, os dois maiores resultados do ano, compatíveis com maior pressão comercial na Black Friday e no Natal.

Na associação exploratória com chuva acumulada em três dias, o percentual de itens atrasados foi de 12,76% na faixa abaixo de 5 mm e 31,48% na faixa de 40 mm ou mais; o atraso médio também subiu de 0,49 para 1,93 dia. Isso é correlação observada, não evidência de causalidade: clima, cidade, região, calendário e volume operacional podem estar relacionados. A recomendação é dimensionar capacidade para novembro e dezembro e acompanhar atraso e avaliação por região, transportadora e faixa de chuva antes de alterar contratos ou prazos.

## Visualizações Criadas

O dashboard interativo foi criado no Superset e usa as views gold do Athena. Ele contém dez gráficos: Big Numbers de receita, ticket médio, percentual de itens atrasados e nota média geral; linha de receita diária; barras de nota por faixa de atraso; barras de atraso por estado e transportadora; barras empilhadas de cancelamentos e devoluções por categoria e canal; barras de itens atrasados por faixa de chuva; e barras de receita por categoria. O filtro nativo `categoria` foi aplicado aos gráficos de receita por categoria e de cancelamentos/devoluções por categoria e canal, e testado com a categoria Eletrônicos. O dashboard local `aws-lab/scripts/dashboard.html`, gerado por `aws-lab/scripts/dashboard_local.py`, permanece como plano B. As consultas estão em `aws-lab/sql/02_views_prontas.sql` e `aws-lab/sql/03_views_atividade.sql`.

## Lições Aprendidas

A camada gold transforma linhas de itens em métricas com denominadores explícitos: receita, ticket, atraso e nota consideram itens entregues; cancelamento/devolução considera todos os itens. O uso de `COUNT(DISTINCT pedido_id)` evita contar itens como pedidos. Também aprendemos que uma associação entre chuva e atraso não identifica causa, pois região e volume operacional podem influenciar os dois. As consultas foram conferidas no Athena, e o filtro nativo permite explorar categorias no dashboard.

## Referências

- Base tratada MercadoFácil e dados de chuva e feriados fornecidos em `aws-lab/data/`.
- Open-Meteo Historical Weather API: https://open-meteo.com/en/docs/historical-weather-api
- BrasilAPI, feriados nacionais: https://brasilapi.com.br/docs#tag/Feriados-Nacionais
- Amazon Athena, consultas SQL compatíveis com Trino: https://docs.aws.amazon.com/athena/latest/ug/what-is.html
- Apache Superset: https://superset.apache.org/docs/intro/

## Checklist de Entregáveis

- [x] Dashboard interativo criado no Superset com dez gráficos e filtro nativo testado
- [x] O dashboard do Superset foi conectado às views gold do Athena, sobre a base tratada da Aula 14
- [x] Roteiro/slides para a apresentação de 8 minutos estão em `APRESENTACAO_FINAL.md` (personalizar com nomes do grupo e ensaiar)
- [x] Capturas do dashboard com os gráficos e filtro aplicado anexadas em `evidencias/`
