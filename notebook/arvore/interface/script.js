// Integração da interface com o modelo: o botão chama o servidor (POST /api/medicao),
// que mede a rede por ICMP, calcula as métricas relativas e classifica com o modelo treinado.

const ROTULOS = { OK: "OK", RISCO: "RISCO", FALHA: "FALHA" };

function elemento(tag, classe, texto) {
    const el = document.createElement(tag);
    if (classe) el.className = classe;
    if (texto !== undefined) el.textContent = texto;
    return el;
}

function fmt(valor, unidade, casas) {
    if (valor === null || valor === undefined) return "—";
    return valor.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas }) + " " + unidade;
}

function limpar_resultado() {
    document.getElementById("container_sec_info").classList.add("oculto");
    const painel = document.getElementById("status_rede_tempo_real");
    painel.className = "";
    document.getElementById("status_rede_texto").textContent = "";
    const info = document.getElementById("info_medicao");
    info.classList.remove("erro");
    info.replaceChildren();
}

function mostrar_resultado(d) {
    const painel = document.getElementById("status_rede_tempo_real");
    painel.className = "status_" + d.status.toLowerCase();
    document.getElementById("status_rede_texto").textContent = ROTULOS[d.status];
    document.getElementById("container_sec_info").classList.remove("oculto");

    const info = document.getElementById("info_medicao");
    info.appendChild(elemento("div", "info_mensagem", d.mensagem));

    const m = d.metricas;
    const variacao = m.variacao_pct === null ? "" : ` (${m.variacao_pct > 0 ? "+" : ""}${m.variacao_pct}%)`;
    const metricas = elemento("div", "info_metricas");
    [
        ["Latência: ", fmt(m.latencia_ms, "ms", 1) + variacao],
        ["Normal da rede: ", fmt(m.normal_ms, "ms", 1)],
        ["Jitter: ", fmt(m.jitter_ms, "ms", 2)],
        ["Perda de pacotes: ", fmt(m.perda_pct, "%", 0)],
    ].forEach(([rotulo, valor]) => {
        const linha = elemento("div");
        linha.appendChild(elemento("span", null, rotulo));
        linha.appendChild(document.createTextNode(valor));
        metricas.appendChild(linha);
    });
    info.appendChild(metricas);

    d.alvos.forEach(a => {
        const linha = elemento("div", "info_alvo");
        linha.appendChild(elemento("div", null, `${a.nome} (${a.endereco})  ${fmt(a.latencia_ms, "ms", 1)}`));
        linha.appendChild(elemento("b", a.status ? "status_" + a.status.toLowerCase() : "", a.status || "—"));
        info.appendChild(linha);
    });

    let rodape = `Medido às ${d.medido_em}` + (d.referencia.simulada ? "" : ` (${d.duracao_s} s)`);
    if (d.referencia.simulada) rodape += " • MODO DEMONSTRAÇÃO";
    else if (d.referencia.criada_agora) rodape += " • referência criada agora";
    else if (d.referencia.provisoria) rodape += " • referência provisória";
    info.appendChild(elemento("div", "info_rodape", rodape));
}

function mostrar_erro(texto) {
    // Sem resultado válido: o painel de status continua escondido e o container só mostra o aviso.
    const info = document.getElementById("info_medicao");
    info.classList.add("erro");
    info.replaceChildren(elemento("div", "info_erro", texto));
}

async function obter_medicao() {
    const botao = document.getElementById("botao_acao");
    const barra = document.getElementById("carregando_medicao");

    botao.disabled = true;
    limpar_resultado();
    barra.classList.remove("oculto");

    try {
        const resposta = await fetch("/api/medicao", { method: "POST" });
        const dados = await resposta.json().catch(() => ({}));
        if (!resposta.ok) throw new Error(dados.erro || "Falha ao medir a rede.");
        mostrar_resultado(dados);
    } catch (e) {
        mostrar_erro(e instanceof TypeError
            ? "Servidor indisponível. Inicie com: python -m app.servidor"
            : e.message);
    } finally {
        barra.classList.add("oculto");
        botao.disabled = false;
    }
}
