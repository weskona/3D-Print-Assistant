// Sidebar panel of the 3D Print Assistant integration (no external dependencies).
// Material Design Icons paths, drawn inline so the panel needs no icon font.
const ICONS = {
  edit: "M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z",
  delete: "M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",
  restore: "M12,3A9,9 0 0,0 3,12H0L4,16L8,12H5A7,7 0 0,1 12,5A7,7 0 0,1 19,12A7,7 0 0,1 12,19C10.5,19 9.09,18.5 7.94,17.7L6.5,19.14C8.04,20.3 9.94,21 12,21A9,9 0 0,0 21,12A9,9 0 0,0 12,3M14,12A2,2 0 0,0 12,10A2,2 0 0,0 10,12A2,2 0 0,0 12,14A2,2 0 0,0 14,12Z",
};

const LOW_PERCENT = 15; // same threshold as the red stock bar

const COMMON_MATERIALS = ["PLA", "PLA+", "PETG", "ABS", "ASA", "TPU", "PC", "PA", "PA-CF", "PET-CF", "PVA"];

// English is the source language; add further languages to TRANSLATIONS.
const TRANSLATIONS = {
  en: {
    no_printer: "No printer configured.",
    prints: "Prints",
    success_rate: "{rate} % successful",
    filament: "Filament",
    energy: "Energy",
    total_cost: "Total cost",
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
    electricity_cost: "Electricity cost",
    total: "Total",
    cost_split: "Filament {filament} · Electricity {energy}",
    current_print: "Current print",
    status_running: "Printing",
    status_pause: "Paused",
    status_prepare: "Preparing",
    elapsed: "Elapsed",
    time_remaining: "Remaining",
    finishes: "Finishes",
    layer: "Layer",
    print_weight: "Filament weight",
    nozzle_bed: "Nozzle / bed",
    spool_label: "Spool",
    filament_cost: "Filament cost",
    energy_cost_so_far: "Electricity so far",
    cost_estimate: "Estimated cost",
    cost_hint: "Whole print + electricity so far",
    tab_overview: "Overview",
    tab_filament: "Filament",
    tab_ams: "AMS",
    spools: "Spools",
    slots: "Slots",
    add_spool: "Add spool",
    edit: "Edit",
    delete: "Delete",
    save: "Save",
    cancel: "Cancel",
    confirm_delete: "Delete spool \"{name}\"?",
    brand: "Brand",
    color: "Color",
    price_per_kg: "Price per kg",
    initial_weight: "Initial weight (g)",
    remaining_weight: "Remaining (g)",
    notes: "Notes",
    stock: "Stock",
    slot: "Slot",
    no_spools: "No spools yet. Add your first spool.",
    no_slots: "No AMS or external spool slots found for this printer.",
    assign_spool: "Spool",
    none: "none",
    admin_only: "Only administrators can change the filament inventory.",
    price: "Price",
    suggest_hint: "Pick a name you already have to fill in the other fields.",
    catalog: "Bambu Lab catalog",
    catalog_filament: "Filament",
    catalog_color: "Color",
    catalog_choose: "– choose –",
    catalog_hint: "Pick a Bambu Lab filament and color to fill in name, material, brand and color. You can still change every field.",
    filter_search: "Search name, material, brand, notes",
    all: "All",
    status: "Status",
    status_stock: "In stock",
    status_slot: "In a slot",
    status_low: "Low stock",
    filter_count: "{shown} of {total} spools",
    filter_reset: "Reset filter",
    no_match: "No spools match the filter.",
    stock_badge: "In stock",
    rfid_tag: "RFID tag (clear to unlink)",
    correct_hint: "Wrong spool? Pick the right one: the tag moves to it, and the automatic match stays corrected. Choosing \"none\" stops automatic assignment for the spool currently in this slot.",
    quantity: "Quantity (e.g. 4 for a 4-pack)",
    restore: "Restore",
    archived_spools: "Archived spools ({count})",
    no_archived: "No archived spools. Empty spools are archived automatically.",
    import_ams: "Import from AMS",
    import_result: "Imported from AMS: {created} created, {assigned} assigned, {adopted} linked.",
    import_nothing: "Nothing to import: all loaded slots already have a spool.",
  },
  de: {
    no_printer: "Kein Drucker eingerichtet.",
    prints: "Drucke",
    success_rate: "{rate} % erfolgreich",
    filament: "Filament",
    energy: "Strom",
    total_cost: "Gesamtkosten",
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
    electricity_cost: "Stromkosten",
    total: "Gesamt",
    cost_split: "Filament {filament} · Strom {energy}",
    current_print: "Aktueller Druck",
    status_running: "Druckt",
    status_pause: "Pausiert",
    status_prepare: "Bereitet vor",
    elapsed: "Dauer bisher",
    time_remaining: "Restzeit",
    finishes: "Fertig um",
    layer: "Schicht",
    print_weight: "Filamentgewicht",
    nozzle_bed: "Düse / Bett",
    spool_label: "Spule",
    filament_cost: "Filamentkosten",
    energy_cost_so_far: "Strom bisher",
    cost_estimate: "Geschätzte Kosten",
    cost_hint: "Ganzer Druck + bisheriger Strom",
    tab_overview: "Übersicht",
    tab_filament: "Filament",
    tab_ams: "AMS",
    spools: "Spulen",
    slots: "Slots",
    add_spool: "Spule hinzufügen",
    edit: "Bearbeiten",
    delete: "Löschen",
    save: "Speichern",
    cancel: "Abbrechen",
    confirm_delete: "Spule „{name}“ löschen?",
    brand: "Hersteller",
    color: "Farbe",
    price_per_kg: "Preis pro kg",
    initial_weight: "Anfangsgewicht (g)",
    remaining_weight: "Rest (g)",
    notes: "Notizen",
    stock: "Bestand",
    slot: "Slot",
    no_spools: "Noch keine Spulen. Lege deine erste Spule an.",
    no_slots: "Keine AMS- oder Externe-Spule-Slots für diesen Drucker gefunden.",
    assign_spool: "Spule",
    none: "keine",
    admin_only: "Nur Administratoren können den Filamentbestand ändern.",
    price: "Preis",
    suggest_hint: "Wähle einen vorhandenen Namen, um die übrigen Felder auszufüllen.",
    catalog: "Bambu-Lab-Katalog",
    catalog_filament: "Filament",
    catalog_color: "Farbe",
    catalog_choose: "– wählen –",
    catalog_hint: "Wähle ein Bambu-Lab-Filament und eine Farbe, um Name, Material, Hersteller und Farbe auszufüllen. Du kannst jedes Feld danach noch ändern.",
    filter_search: "Suche in Name, Material, Hersteller, Notizen",
    all: "Alle",
    status: "Status",
    status_stock: "Vorrat",
    status_slot: "In einem Slot",
    status_low: "Niedriger Bestand",
    filter_count: "{shown} von {total} Spulen",
    filter_reset: "Filter zurücksetzen",
    no_match: "Keine Spulen entsprechen dem Filter.",
    stock_badge: "Vorrat",
    rfid_tag: "RFID-Tag (leeren zum Lösen)",
    correct_hint: "Falsche Spule? Wähle die richtige: Der Tag wandert zu ihr, die automatische Zuordnung bleibt korrigiert. „keine“ stoppt die automatische Zuordnung für die Spule, die gerade in diesem Slot steckt.",
    quantity: "Anzahl (z. B. 4 für ein 4er-Pack)",
    restore: "Wiederherstellen",
    archived_spools: "Archivierte Spulen ({count})",
    no_archived: "Keine archivierten Spulen. Leere Spulen werden automatisch archiviert.",
    import_ams: "Aus AMS importieren",
    import_result: "Aus AMS importiert: {created} angelegt, {assigned} zugeordnet, {adopted} verknüpft.",
    import_nothing: "Nichts zu importieren: alle belegten Slots haben schon eine Spule.",
  },
};

class DruckAssistantPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._data = null;
    this._selected = null;
    this._tab = "overview";
    this._editing = null;
    this._filter = { text: "", material: "", brand: "", status: "" };
    this._refocusSearch = null;
    this._expanded = new Set();
    this._busy = null;
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
    clearTimeout(this._timer);
    this._timer = null;
  }

  async _start() {
    this._render();
    await this._load();
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
      this._spools = this._data.spools || [];
      const ids = this._data.printers.map((p) => p.entry_id);
      if (!ids.includes(this._selected)) this._selected = ids[0] || null;
    } catch (e) {
      this._error = e && e.message ? e.message : String(e);
    }
    // Never re-render while a form is open or the user is typing in a field.
    const typing = ["INPUT", "SELECT", "TEXTAREA"].includes(this.shadowRoot.activeElement?.tagName);
    if (this._editing === null && !typing) this._render();
    // Refresh faster while a print is running so progress and costs stay live.
    const printing = (this._data?.printers || []).some((p) => p.current_print);
    clearTimeout(this._timer);
    this._timer = setTimeout(() => this._load(), printing ? 10000 : 30000);
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

  async _call(msg, describe) {
    this._notice = null;
    this._noticeOk = false;
    try {
      const result = await this._hass.connection.sendMessagePromise(msg);
      if (describe) { this._notice = describe(result); this._noticeOk = true; }
    } catch (e) {
      this._notice = e && e.message ? e.message : String(e);
    }
    this._editing = null;
    await this._load();
    this._render();
  }

  /** The Bambu Lab catalog is read once; the form still works without it. */
  async _loadCatalog() {
    if (this._catalog !== undefined) return;
    try {
      this._catalog = await this._hass.connection.sendMessagePromise({ type: "druck_assistant/catalog" });
    } catch (e) {
      this._catalog = null;
    }
  }

  _isAdmin() { return !!this._hass?.user?.is_admin; }

  /** A round icon button with a tooltip and an accessible name. */
  _iconButton(icon, label, onclick, danger = false) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("aria-hidden", "true");
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", ICONS[icon]);
    path.setAttribute("fill", "currentColor");
    svg.append(path);
    const button = this._el("button", { class: "icon-btn" + (danger ? " danger" : ""), title: label, "aria-label": label, onclick });
    button.append(svg);
    return button;
  }

  _confirmDelete(sp) {
    if (confirm(this._t("confirm_delete", { name: sp.name }))) {
      this._call({ type: "druck_assistant/spool_delete", spool_id: sp.id });
    }
  }

  _field(label, input) {
    return this._el("label", { class: "field" }, this._el("span", {}, label), input);
  }

  _renderForm(spool) {
    const v = { name: "", material: "", brand: "", color: "#808080", price_per_kg: "", initial_weight_g: 1000, remaining_g: 1000, notes: "", rfid: "", ...spool };
    // The color picker only takes #rrggbb; the tray color may carry an alpha channel.
    v.color = /^#[0-9a-f]{6}/i.test(v.color || "") ? v.color.slice(0, 7).toLowerCase() : "#808080";
    const inputs = {};
    const touched = new Set();
    const qty = this._el("input", { type: "number", min: "1", max: "50", step: "1", value: "1" });

    // Suggestions from everything captured so far (archived spools included).
    const base = (name) => name.replace(/\s+#\d+$/, "").trim();
    const unique = (values) => [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b));
    const lists = {
      name: unique(this._spools.map((sp) => base(sp.name))),
      material: unique([...COMMON_MATERIALS, ...this._spools.map((sp) => sp.material)]),
      brand: unique(["Bambu Lab", ...this._spools.map((sp) => sp.brand)]),
    };
    const datalists = Object.entries(lists).map(([key, options]) =>
      this._el("datalist", { id: `suggest-${key}` }, ...options.map((o) => this._el("option", { value: o }))));

    const mk = (key, type = "text", extra = {}) => {
      inputs[key] = this._el("input", { type, value: v[key] ?? "", ...(lists[key] ? { list: `suggest-${key}`, autocomplete: "off" } : {}), ...extra });
      inputs[key].addEventListener("input", () => touched.add(key));
      return inputs[key];
    };
    // Picking a known name fills the remaining fields from the newest spool with that name.
    const fromTemplate = () => {
      if (spool.id) return;
      const name = inputs.name.value.trim().toLowerCase();
      const tpl = [...this._spools].reverse().find((sp) => base(sp.name).toLowerCase() === name);
      if (!tpl) return;
      const fill = { material: tpl.material, brand: tpl.brand, price_per_kg: tpl.price_per_kg ?? "", initial_weight_g: tpl.initial_weight_g, remaining_g: tpl.initial_weight_g,
        color: /^#[0-9a-f]{6}/i.test(tpl.color || "") ? tpl.color.slice(0, 7).toLowerCase() : "#808080" };
      for (const [key, value] of Object.entries(fill)) {
        if (!touched.has(key)) inputs[key].value = value;
      }
    };
    const form = this._el("div", { class: "dialog form", role: "dialog" },
      this._el("h2", {}, spool.id ? this._t("edit") : this._t("add_spool")),
      this._field(this._t("name"), mk("name")),
      spool.id ? "" : this._el("div", { class: "sub notice" }, this._t("suggest_hint")),
      this._field(this._t("material"), mk("material", "text", { placeholder: "PLA" })),
      this._field(this._t("brand"), mk("brand")),
      this._field(this._t("color"), mk("color", "color")),
      this._field(this._t("price_per_kg"), mk("price_per_kg", "number", { min: "0", step: "0.01" })),
      this._field(this._t("initial_weight"), mk("initial_weight_g", "number", { min: "1", step: "1" })),
      this._field(this._t("remaining_weight"), mk("remaining_g", "number", { min: "0", step: "1" })),
      this._field(this._t("notes"), mk("notes")),
      spool.id ? this._field(this._t("rfid_tag"), mk("rfid")) : this._field(this._t("quantity"), qty),
      ...datalists,
      this._el("div", { class: "actions" },
        this._el("button", { class: "primary", onclick: () => {
          const out = {};
          for (const [k, el] of Object.entries(inputs)) out[k] = el.value;
          if (spool.id) out.id = spool.id; else delete out.rfid;
          this._call({ type: "druck_assistant/spool_save", spool: out, ...(spool.id ? {} : { quantity: parseInt(qty.value, 10) || 1 }) });
        } }, this._t("save")),
        this._el("button", { onclick: () => { this._editing = null; this._render(); } }, this._t("cancel")),
        ...(spool.id ? [
          this._el("button", { onclick: () => this._confirmDelete(spool) }, this._t("delete")),
        ] : [])));
    inputs.name.addEventListener("change", fromTemplate);
    if (!spool.id && this._catalog && this._catalog.products?.length) {
      const german = (this._hass?.locale?.language || this._hass?.language || "en").startsWith("de");
      const colorLabel = (c) => `${german && c.name_de ? c.name_de : c.name} (${c.code})`;
      const productSel = this._el("select", {}, this._el("option", { value: "" }, this._t("catalog_choose")),
        ...this._catalog.products.map((p, i) => this._el("option", { value: String(i) }, p.name)));
      const colorSel = this._el("select", {}, this._el("option", { value: "" }, this._t("catalog_choose")));
      colorSel.disabled = true;
      const swatch = this._el("span", { class: "dot", style: "background:transparent" });
      const product = () => this._catalog.products[parseInt(productSel.value, 10)];
      productSel.addEventListener("change", () => {
        colorSel.replaceChildren(this._el("option", { value: "" }, this._t("catalog_choose")));
        const p = productSel.value === "" ? null : product();
        colorSel.disabled = !p;
        swatch.style.background = "transparent";
        if (!p) return;
        p.colors.forEach((c, i) => colorSel.append(this._el("option", { value: String(i) }, colorLabel(c))));
        inputs.name.value = p.name;
        inputs.material.value = p.material;
        inputs.brand.value = p.brand;
        for (const key of ["name", "material", "brand"]) touched.add(key);
      });
      colorSel.addEventListener("change", () => {
        const p = product();
        const c = colorSel.value === "" ? null : p.colors[parseInt(colorSel.value, 10)];
        if (!c) { swatch.style.background = "transparent"; return; }
        inputs.color.value = c.hex.toLowerCase();
        touched.add("color");
        swatch.style.background = c.hex;
        // The color name tells same-type spools apart in the notes.
        if (!touched.has("notes")) inputs.notes.value = `${c.name} (${c.code})`;
      });
      const picker = this._el("div", { class: "catalog" },
        this._el("h3", {}, this._t("catalog")),
        this._el("div", { class: "sub notice" }, this._t("catalog_hint")),
        this._field(this._t("catalog_filament"), productSel),
        this._field(this._t("catalog_color"), this._el("div", { class: "row" }, colorSel, swatch)));
      const anchor = form.querySelector("h2");
      anchor.after(picker);
    }
    return this._el("div", { class: "overlay" }, form);
  }

  /**
   * A Bambu Lab spool in a slot is filled in by its RFID tag, so it can be edited once the tag
   * was detected. A spool in stock (in no slot) can always be edited, as can spools of other
   * brands, which have no tag.
   */
  _canEdit(sp, admin, slotOf) {
    return admin && (!!sp.rfid || !slotOf[sp.id] || (sp.brand || "").trim().toLowerCase() !== "bambu lab");
  }

  /**
   * Row buttons of a spool: Edit where editing is allowed; an untagged Bambu Lab spool in a
   * slot has nothing to edit, but can be deleted. Spools are archived automatically when they
   * run empty, not by hand from the row.
   */
  _rowActions(sp, admin, slotOf) {
    if (!admin) return [];
    if (this._canEdit(sp, admin, slotOf)) {
      return [
        this._iconButton("edit", this._t("edit"), () => { this._editing = sp; this._render(); }),
        this._iconButton("delete", this._t("delete"), () => this._confirmDelete(sp), true),
      ];
    }
    return [this._iconButton("delete", this._t("delete"), () => this._confirmDelete(sp), true)];
  }

  _matchesFilter(sp, slotOf) {
    const f = this._filter;
    if (f.material && sp.material !== f.material) return false;
    if (f.brand && (sp.brand || "") !== f.brand) return false;
    if (f.status === "stock" && slotOf[sp.id]) return false;
    if (f.status === "slot" && !slotOf[sp.id]) return false;
    if (f.status === "low" && sp.remaining_percent > LOW_PERCENT) return false;
    const text = f.text.trim().toLowerCase();
    if (!text) return true;
    return [sp.name, sp.material, sp.brand, sp.notes, sp.color].some((v) => (v || "").toLowerCase().includes(text));
  }

  _renderFilter(spools, shown) {
    const f = this._filter;
    const unique = (values) => [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b));
    const select = (key, label, options) => {
      const sel = this._el("select", { onchange: (e) => { f[key] = e.target.value; this._render(); } },
        this._el("option", { value: "" }, `${label}: ${this._t("all")}`),
        ...options.map(([value, text]) => {
          const o = this._el("option", { value }, text);
          if (f[key] === value) o.selected = true;
          return o;
        }));
      return sel;
    };
    const search = this._el("input", { type: "search", class: "filter-search", placeholder: this._t("filter_search"), value: f.text });
    search.addEventListener("input", () => {
      f.text = search.value;
      this._refocusSearch = search.selectionStart;
      this._render();
    });
    if (this._refocusSearch !== null) {
      // The list is rebuilt while typing: keep focus and caret in the search box.
      const caret = this._refocusSearch;
      this._refocusSearch = null;
      queueMicrotask(() => { search.focus(); search.setSelectionRange(caret, caret); });
    }
    const active = f.text || f.material || f.brand || f.status;
    return this._el("div", { class: "filter" },
      search,
      select("material", this._t("material"), unique(spools.map((sp) => sp.material)).map((m) => [m, m])),
      select("brand", this._t("brand"), unique(spools.map((sp) => sp.brand)).map((b) => [b, b])),
      select("status", this._t("status"), [["stock", this._t("status_stock")], ["slot", this._t("status_slot")], ["low", this._t("status_low")]]),
      active
        ? this._el("span", { class: "sub" }, this._t("filter_count", { shown, total: spools.length }))
        : "",
      active
        ? this._el("button", { onclick: () => { this._filter = { text: "", material: "", brand: "", status: "" }; this._render(); } }, this._t("filter_reset"))
        : "");
  }

  /** Spools of the same type (name without " #n", material and color) form one inventory row. */
  _groups(spools) {
    const groups = new Map();
    for (const sp of spools) {
      // The alpha channel of the tray color is ignored; different colors are separate rows.
      const color = /^#[0-9a-f]{6}/i.test(sp.color || "") ? sp.color.slice(0, 7).toLowerCase() : "";
      const key = `${sp.name.replace(/\s+#\d+$/, "").toLowerCase()}|${sp.material.toLowerCase()}|${color}`;
      if (!groups.has(key)) {
        groups.set(key, { key, name: sp.name.replace(/\s+#\d+$/, ""), material: sp.material, brand: "", color: sp.color, spools: [], remaining: 0, initial: 0 });
      }
      const g = groups.get(key);
      g.spools.push(sp);
      g.brand = g.brand || sp.brand;
      g.remaining += sp.remaining_g;
      g.initial += sp.initial_weight_g;
    }
    for (const g of groups.values()) {
      // Average price per kg of the purchases, weighted by spool size.
      const priced = g.spools.filter((sp) => sp.price_per_kg != null);
      const weight = priced.reduce((sum, sp) => sum + sp.initial_weight_g, 0);
      g.avgPrice = weight ? priced.reduce((sum, sp) => sum + sp.price_per_kg * sp.initial_weight_g, 0) / weight : null;
      g.percent = g.initial ? (g.remaining / g.initial) * 100 : 0;
    }
    return [...groups.values()];
  }

  _renderFilament(main, printer) {
    const admin = this._isAdmin();
    const cur = printer?.currency || "EUR";
    if (this._notice) main.append(this._el("div", { class: this._noticeOk ? "sub notice" : "error" }, this._notice));
    if (!admin) main.append(this._el("div", { class: "sub notice" }, this._t("admin_only")));

    const slotOf = {};
    for (const p of this._data.printers) for (const sl of p.slots || []) if (sl.spool_id) slotOf[sl.spool_id] = sl.label;

    const activeSpools = this._spools.filter((sp) => !sp.archived);
    const archivedSpools = this._spools.filter((sp) => sp.archived);
    const card = this._el("div", { class: "card" }, this._el("h2", {}, this._t("spools")));
    if (admin) {
      card.append(
        this._el("button", { class: "primary", onclick: async () => { await this._loadCatalog(); this._editing = {}; this._render(); } }, this._t("add_spool")),
        this._el("button", { onclick: () => this._call({ type: "druck_assistant/import_ams" }, (r) =>
          r.created + r.assigned + r.adopted
            ? this._t("import_result", r)
            : this._t("import_nothing")) }, this._t("import_ams")));
    }
    // The table shows the filtered spools and sums only those, so what you see is what is added up.
    const filtered = activeSpools.filter((sp) => this._matchesFilter(sp, slotOf));
    const groups = this._groups(filtered);
    if (activeSpools.length) card.append(this._renderFilter(activeSpools, filtered.length));
    if (!activeSpools.length) {
      card.append(this._el("div", { class: "empty" }, this._t("no_spools")));
    } else if (!groups.length) {
      card.append(this._el("div", { class: "empty" }, this._t("no_match")));
    } else {
      const table = this._el("table", {});
      const heads = ["name", "material", "brand", "stock", "price"].map((k) => this._t(k));
      table.append(this._el("tr", {}, ...heads.map((h) => this._el("th", {}, h)), this._el("th", {}, "")));
      for (const g of groups) {
        const dot = this._el("span", { class: "dot", style: `background:${/^#[0-9a-f]{6,8}$/i.test(g.color) ? g.color : "transparent"}` });
        const pct = Math.max(0, Math.min(100, g.percent));
        const bar = this._el("div", { class: "bar" }, this._el("div", { class: "fill" + (pct <= 15 ? " low" : ""), style: `width:${pct}%` }));
        const actions = this._el("td", {});
        // A single-spool type is managed from its own row; several spools from their sub-rows.
        if (g.spools.length === 1) actions.append(...this._rowActions(g.spools[0], admin, slotOf));
        // A type with several spools expands on a click on its name to list them one by one.
        const multi = g.spools.length > 1;
        const expanded = multi && this._expanded.has(g.key);
        const toggle = () => {
          if (this._expanded.has(g.key)) this._expanded.delete(g.key); else this._expanded.add(g.key);
          this._render();
        };
        table.append(this._el("tr", {},
          this._el("td", multi
            ? { class: "link", title: g.color || "", role: "button", "aria-expanded": String(expanded), onclick: toggle }
            : { title: g.color || "" },
          multi ? this._el("span", { class: "chevron" }, expanded ? "▾" : "▸") : "", dot, g.name,
            multi ? this._el("span", { class: "badge" }, `× ${g.spools.length}`) : "",
            !multi && !slotOf[g.spools[0].id] ? this._el("span", { class: "badge stock" }, this._t("stock_badge")) : ""),
          this._el("td", {}, g.material),
          this._el("td", {}, g.brand || "–"),
          this._el("td", {}, bar, `${this._fmtNum(g.remaining, 0)} / ${this._fmtNum(g.initial, 0)} g (${this._fmtNum(g.percent, 0)} %)`),
          this._el("td", {}, g.avgPrice != null ? `${this._fmtMoney(g.avgPrice, cur)}/kg` : "–"),
          actions));
        if (expanded) {
          for (const sp of g.spools) {
            const spct = Math.max(0, Math.min(100, sp.remaining_percent));
            table.append(this._el("tr", { class: "sub-row" },
              this._el("td", { class: "indent" }, sp.name,
                sp.rfid ? this._el("span", { class: "badge", title: sp.rfid }, "RFID") : "",
                slotOf[sp.id]
                  ? this._el("span", { class: "sub" }, ` · ${slotOf[sp.id]}`)
                  : this._el("span", { class: "badge stock" }, this._t("stock_badge"))),
              this._el("td", {}, ""),
              this._el("td", {}, ""),
              this._el("td", {},
                this._el("div", { class: "bar" }, this._el("div", { class: "fill" + (spct <= 15 ? " low" : ""), style: `width:${spct}%` })),
                `${this._fmtNum(sp.remaining_g, 0)} / ${this._fmtNum(sp.initial_weight_g, 0)} g (${this._fmtNum(sp.remaining_percent, 0)} %)`),
              this._el("td", {}, sp.price_per_kg != null ? `${this._fmtMoney(sp.price_per_kg, cur)}/kg` : "–"),
              this._el("td", {}, ...this._rowActions(sp, admin, slotOf))));
          }
        }
      }
      card.append(table);
    }
    main.append(card);

    const details = this._el("details", { class: "card" },
      this._el("summary", {}, this._t("archived_spools", { count: archivedSpools.length })));
    if (this._archiveOpen) details.open = true;
    details.addEventListener("toggle", () => { this._archiveOpen = details.open; });
    if (!archivedSpools.length) {
      details.append(this._el("div", { class: "empty" }, this._t("no_archived")));
    } else {
      const table = this._el("table", {});
      table.append(this._el("tr", {}, ...["name", "material", "brand", "stock"].map((k) => this._el("th", {}, this._t(k))), this._el("th", {}, "")));
      for (const sp of archivedSpools) {
        const actions = this._el("td", {});
        if (admin) {
          actions.append(
            this._iconButton("restore", this._t("restore"), () => this._call({ type: "druck_assistant/spool_archive", spool_id: sp.id, archived: false })),
            this._iconButton("delete", this._t("delete"), () => this._confirmDelete(sp), true));
        }
        table.append(this._el("tr", {},
          this._el("td", {}, sp.name, sp.rfid ? this._el("span", { class: "badge", title: sp.rfid }, "RFID") : ""),
          this._el("td", {}, sp.material),
          this._el("td", {}, sp.brand || "–"),
          this._el("td", {}, `${this._fmtNum(sp.remaining_g, 0)} / ${this._fmtNum(sp.initial_weight_g, 0)} g`),
          actions));
      }
      details.append(table);
    }
    main.append(details);

    // Forms are popups over the list.
    if (this._editing !== null) main.append(this._renderForm(this._editing));
  }

  _renderAms(main, printer) {
    const admin = this._isAdmin();
    if (this._notice) main.append(this._el("div", { class: this._noticeOk ? "sub notice" : "error" }, this._notice));
    if (!admin) main.append(this._el("div", { class: "sub notice" }, this._t("admin_only")));
    const activeSpools = this._spools.filter((sp) => !sp.archived);
    const slotsCard = this._el("div", { class: "card" }, this._el("h2", {}, this._t("slots")));
    const slots = printer?.slots || [];
    if (!slots.length) {
      slotsCard.append(this._el("div", { class: "empty" }, this._t("no_slots")));
    } else {
      const table = this._el("table", {});
      table.append(this._el("tr", {}, ...["slot", "material", "assign_spool"].map((k) => this._el("th", {}, this._t(k)))));
      for (const sl of slots) {
        const sel = this._el("select", { onchange: (e) => this._call({ type: "druck_assistant/spool_assign", slot_key: sl.key, spool_id: e.target.value || null }) },
          this._el("option", { value: "" }, this._t("none")),
          ...activeSpools.map((sp) => {
            const o = this._el("option", { value: sp.id }, `${sp.name} (${sp.material})`);
            if (sp.id === sl.spool_id) o.selected = true;
            return o;
          }));
        if (!admin) sel.disabled = true;
        const dot = this._el("span", { class: "dot", style: `background:${/^#[0-9a-f]{6,8}$/i.test(sl.color || "") ? sl.color : "transparent"}` });
        table.append(this._el("tr", {},
          this._el("td", {}, sl.active ? "▶ " : "", sl.label, sl.tagged ? this._el("span", { class: "badge" }, "RFID") : ""),
          this._el("td", {}, dot, `${sl.type || "–"}${sl.remain != null ? `, ${sl.remain} %` : ""}`),
          this._el("td", {}, sel)));
      }
      slotsCard.append(table);
    }
    if (slots.length && admin) slotsCard.append(this._el("div", { class: "sub notice" }, this._t("correct_hint")));
    main.append(slotsCard);
  }

  /** The print in progress with progress, times, layer, weight, temperatures and cost estimate. */
  _renderCurrentPrint(printer, cur) {
    const card = this._el("div", { class: "card" });
    const c = printer.current_print;
    const f = printer.filament;
    if (!c) {
      card.append(this._el("h2", {}, this._t("current")), this._el("div", { class: "sub" }, this._t("no_active_print")));
      if (f && f.type) {
        const line = this._el("div", { style: "margin-top:6px" });
        if (f.color) line.append(this._el("span", { class: "dot", style: `background:${/^#[0-9a-f]{3,8}$/i.test(f.color) ? f.color : "transparent"}` }));
        line.append(`${f.name || f.type}, ${f.price_per_kg != null ? this._fmtMoney(f.price_per_kg, cur) + "/kg" : ""}${f.remain != null ? `, ${this._t("remaining", { value: f.remain })}` : ""}`);
        card.append(line);
      }
      return card;
    }
    const known = (v) => v !== null && v !== undefined;
    const money = (v) => (known(v) ? this._fmtMoney(v, cur) : "–");
    const elapsedMin = c.started && !Number.isNaN(Date.parse(c.started)) ? Math.max(0, (Date.now() - Date.parse(c.started)) / 60000) : null;
    const pct = known(c.progress) ? Math.max(0, Math.min(100, c.progress)) : null;
    const dot = /^#[0-9a-f]{6,8}$/i.test(c.color || "") ? this._el("span", { class: "dot", style: `background:${c.color}` }) : "";

    card.append(this._el("h2", {}, this._t("current_print")),
      this._el("div", { class: "print-title" }, c.name || this._t("unknown"),
        this._el("span", { class: "badge stock" }, this._t(`status_${c.status}`) === `status_${c.status}` ? c.status : this._t(`status_${c.status}`))));
    if (pct !== null) {
      card.append(this._el("div", { class: "progress" },
        this._el("div", { class: "bar wide" }, this._el("div", { class: "fill", style: `width:${pct}%` })),
        this._el("span", {}, `${this._fmtNum(pct, 0)} %`)));
    }
    const tiles = [
      [this._t("elapsed"), elapsedMin !== null ? this._fmtDuration(elapsedMin) : "–"],
      [this._t("time_remaining"), known(c.remaining_min) ? this._fmtDuration(c.remaining_min) : "–"],
      [this._t("finishes"), c.end && !Number.isNaN(Date.parse(c.end)) ? new Date(c.end).toLocaleTimeString(this._hass.locale?.language, { hour: "2-digit", minute: "2-digit" }) : "–"],
      [this._t("layer"), known(c.layer) && known(c.total_layers) ? `${this._fmtNum(c.layer, 0)} / ${this._fmtNum(c.total_layers, 0)}` : "–"],
      [this._t("print_weight"), known(c.weight_g) ? `${this._fmtNum(c.weight_g, 1)} g` : "–"],
      [this._t("nozzle_bed"), known(c.nozzle_temp) || known(c.bed_temp) ? `${known(c.nozzle_temp) ? this._fmtNum(c.nozzle_temp, 0) : "–"} / ${known(c.bed_temp) ? this._fmtNum(c.bed_temp, 0) : "–"} °C` : "–"],
    ];
    const grid = this._el("div", { class: "tiles small" }, ...tiles.map(([label, value]) => this._tile(label, value)));
    grid.append(
      this._tile(this._t("filament_cost"), money(c.filament_cost), known(c.price_per_kg) ? `${this._fmtMoney(c.price_per_kg, cur)}/kg` : ""),
      this._tile(this._t("energy_cost_so_far"), money(c.energy_cost), known(c.energy_kwh) ? `${this._fmtNum(c.energy_kwh, 2)} kWh` : ""),
      this._tile(this._t("cost_estimate"), money(c.total_cost), this._t("cost_hint")));
    card.append(grid);
    const spoolLine = [c.spool, c.material].filter(Boolean).join(" · ");
    if (spoolLine) card.append(this._el("div", { class: "sub", style: "margin-top:8px" }, `${this._t("spool_label")}: `, dot, spoolLine));
    return card;
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
      .print-title { font-size: 18px; margin: 2px 0 10px; }
      .progress { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
      .bar.wide { width: auto; flex: 1; height: 8px; margin: 0; }
      .tiles.small { grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); margin-bottom: 0; }
      .tiles.small .value { font-size: 18px; }
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
      .dot { display: inline-block; width: 14px; height: 14px; border-radius: 50%; vertical-align: middle; margin-right: 6px; border: 1px solid var(--divider-color); }
      .ok { color: var(--success-color, #4caf50); } .fail { color: var(--error-color, #f44336); }
      .tabs { display: flex; gap: 4px; }
      .tabs button { background: transparent; color: inherit; border: 0; border-bottom: 2px solid transparent; padding: 6px 10px; font: inherit; cursor: pointer; opacity: .8; }
      .tabs button.active { border-bottom-color: currentColor; opacity: 1; }
      button { font: inherit; padding: 4px 12px; margin-right: 6px; border-radius: 6px; border: 1px solid var(--divider-color); background: var(--card-background-color); color: var(--primary-text-color); cursor: pointer; }
      button.primary { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: transparent; }
      .field { display: flex; flex-direction: column; gap: 2px; margin-bottom: 10px; font-size: 13px; color: var(--secondary-text-color); }
      .field input { font: inherit; padding: 6px 8px; color: var(--primary-text-color); background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: 6px; }
      .filter { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 10px 0; }
      .filter input, .filter select { font: inherit; padding: 5px 8px; color: var(--primary-text-color); background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: 6px; }
      .filter-search { flex: 1; min-width: 200px; }
      .dialog.form { max-width: 480px; }
      .catalog { margin-bottom: 12px; padding-bottom: 4px; border-bottom: 1px solid var(--divider-color); }
      .field select { font: inherit; padding: 6px 8px; color: var(--primary-text-color); background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: 6px; }
      .row { display: flex; align-items: center; gap: 8px; }
      .row select { flex: 1; }
      summary { cursor: pointer; font-weight: 500; }
      details.card[open] summary { margin-bottom: 8px; }
      .overlay { position: fixed; inset: 0; z-index: 10; background: rgba(0,0,0,.5); display: flex; align-items: center; justify-content: center; padding: 16px; }
      .dialog { background: var(--card-background-color, Canvas); color: var(--primary-text-color, CanvasText); border-radius: var(--ha-card-border-radius, 12px); padding: 16px 20px; width: 100%; max-width: 880px; max-height: 90vh; overflow: auto; }
      .dialog h2 { margin: 0 0 4px; font-size: 18px; }
      .dialog h3 { margin: 16px 0 6px; font-size: 14px; font-weight: 500; }
      .dialog .field { max-width: 260px; }
      .icon-btn { width: 32px; height: 32px; padding: 0; margin-right: 2px; display: inline-flex; align-items: center; justify-content: center; border: 0; border-radius: 50%; background: transparent; color: var(--secondary-text-color); cursor: pointer; }
      .icon-btn:hover { background: var(--divider-color); color: var(--primary-text-color); }
      .icon-btn.danger:hover { color: var(--error-color, #f44336); }
      .icon-btn svg { width: 20px; height: 20px; }
      td.link { cursor: pointer; }
      td.link:hover { text-decoration: underline; }
      .chevron { display: inline-block; width: 14px; color: var(--secondary-text-color); }
      tr.sub-row td { font-size: 13px; color: var(--secondary-text-color); border-bottom-style: dashed; }
      tr.sub-row td.indent { padding-left: 38px; }
      .badge.stock { background: var(--primary-color); color: var(--text-primary-color, #fff); }
      .badge { margin-left: 6px; padding: 0 6px; border-radius: 8px; font-size: 11px; background: var(--divider-color); color: var(--secondary-text-color); }
      .notice { padding: 0 0 12px; }
      .bar { width: 120px; height: 6px; border-radius: 3px; background: var(--divider-color); margin-bottom: 4px; }
      .bar .fill { height: 100%; border-radius: 3px; background: var(--success-color, #4caf50); }
      .bar .fill.low { background: var(--error-color, #f44336); }
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
    const tabs = this._el("div", { class: "tabs" },
      ...["overview", "filament", "ams"].map((k) => this._el("button", {
        class: this._tab === k ? "active" : "",
        onclick: () => { this._tab = k; this._editing = null; this._render(); },
      }, this._t(`tab_${k}`))));
    header.append(tabs);
    root.append(header);

    const main = this._el("main");
    root.append(main);

    if (this._error) { main.append(this._el("div", { class: "error" }, this._error)); return; }
    if (!this._data) { main.append(this._el("div", { class: "empty" }, "…")); return; }
    if (this._tab === "filament") { this._renderFilament(main, printer); return; }
    if (this._tab === "ams") { this._renderAms(main, printer); return; }
    if (!printer) { main.append(this._el("div", { class: "empty" }, this._t("no_printer"))); return; }

    const t = printer.totals;
    const cur = printer.currency;
    const rate = t.prints ? Math.round((t.successful / t.prints) * 100) : 0;
    main.append(this._el("div", { class: "tiles" },
      this._tile(this._t("prints"), t.prints, this._t("success_rate", { rate })),
      this._tile(this._t("filament"), `${this._fmtNum(t.weight_g, 0)} g`),
      this._tile(this._t("energy"), `${this._fmtNum(t.energy_kwh, 2)} kWh`, `${this._fmtNum(printer.price_per_kwh, 4)} ${cur}/kWh`),
      this._tile(this._t("total_cost"), this._fmtMoney(t.cost, cur),
        this._t("cost_split", { filament: this._fmtMoney(t.filament_cost ?? t.cost - t.energy_cost, cur), energy: this._fmtMoney(t.energy_cost, cur) })),
    ));

    main.append(this._renderCurrentPrint(printer, cur));

    const hist = this._el("div", { class: "card" }, this._el("h2", {}, this._t("history")));
    if (!printer.history.length) {
      hist.append(this._el("div", { class: "empty" }, this._t("no_history")));
    } else {
      const table = this._el("table", {});
      table.append(this._el("tr", {},
        ...["end", "name", "result", "duration", "material", "weight", "filament_cost", "electricity_cost", "total"].map((k) => this._t(k)).map((h, i) =>
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
          this._el("td", { class: "num", title: r.price_per_kg ? `${this._fmtMoney(r.price_per_kg, cur)}/kg` : "" },
            this._fmtMoney(r.filament_cost ?? r.cost - (r.energy_cost || 0), cur)),
          this._el("td", { class: "num", title: `${this._fmtNum(r.energy_kwh || 0, 3)} kWh` },
            this._fmtMoney(r.energy_cost || 0, cur), this._el("div", { class: "sub" }, `${this._fmtNum(r.energy_kwh || 0, 2)} kWh`)),
          this._el("td", { class: "num" }, this._fmtMoney(r.cost, cur))));
      }
      hist.append(table);
    }
    main.append(hist);
  }
}

customElements.define("druck-assistant-panel", DruckAssistantPanel);
