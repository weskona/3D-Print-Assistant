// Sidebar panel of the 3D Print Assistant integration (no external dependencies).
// Material Design Icons paths, drawn inline so the panel needs no icon font.
const ICONS = {
  edit: "M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z",
  delete: "M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",
  archive: "M3,3H21V7H3V3M4,8H20V21H4V8M9.5,11A0.5,0.5 0 0,0 9,11.5V13H15V11.5A0.5,0.5 0 0,0 14.5,11H9.5Z",
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
    idle: "Idle",
    totals: "Totals",
    electricity_cost: "Electricity cost",
    total: "Total",
    cost_split: "Filament {filament} · Electricity {energy}",
    stage_label: "Current stage",
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
    catalog: "Filament catalog",
    catalog_brand: "Manufacturer",
    catalog_filament: "Filament",
    catalog_color: "Color",
    catalog_choose: "– choose –",
    catalog_hint: "Pick a manufacturer, filament and color to fill in name, material, brand and color. You can still change every field.",
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
    archive: "Archive",
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
    idle: "Bereit",
    totals: "Gesamt",
    electricity_cost: "Stromkosten",
    total: "Gesamt",
    cost_split: "Filament {filament} · Strom {energy}",
    stage_label: "Aktueller Arbeitsschritt",
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
    catalog: "Filament-Katalog",
    catalog_brand: "Hersteller",
    catalog_filament: "Filament",
    catalog_color: "Farbe",
    catalog_choose: "– wählen –",
    catalog_hint: "Wähle Hersteller, Filament und Farbe, um Name, Material, Hersteller und Farbe auszufüllen. Du kannst jedes Feld danach noch ändern.",
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
    archive: "Archivieren",
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
    else this._updateLive();
  }

  /** The state of an entity as Home Assistant shows it (translated), or null if unknown. */
  _entityText(entityId) {
    const state = entityId ? this._hass?.states?.[entityId] : null;
    if (!state || state.state === "unavailable" || state.state === "unknown") return null;
    return this._hass.formatEntityState ? this._hass.formatEntityState(state) : state.state;
  }

  /** Refresh the live values (they follow the entity state, not the 10 second reload). */
  _updateLive() {
    for (const el of this.shadowRoot.querySelectorAll("[data-live-entity]")) {
      const text = this._entityText(el.dataset.liveEntity) ?? "–";
      if (el.textContent !== text) el.textContent = text;
    }
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

  /** The panel font; @font-face does not work inside a shadow root, so it is registered on the page. */
  _loadFont() {
    if (this._fontRequested || !window.FontFace || !document.fonts) return;
    this._fontRequested = true;
    if ([...document.fonts].some((f) => f.family.replace(/"/g, "") === "Outfit")) return;
    const font = new FontFace("Outfit", "url(/druck_assistant_static/fonts/Outfit-variable.woff2)", { weight: "100 900", display: "swap" });
    font.load().then((loaded) => document.fonts.add(loaded)).catch(() => { /* fallback fonts */ });
  }

  async _start() {
    this._loadFont();
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
      const colorLabel = (c) => `${german && c.name_de ? c.name_de : c.name}${c.code ? ` (${c.code})` : ""}`;
      const products = this._catalog.products;
      // Bambu Lab first, the other brands alphabetically.
      const brands = [...new Set(products.map((p) => p.brand))].sort((a, b) =>
        (a === "Bambu Lab" ? -1 : b === "Bambu Lab" ? 1 : a.localeCompare(b)));
      const choose = () => this._el("option", { value: "" }, this._t("catalog_choose"));
      const brandSel = this._el("select", {}, choose(), ...brands.map((b) => this._el("option", { value: b }, b)));
      const productSel = this._el("select", {}, choose());
      const colorSel = this._el("select", {}, choose());
      productSel.disabled = true;
      colorSel.disabled = true;
      const swatch = this._el("span", { class: "dot", style: "background:transparent" });
      const product = () => products[parseInt(productSel.value, 10)];
      brandSel.addEventListener("change", () => {
        productSel.replaceChildren(choose());
        colorSel.replaceChildren(choose());
        colorSel.disabled = true;
        swatch.style.background = "transparent";
        productSel.disabled = brandSel.value === "";
        products.forEach((p, i) => {
          if (p.brand === brandSel.value) productSel.append(this._el("option", { value: String(i) }, p.name));
        });
      });
      productSel.addEventListener("change", () => {
        colorSel.replaceChildren(choose());
        const p = productSel.value === "" ? null : product();
        colorSel.disabled = !p;
        swatch.style.background = "transparent";
        if (!p) return;
        p.colors.forEach((c, i) => colorSel.append(this._el("option", { value: String(i) }, colorLabel(c))));
        inputs.name.value = p.name;
        inputs.material.value = p.material;
        inputs.brand.value = p.brand;
        for (const key of ["name", "material", "brand"]) touched.add(key);
        // Spool size of the product line, when the catalog knows it.
        if (p.weight_g && !touched.has("initial_weight_g")) {
          inputs.initial_weight_g.value = p.weight_g;
          if (!touched.has("remaining_g")) inputs.remaining_g.value = p.weight_g;
        }
      });
      colorSel.addEventListener("change", () => {
        const p = product();
        const c = colorSel.value === "" ? null : p.colors[parseInt(colorSel.value, 10)];
        if (!c) { swatch.style.background = "transparent"; return; }
        inputs.color.value = c.hex.toLowerCase();
        touched.add("color");
        swatch.style.background = c.hex;
        // The color name tells same-type spools apart in the notes.
        if (!touched.has("notes")) inputs.notes.value = `${c.name}${c.code ? ` (${c.code})` : ""}`;
      });
      const picker = this._el("div", { class: "catalog" },
        this._el("h3", {}, this._t("catalog")),
        this._el("div", { class: "sub notice" }, this._t("catalog_hint")),
        this._field(this._t("catalog_brand"), brandSel),
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
   * Row buttons of a spool: Edit where editing is allowed (an untagged Bambu Lab spool in a
   * slot has nothing to edit), Archive and Delete. Spools are also archived automatically when
   * they run empty; archiving by hand is undone with Restore in the archive.
   */
  _rowActions(sp, admin, slotOf) {
    if (!admin) return [];
    const archive = this._iconButton("archive", this._t("archive"), () => this._call({ type: "druck_assistant/spool_archive", spool_id: sp.id, archived: true }));
    const del = this._iconButton("delete", this._t("delete"), () => this._confirmDelete(sp), true);
    if (this._canEdit(sp, admin, slotOf)) {
      return [this._iconButton("edit", this._t("edit"), () => { this._editing = sp; this._render(); }), archive, del];
    }
    return [archive, del];
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
      const grid = this._el("div", { class: "slots" });
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
        const remain = sl.remain != null ? Math.max(0, Math.min(100, sl.remain)) : null;
        grid.append(this._el("div", { class: "slot" + (sl.active ? " active" : "") },
          this._el("div", { class: "top" }, dot, sl.label, sl.tagged ? this._el("span", { class: "badge" }, "RFID") : "",
            this._el("span", { class: "sub" }, `${sl.type || "–"}${remain !== null ? ` · ${remain} %` : ""}`)),
          remain !== null ? this._el("div", { class: "bar", style: "width:100%" }, this._el("div", { class: "fill" + (remain <= 15 ? " low" : ""), style: `width:${remain}%` })) : "",
          this._el("label", { class: "field", style: "margin:0" }, this._el("span", {}, this._t("assign_spool")), sel)));
      }
      slotsCard.append(grid);
    }
    if (slots.length && admin) slotsCard.append(this._el("div", { class: "sub notice" }, this._t("correct_hint")));
    main.append(slotsCard);
  }

  /** The print in progress with progress, times, layer, weight, temperatures and cost estimate. */
  _renderCurrentPrint(printer, cur) {
    const card = this._el("div", { class: "card" });
    const c = printer.current_print;
    const f = printer.filament;
    const statusName = (status) => (this._t(`status_${status}`) === `status_${status}` ? status : this._t(`status_${status}`));
    // The current stage (heating, auto bed leveling, printing, ...) follows its entity live.
    const stage = printer.stage_entity
      ? this._el("div", { class: "stage" }, `${this._t("stage_label")}: `,
        this._el("strong", { "data-live-entity": printer.stage_entity }, this._entityText(printer.stage_entity) ?? "–"))
      : null;
    if (!c) {
      card.append(this._el("div", { class: "hd" }, this._el("h2", {}, this._t("current")), this._el("span", { class: "chip" }, this._t("idle"))),
        this._el("div", { class: "sub" }, this._t("no_active_print")));
      if (stage) card.append(stage);
      if (f && f.type) {
        const line = this._el("div", { style: "margin-top:10px" });
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

    card.append(this._el("div", { class: "hd" }, this._el("h2", {}, this._t("current_print")),
      this._el("span", { class: `chip ${c.status}` }, statusName(c.status))));
    if (pct !== null) {
      card.append(this._el("div", { class: "bignum" }, this._el("b", {}, this._fmtNum(pct, 0)), this._el("small", {}, "%")));
    }
    card.append(this._el("div", { class: "print-title" }, c.name || this._t("unknown")));
    if (pct !== null) {
      card.append(this._el("div", { class: "progress" },
        this._el("div", { class: "bar wide" }, this._el("div", { class: "fill", style: `width:${pct}%` }))));
    }
    if (stage) card.append(stage);
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
    if (spoolLine) card.append(this._el("div", { class: "sub", style: "margin-top:12px" }, `${this._t("spool_label")}: `, dot, spoolLine));
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
      :host {
        --bg: #0b0d12; --panel: #14171e; --line: rgba(255,255,255,.065);
        --tile: rgba(255,255,255,.032); --tile-line: rgba(255,255,255,.07);
        --text: #f3f5f9; --muted: #8b91a1; --dim: #5d6373;
        --green: #34d399; --orange: #fb923c; --gold: #f7b733; --red: #f87171; --blue: #60a5fa; --cyan: #38bdf8;
        display: block; min-height: 100vh; background: var(--bg); color: var(--text); container-type: inline-size;
        font-family: "Outfit", "Plus Jakarta Sans", "Segoe UI", system-ui, sans-serif; -webkit-font-smoothing: antialiased;
        color-scheme: dark;
      }
      * { box-sizing: border-box; }
      .wrap { padding: 18px 22px 28px; }
      header { display: flex; align-items: center; justify-content: center; gap: 14px; flex-wrap: wrap; margin-bottom: 18px; position: relative; }
      header h1 { position: absolute; left: 0; margin: 0; font-size: 13px; font-weight: 600; letter-spacing: .16em; text-transform: uppercase; color: var(--dim); }
      header .printer-select { position: absolute; right: 0; }
      @container (max-width: 900px) { header h1 { display: none; } header .printer-select { position: static; } }
      select, input { font: inherit; color: var(--text); }
      select { height: 38px; padding: 0 12px; border-radius: 13px; border: 1px solid var(--line); background: rgba(255,255,255,.05); }
      select option { background: #171a21; color: var(--text); }
      input { height: 38px; padding: 0 12px; border-radius: 13px; border: 1px solid var(--line); background: rgba(255,255,255,.04); }
      input:focus, select:focus { outline: 2px solid rgba(56,189,248,.5); outline-offset: 1px; }
      input[type=color] { padding: 3px; width: 56px; }
      input[type=checkbox] { height: auto; }
      .tabs { display: inline-flex; gap: 2px; padding: 4px; border-radius: 18px; border: 1px solid var(--line); background: rgba(255,255,255,.03); }
      .tabs button { height: 36px; padding: 0 16px; margin: 0; border: 0; border-radius: 14px; background: transparent; color: var(--muted); font-size: 14.5px; font-weight: 500; }
      .tabs button:hover { color: var(--text); }
      .tabs button.active { background: rgba(255,255,255,.09); color: var(--text); font-weight: 600; }
      main { max-width: 1500px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }
      .grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.25fr); gap: 20px; align-items: start; }
      .col { display: flex; flex-direction: column; gap: 20px; min-width: 0; }
      @container (max-width: 900px) { .grid { grid-template-columns: minmax(0, 1fr); } .wrap { padding: 12px 12px 24px; } }
      .card { background: linear-gradient(180deg, #161920, #12151b); border: 1px solid var(--line); border-radius: 30px; padding: 20px 22px; margin: 0; overflow-x: auto; position: relative; }
      .card h2, .dialog h2 { margin: 0 0 14px; font-size: 15px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
      .card .hd { display: flex; align-items: center; justify-content: space-between; gap: 12px; min-height: 34px; margin-bottom: 14px; }
      .card .hd h2 { margin: 0; }
      .chip { display: inline-flex; align-items: center; gap: 6px; height: 30px; padding: 0 12px; border-radius: 999px; font-size: 13.5px; font-weight: 600; background: rgba(255,255,255,.06); border: 1px solid var(--line); color: var(--muted); white-space: nowrap; }
      .chip.running { color: var(--green); background: rgba(52,211,153,.12); border-color: rgba(52,211,153,.3); }
      .chip.pause { color: var(--orange); background: rgba(251,146,60,.1); border-color: rgba(251,146,60,.3); }
      .tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 8px; }
      .tile { display: flex; flex-direction: column; gap: 2px; padding: 10px 12px; border-radius: 15px; background: var(--tile); border: 1px solid var(--tile-line); min-width: 0; }
      .label { font-size: 11.5px; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
      .value { font-size: 19px; font-weight: 700; font-variant-numeric: tabular-nums; white-space: nowrap; }
      .tiles.small { grid-template-columns: repeat(3, minmax(0, 1fr)); }
      .tiles.small .value { font-size: 18px; }
      .tiles.small .label { white-space: normal; }
      @container (max-width: 560px) { .tiles.small { grid-template-columns: repeat(2, minmax(0, 1fr)); } .tiles.small .tile:last-child { grid-column: 1 / -1; } }
      .sub { color: var(--muted); font-size: 12px; font-weight: 500; }
      .notice { padding: 0 0 12px; }
      .bignum { display: flex; align-items: baseline; gap: 4px; line-height: 1; margin: 4px 0 2px; }
      .bignum b { font-size: 84px; font-weight: 700; letter-spacing: -.02em; font-variant-numeric: tabular-nums; }
      .bignum small { font-size: 30px; font-weight: 500; color: var(--muted); }
      .print-title { font-size: 18px; font-weight: 600; margin: 0 0 12px; color: rgba(243,245,249,.9); overflow-wrap: anywhere; }
      .stage { margin: 0 0 12px; color: var(--muted); font-size: 14.5px; }
      .stage strong { color: var(--text); font-weight: 600; }
      .progress { display: flex; align-items: center; gap: 10px; margin: 6px 0 14px; }
      .bar { position: relative; width: 120px; height: 8px; border-radius: 6px; background: rgba(255,255,255,.07); margin-bottom: 4px; overflow: hidden; }
      .bar.wide { width: auto; flex: 1; height: 12px; margin: 0; }
      .bar .fill { height: 100%; border-radius: 6px; background: linear-gradient(90deg, #34d399, #5eead4); }
      .bar .fill.low { background: linear-gradient(90deg, #f87171, #fb923c); }
      table { width: 100%; border-collapse: collapse; font-size: 14px; }
      th, td { text-align: left; padding: 9px 10px; border-bottom: 1px solid var(--line); white-space: nowrap; }
      th { font-size: 11.5px; letter-spacing: .06em; text-transform: uppercase; font-weight: 600; color: var(--muted); }
      tr:last-child td { border-bottom: 0; }
      td.num, th.num { text-align: right; }
      tr.sub-row td { font-size: 13px; color: var(--muted); background: rgba(255,255,255,.02); }
      tr.sub-row td.indent { padding-left: 38px; }
      td.link { cursor: pointer; }
      td.link:hover { color: var(--green); }
      .chevron { display: inline-block; width: 14px; color: var(--dim); }
      .dot { display: inline-block; width: 14px; height: 14px; border-radius: 50%; vertical-align: middle; margin-right: 8px; border: 1px solid rgba(255,255,255,.25); }
      .ok { color: var(--green); } .fail { color: var(--red); }
      .badge { margin-left: 8px; padding: 1px 8px; border-radius: 999px; font-size: 11px; font-weight: 600; background: rgba(255,255,255,.07); color: var(--muted); border: 1px solid var(--line); }
      .badge.stock { color: var(--cyan); background: rgba(56,189,248,.1); border-color: rgba(56,189,248,.3); }
      button { font: inherit; font-size: 14px; font-weight: 600; height: 38px; padding: 0 14px; margin-right: 8px; border-radius: 13px; border: 1px solid var(--line); background: rgba(255,255,255,.04); color: var(--muted); cursor: pointer; }
      button:hover { color: var(--text); background: rgba(255,255,255,.08); }
      button:focus-visible { outline: 2px solid var(--cyan); outline-offset: 2px; }
      button.primary { background: rgba(52,211,153,.14); border-color: rgba(52,211,153,.35); color: var(--green); }
      button.primary:hover { background: rgba(52,211,153,.22); }
      .icon-btn { width: 36px; height: 36px; padding: 0; margin: 0 2px 0 0; display: inline-flex; align-items: center; justify-content: center; border-radius: 12px; background: transparent; border-color: transparent; color: var(--muted); }
      .icon-btn:hover { background: rgba(255,255,255,.07); border-color: var(--line); color: var(--text); }
      .icon-btn.danger:hover { color: var(--red); }
      .icon-btn svg { width: 19px; height: 19px; }
      .field { display: flex; flex-direction: column; gap: 4px; margin-bottom: 12px; font-size: 12.5px; letter-spacing: .04em; color: var(--muted); }
      .field input, .field select { width: 100%; letter-spacing: 0; font-size: 15px; }
      .field.check { flex-direction: row; align-items: center; gap: 8px; }
      .row { display: flex; align-items: center; gap: 8px; }
      .row select { flex: 1; }
      .filter { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 12px 0; }
      .filter-search { flex: 1; min-width: 200px; }
      .filter .sub { margin-left: 4px; }
      .catalog { margin-bottom: 14px; padding-bottom: 6px; border-bottom: 1px solid var(--line); }
      .catalog h3, .dialog h3 { margin: 0 0 6px; font-size: 13px; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); }
      details.card summary { cursor: pointer; font-size: 15px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }
      details.card[open] summary { margin-bottom: 12px; }
      .overlay { position: fixed; inset: 0; z-index: 10; background: rgba(5,6,9,.62); backdrop-filter: blur(6px); display: flex; align-items: center; justify-content: center; padding: 16px; }
      .dialog { background: linear-gradient(180deg, #171a21, #111419); color: var(--text); border: 1px solid rgba(255,255,255,.09); border-radius: 30px; box-shadow: 0 30px 80px rgba(0,0,0,.6); padding: 22px 24px; width: 100%; max-width: 880px; max-height: 90vh; overflow: auto; }
      .dialog.form { max-width: 480px; }
      .dialog .actions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
      .dialog .actions button { margin: 0; }
      .history { display: flex; flex-direction: column; gap: 8px; }
      .hrow { display: grid; grid-template-columns: auto minmax(0, 1fr) auto; align-items: center; gap: 14px; padding: 11px 14px; border-radius: 18px; background: var(--tile); border: 1px solid var(--tile-line); }
      .hrow .when { display: flex; flex-direction: column; align-items: center; min-width: 52px; font-size: 12px; color: var(--muted); line-height: 1.25; }
      .hrow .when b { font-size: 15px; color: var(--text); font-weight: 600; font-variant-numeric: tabular-nums; }
      .hrow .what { min-width: 0; }
      .hrow .what b { display: block; font-size: 15.5px; font-weight: 600; overflow-wrap: anywhere; }
      .hrow .cost { text-align: right; white-space: nowrap; }
      .hrow .cost b { display: block; font-size: 16px; font-weight: 700; font-variant-numeric: tabular-nums; }
      .hrow.failed { border-color: rgba(248,113,113,.25); }
      .slots { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; }
      .slot { display: flex; flex-direction: column; gap: 8px; padding: 14px 16px; border-radius: 20px; background: var(--tile); border: 1px solid var(--tile-line); }
      .slot.active { border-color: rgba(52,211,153,.4); background: rgba(52,211,153,.06); }
      .slot .top { display: flex; flex-wrap: wrap; align-items: center; gap: 4px 8px; font-weight: 600; white-space: nowrap; }
      .slot .top .sub { margin-left: auto; }
      .slot select { width: 100%; }
      .empty, .error { color: var(--dim); font-size: 14px; padding: 14px 4px; }
      .error { color: var(--red); }
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
      sel.classList.add("printer-select");
      header.append(sel);
    }
    const tabs = this._el("div", { class: "tabs" },
      ...["overview", "filament", "ams"].map((k) => this._el("button", {
        class: this._tab === k ? "active" : "",
        onclick: () => { this._tab = k; this._editing = null; this._render(); },
      }, this._t(`tab_${k}`))));
    header.insertBefore(tabs, header.querySelector(".printer-select"));
    const wrap = this._el("div", { class: "wrap" });
    root.append(wrap);
    wrap.append(header);

    const main = this._el("main");
    wrap.append(main);

    if (this._error) { main.append(this._el("div", { class: "error" }, this._error)); return; }
    if (!this._data) { main.append(this._el("div", { class: "empty" }, "…")); return; }
    if (this._tab === "filament") { this._renderFilament(main, printer); return; }
    if (this._tab === "ams") { this._renderAms(main, printer); return; }
    if (!printer) { main.append(this._el("div", { class: "empty" }, this._t("no_printer"))); return; }

    const t = printer.totals;
    const cur = printer.currency;
    const rate = t.prints ? Math.round((t.successful / t.prints) * 100) : 0;
    const totals = this._el("div", { class: "card" }, this._el("h2", {}, this._t("totals")),
      this._el("div", { class: "tiles" },
        this._tile(this._t("prints"), t.prints, this._t("success_rate", { rate })),
        this._tile(this._t("filament"), `${this._fmtNum(t.weight_g, 0)} g`),
        this._tile(this._t("energy"), `${this._fmtNum(t.energy_kwh, 2)} kWh`, `${this._fmtNum(printer.price_per_kwh, 4)} ${cur}/kWh`),
        this._tile(this._t("total_cost"), this._fmtMoney(t.cost, cur),
          this._t("cost_split", { filament: this._fmtMoney(t.filament_cost ?? t.cost - t.energy_cost, cur), energy: this._fmtMoney(t.energy_cost, cur) }))));

    const hist = this._el("div", { class: "card" }, this._el("h2", {}, this._t("history")));
    if (!printer.history.length) {
      hist.append(this._el("div", { class: "empty" }, this._t("no_history")));
    } else {
      const list = this._el("div", { class: "history" });
      for (const r of printer.history) {
        const ok = r.result !== "failed";
        const finished = new Date(r.finished);
        const lang = this._hass.locale?.language;
        const filamentCost = r.filament_cost ?? r.cost - (r.energy_cost || 0);
        list.append(this._el("div", { class: "hrow" + (ok ? "" : " failed") },
          this._el("div", { class: "when" },
            this._el("span", {}, finished.toLocaleDateString(lang, { day: "2-digit", month: "short" })),
            this._el("b", {}, finished.toLocaleTimeString(lang, { hour: "2-digit", minute: "2-digit" }))),
          this._el("div", { class: "what" },
            this._el("b", {}, r.name),
            this._el("span", { class: "sub" },
              [this._fmtDuration(r.duration_min), r.material || null, `${this._fmtNum(r.weight_g)} g`, `${this._fmtNum(r.energy_kwh || 0, 2)} kWh`].filter(Boolean).join(" · ")),
            ok ? "" : this._el("span", { class: "badge", style: "color:var(--red);margin-left:8px" }, this._t("failed"))),
          this._el("div", { class: "cost", title: this._t("cost_split", { filament: this._fmtMoney(filamentCost, cur), energy: this._fmtMoney(r.energy_cost || 0, cur) }) },
            this._el("b", {}, this._fmtMoney(r.cost, cur)),
            this._el("span", { class: "sub" }, `${this._fmtMoney(filamentCost, cur)} + ${this._fmtMoney(r.energy_cost || 0, cur)}`))));
      }
      hist.append(list);
    }
    main.append(this._el("div", { class: "grid" },
      this._el("div", { class: "col" }, this._renderCurrentPrint(printer, cur)),
      this._el("div", { class: "col" }, totals, hist)));
  }
}

customElements.define("druck-assistant-panel", DruckAssistantPanel);
