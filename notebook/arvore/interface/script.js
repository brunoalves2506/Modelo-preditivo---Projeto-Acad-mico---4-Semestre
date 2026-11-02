// Cidades de referência por país (pontos aproximados, só para desenhar o mapa)
const CIDADES = {
  "São Paulo": [-23.55, -46.63], "Belo Horizonte": [-19.92, -43.94], "Montevidéu": [-34.90, -56.19],
  "Cochabamba": [-17.39, -66.16], "Tóquio": [35.68, 139.69], "Nova Délhi": [28.61, 77.21],
  "Cidade do Cabo": [-33.92, 18.42], "Joanesburgo": [-26.20, 28.05], "Frankfurt": [50.11, 8.68],
  "Munique": [48.14, 11.58], "Düsseldorf": [51.23, 6.77], "Lisboa": [38.72, -9.14],
  "Córdoba": [-31.42, -64.18], "Bahía Blanca": [-38.72, -62.27], "Madri": [40.42, -3.70],
  "Gdańsk": [54.35, 18.65], "Durban": [-29.86, 31.02], "Nairóbi": [-1.29, 36.82],
  "Mumbai": [19.08, 72.88], "Singapura": [1.35, 103.82]
};

const BR = "6977, 6790, 6659 (br-sao), 6891 (br-bhz)";
const ROTAS = [
  { id: "BR→BR", escopo: "curto", de: "Belo Horizonte", para: "São Paulo", origens: BR, destinos: "148.163.220.5 e 23.179.216.22 (br-sao)", fluxos: "8 / 8", rtt: "0,8 a 9,2", ok: 90.5, risco: 3.1, falha: 6.4 },
  { id: "BR→UY", escopo: "regional", de: "São Paulo", para: "Montevidéu", origens: "os mesmos 4 do Brasil", destinos: "200.7.84.24 e 190.64.201.9 (uy-mvd)", fluxos: "8 / 8", rtt: "25 a 34", ok: 85.0, risco: 6.7, falha: 8.3 },
  { id: "BR→BO", escopo: "regional", de: "São Paulo", para: "Cochabamba", origens: "os mesmos 4", destinos: "200.58.72.14 (bo-cbb), só 1 alvo", fluxos: "4 / 4", rtt: "57 a 89", ok: 71.6, risco: 10.1, falha: 18.3 },
  { id: "BR→JP", escopo: "longo", de: "São Paulo", para: "Tóquio", origens: "os mesmos 4", destinos: "103.167.46.8 (jp-osa) e 202.214.97.16 (jp-tyo)", fluxos: "8 / 8", rtt: "260 a 295", ok: 78.6, risco: 9.2, falha: 12.3 },
  { id: "BR→IN", escopo: "longo", de: "São Paulo", para: "Nova Délhi", origens: "os mesmos 4", destinos: "156.154.184.254 (in-del) e 103.179.107.33 (in-nvm)", fluxos: "8 / 8", rtt: "228 a 328", ok: 77.9, risco: 9.3, falha: 12.8 },
  { id: "BR→ZA", escopo: "longo", de: "São Paulo", para: "Cidade do Cabo", origens: "os mesmos 4", destinos: "102.222.103.100 (za-cpt) e 196.10.53.7 (za-jnb)", fluxos: "8 / 8", rtt: "339 a 356", ok: 28.3, risco: 9.2, falha: 62.4, aviso: "62% de FALHA por causa do MAD minúsculo: uma diferença de 1,3 ms já dá z ≈ 4,9. Veja o cartão abaixo da tabela." },
  { id: "DE→DE", escopo: "curto", de: "Munique", para: "Düsseldorf", origens: "7618 (de-fra), 6826, 6447, 6396 (de-muc)", destinos: "212.119.5.254 (de-dus) e 18.153.158.127 (de-fra)", fluxos: "3 / 8", rtt: "4 a 15", ok: 81.6, risco: 4.9, falha: 13.4, aviso: "5 fluxos excluídos: 18.153.158.127 nunca respondeu e o probe 6447 tem cerca de 1 dia de dados." },
  { id: "DE→PT", escopo: "regional", de: "Frankfurt", para: "Lisboa", origens: "os mesmos 4 da Alemanha", destinos: "91.209.16.127 e 185.32.189.249 (pt-lis)", fluxos: "6 / 8", rtt: "33 a 51", ok: 79.6, risco: 4.9, falha: 15.5, aviso: "2 fluxos excluídos: probe 6447 com cerca de 1 dia de dados." },
  { id: "AR→AR", escopo: "curto", de: "Córdoba", para: "Bahía Blanca", origens: "7617, 7505 (ar-bue), 7414, 7542 (ar-cor)", destinos: "190.124.192.162 (ar-bhi) e 138.204.7.245", fluxos: "3 / 8", rtt: "10 a 48", ok: 95.6, risco: 0.7, falha: 3.7, aviso: "5 fluxos excluídos: 138.204.7.245 e o par 7414→190.124.192.162 nunca responderam." },
  { id: "ES→PL", escopo: "regional", de: "Madri", para: "Gdańsk", origens: "7703, 6687, 6926 (es-mad), 7393", destinos: "51.83.252.103 (pl-ozm) e 151.245.112.32 (pl-gdn)", fluxos: "8 / 8", rtt: "44 a 62", ok: 73.5, risco: 6.7, falha: 19.8, aviso: "O fluxo 6926|151.245.112.32 tem 98,8% de FALHA com desvio de só 1,7 ms." },
  { id: "ZA→KE", escopo: "regional", de: "Joanesburgo", para: "Nairóbi", origens: "7782 (za-dur), 6935 e 6993 (za-jnb), 7467 (za-cpt)", destinos: "196.6.220.42 e 197.157.75.67 (ke-nbo)", fluxos: "8 / 8", rtt: "51 a 74", ok: 73.2, risco: 11.3, falha: 15.6 },
  { id: "IN→SG", escopo: "regional", de: "Mumbai", para: "Singapura", origens: "7375, 7269 (in-maa), 6954 (in-bom), 7277", destinos: "102.130.67.116 e 203.175.175.206 (sg-sin)", fluxos: "4 / 8", rtt: "53 a 103", ok: 85.4, risco: 9.3, falha: 5.3, aviso: "4 fluxos excluídos: 102.130.67.116 nunca respondeu." }
];

const COR = { curto: "#3dd9d6", regional: "#b08cff", longo: "#ff9f43" };
const REGIOES = [
  ["América do Sul", [-25, -58], 2600000], ["Europa", [47, 8], 1900000], ["África", [-15, 30], 3300000],
  ["Sul e Sudeste da Ásia", [14, 90], 3300000], ["Japão", [35.5, 137], 900000]
];
const fmt = n => n.toFixed(1).replace(".", ",") + "%";

// Mapa
const mapa = L.map("mapa", {
  attributionControl: false, minZoom: 2, maxZoom: 7, zoomSnap: 0.5,
  maxBounds: [[-80, -190], [85, 190]], maxBoundsViscosity: 1
}).setView([8, 10], 2);

// Continentes e países (Natural Earth, domínio público), desenhados por baixo das rotas
mapa.createPane("terra").style.zIndex = 250;
fetch("https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json")
  .then(r => r.json())
  .then(t => L.geoJSON(topojson.feature(t, t.objects.countries), {
    pane: "terra", interactive: false,
    style: { color: "#4f6156", weight: 0.7, fillColor: "#27312b", fillOpacity: 1 }
  }).addTo(mapa))
  .catch(() => {
    document.getElementById("mapa").insertAdjacentHTML("beforeend",
      '<p class="erro-mapa">Não foi possível carregar o desenho dos continentes. Verifique a internet e atualize a página.</p>');
  });

REGIOES.forEach(([nome, c, raio]) => {
  L.circle(c, { radius: raio, color: "#63ff2f", weight: 1, dashArray: "4 6", fillColor: "#63ff2f", fillOpacity: .05, interactive: false }).addTo(mapa);
  L.marker(c, { interactive: false, icon: L.divIcon({ className: "rotulo-regiao", html: nome, iconSize: [160, 16], iconAnchor: [80, 8] }) }).addTo(mapa);
});

// Curva de Bézier entre duas cidades
function arco(a, b) {
  const m = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2], dx = b[1] - a[1], dy = b[0] - a[0];
  const c = [m[0] + dx * 0.18, m[1] - dy * 0.18], pts = [];
  for (let t = 0; t <= 1.001; t += 1 / 32) {
    pts.push([(1 - t) ** 2 * a[0] + 2 * (1 - t) * t * c[0] + t ** 2 * b[0], (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * c[1] + t ** 2 * b[1]]);
  }
  return pts;
}

const camadas = {};
const nos = new Set();
ROTAS.forEach(r => {
  const a = CIDADES[r.de], b = CIDADES[r.para];
  const linha = L.polyline(arco(a, b), { color: COR[r.escopo], weight: 3, opacity: .75 }).addTo(mapa);
  linha.bindTooltip(`${r.id} (${r.escopo}): ${fmt(r.falha)} de FALHA`, { sticky: true });
  linha.on("click", () => selecionar(r.id));
  camadas[r.id] = linha;
  [r.de, r.para].forEach(n => {
    if (nos.has(n)) return;
    nos.add(n);
    L.circleMarker(CIDADES[n], { radius: 5, color: "#fff", weight: 1, fillColor: "#63ff2f", fillOpacity: 1 }).bindTooltip(n).addTo(mapa);
  });
});

// Tabela
const corpo = document.querySelector("#tabela tbody");
ROTAS.forEach(r => {
  const tr = document.createElement("tr");
  tr.tabIndex = 0;
  tr.dataset.id = r.id;
  tr.dataset.escopo = r.escopo;
  tr.innerHTML = `<td class="rota">${r.id}</td><td><span class="etiqueta ${r.escopo}">${r.escopo}</span></td>
    <td>${r.origens}</td><td>${r.destinos}</td><td class="num">${r.fluxos}</td><td class="num">${r.rtt}</td>
    <td class="num">${fmt(r.ok)}</td><td class="num">${fmt(r.risco)}</td>
    <td class="num ${r.falha > 30 ? "falha-alta" : ""}">${fmt(r.falha)}</td>
    <td><div class="barra" role="img" aria-label="OK ${fmt(r.ok)}, RISCO ${fmt(r.risco)}, FALHA ${fmt(r.falha)}">
      <i class="ok" style="width:${r.ok}%"></i><i class="risco" style="width:${r.risco}%"></i><i class="falha" style="width:${r.falha}%"></i></div></td>`;
  tr.addEventListener("click", () => selecionar(r.id));
  tr.addEventListener("keydown", e => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); selecionar(r.id); } });
  corpo.appendChild(tr);
});

// Seleção e filtro
function selecionar(id) {
  const r = ROTAS.find(x => x.id === id);
  Object.entries(camadas).forEach(([k, l]) => l.setStyle({ weight: k === id ? 6 : 3, opacity: k === id ? 1 : .4 }));
  camadas[id].bringToFront();
  mapa.fitBounds(camadas[id].getBounds(), { padding: [60, 60], maxZoom: 5 });
  document.querySelectorAll("#tabela tbody tr").forEach(tr => tr.classList.toggle("sel", tr.dataset.id === id));
  document.getElementById("detalhe").innerHTML = `<h3>${r.id} (${r.escopo})</h3>
    <dl><dt>Origens (probes)</dt><dd>${r.origens}</dd><dt>Destinos (IPs)</dt><dd>${r.destinos}</dd>
    <dt>Fluxos válidos</dt><dd>${r.fluxos}</dd><dt>RTT normal</dt><dd>${r.rtt} ms</dd>
    <dt>Resultado</dt><dd>OK ${fmt(r.ok)}, RISCO ${fmt(r.risco)}, FALHA ${fmt(r.falha)}</dd></dl>
    ${r.aviso ? `<p><b>Atenção:</b> ${r.aviso}</p>` : ""}`;
}

document.querySelectorAll(".filtro").forEach(btn => btn.addEventListener("click", () => {
  const esc = btn.dataset.escopo;
  document.querySelectorAll(".filtro").forEach(b => b.classList.toggle("ativo", b === btn));
  ROTAS.forEach(r => {
    const mostrar = esc === "todos" || r.escopo === esc;
    if (mostrar) camadas[r.id].addTo(mapa); else mapa.removeLayer(camadas[r.id]);
    camadas[r.id].setStyle({ weight: 3, opacity: .75 });
  });
  document.querySelectorAll("#tabela tbody tr").forEach(tr => {
    tr.classList.remove("sel");
    tr.classList.toggle("oculta", !(esc === "todos" || tr.dataset.escopo === esc));
  });
  mapa.setView([5, 10], 2);
}));
