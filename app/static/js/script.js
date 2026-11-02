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

const COR = { curto: "#50dfff", regional: "#b08cff", longo: "#ff9f43" };
const COR_STATUS = { OK: "#43d6a3", RISCO: "#ffc86a", FALHA: "#ff657d" };
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
    style: { color: "#1d5876", weight: 0.8, fillColor: "#0b2740", fillOpacity: 1 }
  }).addTo(mapa))
  .catch(() => {
    document.getElementById("mapa").insertAdjacentHTML("beforeend",
      '<p class="erro-mapa">Não foi possível carregar o desenho dos continentes. Verifique a internet e atualize a página.</p>');
  });

REGIOES.forEach(([nome, c, raio]) => {
  L.circle(c, { radius: raio, color: "#50dfff", weight: 1, dashArray: "4 6", fillColor: "#50dfff", fillOpacity: .05, interactive: false }).addTo(mapa);
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
const paginasPings = new Map();
const TAMANHO_PAGINA = 500;
let totalPings = 0;
let inicioHistorico = 0;
let fimHistorico = 0;
let indicePing = -1;
let pingAtual = null;
let temporizador = null;
let reproduzindo = false;
let animacaoPing = null;
let marcadorPing = null;
let rotaSelecionada = null;
let horizonteMinutos = 12;
let rotaDoPingAnterior = null;
let revisaoBusca = 0;
let velocidadeReproducao = 2;
ROTAS.forEach(r => {
  const a = CIDADES[r.de], b = CIDADES[r.para];
  const linha = L.polyline(arco(a, b), { color: COR[r.escopo], weight: 3, opacity: .75 }).addTo(mapa);
  linha.bindTooltip(`${r.id}: aguardando ping`, { sticky: true });
  linha.on("click", () => selecionar(r.id));
  camadas[r.id] = linha;
  [r.de, r.para].forEach(n => {
    if (nos.has(n)) return;
    nos.add(n);
    L.circleMarker(CIDADES[n], { radius: 5, color: "#e5f4ff", weight: 1, fillColor: "#50dfff", fillOpacity: 1 }).bindTooltip(n).addTo(mapa);
  });
});

ROTAS.forEach(r => {
  const opcaoRota = document.createElement("option");
  opcaoRota.value = r.id;
  opcaoRota.textContent = r.id.replace("→", " → ");
  document.getElementById("rota-selecionada").appendChild(opcaoRota);
});

// Seleção e filtro
function selecionar(id) {
  const r = ROTAS.find(x => x.id === id);
  if (!r) return;
  rotaSelecionada = id;
  document.getElementById("rota-selecionada").value = id;
  atualizarMapaPing(pingAtual, false);
  mapa.fitBounds(camadas[id].getBounds(), { padding: [60, 60], maxZoom: 5 });
}

function formatarInstante(timestamp) {
  return new Intl.DateTimeFormat("pt-BR", {
    timeZone: "UTC",
    dateStyle: "short",
    timeStyle: "medium",
  }).format(new Date(timestamp * 1000)) + " UTC";
}

function textoTooltip(ping) {
  return `${ping.rota}: previsão ${ping.status} (${fmt(ping.confianca_pct)} de confiança) `
    + `para ${ping.fluxo_id}, cerca de ${horizonteMinutos} min após o ping.`;
}

function atualizarEstilosRotas(ping) {
  const rotaDoPing = ping && ROTAS.find(r => r.id === ping.rota);
  const temSelecao = Boolean(rotaSelecionada);
  ROTAS.forEach(rota => {
    const selecionada = rota.id === rotaSelecionada;
    const pingAtivo = rotaDoPing && rota.id === rotaDoPing.id;
    const linha = camadas[rota.id];
    linha.setStyle({
      color: pingAtivo ? COR_STATUS[ping.status] : COR[rota.escopo],
      weight: selecionada ? 8 : pingAtivo ? 4 : temSelecao ? 2 : 3,
      opacity: !temSelecao ? (pingAtivo ? 1 : .75) : selecionada ? 1 : pingAtivo ? .48 : .14,
      dashArray: null,
    });
    const elemento = linha.getElement();
    if (elemento) elemento.classList.toggle("rota-destacada", selecionada);
  });
  if (rotaSelecionada) camadas[rotaSelecionada].bringToFront();
}

function atualizarMapaPing(ping, animar) {
  if (rotaDoPingAnterior && camadas[rotaDoPingAnterior]) {
    const anterior = ROTAS.find(r => r.id === rotaDoPingAnterior);
    camadas[rotaDoPingAnterior].setTooltipContent(`${anterior.id}: aguardando próximo ping`);
  }
  atualizarEstilosRotas(ping);
  if (!ping) {
    rotaDoPingAnterior = null;
    return;
  }

  const rota = ROTAS.find(r => r.id === ping.rota);
  if (!rota) return;
  camadas[rota.id].setTooltipContent(textoTooltip(ping));
  rotaDoPingAnterior = rota.id;

  if (animacaoPing !== null) window.cancelAnimationFrame(animacaoPing);
  if (!marcadorPing) {
    marcadorPing = L.circleMarker(CIDADES[rota.de], {
      radius: 7,
      color: "#fff",
      weight: 2,
      fillColor: COR_STATUS[ping.status],
      fillOpacity: 1,
    }).bindTooltip(`${ping.status}: ${ping.fluxo_id}`, { sticky: true }).addTo(mapa);
  }
  const pontos = camadas[rota.id].getLatLngs();
  if (!pontos.length) return;
  marcadorPing.setStyle({ fillColor: COR_STATUS[ping.status] });
  marcadorPing.setTooltipContent(`${ping.status}: ${ping.fluxo_id}`);
  if (!animar) {
    marcadorPing.setLatLng(pontos[0]);
    return;
  }

  const inicioAnimacao = performance.now();
  const duracao = Math.max(80, 1200 / velocidadeReproducao);
  function moverPing(agora) {
    const progresso = Math.max(0, Math.min((agora - inicioAnimacao) / duracao, 1));
    const posicao = progresso * (pontos.length - 1);
    const indice = Math.min(Math.floor(posicao), pontos.length - 1);
    const proporcao = posicao - indice;
    const atual = pontos[indice];
    const proximo = pontos[Math.min(indice + 1, pontos.length - 1)];
    if (!atual || !proximo) return;
    marcadorPing.setLatLng([
      atual.lat + (proximo.lat - atual.lat) * proporcao,
      atual.lng + (proximo.lng - atual.lng) * proporcao,
    ]);
    if (progresso < 1) animacaoPing = window.requestAnimationFrame(moverPing);
    else animacaoPing = null;
  }
  animacaoPing = window.requestAnimationFrame(moverPing);
}

async function carregarPaginaPings(indice) {
  const offset = Math.floor(indice / TAMANHO_PAGINA) * TAMANHO_PAGINA;
  if (paginasPings.has(offset)) return paginasPings.get(offset);

  const resposta = await fetch(`/api/pings-previstos?offset=${offset}&limite=${TAMANHO_PAGINA}`);
  if (!resposta.ok) {
    const erro = await resposta.json();
    throw new Error(erro.erro || `O servidor respondeu com status ${resposta.status}.`);
  }
  const pagina = await resposta.json();
  paginasPings.set(offset, pagina.pings);
  return pagina.pings;
}

async function mostrarPing(indice) {
  const indiceLimitado = Math.max(0, Math.min(indice, totalPings - 1));
  const revisao = ++revisaoBusca;
  try {
    const offset = Math.floor(indiceLimitado / TAMANHO_PAGINA) * TAMANHO_PAGINA;
    const pings = await carregarPaginaPings(indiceLimitado);
    if (revisao !== revisaoBusca) return;
    pingAtual = pings[indiceLimitado - offset];
    if (!pingAtual) throw new Error(`O ping ${indiceLimitado + 1} não existe na resposta do servidor.`);
    indicePing = indiceLimitado;
    document.getElementById("ping-selecionado").value = indicePing;
    document.getElementById("rotulo-ping").textContent =
      `${(indicePing + 1).toLocaleString("pt-BR")} de ${totalPings.toLocaleString("pt-BR")} · `
      + `${formatarInstante(pingAtual.timestamp)} → ${formatarInstante(pingAtual.previsto_em)}`;
    document.getElementById("ping-anterior").disabled = indicePing === 0;
    document.getElementById("proximo-ping").disabled = indicePing === totalPings - 1;
    document.getElementById("resumo-previsao").textContent =
      `${pingAtual.fluxo_id} em ${pingAtual.rota}: previsão ${pingAtual.status} `
      + `(${fmt(pingAtual.confianca_pct)} de confiança) para ${horizonteMinutos} min após a medição.`;
    atualizarMapaPing(pingAtual, true);
  } catch (erro) {
    pararReproducao();
    document.getElementById("resumo-previsao").textContent =
      `Não foi possível carregar o ping: ${erro.message}`;
  }
}

function pararReproducao() {
  reproduzindo = false;
  revisaoBusca += 1;
  if (temporizador !== null) {
    window.clearTimeout(temporizador);
    temporizador = null;
  }
  document.getElementById("reproduzir").textContent = "Reproduzir";
}

function agendarProximoPing() {
  temporizador = window.setTimeout(async () => {
    if (!reproduzindo) return;
    if (indicePing >= totalPings - 1) {
      pararReproducao();
      return;
    }
    await mostrarPing(indicePing + 1);
    if (reproduzindo) agendarProximoPing();
  }, 1200 / velocidadeReproducao);
}

function iniciarReproducao() {
  if (indicePing >= totalPings - 1) {
    mostrarPing(0).then(() => {
      if (indicePing !== 0) return;
      reproduzindo = true;
      document.getElementById("reproduzir").textContent = "Pausar";
      agendarProximoPing();
    });
    return;
  }
  reproduzindo = true;
  document.getElementById("reproduzir").textContent = "Pausar";
  agendarProximoPing();
}

async function carregarPrevisoes() {
  const resposta = await fetch(`/api/pings-previstos?offset=0&limite=${TAMANHO_PAGINA}`);
  if (!resposta.ok) throw new Error(`O servidor respondeu com status ${resposta.status}.`);
  const pagina = await resposta.json();
  if (!Number.isInteger(pagina.total) || pagina.total < 1 || !Array.isArray(pagina.pings) || !pagina.pings.length) {
    throw new Error("A resposta do histórico não contém pings previstos válidos.");
  }
  paginasPings.set(0, pagina.pings);
  totalPings = pagina.total;
  inicioHistorico = pagina.inicio;
  fimHistorico = pagina.fim;
  horizonteMinutos = pagina.horizonte_minutos;
  const controle = document.getElementById("ping-selecionado");
  controle.max = totalPings - 1;
  controle.disabled = false;
  ["ping-anterior", "proximo-ping", "reproduzir", "velocidade-reproducao"].forEach(id => {
    document.getElementById(id).disabled = false;
  });
  document.getElementById("resumo-previsao").textContent =
    `Histórico de ${formatarInstante(inicioHistorico)} a ${formatarInstante(fimHistorico)}. `
    + `${totalPings.toLocaleString("pt-BR")} pings disponíveis; cada resultado prevê a classe `
    + `aproximadamente ${horizonteMinutos} minutos depois.`;
  await mostrarPing(0);
}

document.getElementById("ping-selecionado").addEventListener("input", evento => {
  pararReproducao();
  mostrarPing(Number(evento.target.value));
});
document.getElementById("ping-anterior").addEventListener("click", () => {
  pararReproducao();
  mostrarPing(indicePing - 1);
});
document.getElementById("proximo-ping").addEventListener("click", () => {
  pararReproducao();
  mostrarPing(indicePing + 1);
});
document.getElementById("reproduzir").addEventListener("click", () => {
  if (reproduzindo) {
    pararReproducao();
    return;
  }
  iniciarReproducao();
});
document.getElementById("velocidade-reproducao").addEventListener("change", () => {
  velocidadeReproducao = Number(document.getElementById("velocidade-reproducao").value);
  if (!reproduzindo) return;
  if (temporizador !== null) window.clearTimeout(temporizador);
  agendarProximoPing();
});

document.getElementById("rota-selecionada").addEventListener("change", evento => {
  if (evento.target.value) {
    selecionar(evento.target.value);
    return;
  }
  rotaSelecionada = null;
  atualizarMapaPing(pingAtual, false);
  mapa.setView([5, 10], 2);
});

document.querySelectorAll(".filtro").forEach(btn => btn.addEventListener("click", () => {
  const esc = btn.dataset.escopo;
  document.querySelectorAll(".filtro").forEach(b => b.classList.toggle("ativo", b === btn));
  ROTAS.forEach(r => {
    const mostrar = esc === "todos" || r.escopo === esc;
    if (mostrar) camadas[r.id].addTo(mapa); else mapa.removeLayer(camadas[r.id]);
  });
  rotaSelecionada = null;
  document.getElementById("rota-selecionada").value = "";
  atualizarMapaPing(pingAtual, false);
  mapa.setView([5, 10], 2);
}));

carregarPrevisoes().catch(erro => {
  document.getElementById("resumo-previsao").textContent =
    `Não foi possível carregar os pings previstos: ${erro.message} Inicie a interface pelo servidor Flask e tente novamente.`;
});
