# Apresentação final — MercadoFácil (pitch de 8 minutos)

> Roteiro preparado para a entrega. Integrantes: Grazielli Monteiro (RA 6325165), Andrey Rodrigues (RA 6325231), Lucas José (RA 6325123) e Fabio (RA 6325250). Abram o dashboard `aws-lab/scripts/dashboard.html`; se o Superset estiver disponível, usem o dashboard dele e mostrem o filtro nativo.

## Slide 1 — Problema de negócio (1 min)

**Na tela:** “Onde atrasamos, como isso afeta o cliente e como períodos de pico pressionam a operação?”

**Fala:** A MercadoFácil precisa entender onde as entregas atrasam e o impacto na avaliação dos clientes. Também queremos verificar como Black Friday e Natal afetam a demanda. Analisamos uma base tratada de 10 mil itens de pedidos de 2025, sem dados pessoais.

## Slide 2 — Dados e arquitetura (2 min)

**Na tela:** `CSV tratado + chuva + feriados → S3 → Glue Catalog → Athena / views gold → Superset ou dashboard local`

**Fala:** O CSV contém pedidos, itens, status, valores, logística e avaliações. Cruzamos os pedidos com chuva diária por cidade e data e com feriados nacionais pela data. No fluxo da atividade, Terraform provisiona S3, Glue e Athena e pode criar uma instância Superset. As views SQL organizam as métricas para o consumo do dashboard. A receita considera itens entregues; as taxas de cancelamento e devolução usam todos os itens. Um pedido pode ter vários itens, então contamos pedidos distintos quando a métrica é de pedidos.

## Slide 3 — Indicadores executivos (1 min)

**Na tela:** KPIs: receita R$ 3.297.891,59; 6.706 pedidos entregues; 16,27% de itens entregues atrasados; nota média 4,11.

**Fala:** A base tem 10 mil itens: 9.244 entregues, 408 devolvidos e 348 cancelados. A receita dos entregues foi de aproximadamente R$ 3,30 milhões. Esses indicadores dão contexto para explorar qualidade logística e experiência do cliente.

## Slide 4 — Atraso e experiência (1 min)

**Na tela:** gráfico de nota média por faixa de atraso e gráfico logístico por estado.

**Fala:** A nota média foi 4,39 para entregas no prazo, 3,59 com 1 a 3 dias de atraso, 2,35 com 4 a 7 dias e 1,24 com 8 dias ou mais. O padrão é consistente com uma associação entre atraso e pior avaliação. O gráfico por estado ajuda a localizar onde investigar transportadoras e centros de distribuição. A recomendação é priorizar a análise dos atrasos longos e acompanhar a operação por estado e transportadora.

## Slide 5 — Sazonalidade, problemas e chuva (2 min)

**Na tela:** série diária com Black Friday/Natal, cancelamento/devolução por categoria e canal, atraso por chuva; demonstrar o filtro de categoria (Eletrônicos).

**Fala:** Novembro teve R$ 398.823,07 em receita e dezembro R$ 417.595,73, os dois maiores totais mensais. Isso indica demanda elevada no período e justifica planejar capacidade logística. Na análise de chuva, o percentual de atrasos vai de 12,76% na faixa abaixo de 5 mm para 31,48% na faixa de 40 mm ou mais. É uma correlação observacional: diferenças entre cidades e regiões podem explicar parte do padrão; não podemos afirmar causalidade com esta análise. O filtro de categoria permite explorar como os indicadores de categoria mudam no dashboard.

## Slide 6 — Recomendação e limites (1 min)

**Na tela:** “Planejar capacidade para nov/dez; monitorar atrasos longos por estado/transportadora; investigar clima junto com região.”

**Fala:** Recomendamos reforçar a previsão de capacidade para novembro e dezembro, acompanhar atrasos longos por estado e transportadora e avaliar clima junto com localização antes de tomar decisões sobre prazos ou contratos. A análise é descritiva; não estima causalidade. Próximos passos: validar as views no Athena, comparar regiões e transportadoras e manter o dashboard atualizado. Obrigado.

## Demonstração ao vivo

1. Apresentar os KPIs e explicar os denominadores.
2. Filtrar a categoria Eletrônicos e observar os gráficos de categoria e problemas por categoria/canal.
3. Mostrar nota por atraso, sazonalidade e faixa de chuva.
4. Encerrar com a recomendação e a ressalva de correlação versus causalidade.

## Perguntas técnicas para preparar

- Por que há 10.000 itens e menos pedidos distintos?
- Quais itens entram no denominador de cada KPI?
- Por que o resultado da chuva não prova causa?
- O que precisa ser feito para publicar a versão Superset e destruir os recursos AWS ao final?
