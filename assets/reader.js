(() => {
  const printButton = document.querySelector("[data-print]");
  printButton.hidden = false;
  printButton.addEventListener("click", () => window.print());

  const sections = [...document.querySelectorAll("section.chapter")];
  const toc = [...document.querySelectorAll("nav a[href^='#']")];
  const mobileMenu = document.querySelector(".mobile-nav details");
  mobileMenu.querySelector("nav").addEventListener("click", e => {
    if (e.target.closest("a")) mobileMenu.open = false;
  });
  mobileMenu.addEventListener("keydown", e => {
    if (e.key === "Escape") {
      mobileMenu.open = false;
      mobileMenu.querySelector("summary").focus();
    }
  });
  const progress = document.querySelector(".reading-progress");
  const meter = progress.querySelector("progress");
  const percentage = progress.querySelector("[data-percent]");
  progress.hidden = false;
  let previous = -1;
  let currentId = "";
  let updating = false;
  function updatePosition() {
    updating = false;
    const main = document.querySelector("article");
    const rect = main.getBoundingClientRect();
    const scrollable = Math.max(1, rect.height - window.innerHeight);
    const value = Math.max(0, Math.min(100, Math.round((-rect.top / scrollable) * 100)));
    if (value !== previous) {
      previous = value;
      meter.value = value;
      percentage.textContent = value + "%";
    }
    const position = Math.min(innerHeight * 0.27, 170);
    const active = sections.filter(el => el.getBoundingClientRect().top <= position).pop();
    const id = active ? active.id : "";
    if (id !== currentId) {
      currentId = id;
      for (const link of toc) {
        if (link.dataset.section === id) link.setAttribute("aria-current", "true");
        else link.removeAttribute("aria-current");
      }
    }
  }
  function queueUpdate() {
    if (!updating) {
      updating = true;
      requestAnimationFrame(updatePosition);
    }
  }
  addEventListener("scroll", queueUpdate, { passive: true });
  addEventListener("resize", queueUpdate);
  addEventListener("hashchange", queueUpdate);
  updatePosition();

  for (const figure of document.querySelectorAll("[data-recut]")) {
    const panels = [...figure.querySelectorAll("[data-step-panel]")];
    const menu = figure.querySelector(".step-nav");
    const actions = figure.querySelector(".step-actions");
    const tabs = [...menu.querySelectorAll("button")];
    const back = actions.querySelector("[data-prev]");
    const next = actions.querySelector("[data-next]");
    const status = actions.querySelector(".position");
    let selected = 0;
    function show(i, focus = false) {
      selected = Math.max(0, Math.min(tabs.length - 1, i));
      panels.forEach((p, k) => {
        p.hidden = k !== selected;
        p.setAttribute("role", "tabpanel");
        p.setAttribute("aria-labelledby", tabs[k].id);
      });
      tabs.forEach((tab, k) => {
        tab.classList.toggle("active", k === selected);
        tab.setAttribute("role", "tab");
        tab.setAttribute("aria-selected", String(k === selected));
        tab.tabIndex = k === selected ? 0 : -1;
      });
      status.textContent = (selected + 1) + " / " + tabs.length;
      back.disabled = selected === 0;
      next.disabled = selected === tabs.length - 1;
      if (focus) tabs[selected].focus();
    }
    tabs.forEach((tab, i) => tab.addEventListener("click", () => show(i)));
    menu.addEventListener("keydown", e => {
      const movement = { ArrowLeft: selected - 1, ArrowRight: selected + 1, Home: 0, End: tabs.length - 1 };
      if (!(e.key in movement)) return;
      e.preventDefault();
      show(movement[e.key], true);
    });
    back.addEventListener("click", () => show(selected - 1));
    next.addEventListener("click", () => show(selected + 1));
    menu.setAttribute("role", "tablist");
    menu.hidden = actions.hidden = false;
    show(0);
  }
})();
