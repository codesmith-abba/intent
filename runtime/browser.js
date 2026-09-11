(function (global) {
  "use strict";

  class RuntimeError extends Error {
    constructor(message, cause) {
      super(message);
      this.name = "ITLRuntimeError";
      this.cause = cause;
    }
  }

  class AssetManager {
    constructor(root) {
      this.root = root || "./assets/";
    }

    resolve(source) {
      if (!source) return null;
      if (/^(https?:|data:|blob:|\/)/.test(source)) return source;
      return this.root.replace(/\/$/, "") + "/" + source.replace(/^\//, "");
    }
  }

  class BrowserRuntime {
    constructor(options) {
      const config = options || {};
      this.root = config.root || document.body;
      this.assetManager = new AssetManager(config.assetRoot || "./assets/");
      this.errorTarget = config.errorTarget || this.root;
      this.manifest = null;
      this.pages = new Map();
      this.state = { currentPage: null };
      this.listeners = new Set();
    }

    async start(source) {
      try {
        this.manifest = typeof source === "string" ? await this.load(source) : source;
        this.validateManifest(this.manifest);
        this.pages = new Map(this.manifest.pages.map((page) => [page.name, page]));
        this.state.currentPage = this.resolveInitialPage();
        this.bindEvents();
        this.render();
        this.emit("ready", this.state.currentPage);
        return this;
      } catch (error) {
        this.report(error);
        throw error;
      }
    }

    async load(url) {
      const response = await global.fetch(url, { headers: { Accept: "application/json" } });
      if (!response.ok) throw new RuntimeError("Unable to load runtime manifest: " + response.status);
      return response.json();
    }

    validateManifest(manifest) {
      if (!manifest || manifest.version !== "0.1") {
        throw new RuntimeError("Unsupported or missing ITL runtime manifest.");
      }
      if (!Array.isArray(manifest.pages) || manifest.pages.length === 0) {
        throw new RuntimeError("Runtime manifest contains no pages.");
      }
    }

    resolveInitialPage() {
      const requested = global.location.hash
        ? decodeURIComponent(global.location.hash.slice(1))
        : this.manifest.initialPage;
      return this.pages.has(requested) ? requested : this.manifest.initialPage;
    }

    navigate(name) {
      if (!this.pages.has(name)) throw new RuntimeError("Unknown ITL page: " + name);
      this.state.currentPage = name;
      global.history.pushState({ itlPage: name }, "", "#" + encodeURIComponent(name));
      this.render();
      this.emit("navigate", name);
    }

    bindEvents() {
      global.addEventListener("popstate", () => {
        this.state.currentPage = this.resolveInitialPage();
        this.render();
      });
      global.addEventListener("hashchange", () => {
        this.state.currentPage = this.resolveInitialPage();
        this.render();
      });
      this.root.addEventListener("click", (event) => {
        const target = event.target.closest("[data-itl-navigate]");
        if (target) {
          event.preventDefault();
          this.navigate(target.getAttribute("data-itl-navigate"));
        }
      });
    }

    render() {
      const page = this.pages.get(this.state.currentPage);
      if (!page) throw new RuntimeError("Unable to render page: " + this.state.currentPage);
      this.root.replaceChildren(this.renderPage(page));
      document.title = page.name;
    }

    renderPage(page) {
      const wrapper = document.createElement("main");
      wrapper.className = "itl-page";
      wrapper.dataset.itlPage = page.name;
      if (page.theme) wrapper.dataset.itlTheme = page.theme;

      const nav = document.createElement("nav");
      nav.className = "itl-navigation";
      for (const candidate of this.pages.keys()) {
        const link = document.createElement("a");
        link.href = "#" + encodeURIComponent(candidate);
        link.dataset.itlNavigate = candidate;
        link.textContent = candidate;
        nav.appendChild(link);
      }
      wrapper.appendChild(nav);

      if (page.intent) wrapper.appendChild(this.renderIntent(page.intent, "page-intent"));
      for (const component of page.components || []) {
        wrapper.appendChild(this.renderComponent(component));
      }
      return wrapper;
    }

    renderComponent(component) {
      if (component && Object.prototype.hasOwnProperty.call(component, "headline")) {
        return this.renderHero(component);
      }
      return this.renderSection(component);
    }

    renderHero(hero) {
      const section = document.createElement("section");
      section.className = "itl-hero";
      if (hero.image) {
        const image = document.createElement("img");
        image.src = this.assetManager.resolve(hero.image);
        image.alt = hero.name || "";
        image.addEventListener("error", () => this.report(new RuntimeError("Unable to load asset: " + hero.image), false));
        section.appendChild(image);
      }
      const title = document.createElement("h1");
      title.textContent = hero.headline || hero.name || "";
      section.appendChild(title);
      if (hero.subtitle) {
        const subtitle = document.createElement("p");
        subtitle.textContent = hero.subtitle;
        section.appendChild(subtitle);
      }
      if (hero.action) {
        const destination = this.findActionPage(hero.action);
        const button = document.createElement("button");
        button.textContent = hero.action;
        if (destination) button.dataset.itlNavigate = destination;
        else button.addEventListener("click", () => this.emit("action", hero.action));
        section.appendChild(button);
      }
      if (hero.intent) section.appendChild(this.renderIntent(hero.intent, "component-intent"));
      return section;
    }

    renderSection(sectionData) {
      const section = document.createElement("section");
      section.className = "itl-section";
      const heading = document.createElement("h2");
      heading.textContent = sectionData.name || "Section";
      section.appendChild(heading);
      if (sectionData.intent) section.appendChild(this.renderIntent(sectionData.intent, "component-intent"));
      for (const child of sectionData.children || []) section.appendChild(this.renderSection(child));
      return section;
    }

    renderIntent(intent, className) {
      const container = document.createElement("div");
      container.className = className;
      for (const line of String(intent).split(/\n+/).map((item) => item.trim()).filter(Boolean)) {
        const paragraph = document.createElement("p");
        paragraph.textContent = line;
        container.appendChild(paragraph);
      }
      return container;
    }

    findActionPage(action) {
      const normalized = String(action).toLowerCase();
      for (const name of this.pages.keys()) {
        if (normalized.includes(String(name).toLowerCase())) return name;
      }
      return null;
    }

    on(event, callback) {
      const listener = { event, callback };
      this.listeners.add(listener);
      return () => this.listeners.delete(listener);
    }

    emit(event, payload) {
      for (const listener of this.listeners) {
        if (listener.event === event) listener.callback(payload, this);
      }
    }

    report(error, render = true) {
      const normalized = error instanceof Error ? error : new RuntimeError(String(error));
      global.console.error(normalized);
      if (!render) return;
      const panel = document.createElement("pre");
      panel.className = "itl-runtime-error";
      panel.textContent = normalized.name + ": " + normalized.message;
      this.errorTarget.replaceChildren(panel);
    }
  }

  global.ITLBrowserRuntime = { BrowserRuntime, AssetManager, RuntimeError };
})(window);
