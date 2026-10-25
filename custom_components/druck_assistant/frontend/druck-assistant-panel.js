// Sidebar panel of the 3D Print Assistant integration (no external dependencies).
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
    add_stock: "Add stock",
    suggest_hint: "Pick a name you already have to fill in the other fields.",
    catalog: "Bambu Lab catalog",
    catalog_filament: "Filament",
    catalog_color: "Color",
    catalog_choose: "– choose –",
    catalog_hint: "Pick a Bambu Lab filament and color to fill in name, material, brand and color. You can still change every field.",
    stock_badge: "In stock",
    spools_of_type: "Spools of this type",
    close: "Close",
    add_stock_hint: "New full spools of this type. Existing spools keep their price.",
    purchased_quantity: "Purchased quantity",
    add: "Add",
    rfid_tag: "RFID tag (clear to unlink)",
    correct_hint: "Wrong spool? Pick the right one: the tag moves to it, and the automatic match stays corrected. Choosing \"none\" stops automatic assignment for the spool currently in this slot.",
    quantity: "Quantity (e.g. 4 for a 4-pack)",
    archive: "Archive",
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
    add_stock: "Bestand hinzufügen",
    suggest_hint: "Wähle einen vorhandenen Namen, um die übrigen Felder auszufüllen.",
    catalog: "Bambu-Lab-Katalog",
    catalog_filament: "Filament",
    catalog_color: "Farbe",
    catalog_choose: "– wählen –",
    catalog_hint: "Wähle ein Bambu-Lab-Filament und eine Farbe, um Name, Material, Hersteller und Farbe auszufüllen. Du kannst jedes Feld danach noch ändern.",
    stock_badge: "Vorrat",
    spools_of_type: "Spulen dieser Sorte",
    close: "Schließen",
    add_stock_hint: "Neue volle Spulen dieser Sorte. Vorhandene Spulen behalten ihren Preis.",
    purchased_quantity: "Gekaufte Anzahl",
    add: "Hinzufügen",
    rfid_tag: "RFID-Tag (leeren zum Lösen)",
    correct_hint: "Falsche Spule? Wähle die richtige: Der Tag wandert zu ihr, die automatische Zuordnung bleibt korrigiert. „keine“ stoppt die automatische Zuordnung für die Spule, die gerade in diesem Slot steckt.",
    quantity: "Anzahl (z. B. 4 für ein 4er-Pack)",
    archive: "Archivieren",
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
    this._dialog = null;
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
      this._spools = this._data.spools || [];
      const ids = this._data.printers.map((p) => p.entry_id);
      if (!ids.includes(this._selected)) this._selected = ids[0] || null;
    } catch (e) {
      this._error = e && e.message ? e.message : String(e);
    }
    if (this._editing === null && this._dialog === null) this._render(); // never re-render while a form is open
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

  async _call(msg, describe, keepDialog = false) {
    this._notice = null;
    this._noticeOk = false;
    try {
      const result = await this._hass.connection.sendMessagePromise(msg);
      if (describe) { this._notice = describe(result); this._noticeOk = true; }
    } catch (e) {
      this._notice = e && e.message ? e.message : String(e);
    }
    this._editing = null;
    if (!keepDialog) this._dialog = null;
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
          this._call({ type: "druck_assistant/spool_save", spool: out, ...(spool.id ? {} : { quantity: parseInt(qty.value, 10) || 1 }) }, null, true);
        } }, this._t("save")),
        this._el("button", { onclick: () => { this._editing = null; this._render(); } }, this._t("cancel"))));
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

  _renderDialog(group, slotOf, cur, admin) {
    const qty = this._el("input", { type: "number", min: "1", max: "50", step: "1", value: "1" });
    const last = group.spools[group.spools.length - 1];
    const price = this._el("input", { type: "number", min: "0", step: "0.01", value: last.price_per_kg ?? "" });
    const close = () => { this._dialog = null; this._render(); };

    const dialog = this._el("div", { class: "dialog", role: "dialog" },
      this._el("h2", {}, group.name),
      this._el("div", { class: "sub notice" }, `${group.material}${group.brand ? `, ${group.brand}` : ""}${group.color ? `, ${group.color.slice(0, 7)}` : ""}`));

    if (admin) {
      dialog.append(
        this._el("h3", {}, this._t("add_stock")),
        this._el("div", { class: "sub notice" }, this._t("add_stock_hint")),
        this._field(this._t("purchased_quantity"), qty),
        this._field(`${this._t("price_per_kg")} (${cur})`, price),
        this._el("div", { class: "actions" },
          this._el("button", { class: "primary", onclick: () => this._call({
            type: "druck_assistant/spool_add_stock", spool_id: last.id,
            quantity: parseInt(qty.value, 10) || 1,
            price_per_kg: price.value === "" ? null : price.value,
          }, null, true) }, this._t("add"))));
    }

    const table = this._el("table", {});
    table.append(this._el("tr", {}, ...["name", "stock", "price", "slot"].map((k) => this._el("th", {}, this._t(k))), this._el("th", {}, "")));
    for (const sp of group.spools) {
      const actions = this._el("td", {});
      if (admin) {
        actions.append(
          this._el("button", { onclick: () => { this._editing = sp; this._render(); } }, this._t("edit")),
          this._el("button", { onclick: () => this._call({ type: "druck_assistant/spool_archive", spool_id: sp.id, archived: true }, null, true) }, this._t("archive")),
          this._el("button", { onclick: () => { if (confirm(this._t("confirm_delete", { name: sp.name }))) this._call({ type: "druck_assistant/spool_delete", spool_id: sp.id }, null, true); } }, this._t("delete")));
      }
      table.append(this._el("tr", {},
        this._el("td", {}, sp.name, sp.rfid ? this._el("span", { class: "badge", title: sp.rfid }, "RFID") : "",
          slotOf[sp.id] ? "" : this._el("span", { class: "badge stock" }, this._t("stock_badge"))),
        this._el("td", {}, `${this._fmtNum(sp.remaining_g, 0)} / ${this._fmtNum(sp.initial_weight_g, 0)} g (${this._fmtNum(sp.remaining_percent, 0)} %)`),
        this._el("td", {}, sp.price_per_kg != null ? `${this._fmtMoney(sp.price_per_kg, cur)}/kg` : "–"),
        this._el("td", {}, slotOf[sp.id] || "–"),
        actions));
    }
    dialog.append(this._el("h3", {}, this._t("spools_of_type")), table,
      this._el("div", { class: "actions" }, this._el("button", { onclick: close }, this._t("close"))));

    const overlay = this._el("div", { class: "overlay", onclick: (e) => { if (e.target === overlay) close(); } }, dialog);
    return overlay;
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
    const groups = this._groups(activeSpools);
    if (this._dialog && !groups.some((g) => g.key === this._dialog)) this._dialog = null;
    if (!groups.length) {
      card.append(this._el("div", { class: "empty" }, this._t("no_spools")));
    } else {
      const table = this._el("table", {});
      const heads = ["name", "material", "brand", "stock", "price"].map((k) => this._t(k));
      table.append(this._el("tr", {}, ...heads.map((h) => this._el("th", {}, h)), this._el("th", {}, "")));
      for (const g of groups) {
        const open = () => { this._dialog = g.key; this._render(); };
        const dot = this._el("span", { class: "dot", style: `background:${/^#[0-9a-f]{6,8}$/i.test(g.color) ? g.color : "transparent"}` });
        const pct = Math.max(0, Math.min(100, g.percent));
        const bar = this._el("div", { class: "bar" }, this._el("div", { class: "fill" + (pct <= 15 ? " low" : ""), style: `width:${pct}%` }));
        const actions = this._el("td", {});
        if (admin) actions.append(this._el("button", { onclick: open }, this._t("add_stock")));
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
              this._el("td", {}, "")));
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
            this._el("button", { onclick: () => this._call({ type: "druck_assistant/spool_archive", spool_id: sp.id, archived: false }) }, this._t("restore")),
            this._el("button", { onclick: () => { if (confirm(this._t("confirm_delete", { name: sp.name }))) this._call({ type: "druck_assistant/spool_delete", spool_id: sp.id }); } }, this._t("delete")));
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

    // Forms are popups over the list; the form of a spool shows on top of the type popup it was opened from.
    const open = groups.find((g) => g.key === this._dialog);
    if (this._editing !== null) main.append(this._renderForm(this._editing));
    else if (open) main.append(this._renderDialog(open, slotOf, cur, admin));
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
      .dot { display: inline-block; width: 14px; height: 14px; border-radius: 50%; vertical-align: middle; margin-right: 6px; border: 1px solid var(--divider-color); }
      .ok { color: var(--success-color, #4caf50); } .fail { color: var(--error-color, #f44336); }
      .tabs { display: flex; gap: 4px; }
      .tabs button { background: transparent; color: inherit; border: 0; border-bottom: 2px solid transparent; padding: 6px 10px; font: inherit; cursor: pointer; opacity: .8; }
      .tabs button.active { border-bottom-color: currentColor; opacity: 1; }
      button { font: inherit; padding: 4px 12px; margin-right: 6px; border-radius: 6px; border: 1px solid var(--divider-color); background: var(--card-background-color); color: var(--primary-text-color); cursor: pointer; }
      button.primary { background: var(--primary-color); color: var(--text-primary-color, #fff); border-color: transparent; }
      .field { display: flex; flex-direction: column; gap: 2px; margin-bottom: 10px; font-size: 13px; color: var(--secondary-text-color); }
      .field input { font: inherit; padding: 6px 8px; color: var(--primary-text-color); background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: 6px; }
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
