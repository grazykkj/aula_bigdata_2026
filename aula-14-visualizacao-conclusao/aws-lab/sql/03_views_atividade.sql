-- Camada gold da Aula 14. Execute cada CREATE OR REPLACE no Athena.
-- Convencao: receita = valor_total dos itens entregues.

-- A) Relação entre atraso logístico e avaliação (somente entregues avaliados).
CREATE OR REPLACE VIEW vw_atraso_nota AS
SELECT CASE
         WHEN atraso_dias = 0 THEN '1) 0 - no prazo'
         WHEN atraso_dias BETWEEN 1 AND 3 THEN '2) 1-3 dias'
         WHEN atraso_dias BETWEEN 4 AND 7 THEN '3) 4-7 dias'
         ELSE '4) 8+ dias'
       END AS faixa_atraso,
       COUNT(*) AS avaliacoes,
       ROUND(AVG(CAST(nota_avaliacao AS DOUBLE)), 2) AS nota_media
FROM pedidos
WHERE status_pedido = 'entregue' AND nota_avaliacao IS NOT NULL
GROUP BY 1;

-- B) Participação de cancelamentos/devoluções no total de itens da categoria/canal.
CREATE OR REPLACE VIEW vw_problemas_categoria AS
SELECT categoria, canal, COUNT(*) AS itens,
       ROUND(100.0 * SUM(CASE WHEN status_pedido = 'cancelado' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_cancelado,
       ROUND(100.0 * SUM(CASE WHEN status_pedido = 'devolvido' THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_devolvido
FROM pedidos
GROUP BY categoria, canal;

-- C) Série temporal diária, considerando somente pedidos entregues.
CREATE OR REPLACE VIEW vw_serie_diaria AS
SELECT data_pedido AS dia,
       COUNT(DISTINCT pedido_id) AS pedidos,
       ROUND(SUM(valor_total), 2) AS receita,
       ROUND(SUM(valor_total) / COUNT(DISTINCT pedido_id), 2) AS ticket_medio
FROM pedidos
WHERE status_pedido = 'entregue'
GROUP BY data_pedido;

-- D) KPIs executivos em uma linha. Taxas de problema usam todos os itens.
CREATE OR REPLACE VIEW vw_kpis AS
SELECT ROUND(SUM(CASE WHEN status_pedido = 'entregue' THEN valor_total ELSE 0 END), 2) AS receita_total,
       COUNT(DISTINCT CASE WHEN status_pedido = 'entregue' THEN pedido_id END) AS pedidos,
       ROUND(SUM(CASE WHEN status_pedido = 'entregue' THEN valor_total ELSE 0 END) /
             NULLIF(COUNT(DISTINCT CASE WHEN status_pedido = 'entregue' THEN pedido_id END), 0), 2) AS ticket_medio,
       ROUND(100.0 * SUM(CASE WHEN status_pedido = 'entregue' AND atraso_dias > 0 THEN 1 ELSE 0 END) /
             NULLIF(SUM(CASE WHEN status_pedido = 'entregue' THEN 1 ELSE 0 END), 0), 2) AS pct_itens_atrasados,
       ROUND(AVG(CASE WHEN status_pedido = 'entregue' THEN CAST(nota_avaliacao AS DOUBLE) END), 2) AS nota_media,
       ROUND(100.0 * SUM(CASE WHEN status_pedido IN ('cancelado', 'devolvido') THEN 1 ELSE 0 END) /
             NULLIF(COUNT(*), 0), 2) AS pct_cancelado_devolvido
FROM pedidos;

-- E) Chuva acumulada do dia do pedido e dois dias seguintes. Associação é
-- observacional; região/cidade pode confundir qualquer relação com atraso.
CREATE OR REPLACE VIEW vw_atraso_chuva AS
SELECT CASE
         WHEN c.chuva_3d_mm < 5 THEN '1) sem chuva (<5 mm)'
         WHEN c.chuva_3d_mm < 20 THEN '2) fraca (5-20)'
         WHEN c.chuva_3d_mm < 40 THEN '3) forte (20-40)'
         ELSE '4) muito forte (40+)'
       END AS faixa_chuva,
       COUNT(*) AS itens,
       ROUND(AVG(CAST(p.atraso_dias AS DOUBLE)), 2) AS atraso_medio_dias,
       ROUND(100.0 * AVG(CASE WHEN p.atraso_dias > 0 THEN 1.0 ELSE 0.0 END), 2) AS pct_atrasados
FROM pedidos p
JOIN chuva_diaria c ON p.cidade = c.cidade AND p.data_pedido = c.dia
WHERE p.status_pedido = 'entregue'
GROUP BY 1;

-- F) Compara operação em feriados nacionais e dias comuns.
CREATE OR REPLACE VIEW vw_feriados AS
WITH dias_feriados AS (SELECT DISTINCT dia FROM feriados)
SELECT CASE WHEN f.dia IS NOT NULL THEN 'feriado' ELSE 'dia comum' END AS tipo_dia,
       COUNT(DISTINCT p.data_pedido) AS dias,
       COUNT(DISTINCT p.pedido_id) AS pedidos,
       ROUND(CAST(COUNT(DISTINCT p.pedido_id) AS DOUBLE) / NULLIF(COUNT(DISTINCT p.data_pedido), 0), 2) AS pedidos_por_dia,
       ROUND(AVG(CAST(p.atraso_dias AS DOUBLE)), 2) AS atraso_medio_dias
FROM pedidos p
LEFT JOIN dias_feriados f ON p.data_pedido = f.dia
WHERE p.status_pedido = 'entregue'
GROUP BY 1;

-- Bônus: identifica transportadoras com maior incidência de atraso e volume
-- suficiente para comparação (mínimo de 30 itens entregues).
CREATE OR REPLACE VIEW vw_transportadora_desempenho AS
SELECT transportadora, regiao,
       COUNT(*) AS itens_entregues,
       ROUND(AVG(CAST(atraso_dias AS DOUBLE)), 2) AS atraso_medio_dias,
       ROUND(100.0 * AVG(CASE WHEN atraso_dias > 0 THEN 1.0 ELSE 0.0 END), 2) AS pct_atrasados,
       ROUND(AVG(CAST(nota_avaliacao AS DOUBLE)), 2) AS nota_media
FROM pedidos
WHERE status_pedido = 'entregue'
GROUP BY transportadora, regiao
HAVING COUNT(*) >= 30;
