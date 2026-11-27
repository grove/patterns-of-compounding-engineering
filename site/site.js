/* Optional filtering. Every article remains reachable without JavaScript. */
(() => {
  const tools = document.querySelector(".catalog-tools");
  if (!tools) return;
  const input = document.querySelector("#pattern-search");
  const buttons = Array.from(document.querySelectorAll("[data-filter]"));
  const groups = Array.from(document.querySelectorAll(".pattern-group"));
  const status = document.querySelector("#filter-status");
  const empty = document.querySelector("#no-results");
  let filter = "all";

  function update() {
    const terms = input.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const group of groups) {
      let matches = 0;
      for (const row of group.querySelectorAll(".pattern-row")) {
        const show = (filter === "all" || group.dataset.group === filter) &&
          terms.every(term => row.dataset.search.includes(term));
        row.hidden = !show;
        if (show) matches += 1;
      }
      group.hidden = matches === 0;
      visible += matches;
    }
    status.hidden = filter === "all" && terms.length === 0;
    status.textContent = visible + (visible === 1 ? " pattern found" : " patterns found");
    empty.hidden = visible !== 0;
  }

  for (const button of buttons) {
    button.addEventListener("click", () => {
      filter = button.dataset.filter;
      for (const other of buttons) other.setAttribute("aria-pressed", String(other === button));
      update();
    });
  }
  input.addEventListener("input", update);
  tools.hidden = false;
})();

