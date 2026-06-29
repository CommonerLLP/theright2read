/* RTR theme — persisted light/dark, respects system, no flash.
   Load in <head> (blocking) so the saved theme applies before first paint. */
(function () {
  var KEY = "rtr-theme";
  try {
    var saved = localStorage.getItem(KEY);
    if (saved) document.documentElement.setAttribute("data-theme", saved);
  } catch (e) {}
  function current() {
    return document.documentElement.getAttribute("data-theme")
      || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  }
  function paintLabels(mode) {
    document.querySelectorAll("[data-theme-label]").forEach(function (el) {
      el.textContent = mode === "dark" ? "☾" : "☀";
    });
  }
  window.RTRTheme = {
    current: current,
    set: function (mode) {
      document.documentElement.setAttribute("data-theme", mode);
      try { localStorage.setItem(KEY, mode); } catch (e) {}
      paintLabels(mode);
    },
    toggle: function () { this.set(current() === "dark" ? "light" : "dark"); }
  };
  document.addEventListener("DOMContentLoaded", function () { paintLabels(current()); });
})();
