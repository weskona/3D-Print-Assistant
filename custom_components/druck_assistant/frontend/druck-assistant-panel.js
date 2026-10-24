// Sidebar panel of the 3D Print Assistant integration (no external dependencies).
// English is the source language; add further languages to TRANSLATIONS.
const TRANSLATIONS = {
  en: {
    no_printer: "No printer configured.",
    prints: "Prints",
    success_rate: "{rate} % successful",
    filament: "Filament",
    energy: "Energy",
    total_cost: "Total cost",
    of_which_energy: "of which energy {value}",
    current: "Current",
    print_running: "Printing: {name} (since {since})",
    no_active_print: "No print active.",
    remaining: "{value} % left",
    history: "Print history",
    no_history: "No prints recorded yet.",
    end: "Finished",
    name: "Name",
    result: "Result",
    duration: "Duration",
    material: "Material",
    weight: "Weight",
    cost: "Cost",
    success: "Successful",
    failed: "Failed",
    unknown: "unknown",
  },
  de: {
    no_printer: "Kein Drucker eingerichtet.",
    prints: "Drucke",
    success_rate: "{rate} % erfolgreich",
    filament: "Filament",
    energy: "Strom",
    total_cost: "Gesamtkosten",
    of_which_energy: "davon Strom {value}",
    current: "Aktuell",
    print_running: "Druck läuft: {name} (seit {since})",
    no_active_print: "Kein Druck aktiv.",
    remaining: "{value} % Rest",
    history: "Druckhistorie",
    no_history: "Noch keine Drucke aufgezeichnet.",
    end: "Ende",
    name: "Name",
    result: "Ergebnis",
    duration: "Dauer",
    material: "Material",
    weight: "Gewicht",
    cost: "Kosten",
    success: "Erfolgreich",
    failed: "Fehlgeschlagen",
    unknown: "unbekannt",
  },
};

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

  _t(key, vars = {}) {
    const lang = (this._hass?.locale?.language || this._hass?.language || "en").split("-")[0];
    const text = (TRANSLATIONS[lang] || TRANSLATIONS.en)[key] ?? TRANSLATIONS.en[key] ?? key;
    return text.replace(/\{(\w+)\}/g, (_, k) => vars[k] ?? "");
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

    const header = this._el("header", {}, this._el("h1", {}, "3D Print Assistant"));
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
    if (!printer) { main.append(this._el("div", { class: "empty" }, this._t("no_printer"))); return; }

    const t = printer.totals;
    const cur = printer.currency;
    const rate = t.prints ? Math.round((t.successful / t.prints) * 100) : 0;
    main.append(this._el("div", { class: "tiles" },
      this._tile(this._t("prints"), t.prints, this._t("success_rate", { rate })),
      this._tile(this._t("filament"), `${this._fmtNum(t.weight_g, 0)} g`),
      this._tile(this._t("energy"), `${this._fmtNum(t.energy_kwh, 2)} kWh`, `${this._fmtNum(printer.price_per_kwh, 4)} ${cur}/kWh`),
      this._tile(this._t("total_cost"), this._fmtMoney(t.cost, cur), this._t("of_which_energy", { value: this._fmtMoney(t.energy_cost, cur) })),
    ));

    const now = this._el("div", { class: "card" }, this._el("h2", {}, this._t("current")));
    const s = printer.session;
    const f = printer.filament;
    if (s) {
      now.append(this._el("div", {}, this._t("print_running", { name: s.name || this._t("unknown"), since: this._fmtDate(s.started) })));
    } else {
      now.append(this._el("div", { class: "sub" }, this._t("no_active_print")));
    }
    if (f && f.type) {
      const line = this._el("div", { style: "margin-top:6px" });
      if (f.color) line.append(this._el("span", { class: "dot", style: `background:${/^#[0-9a-f]{3,8}$/i.test(f.color) ? f.color : "transparent"}` }));
      line.append(`${f.name || f.type}, ${f.price_per_kg != null ? this._fmtMoney(f.price_per_kg, cur) + "/kg" : ""}${f.remain != null ? `, ${this._t("remaining", { value: f.remain })}` : ""}`);
      now.append(line);
    }
    main.append(now);

    const hist = this._el("div", { class: "card" }, this._el("h2", {}, this._t("history")));
    if (!printer.history.length) {
      hist.append(this._el("div", { class: "empty" }, this._t("no_history")));
    } else {
      const table = this._el("table", {});
      table.append(this._el("tr", {},
        ...["end", "name", "result", "duration", "material", "weight", "energy", "cost"].map((k) => this._t(k)).map((h, i) =>
          this._el("th", { class: i >= 5 ? "num" : "" }, h))));
      for (const r of printer.history) {
        const ok = r.result !== "failed";
        table.append(this._el("tr", {},
          this._el("td", {}, this._fmtDate(r.finished)),
          this._el("td", {}, r.name),
          this._el("td", { class: ok ? "ok" : "fail" }, this._t(ok ? "success" : "failed")),
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
