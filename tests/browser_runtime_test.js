const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

class Element {
  constructor(tag) {
    this.tagName = tag;
    this.children = [];
    this.dataset = {};
    this.className = "";
    this.textContent = "";
    this.listeners = {};
  }
  appendChild(child) { this.children.push(child); return child; }
  replaceChildren(...children) { this.children = children; }
  addEventListener(event, callback) { this.listeners[event] = callback; }
  closest(selector) {
    if (selector === "[data-itl-navigate]" && this.dataset.itlNavigate) return this;
    return null;
  }
  setAttribute(name, value) { this[name] = value; }
}

const document = {
  body: new Element("body"),
  title: "",
  createElement: (tag) => new Element(tag),
  getElementById: () => new Element("div"),
};
const listeners = {};
const windowObject = {
  document,
  location: { hash: "" },
  history: { pushState: (_state, _title, hash) => { windowObject.location.hash = hash; } },
  addEventListener: (event, callback) => { listeners[event] = callback; },
  fetch: async () => { throw new Error("fetch is not used in this test"); },
  console,
};

const source = fs.readFileSync("runtime/browser.js", "utf8");
vm.runInNewContext(source, { window: windowObject, document, console });
const { BrowserRuntime, AssetManager, RuntimeError } = windowObject.ITLBrowserRuntime;

const root = new Element("main");
const runtime = new BrowserRuntime({ root, assetRoot: "./assets/" });
const manifest = {
  version: "0.1",
  application: { name: "Demo", target: "web" },
  initialPage: "home",
  pages: [
    {
      name: "home",
      theme: "light",
      intent: "Welcome to the demo",
      components: [
        { name: "welcome", intent: "Intro", headline: "Hello", subtitle: "World", action: "Go catalog", image: "assets/hero.svg" },
        { name: "featured", intent: "Featured products", children: [] },
      ],
    },
    { name: "catalog", theme: "light", intent: "Catalog", components: [] },
  ],
};

(async () => {
  await runtime.start(manifest);
  assert.equal(runtime.state.currentPage, "home");
  assert.equal(root.children[0].dataset.itlPage, "home");
  assert.equal(document.title, "home");

  runtime.navigate("catalog");
  assert.equal(runtime.state.currentPage, "catalog");
  assert.equal(root.children[0].dataset.itlPage, "catalog");

  assert.throws(() => runtime.navigate("missing"), RuntimeError);
  assert.equal(new AssetManager("./assets/").resolve("hero.svg"), "./assets/hero.svg");
  assert.equal(new AssetManager().resolve("https://example.com/a.svg"), "https://example.com/a.svg");

  console.log("Browser runtime tests passed.");
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
