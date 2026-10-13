/* Animation des Anlagenschemas (docs/img/anlage_schema.svg) auf der Doku-Webseite.
   Vereinfachte Veranschaulichung des Prinzips – kein Abbild des SPS-Programms:
   Pakete mit zufälligen Eigenschaften laufen über das Band, die Sensoren melden sie,
   an ST5 steht das Ziel fest, die Sortierer Q1–Q3 schieben sie in ihre Ausgänge, der Rest
   läuft in den Ausschuss. Zuschaltbare Störung "Sortierer Q2 klemmt" mit Quittierung. */
(function () {
  var X0 = 90, PX = 7;                     // Band: 0 % bei x = 90, 1 % = 7 px
  var BELT_Y = 150;                        // Bandmitte
  var SPEED = 5;                           // % pro Sekunde (0,5 m/s auf 10 m)
  var STATIONS = [2, 15, 25, 35, 45, 55];  // ST1..ST5, S6
  var DECIDE = 45;                         // ab ST5 steht das Ziel fest
  var SORTER_POS = [65, 75, 85];           // Q1..Q3
  var DROP_Y = 241;                        // Mitte der Ausgänge 1–3
  var END_X = 862;                         // Mitte von Ausgang 4
  var MAX_PACKAGES = 5;
  var reduceMotion = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  function fmtKg(w) { return w.toFixed(1).replace(".", ",") + " kg"; }
  function plural(n) { return n + (n === 1 ? " Paket" : " Pakete"); }

  function newPackage(id) {
    var metal = Math.random() < 0.3, big = Math.random() < 0.5;
    var weight = Math.round((0.3 + Math.random() * 5.4) * 10) / 10;
    var ok = Math.random() < 0.85;
    var target = 4, reason = "";
    if (!ok) reason = "beschädigt";
    else if (weight < 0.5) reason = "zu leicht";
    else if (weight > 5.0) reason = "zu schwer";
    else target = metal ? 1 : (big ? 3 : 2);
    return { id: id, metal: metal, big: big, weight: weight, ok: ok, target: target, reason: reason,
             p: 0, x: X0, y: BELT_Y, w: big ? 32 : 26, h: big ? 24 : 20,
             state: "belt", decided: false, fade: 1, el: null };
  }

  function init(box) {
    var svg = box.querySelector("svg");
    var layer = svg.querySelector(".s-layer");
    var mover = svg.querySelector(".s-mv");
    var sensors = svg.querySelectorAll(".s-sens");
    var cyls = svg.querySelectorAll(".s-cyl"), rods = svg.querySelectorAll(".s-rod");
    var counters = svg.querySelectorAll(".s-cnt");   // Ausgang 1, 2, 3, 4
    var h1 = svg.querySelector(".s-h1"), h2 = svg.querySelector(".s-h2");
    layer.querySelectorAll(".s-static").forEach(function (r) { r.remove(); });

    // Bedienleiste
    var bar = document.createElement("div");
    bar.className = "anim-ctl";
    bar.innerHTML =
      '<button type="button" data-act="run"></button>' +
      '<label><input type="checkbox" data-act="jam"> Störung: Sortierer Q2 klemmt</label>' +
      '<button type="button" data-act="ack" disabled>Quittieren</button>' +
      '<span class="anim-status" aria-live="polite"></span>';
    var info = document.createElement("p");
    info.className = "anim-info";
    info.textContent = "Ein Paket nach dem anderen kommt aufs Band …";
    box.appendChild(bar); box.appendChild(info);
    var btnRun = bar.querySelector('[data-act="run"]'), btnAck = bar.querySelector('[data-act="ack"]');
    var chkJam = bar.querySelector('[data-act="jam"]'), status = bar.querySelector(".anim-status");

    var packages = [], nextId = 1, count = [0, 0, 0, 0];
    var sorters = SORTER_POS.map(function (pos, i) {
      return { pos: pos, x: X0 + pos * PX, state: "idle", t: 0, pkg: null, rodLen: 16, rod: rods[i], cyl: cyls[i] };
    });
    var running = !reduceMotion, visible = false, last = null, looping = false;
    var spawnIn = 0.5, beltOffset = 0;
    var jam = false, fault = false, acked = false;

    function say(text, alarm) { status.textContent = text; status.classList.toggle("alarm", !!alarm); }
    function updateButtons() {
      btnRun.textContent = running ? "Pause" : "Start";
      btnAck.disabled = !fault;
    }
    function idleText() { say(running ? "Automatik läuft" : "Pause – Start drücken"); }

    function raiseFault() {
      fault = true; acked = false;
      say("Störung: Sortierer Q2 klemmt – Band steht. Erst Ursache beheben, dann quittieren.", true);
      updateButtons();
    }
    function clearFault() {
      fault = false; acked = false;
      idleText(); updateButtons();
    }

    btnRun.addEventListener("click", function () {
      running = !running; updateButtons();
      if (!fault) idleText();
      if (running) kick();
    });
    btnAck.addEventListener("click", function () {
      if (!fault) return;
      acked = true;
      if (!jam) clearFault();
      else say("Quittiert – die Ursache besteht noch: Häkchen „Sortierer Q2 klemmt“ entfernen.", true);
    });
    chkJam.addEventListener("change", function () {
      jam = chkJam.checked;
      if (!jam && fault) {
        if (acked) clearFault();
        else say("Ursache behoben – jetzt quittieren.", true);
      }
    });

    function flash(i) {
      var s = sensors[i];
      s.classList.add("on");
      setTimeout(function () { s.classList.remove("on"); }, 250);
    }

    function describe(pkg) {
      var text = "Paket " + pkg.id + ": " + (pkg.metal ? "Metall" : "Kunststoff") + ", " + (pkg.big ? "groß" : "klein") +
                 ", " + fmtKg(pkg.weight) + ", " + (pkg.ok ? "Qualität OK" : "beschädigt") + " → ";
      info.textContent = text + (pkg.target === 4 ? "Ausgang 4 – Ausschuss (" + pkg.reason + ")" : "Ausgang " + pkg.target);
    }

    function arrive(pkg) {
      count[pkg.target - 1]++;
      counters[pkg.target - 1].textContent = plural(count[pkg.target - 1]);
      pkg.state = "fade";
    }

    function step(dt) {
      var beltRuns = !fault;
      // neue Pakete am Einlauf
      if (beltRuns) {
        spawnIn -= dt;
        var onBelt = packages.filter(function (k) { return k.state === "belt"; });
        var lastPkg = packages[packages.length - 1];
        if (spawnIn <= 0 && onBelt.length < MAX_PACKAGES && (!lastPkg || lastPkg.p > 12 || lastPkg.state !== "belt")) {
          packages.push(newPackage(nextId++));
          spawnIn = 2.5 + Math.random() * 2;
        }
        beltOffset += SPEED * PX * dt;
      }
      packages.forEach(function (pkg) {
        if (pkg.state === "belt" && beltRuns) {
          var before = pkg.p;
          pkg.p += SPEED * dt;
          STATIONS.forEach(function (pos, i) { if (before < pos && pkg.p >= pos) flash(i); });
          if (before < DECIDE && pkg.p >= DECIDE) { pkg.decided = true; describe(pkg); }
          var s = sorters[pkg.target - 1];
          if (pkg.target <= 3 && s.state === "idle" && pkg.p >= s.pos && before < s.pos + 1) {
            pkg.p = s.pos; pkg.state = "push"; s.state = "out"; s.t = 0; s.pkg = pkg;
          }
          if (pkg.p >= 100) {
            pkg.state = "end";
            if (pkg.target !== 4) { pkg.target = 4; pkg.reason = "Sortierer war belegt"; }
          }
          pkg.x = X0 + pkg.p * PX;
        } else if (pkg.state === "drop") {
          pkg.y = Math.min(DROP_Y, pkg.y + 160 * dt);
          if (pkg.y >= DROP_Y) arrive(pkg);
        } else if (pkg.state === "end") {
          pkg.x = Math.min(END_X, pkg.x + SPEED * PX * dt);
          if (pkg.x >= END_X) arrive(pkg);
        } else if (pkg.state === "fade") {
          pkg.fade -= dt * 2.5;
          if (pkg.fade <= 0) pkg.state = "gone";
        }
      });
      // Sortierer: ausfahren, Paket vom Band schieben, einfahren
      sorters.forEach(function (s, i) {
        if (s.state === "out") {
          s.t += dt;
          var k = Math.min(1, s.t / 0.35);
          if (i === 1 && jam && k >= 0.4) { s.state = "stuck"; s.t = 0; }
          s.rodLen = 16 + 46 * k;
          var tip = 114 + s.rodLen;
          s.pkg.y = Math.max(BELT_Y, tip + s.pkg.h / 2);
          if (k >= 1) { s.pkg.state = "drop"; s.pkg = null; s.state = "back"; s.t = 0; }
        } else if (s.state === "stuck") {
          s.t += dt;
          if (!jam) { s.state = "out"; s.t = 0.4 * 0.35; }
          else if (s.t >= 1 && !fault) raiseFault();
        } else if (s.state === "back") {
          s.t += dt;
          s.rodLen = Math.max(16, 62 - 46 * s.t / 0.3);
          if (s.rodLen <= 16) s.state = "idle";
        }
      });
      packages = packages.filter(function (k) {
        if (k.state === "gone") { if (k.el) k.el.remove(); return false; }
        return true;
      });
    }

    function render(now) {
      packages.forEach(function (pkg) {
        if (!pkg.el) {
          pkg.el = document.createElementNS("http://www.w3.org/2000/svg", "rect");
          pkg.el.setAttribute("rx", "2");
          pkg.el.setAttribute("width", pkg.w); pkg.el.setAttribute("height", pkg.h);
          layer.appendChild(pkg.el);
        }
        pkg.el.setAttribute("class", "s-pkg s-p" + (pkg.decided ? pkg.target : 0));
        pkg.el.setAttribute("x", (pkg.x - pkg.w / 2).toFixed(1));
        pkg.el.setAttribute("y", (pkg.y - pkg.h / 2).toFixed(1));
        pkg.el.setAttribute("opacity", Math.max(0, pkg.fade).toFixed(2));
      });
      sorters.forEach(function (s, i) {
        s.rod.setAttribute("height", s.rodLen.toFixed(1));
        var alarm = i === 1 && (s.state === "stuck" || (fault && jam));
        s.rod.classList.toggle("alarm", alarm); s.cyl.classList.toggle("alarm", alarm);
      });
      mover.setAttribute("stroke-dashoffset", (-beltOffset).toFixed(1));
      var blink = Math.floor(now / 500) % 2 === 0;
      h1.classList.toggle("on", !fault && (running || blink));       // Dauerlicht = Automatik, Blinken = bereit
      h2.classList.toggle("on", fault && (acked || blink));          // Blinken = neu, Dauerlicht = quittiert
    }

    function frame(now) {
      if (!visible) { last = null; looping = false; return; }
      var dt = last === null ? 0 : Math.min(0.1, (now - last) / 1000);
      last = now;
      if (running) step(dt);
      render(now);
      requestAnimationFrame(frame);
    }
    function kick() { if (visible && !looping) { looping = true; requestAnimationFrame(frame); } }

    // nur rechnen, solange das Schema zu sehen ist
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        if (visible) kick();
      }).observe(box);
    } else { visible = true; kick(); }

    updateButtons(); idleText();
    render(performance.now());
  }

  document.querySelectorAll(".schema[data-anim]").forEach(init);
})();
