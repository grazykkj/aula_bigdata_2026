"""PLANO B: gera um dashboard HTML local a partir do CSV (sem AWS, sem Superset).

Use se o Superset nao subir a tempo ou se o Learner Lab estiver instavel. O
resultado tambem serve de modelo do que o dashboard do Superset deve mostrar.
So usa a biblioteca padrao; o HTML carrega Chart.js de um CDN (precisa de
internet no navegador).

    python3 dashboard_local.py            # gera dashboard.html ao lado do script
    python3 dashboard_local.py --abrir    # e abre no navegador
"""
import csv
import json
import os
import sys
import webbrowser
from collections import defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(AQUI, "..", "data", "pedidos_mercadofacil_tratado.csv")
CHUVA = os.path.join(AQUI, "..", "data", "chuva_diaria.csv")
SAIDA = os.path.join(AQUI, "dashboard.html")


def carregar():
    with open(CSV, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def carregar_chuva():
    with open(CHUVA, encoding="utf-8") as f:
        return {(r["cidade"], r["dia"]): float(r["chuva_3d_mm"]) for r in csv.DictReader(f)}


def agregar(linhas, incluir_regioes=True):
    chuva = carregar_chuva()
    entregues = [r for r in linhas if r["status_pedido"] == "entregue"]

    por_dia = defaultdict(float)
    por_cat = defaultdict(float)
    for r in entregues:
        por_dia[r["data_pedido"]] += float(r["valor_total"])
        por_cat[r["categoria"]] += float(r["valor_total"])

    atraso_regiao = defaultdict(list)
    atraso_estado = defaultdict(list)
    for r in entregues:
        atraso_regiao[r["regiao"]].append(float(r["atraso_dias"]))
        atraso_estado[r["estado"]].append(float(r["atraso_dias"]))

    faixas = {"0 (no prazo)": [], "1-3": [], "4-7": [], "8+": []}
    for r in entregues:
        if r["nota_avaliacao"] == "":
            continue
        a = int(r["atraso_dias"])
        chave = "0 (no prazo)" if a == 0 else "1-3" if a <= 3 else "4-7" if a <= 7 else "8+"
        faixas[chave].append(int(r["nota_avaliacao"]))

    problemas = defaultdict(lambda: [0, 0, 0])  # itens, cancelado, devolvido
    for r in linhas:
        p = problemas[(r["categoria"], r["canal"])]
        p[0] += 1
        p[1] += r["status_pedido"] == "cancelado"
        p[2] += r["status_pedido"] == "devolvido"

    faixas_chuva = {"<5 mm": [], "5-20": [], "20-40": [], "40+": []}
    for r in entregues:
        mm = chuva[(r["cidade"], r["data_pedido"])]
        chave = "<5 mm" if mm < 5 else "5-20" if mm < 20 else "20-40" if mm < 40 else "40+"
        faixas_chuva[chave].append(float(r["atraso_dias"]))

    def media(v):
        return round(sum(v) / len(v), 2) if v else 0

    dias = sorted(por_dia)
    cats = sorted(por_cat, key=por_cat.get, reverse=True)
    estados = sorted(atraso_estado)
    chaves_problema = sorted(problemas, key=lambda k: (k[0], k[1]))
    dados = {
        "kpis": {
            "receita": round(sum(por_dia.values()), 2),
            "pedidos": len({r["pedido_id"] for r in entregues}),
            "atrasados": round(100 * sum(float(r["atraso_dias"]) > 0 for r in entregues) / len(entregues), 1),
            "nota": media([int(r["nota_avaliacao"]) for r in entregues if r["nota_avaliacao"] != ""]),
        },
        "dia": {"x": dias, "y": [round(por_dia[d], 2) for d in dias]},
        "cat": {"x": cats, "y": [round(por_cat[c], 2) for c in cats]},
        "estado": {"x": estados, "y": [media(atraso_estado[e]) for e in estados]},
        "nota": {"x": list(faixas), "y": [media(v) for v in faixas.values()]},
        "chuva": {"x": list(faixas_chuva), "y": [media(v) for v in faixas_chuva.values()]},
        "problemas": {
            "x": [f"{c} / {canal}" for c, canal in chaves_problema],
            "cancel": [round(100 * problemas[k][1] / problemas[k][0], 2) for k in chaves_problema],
            "devol": [round(100 * problemas[k][2] / problemas[k][0], 2) for k in chaves_problema],
        },
    }
    if incluir_regioes:
        regioes = sorted({r["regiao"] for r in linhas})
        dados["por_regiao"] = {regiao: agregar([r for r in linhas if r["regiao"] == regiao], False) for regiao in regioes}
        dados["regioes"] = regioes
    return dados


HTML = """<!doctype html><html lang="pt-br"><meta charset="utf-8">
<title>MercadoFacil - Dashboard (Plano B)</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>body{font-family:sans-serif;margin:24px;background:#f5f6f8}
.kpis{display:flex;gap:16px;margin-bottom:16px;flex-wrap:wrap}.kpi{background:#fff;padding:16px 24px;border-radius:8px}
.kpi b{display:block;font-size:26px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.card{background:#fff;padding:12px;border-radius:8px}label{display:inline-block;margin:12px 0}</style>
<h1>MercadoFacil 2025 - visao executiva</h1>
<label>Filtrar região: <select id="filtro-regiao"><option value="Todas">Todas as regiões</option></select></label>
<div class="kpis" id="kpis"></div>
<div class="grid">
<div class="card"><canvas id="c1"></canvas></div><div class="card"><canvas id="c2"></canvas></div>
<div class="card"><canvas id="c3"></canvas></div><div class="card"><canvas id="c4"></canvas></div>
<div class="card"><canvas id="c5"></canvas></div><div class="card"><canvas id="c6"></canvas></div></div>
<script>
const D = __DADOS__;
const fmt = new Intl.NumberFormat('pt-BR');
const charts = {};
const seletor = document.getElementById('filtro-regiao');
D.regioes.forEach(r => seletor.add(new Option(r, r)));
function render(d){
const k=d.kpis;
document.getElementById('kpis').innerHTML =
 `<div class=kpi>Receita (entregues)<b>R$ ${fmt.format(k.receita)}</b></div>`+
 `<div class=kpi>Pedidos<b>${fmt.format(k.pedidos)}</b></div>`+
 `<div class=kpi>Itens atrasados<b>${k.atrasados}%</b></div>`+
 `<div class=kpi>Nota media<b>${k.nota}</b></div>`;
function g(id,type,titulo,x,datasets,stacked=false){if(charts[id])charts[id].destroy();charts[id]=new Chart(document.getElementById(id),{type,
 data:{labels:x,datasets},options:{responsive:true,plugins:{title:{display:true,text:titulo}},scales:{x:{stacked,title:{display:true,text:'Categoria / período'}},y:{stacked,title:{display:true,text:'Valor da métrica'}}}}})}
g('c1','line','Receita diária (R$) — destaque para Black Friday e Natal',d.dia.x,[{label:'receita',data:d.dia.y,borderColor:'#1f77b4',pointRadius:0}]);
g('c2','bar','Nota média por faixa de atraso (dias)',d.nota.x,[{label:'nota (1 a 5)',data:d.nota.y,backgroundColor:'#ff7f0e'}]);
g('c3','bar','Atraso médio por estado (dias)',d.estado.x,[{label:'dias',data:d.estado.y,backgroundColor:'#d62728'}]);
g('c4','bar','Receita por categoria (R$)',d.cat.x,[{label:'receita',data:d.cat.y,backgroundColor:'#2ca02c'}]);
g('c5','bar','Cancelamento e devolução por categoria / canal (%)',d.problemas.x,[
 {label:'% cancelado',data:d.problemas.cancel,backgroundColor:'#9467bd'},
 {label:'% devolvido',data:d.problemas.devol,backgroundColor:'#8c564b'}],true);
g('c6','bar','Atraso médio por faixa de chuva acumulada em 3 dias',d.chuva.x,[{label:'dias',data:d.chuva.y,backgroundColor:'#17becf'}]);
}
render(D);
seletor.addEventListener('change',()=>render(seletor.value==='Todas'?D:D.por_regiao[seletor.value]));
</script></html>"""


def main():
    dados = agregar(carregar())
    with open(SAIDA, "w", encoding="utf-8") as f:
        f.write(HTML.replace("__DADOS__", json.dumps(dados, ensure_ascii=False)))
    print(f"Gerado: {SAIDA}")
    if "--abrir" in sys.argv:
        webbrowser.open("file://" + SAIDA)


if __name__ == "__main__":
    main()
