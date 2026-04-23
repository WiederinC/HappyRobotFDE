const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";

const C = {
  bg:       "0B0F19",
  card:     "1A2035",
  border:   "2A3450",
  accent:   "3B82F6",   // blue
  warn:     "F59E0B",   // amber for branches
  success:  "10B981",   // green for end
  white:    "FFFFFF",
  dim:      "94A3B8",
  arrow:    "3B5BDB",
};

const slide = pres.addSlide();
slide.background = { color: C.bg };

// ── Title ──────────────────────────────────────────────────────────────
slide.addText("Agent Call Flow", {
  x: 0.4, y: 0.18, w: 9.2, h: 0.45,
  fontSize: 22, bold: true, color: C.white, fontFace: "Calibri",
  margin: 0,
});
slide.addText("How Alex handles every inbound carrier call", {
  x: 0.4, y: 0.62, w: 9.2, h: 0.28,
  fontSize: 11, color: C.dim, fontFace: "Calibri", margin: 0,
});

// ── Divider ────────────────────────────────────────────────────────────
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.4, y: 0.95, w: 9.2, h: 0.02,
  fill: { color: C.border }, line: { color: C.border },
});

// ── Helper fns ─────────────────────────────────────────────────────────
function card(x, y, w, h, num, title, body, accentColor) {
  const ac = accentColor || C.accent;
  // card bg
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w, h,
    fill: { color: C.card },
    line: { color: C.border, width: 0.5 },
  });
  // left accent bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x, y, w: 0.04, h,
    fill: { color: ac },
    line: { color: ac },
  });
  // number circle bg
  slide.addShape(pres.shapes.OVAL, {
    x: x + 0.12, y: y + 0.1, w: 0.28, h: 0.28,
    fill: { color: ac },
    line: { color: ac },
  });
  // number
  slide.addText(String(num), {
    x: x + 0.12, y: y + 0.1, w: 0.28, h: 0.28,
    fontSize: 9, bold: true, color: C.white,
    align: "center", valign: "middle", fontFace: "Calibri", margin: 0,
  });
  // title
  slide.addText(title, {
    x: x + 0.46, y: y + 0.08, w: w - 0.54, h: 0.24,
    fontSize: 10, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  // body
  slide.addText(body, {
    x: x + 0.46, y: y + 0.32, w: w - 0.54, h: h - 0.4,
    fontSize: 8.5, color: C.dim, fontFace: "Calibri", margin: 0,
  });
}

function arrow(x, y) {
  // horizontal arrow between cards
  slide.addShape(pres.shapes.LINE, {
    x, y, w: 0.14, h: 0,
    line: { color: C.accent, width: 1.5 },
  });
  // arrowhead chevron
  slide.addText("›", {
    x: x + 0.06, y: y - 0.1, w: 0.14, h: 0.2,
    fontSize: 11, color: C.accent, align: "left", margin: 0, fontFace: "Calibri",
  });
}

// ── Row 1 — main steps 1–4 ─────────────────────────────────────────────
const R1Y  = 1.08;
const CARDW = 2.05;
const CARDH = 1.08;
const GAP   = 0.22;
const STEP  = CARDW + GAP;
const X0    = 0.42;

card(X0 + 0*STEP, R1Y, CARDW, CARDH, 1, "GREET",
  "Say hello once.\nAsk for MC number.\nDo not call any tool yet.");

arrow(X0 + CARDW, R1Y + CARDH/2 - 0.02);

card(X0 + 1*STEP, R1Y, CARDW, CARDH, 2, "VERIFY + HISTORY",
  "Call verify_carrier &\ncarrier_history silently.\nIneligible → end call.");

arrow(X0 + 1*STEP + CARDW, R1Y + CARDH/2 - 0.02);

card(X0 + 2*STEP, R1Y, CARDW, CARDH, 3, "UNDERSTAND NEED",
  "Specific lane → Step 4\nOpen availability → Step 5\nDeadhead position → Step 4");

arrow(X0 + 2*STEP + CARDW, R1Y + CARDH/2 - 0.02);

card(X0 + 3*STEP, R1Y, CARDW, CARDH, 4, "SEARCH & PITCH",
  "Search silently. Pitch:\nrate · RPM · fuel net\n· details. Then wait.");

// ── Down arrow between rows ────────────────────────────────────────────
const MID_R1 = R1Y + CARDH;
const MID_R2 = 2.42;
const downX  = X0 + 3*STEP + CARDW/2;

slide.addShape(pres.shapes.LINE, {
  x: downX, y: MID_R1, w: 0, h: MID_R2 - MID_R1,
  line: { color: C.accent, width: 1.5 },
});
slide.addText("↓", {
  x: downX - 0.1, y: MID_R2 - 0.18, w: 0.22, h: 0.22,
  fontSize: 10, color: C.accent, align: "center", margin: 0, fontFace: "Calibri",
});

// ── Row 2 — main steps 5–8 (right to left layout) ─────────────────────
const R2Y = 2.42;

card(X0 + 3*STEP, R2Y, CARDW, CARDH, 5, "NEGOTIATE",
  "Up to 3 rounds.\nMax +10% loadboard rate.\nNever match directly.");

// left-pointing arrow
slide.addShape(pres.shapes.LINE, {
  x: X0 + 2*STEP + CARDW + 0.02, y: R2Y + CARDH/2,
  w: GAP - 0.04, h: 0,
  line: { color: C.accent, width: 1.5 },
});
slide.addText("‹", {
  x: X0 + 2*STEP + CARDW - 0.04, y: R2Y + CARDH/2 - 0.1,
  w: 0.14, h: 0.2,
  fontSize: 11, color: C.accent, align: "left", margin: 0, fontFace: "Calibri",
});

card(X0 + 2*STEP, R2Y, CARDW, CARDH, 6, "BOOK",
  'Collect email FIRST.\nCall book_load silently.\nSay "Locked in." on success.');

slide.addShape(pres.shapes.LINE, {
  x: X0 + 1*STEP + CARDW + 0.02, y: R2Y + CARDH/2,
  w: GAP - 0.04, h: 0,
  line: { color: C.accent, width: 1.5 },
});
slide.addText("‹", {
  x: X0 + 1*STEP + CARDW - 0.04, y: R2Y + CARDH/2 - 0.1,
  w: 0.14, h: 0.2,
  fontSize: 11, color: C.accent, align: "left", margin: 0, fontFace: "Calibri",
});

card(X0 + 1*STEP, R2Y, CARDW, CARDH, 7, "CONNECTING LOAD",
  "Search origin = delivery city.\nOffer if pickup > delivery.\nWait for response.");

slide.addShape(pres.shapes.LINE, {
  x: X0 + 0*STEP + CARDW + 0.02, y: R2Y + CARDH/2,
  w: GAP - 0.04, h: 0,
  line: { color: C.success, width: 1.5 },
});
slide.addText("‹", {
  x: X0 + 0*STEP + CARDW - 0.04, y: R2Y + CARDH/2 - 0.1,
  w: 0.14, h: 0.2,
  fontSize: 11, color: C.success, align: "left", margin: 0, fontFace: "Calibri",
});

card(X0 + 0*STEP, R2Y, CARDW, CARDH, 8, "RECORD & END",
  'Call record_call silently.\n"You\'re all set — safe travels."\nCall ends.', C.success);

// ── Branch paths ───────────────────────────────────────────────────────
const BY = 3.78;
const BW = 1.85;
const BH = 0.7;

// Ineligible branch (from step 2)
const b1x = X0 + 1*STEP + 0.1;
slide.addShape(pres.shapes.LINE, {
  x: b1x + BW/2, y: R1Y + CARDH, w: 0, h: BY - (R1Y + CARDH),
  line: { color: C.warn, width: 1, dashType: "dash" },
});
slide.addShape(pres.shapes.RECTANGLE, {
  x: b1x, y: BY, w: BW, h: BH,
  fill: { color: "1C1A0F" },
  line: { color: C.warn, width: 0.5 },
});
slide.addText("INELIGIBLE", {
  x: b1x + 0.08, y: BY + 0.06, w: BW - 0.1, h: 0.22,
  fontSize: 8.5, bold: true, color: C.warn, fontFace: "Calibri", margin: 0,
});
slide.addText("Decline politely.\nrecord_call → end.", {
  x: b1x + 0.08, y: BY + 0.28, w: BW - 0.1, h: 0.36,
  fontSize: 8, color: C.dim, fontFace: "Calibri", margin: 0,
});

// No loads → waitlist (from step 4)
const b2x = X0 + 3*STEP + 0.1;
slide.addShape(pres.shapes.LINE, {
  x: b2x + BW/2 - 0.1, y: R1Y + CARDH, w: 0, h: BY - (R1Y + CARDH),
  line: { color: C.warn, width: 1, dashType: "dash" },
});
slide.addShape(pres.shapes.RECTANGLE, {
  x: b2x - 0.1, y: BY, w: BW, h: BH,
  fill: { color: "1C1A0F" },
  line: { color: C.warn, width: 0.5 },
});
slide.addText("WAITLIST", {
  x: b2x - 0.02, y: BY + 0.06, w: BW - 0.1, h: 0.22,
  fontSize: 8.5, bold: true, color: C.warn, fontFace: "Calibri", margin: 0,
});
slide.addText("After 3 failed searches.\nadd_to_waitlist → end.", {
  x: b2x - 0.02, y: BY + 0.28, w: BW - 0.1, h: 0.36,
  fontSize: 8, color: C.dim, fontFace: "Calibri", margin: 0,
});

// Rate hold (from step 5)
const b3x = X0 + 2*STEP + 0.1;
slide.addShape(pres.shapes.LINE, {
  x: b3x + BW/2, y: R2Y + CARDH, w: 0, h: BY - (R2Y + CARDH),
  line: { color: C.warn, width: 1, dashType: "dash" },
});
slide.addShape(pres.shapes.RECTANGLE, {
  x: b3x, y: BY, w: BW, h: BH,
  fill: { color: "1C1A0F" },
  line: { color: C.warn, width: 0.5 },
});
slide.addText("RATE HOLD", {
  x: b3x + 0.08, y: BY + 0.06, w: BW - 0.1, h: 0.22,
  fontSize: 8.5, bold: true, color: C.warn, fontFace: "Calibri", margin: 0,
});
slide.addText("3 rounds, no deal.\nadd_to_waitlist → end.", {
  x: b3x + 0.08, y: BY + 0.28, w: BW - 0.1, h: 0.36,
  fontSize: 8, color: C.dim, fontFace: "Calibri", margin: 0,
});

// Circuit Planning note
const b4x = X0 + 0.1;
slide.addShape(pres.shapes.RECTANGLE, {
  x: b4x, y: BY, w: BW, h: BH,
  fill: { color: "0C1A1F" },
  line: { color: "0EA5E9", width: 0.5 },
});
slide.addShape(pres.shapes.RECTANGLE, {
  x: b4x, y: BY, w: 0.04, h: BH,
  fill: { color: "0EA5E9" },
  line: { color: "0EA5E9" },
});
slide.addText("CIRCUIT (Step 5)", {
  x: b4x + 0.12, y: BY + 0.06, w: BW - 0.2, h: 0.22,
  fontSize: 8.5, bold: true, color: "7DD3FC", fontFace: "Calibri", margin: 0,
});
slide.addText("Open availability.\nChain loads by RPM.", {
  x: b4x + 0.12, y: BY + 0.28, w: BW - 0.2, h: 0.36,
  fontSize: 8, color: C.dim, fontFace: "Calibri", margin: 0,
});

// ── Legend ─────────────────────────────────────────────────────────────
slide.addShape(pres.shapes.LINE, {
  x: 0.42, y: 5.3, w: 0.3, h: 0,
  line: { color: C.accent, width: 1.5 },
});
slide.addText("Main flow", {
  x: 0.76, y: 5.22, w: 1.0, h: 0.22,
  fontSize: 8, color: C.dim, fontFace: "Calibri", margin: 0,
});

slide.addShape(pres.shapes.LINE, {
  x: 1.8, y: 5.3, w: 0.3, h: 0,
  line: { color: C.warn, width: 1, dashType: "dash" },
});
slide.addText("Exception branch", {
  x: 2.14, y: 5.22, w: 1.3, h: 0.22,
  fontSize: 8, color: C.dim, fontFace: "Calibri", margin: 0,
});

slide.addShape(pres.shapes.LINE, {
  x: 3.5, y: 5.3, w: 0.3, h: 0,
  line: { color: C.success, width: 1.5 },
});
slide.addText("Success path", {
  x: 3.84, y: 5.22, w: 1.0, h: 0.22,
  fontSize: 8, color: C.dim, fontFace: "Calibri", margin: 0,
});

pres.writeFile({ fileName: "/Users/constantinwiederin/Documents/happyrobot-carrier/Agent_Call_Flow.pptx" });
console.log("Saved: Agent_Call_Flow.pptx");
