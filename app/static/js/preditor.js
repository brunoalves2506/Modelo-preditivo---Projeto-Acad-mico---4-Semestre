// Preditor: os botões chamam o servidor, que mede a rede por ICMP, calcula as métricas relativas ao baseline
// e usa a floresta final (Tarefa 5) para prever o estado da rede cerca de 12 minutos à frente.

const ROTULOS = { OK: "OK", RISCO: "RISCO", FALHA: "FALHA" };
let calibrando = false;
let sondagem = null;

function elemento(tag, classe, texto) {
    const el = document.createElement(tag);
    if (classe) el.className = classe;
    if (texto !== undefined) el.textContent = texto;
    return el;
}

function formatar_valor(valor, unidade, casas) {
    if (valor === null || valor === undefined) return "—";
    return valor.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas }) + " " + unidade;
}

function duracao(segundos) {
    if (segundos === null || segundos === undefined) return "calculando...";
    return segundos >= 90 ? `~${Math.round(segundos / 60)} min` : `~${Math.max(segundos, 1)} s`;
}

function limpar_resultado() {
    document.getElementById("container_sec_info").classList.add("oculto");
    document.getElementById("status_rede_tempo_real").className = "";
    document.getElementById("status_rede_texto").textContent = "";
    const info = document.getElementById("info_medicao");
    info.classList.remove("erro");
    info.replaceChildren();
}

function mostrar_carregando(frase) {
    document.getElementById("frase_carregando").textContent = frase;
    document.getElementById("carregando_medicao").classList.remove("oculto");
}

function esconder_carregando() {
    document.getElementById("carregando_medicao").classList.add("oculto");
}

function mostrar_erro(texto) {
    // Sem resultado válido: o painel de status continua escondido e o container só mostra o aviso.
    const info = document.getElementById("info_medicao");
    info.classList.add("erro");
    info.replaceChildren(elemento("div", "info_erro", texto));
}

// ---------- previsão ----------

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
        ["Latência: ", formatar_valor(m.latencia_ms, "ms", 1) + variacao],
        ["Normal da rede: ", formatar_valor(m.normal_ms, "ms", 1)],
        ["Jitter: ", formatar_valor(m.jitter_ms, "ms", 2)],
        ["Perda de pacotes: ", formatar_valor(m.perda_pct, "%", 0)],
    ].forEach(([rotulo, valor]) => {
        const linha = elemento("div");
        linha.appendChild(elemento("span", null, rotulo));
        linha.appendChild(document.createTextNode(valor));
        metricas.appendChild(linha);
    });
    info.appendChild(metricas);

    d.alvos.forEach(a => {
        const linha = elemento("div", "info_alvo");
        linha.appendChild(elemento("div", null, `${a.nome} (${a.endereco})  ${formatar_valor(a.latencia_ms, "ms", 1)}`));
        const confianca = a.confianca_pct === null || a.confianca_pct === undefined ? "" : ` · ${a.confianca_pct}%`;
        linha.appendChild(elemento("b", a.status ? "status_" + a.status.toLowerCase() : "", a.status ? a.status + confianca : "—"));
        info.appendChild(linha);
    });

    const r = d.referencia;
    let rodape = `Medido às ${d.medido_em}` + (r.simulada ? "" : ` (${d.duracao_s} s)`);
    if (r.simulada) rodape += " • MODO DEMONSTRAÇÃO";
    else {
        rodape += ` • baseline de ${r.calibrada_em} (${r.amostras} amostras)`;
        if (r.provisoria) rodape += " • INCOMPLETO";
    }
    info.appendChild(elemento("div", "info_rodape", rodape));
}

function travar(travado) {
    document.getElementById("botao_acao").disabled = travado;
}

async function obter_medicao() {
    if (calibrando) return;
    travar(true);
    document.getElementById("botao_calibrar").disabled = true;
    limpar_resultado();
    mostrar_carregando("Obtendo Métricas");

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
        esconder_carregando();
        travar(false);
        document.getElementById("botao_calibrar").disabled = false;
    }
}

// ---------- calibração (baseline da rede que será predita) ----------

function desenhar_calibracao(e) {
    const info = document.getElementById("info_medicao");
    info.classList.add("erro");
    const barra = elemento("div", "progresso");
    const preenchimento = elemento("div");
    preenchimento.style.width = e.percentual + "%";
    barra.appendChild(preenchimento);
    info.replaceChildren(
        elemento("div", "info_mensagem", `Calibrando a rede: ${e.percentual}%`),
        barra,
        elemento("div", null, `Tempo restante: ${duracao(e.restante_s)} • decorrido: ${duracao(e.decorrido_s)}`),
        elemento("div", "info_rodape", "Deixe a rede parada (sem downloads, streaming ou jogos) até terminar. Clique em Cancelar para desistir."),
    );
}

function desenhar_fim_calibracao(e) {
    const info = document.getElementById("info_medicao");
    info.classList.add("erro");
    if (e.erro) { mostrar_erro("Falha na calibração: " + e.erro); return; }
    if (e.cancelada) {
        info.replaceChildren(elemento("div", "info_mensagem", "Calibração cancelada."),
            elemento("div", null, "O baseline anterior foi mantido."));
        return;
    }
    const r = e.resultado;
    const itens = [elemento("div", "info_mensagem", r.simulada ? "Calibração simulada (demonstração)."
        : r.completo ? "Calibração concluída. Baseline salvo." : "Calibração incompleta.")];
    r.alvos.forEach(a => {
        const linha = elemento("div", "info_alvo");
        linha.appendChild(elemento("div", null, `${a.nome} (${a.endereco})  normal: ${formatar_valor(a.normal_ms, "ms", 1)}`));
        linha.appendChild(elemento("b", a.ok && a.amostras >= 1500 ? "status_ok" : "status_risco",
            a.ok ? `${a.amostras} amostras` : "sem resposta"));
        itens.push(linha);
    });
    if (!r.completo && !r.simulada) {
        itens.push(elemento("div", "info_aviso", "Menos de 1500 amostras válidas em algum destino. Refaça com a rede estável."));
    } else {
        itens.push(elemento("div", "info_rodape", "Pronto: já pode clicar em Fazer Medição."));
    }
    info.replaceChildren(...itens);
}

function entrar_modo_calibracao() {
    calibrando = true;
    travar(true);
    document.getElementById("botao_calibrar").textContent = "Cancelar";
    mostrar_carregando("Calibrando a rede");
}

function sair_modo_calibracao() {
    calibrando = false;
    if (sondagem) { clearInterval(sondagem); sondagem = null; }
    document.getElementById("botao_calibrar").textContent = "Calibrar";
    document.getElementById("botao_calibrar").disabled = false;
    esconder_carregando();
    travar(false);
}

async function consultar_calibracao() {
    try {
        const resposta = await fetch("/api/calibracao");
        const e = await resposta.json();
        if (e.ativa) { desenhar_calibracao(e); return; }
        sair_modo_calibracao();
        if (e.resultado || e.cancelada || e.erro) desenhar_fim_calibracao(e);
    } catch (_) {
        sair_modo_calibracao();
        mostrar_erro("Servidor indisponível. Inicie com: python -m app.servidor");
    }
}

async function calibrar_rede() {
    if (calibrando) {                                   // o mesmo botão cancela
        document.getElementById("botao_calibrar").disabled = true;
        await fetch("/api/calibracao", { method: "DELETE" });
        return;
    }
    limpar_resultado();
    try {
        const resposta = await fetch("/api/calibracao", { method: "POST" });
        const dados = await resposta.json().catch(() => ({}));
        if (!resposta.ok) throw new Error(dados.erro || "Não foi possível iniciar a calibração.");
        entrar_modo_calibracao();
        desenhar_calibracao(dados);
        sondagem = setInterval(consultar_calibracao, 1000);
    } catch (e) {
        mostrar_erro(e instanceof TypeError ? "Servidor indisponível. Inicie com: python -m app.servidor" : e.message);
    }
}

// Se a página for recarregada no meio de uma calibração, volta a acompanhá-la.
fetch("/api/calibracao").then(r => r.json()).then(e => {
    if (!e.ativa) return;
    entrar_modo_calibracao();
    desenhar_calibracao(e);
    sondagem = setInterval(consultar_calibracao, 1000);
}).catch(() => {});
