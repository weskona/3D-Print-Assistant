// Sidebar panel of the 3D-Druck-Assistant integration (no external dependencies).
class DruckAssistantPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._data = null;
    this._selected = null;
    this._error = null;
    this._unsub = [];
    this._timer = null;
  }

  set hass(hass) {
    const first = !this._hass;
    this._hass = hass;
    if (first) this._start();
  }

  set narrow(v) { this._narrow = v; }
  set panel(v) { this._panel = v; }

  connectedCallback() {
    if (this._hass && !this._timer) this._start();
  }

  disconnectedCallback() {
    this._unsub.forEach((u) => u());
    this._unsub = [];
    clearInterval(this._timer);
    this._timer = null;
  }

  async _start() {
    this._render();
    await this._load();
    this._timer = setInterval(() => this._load(), 30000);
    for (const ev of ["druck_assistant_print_started", "druck_assistant_print_finished", "druck_assistant_print_failed"]) {
      try {
        this._unsub.push(await this._hass.connection.subscribeEvents(() => this._load(), ev));
      } catch (e) { /* refresh by timer only */ }
    }
  }

  async _load() {
    try {
      this._data = await this._hass.connection.sendMessagePromise({ type: "druck_assistant/data" });
      this._error = null;
      const ids = this._data.printers.map((p) => p.entry_id);
      if (!ids.includes(this._selected)) this._selected = ids[0] || null;
    } catch (e) {
      this._error = e && e.message ? e.message : String(e);
    }
    this._render();
  }

  _fmtMoney(v, cur) {
    return new Intl.NumberFormat(this._hass.locale?.language, { style: "currency", currency: cur || "EUR" }).format(v || 0);
  }
  _fmtNum(v, digits = 1) {
    return new Intl.NumberFormat(this._hass.locale?.language, { maximumFractionDigits: digits }).format(v || 0);
  }
  _fmtDate(iso) {
    return iso ? new Date(iso).toLocaleString(this._hass.locale?.language) : "";
  }
  _fmtDuration(min) {
    const m = Math.round(min || 0);
    return m >= 60 ? `${Math.floor(m / 60)} h ${m % 60} min` : `${m} min`;
  }

  _el(tag, props = {}, ...children) {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(props)) {
      if (k === "class") el.className = v;
      else if (k === "style") el.style.cssText = v;
      else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else el.setAttribute(k, v);
    }
    for (const c of children) el.append(c instanceof Node ? c : document.createTextNode(String(c ?? "")));
    return el;
  }

  _tile(label, value, sub) {
    return this._el("div", { class: "tile" },
      this._el("div", { class: "label" }, label),
      this._el("div", { class: "value" }, value),
      sub ? this._el("div", { class: "sub" }, sub) : "");
  }

  _render() {
    const root = this.shadowRoot;
    root.replaceChildren(this._el("style", {}, `
      :host { display: block; background: var(--primary-background-color); color: var(--primary-text-color); min-height: 100vh; }
      header { display: flex; align-items: center; gap: 12px; padding: 12px 16px; background: var(--app-header-background-color, var(--primary-color)); color: var(--app-header-text-color, #fff); }
      header h1 { font-size: 20px; font-weight: 400; margin: 0; flex: 1; }
      select { font: inherit; padding: 4px 8px; }
      main { padding: 16px; max-width: 1100px; margin: 0 auto; }
      .tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 16px; }
      .tile, .card { background: var(--card-background-color); border-radius: var(--ha-card-border-radius, 12px); box-shadow: var(--ha-card-box-shadow, 0 1px 3px rgba(0,0,0,.2)); padding: 12px 16px; }
      .label { color: var(--secondary-text-color); font-size: 13px; }
      .value { font-size: 24px; margin-top: 4px; }
      .sub { color: var(--secondary-text-color); font-size: 12px; margin-top: 2px; }
      .card { margin-bottom: 16px; overflow-x: auto; }
      .card h2 { font-size: 16px; font-weight: 500; margin: 0 0 8px; }
      table { width: 100%; border-collapse: collapse; font-size: 14px; }
      th, td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--divider-color); white-space: nowrap; }
      th { color: var(--secondary-text-color); font-weight: 500; }
      td.num, th.num { text-align: right; }
      .dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; vertical-align: middle; margin-right: 6px; border: 1px solid var(--divider-color); }
      .ok { color: var(--success-color, #4caf50); } .fail { color: var(--error-color, #f44336); }
      .empty, .error { color: var(--secondary-text-color); padding: 16px; }
      .error { color: var(--error-color, #f44336); }
    `));

    const printers = this._data?.printers || [];
    const printer = printers.find((p) => p.entry_id === this._selected);

    const header = this._el("header", {}, this._el("h1", {}, "3D-Druck-Assistant"));
    if (printers.length > 1) {
      const sel = this._el("select", { onchange: (e) => { this._selected = e.target.value; this._render(); } },
        ...printers.map((p) => {
          const o = this._el("option", { value: p.entry_id }, p.title);
          if (p.entry_id === this._selected) o.selected = true;
          return o;
        }));
      header.append(sel);
    }
    root.append(header);

    const main = this._el("main");
    root.append(main);

    if (this._error) { main.append(this._el("div", { class: "error" }, this._error)); return; }
    if (!this._data) { main.append(this._el("div", { class: "empty" }, "…")); return; }
    if (!printer) { main.append(this._el("div", { class: "empty" }, "Kein Drucker eingerichtet.")); return; }

    const t = printer.totals;
    const cur = printer.currency;
    const rate = t.prints ? Math.round((t.successful / t.prints) * 100) : 0;
    main.append(this._el("div", { class: "tiles" },
      this._tile("Drucke", t.prints, `${rate} % erfolgreich`),
      this._tile("Filament", `${this._fmtNum(t.weight_g, 0)} g`),
      this._tile("Strom", `${this._fmtNum(t.energy_kwh, 2)} kWh`, `${this._fmtNum(printer.price_per_kwh, 4)} ${cur}/kWh`),
      this._tile("Gesamtkosten", this._fmtMoney(t.cost, cur), `davon Strom ${this._fmtMoney(t.energy_cost, cur)}`),
    ));

    const now = this._el("div", { class: "card" }, this._el("h2", {}, "Aktuell"));
    const s = printer.session;
    const f = printer.filament;
    if (s) {
      now.append(this._el("div", {}, `Druck läuft: ${s.name || "unbekannt"} (seit ${this._fmtDate(s.started)})`));
    } else {
      now.append(this._el("div", { class: "sub" }, "Kein Druck aktiv."));
    }
    if (f && f.type) {
      const line = this._el("div", { style: "margin-top:6px" });
      if (f.color) line.append(this._el("span", { class: "dot", style: `background:${/^#[0-9a-f]{3,8}$/i.test(f.color) ? f.color : "transparent"}` }));
      line.append(`${f.name || f.type}, ${f.price_per_kg != null ? this._fmtMoney(f.price_per_kg, cur) + "/kg" : ""}${f.remain != null ? `, ${f.remain} % Rest` : ""}`);
      now.append(line);
    }
    main.append(now);

    const hist = this._el("div", { class: "card" }, this._el("h2", {}, "Druckhistorie"));
    if (!printer.history.length) {
      hist.append(this._el("div", { class: "empty" }, "Noch keine Drucke aufgezeichnet."));
    } else {
      const table = this._el("table", {});
      table.append(this._el("tr", {},
        ...["Ende", "Name", "Ergebnis", "Dauer", "Material", "Gewicht", "Strom", "Kosten"].map((h, i) =>
          this._el("th", { class: i >= 5 ? "num" : "" }, h))));
      for (const r of printer.history) {
        const ok = r.result !== "failed";
        table.append(this._el("tr", {},
          this._el("td", {}, this._fmtDate(r.finished)),
          this._el("td", {}, r.name),
          this._el("td", { class: ok ? "ok" : "fail" }, ok ? "Erfolgreich" : "Fehlgeschlagen"),
          this._el("td", {}, this._fmtDuration(r.duration_min)),
          this._el("td", {}, r.material || "–"),
          this._el("td", { class: "num" }, `${this._fmtNum(r.weight_g)} g`),
          this._el("td", { class: "num" }, `${this._fmtNum(r.energy_kwh || 0, 3)} kWh`),
          this._el("td", { class: "num" }, this._fmtMoney(r.cost, cur))));
      }
      hist.append(table);
    }
    main.append(hist);
  }
}

customElements.define("druck-assistant-panel", DruckAssistantPanel);
