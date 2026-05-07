#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Array Space Explorer v2 - 3D browser UI for N-dimensional arrays.
Features: sidebar with array list + delete, pipeline builder, fast WASD.
Run: python array_visualizer.py
"""

from __future__ import annotations

import argparse
import http.server
import socket
import threading
import time
import webbrowser

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Array Space Explorer</title>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #080810;
  --surface: rgba(15,15,24,0.97);
  --surface2: rgba(22,22,35,0.95);
  --border: rgba(255,255,255,0.09);
  --border2: rgba(255,255,255,0.15);
  --accent: #6374ff;
  --accent-dim: rgba(99,116,255,0.18);
  --green: #3bd48a;
  --red: #ff5555;
  --amber: #f0a020;
  --text: #dddad4;
  --muted: rgba(255,255,255,0.32);
  --mono: 'JetBrains Mono','Fira Code',monospace;
  --ui: 'Inter','Segoe UI',system-ui,sans-serif;
  --sidebar-w: 272px;
  --sidebar-min: 200px;
  --sidebar-max: 520px;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--ui);
  overflow: hidden;
  width: 100vw; height: 100vh;
  display: flex;
  user-select: none;
}

/* ======== SIDEBAR ======== */
#sidebar {
  width: var(--sidebar-w);
  flex-shrink: 0;
  background: var(--surface);
  border-right: 0.5px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  z-index: 10;
}

#sidebar-resizer {
  width: 6px;
  flex-shrink: 0;
  cursor: col-resize;
  background: transparent;
  position: relative;
  z-index: 11;
}
#sidebar-resizer::before{
  content:"";
  position:absolute;
  top:0; bottom:0; left:2px; right:2px;
  background: rgba(255,255,255,0.03);
  border-left: 0.5px solid rgba(255,255,255,0.06);
  border-right: 0.5px solid rgba(255,255,255,0.02);
}
#sidebar-resizer:hover::before{
  background: rgba(255,255,255,0.06);
}
#sidebar-resizer.dragging::before{
  background: rgba(99,116,255,0.18);
  border-left-color: rgba(99,116,255,0.35);
}

#sidebar-tabs {
  display: flex;
  border-bottom: 0.5px solid var(--border);
  flex-shrink: 0;
}
.stab {
  flex: 1; padding: 11px 4px; font-size: 11px; font-weight: 500;
  text-align: center; cursor: pointer; color: var(--muted);
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
  letter-spacing: 0.05em; text-transform: uppercase;
}
.stab.active { color: var(--accent); border-bottom-color: var(--accent); }

.tab-pane { display: none; flex-direction: column; flex: 1; overflow: hidden; min-height: 0; }
.tab-pane.active { display: flex; }

/* ---- Arrays tab ---- */
#array-add-bar {
  display: flex; gap: 4px; flex-wrap: wrap;
  padding: 10px 10px 8px; border-bottom: 0.5px solid var(--border);
  flex-shrink: 0;
}
.nd-btn {
  flex: 1; min-width: 28px;
  background: var(--accent-dim); border: 0.5px solid rgba(99,116,255,0.3);
  color: #a0abff; border-radius: 6px; padding: 5px 2px;
  font-size: 11px; font-family: var(--ui); cursor: pointer;
  transition: background 0.12s;
}
.nd-btn:hover { background: rgba(99,116,255,0.32); }

#custom-dim-row {
  display: flex; gap: 5px;
  padding: 7px 10px 8px; border-bottom: 0.5px solid var(--border);
  flex-shrink: 0;
}
#dim-input {
  flex: 1; background: rgba(0,0,0,0.35); border: 0.5px solid var(--border2);
  color: var(--text); border-radius: 6px; padding: 5px 8px;
  font-size: 11px; font-family: var(--mono); outline: none;
}
#dim-input:focus { border-color: var(--accent); }
#dim-input::placeholder { color: var(--muted); }

#array-list {
  flex: 1; overflow-y: auto; padding: 6px 8px; min-height: 0;
}
#array-list::-webkit-scrollbar { width: 4px; }
#array-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

.arr-item {
  display: flex; align-items: center; gap: 7px;
  padding: 7px 8px; border-radius: 8px; margin-bottom: 3px;
  cursor: pointer; border: 0.5px solid transparent;
  transition: background 0.1s, border-color 0.1s;
}
.arr-item:hover { background: rgba(255,255,255,0.04); }
.arr-item.active { background: var(--accent-dim); border-color: rgba(99,116,255,0.35); }

.arr-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 1px; }
.arr-info { flex: 1; min-width: 0; }
.arr-name { font-size: 12px; font-weight: 500; color: var(--text); }
.arr-meta { font-size: 10px; color: var(--muted); font-family: var(--mono); margin-top: 1px; }
.arr-del {
  width: 22px; height: 22px; border-radius: 5px; flex-shrink: 0;
  background: transparent; border: none; color: var(--muted);
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  font-size: 15px; line-height: 1; transition: background 0.1s, color 0.1s;
}
.arr-del:hover { background: rgba(255,85,85,0.18); color: var(--red); }

.arr-footer {
  display: flex; gap: 4px; flex-wrap: wrap;
  padding: 8px 10px; border-top: 0.5px solid var(--border);
  flex-shrink: 0;
}
.sm-btn {
  flex: 1; min-width: 48px;
  background: rgba(255,255,255,0.05); border: 0.5px solid var(--border2);
  color: var(--text); border-radius: 6px; padding: 5px 4px;
  font-size: 10px; font-family: var(--ui); cursor: pointer;
  transition: background 0.12s; white-space: nowrap; text-align: center;
}
.sm-btn:hover { background: rgba(255,255,255,0.11); }
.sm-btn.red:hover { background: rgba(255,85,85,0.18); color: var(--red); }

/* ---- Pipeline tab ---- */
#pipeline-tab { flex-direction: row; }
#pipeline-main { display: flex; flex-direction: column; flex: 1; min-width: 0; }

#pipe-header {
  padding: 10px 12px 8px; border-bottom: 0.5px solid var(--border); flex-shrink: 0;
}
#pipe-header p { font-size: 10px; color: var(--muted); line-height: 1.6; margin-top: 3px; }

.step-add-bar {
  display: flex; gap: 4px; flex-wrap: wrap;
  padding: 7px 8px; border-bottom: 0.5px solid var(--border);
  flex-shrink: 0;
}
.add-step-btn {
  background: rgba(255,255,255,0.04); border: 0.5px solid var(--border);
  color: var(--muted); border-radius: 6px; padding: 4px 7px;
  font-size: 10px; font-family: var(--ui); cursor: pointer;
  transition: all 0.12s; white-space: nowrap;
}
.add-step-btn:hover { background: rgba(255,255,255,0.1); color: var(--text); border-color: var(--border2); }

#step-list {
  flex: 1; overflow-y: auto; padding: 6px 8px; min-height: 0;
}
#step-list::-webkit-scrollbar { width: 4px; }
#step-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

.step-card {
  background: var(--surface2); border: 0.5px solid var(--border);
  border-radius: 9px; padding: 9px 10px; margin-bottom: 6px;
  transition: border-color 0.2s;
}
.step-card.running { border-color: var(--amber); }
.step-card.done    { border-color: rgba(59,212,138,0.4); }
.step-card.error   { border-color: rgba(255,85,85,0.4); }

.step-header { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
.step-num {
  width: 18px; height: 18px; border-radius: 50%;
  background: var(--accent-dim); border: 0.5px solid rgba(99,116,255,0.4);
  color: #a0abff; font-size: 10px; font-weight: 600;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.step-type { font-size: 11px; font-weight: 500; color: var(--text); flex: 1; }
.step-del {
  width: 18px; height: 18px; border-radius: 4px;
  background: transparent; border: none; color: var(--muted);
  cursor: pointer; font-size: 13px; display: flex; align-items: center; justify-content: center;
  transition: color 0.1s;
}
.step-del:hover { color: var(--red); }

.step-row { display: flex; align-items: center; gap: 5px; margin-bottom: 5px; }
.step-label { font-size: 10px; color: var(--muted); width: 40px; flex-shrink: 0; }
.step-select {
  flex: 1; background: rgba(0,0,0,0.35); border: 0.5px solid var(--border2);
  color: var(--text); border-radius: 5px; padding: 4px 7px;
  font-size: 10px; font-family: var(--mono); outline: none; cursor: pointer;
  appearance: none; -webkit-appearance: none;
}
.step-select:focus { border-color: var(--accent); }
.step-num-in {
  background: rgba(0,0,0,0.35); border: 0.5px solid var(--border2);
  color: var(--text); border-radius: 5px; padding: 4px 6px;
  font-size: 10px; font-family: var(--mono); outline: none; width: 60px;
}
.step-num-in:focus { border-color: var(--accent); }
.step-num-in.wide { width: 100%; }

.step-status { font-size: 10px; margin-top: 4px; min-height: 14px; }
.step-status.ok  { color: var(--green); }
.step-status.err { color: var(--red); }
.step-status.run { color: var(--amber); }

#pipe-controls {
  display: flex; gap: 5px; padding: 8px 10px;
  border-top: 0.5px solid var(--border); flex-shrink: 0;
}

/* Pipeline code drawer */
#pipe-code-drawer {
  width: 28px;
  flex-shrink: 0;
  position: relative;
  border-left: 0.5px solid var(--border);
  background: var(--surface);
  overflow: visible;
  transition: width 0.15s ease;
}
#pipe-code-drawer.open { width: 360px; }
#pipe-code-tab {
  position: absolute;
  left: 0; top: 12px;
  width: 28px; height: 72px;
  background: rgba(255,255,255,0.06);
  border: 0.5px solid var(--border);
  border-left: none;
  border-radius: 0 8px 8px 0;
  display: flex; align-items: center; justify-content: center;
  color: var(--muted);
  cursor: pointer;
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  user-select: none;
}
#pipe-code-tab:hover { color: var(--text); background: rgba(255,255,255,0.1); }
#pipe-code-drawer.open #pipe-code-tab { color: var(--accent); }
#pipe-code-panel { height: 100%; display: flex; flex-direction: column; }
#pipe-code-header {
  padding: 10px 10px 8px;
  border-bottom: 0.5px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  gap: 8px;
}
#pipe-code-drawer:not(.open) #pipe-code-panel { display: none; }
#pipe-code-title { font-size: 10px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--accent); }
#pipe-code-actions { display: flex; gap: 6px; }
.mini-btn {
  background: rgba(255,255,255,0.06);
  border: 0.5px solid rgba(255,255,255,0.12);
  color: var(--text);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 10px;
  font-family: var(--ui);
  cursor: pointer;
  transition: background 0.12s, border-color 0.12s;
}
.mini-btn:hover { background: rgba(255,255,255,0.11); border-color: rgba(255,255,255,0.18); }
#pipe-python {
  flex: 1;
  margin: 0;
  padding: 10px 10px 14px;
  overflow: auto;
  font-family: var(--mono);
  font-size: 10px;
  color: var(--text);
  line-height: 1.55;
  white-space: pre;
}
#pipe-python::-webkit-scrollbar { width: 6px; height: 6px; }
#pipe-python::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 4px; }

/* ---- Info tab ---- */
#info-tab { padding: 12px 14px; gap: 0; overflow-y: auto; }
.info-section { margin-bottom: 14px; }
.info-section-title {
  font-size: 10px; font-weight: 600; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--accent); margin-bottom: 8px;
}
.info-row { display: flex; justify-content: space-between; margin-bottom: 5px; }
.info-key { color: var(--muted); font-size: 11px; }
.info-val { color: var(--text); font-family: var(--mono); font-size: 11px; }
.info-divider { border: none; border-top: 0.5px solid var(--border); margin: 10px 0; }

/* ======== CANVAS AREA ======== */
#canvas-wrap { flex: 1; position: relative; overflow: hidden; }
canvas { display: block; width: 100%; height: 100%; }

/* floating toolbar */
#toolbar {
  position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 5px; align-items: center;
  background: var(--surface); border: 0.5px solid var(--border);
  border-radius: 10px; padding: 6px 10px;
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 24px rgba(0,0,0,0.5); z-index: 5; white-space: nowrap;
}
.btn {
  background: rgba(255,255,255,0.06); border: 0.5px solid rgba(255,255,255,0.12);
  color: var(--text); border-radius: 6px; padding: 4px 9px;
  font-size: 11px; font-family: var(--ui); cursor: pointer;
  transition: all 0.12s; white-space: nowrap;
}
.btn:hover { background: rgba(255,255,255,0.13); }
.btn.active { background: var(--accent-dim); border-color: var(--accent); color: #a0abff; }
.sep { width: 1px; height: 20px; background: var(--border); margin: 0 2px; }

/* cell panel */
#cell-panel {
  position: absolute; bottom: 12px; right: 12px;
  background: var(--surface); border: 0.5px solid rgba(99,116,255,0.3);
  border-radius: 10px; padding: 12px 14px;
  backdrop-filter: blur(12px); font-size: 11px;
  min-width: 200px; display: none; z-index: 5;
}
.panel-title {
  font-size: 10px; font-weight: 600; letter-spacing: 0.1em;
  text-transform: uppercase; color: var(--accent); margin-bottom: 8px;
}
#cell-input {
  width: 100%; background: rgba(0,0,0,0.4);
  border: 0.5px solid rgba(99,116,255,0.45); border-radius: 6px;
  color: #fff; padding: 5px 8px; font-size: 13px;
  font-family: var(--mono); outline: none; margin-top: 6px;
}
#cell-input:focus { border-color: var(--accent); }
.hint { font-size: 10px; color: var(--muted); margin-top: 5px; }

/* hints */
#hints {
  position: absolute; bottom: 12px; left: 12px;
  font-size: 10px; color: var(--muted); line-height: 2;
  pointer-events: none; z-index: 5;
}
#hints kbd {
  background: rgba(255,255,255,0.07); border: 0.5px solid rgba(255,255,255,0.14);
  border-radius: 3px; padding: 1px 5px; font-family: var(--mono);
  font-size: 10px; color: rgba(255,255,255,0.5);
}

/* crosshair */
#xhair {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
  width: 12px; height: 12px; pointer-events: none; opacity: 0.28; z-index: 4;
}
#xhair::before, #xhair::after { content:''; position:absolute; background:#fff; }
#xhair::before { width:1px; height:100%; left:50%; top:0; }
#xhair::after  { height:1px; width:100%; top:50%; left:0; }
</style>
</head>
<body>

<!-- ======== SIDEBAR ======== -->
<div id="sidebar">
  <div id="sidebar-tabs">
    <div class="stab active" onclick="showTab('arrays')">Arrays</div>
    <div class="stab" onclick="showTab('pipeline')">Pipeline</div>
    <div class="stab" onclick="showTab('info')">Info</div>
  </div>

  <!-- ARRAYS TAB -->
  <div class="tab-pane active" id="arrays-tab">
    <div id="array-add-bar">
      <button class="nd-btn" onclick="addArray(1)">1D</button>
      <button class="nd-btn" onclick="addArray(2)">2D</button>
      <button class="nd-btn" onclick="addArray(3)">3D</button>
      <button class="nd-btn" onclick="addArray(4)">4D</button>
      <button class="nd-btn" onclick="addArray(5)">5D</button>
    </div>
    <div id="custom-dim-row">
      <input id="dim-input" placeholder="e.g. 3×4×2" onkeydown="if(event.key==='Enter')addCustom()"/>
      <button class="sm-btn" onclick="addCustom()" style="flex:0;padding:5px 10px">+ Add</button>
    </div>
    <div id="array-list"></div>
    <div class="arr-footer">
      <button class="sm-btn" onclick="fillSel(0)">Fill 0s</button>
      <button class="sm-btn" onclick="fillSel('rand')">Rand</button>
      <button class="sm-btn" onclick="fillSel('idx')">Idx</button>
      <button class="sm-btn" onclick="snapSelected()">⊞ Snap</button>
      <button class="sm-btn red" onclick="deleteSel()">✕ Del</button>
    </div>
  </div>

  <!-- PIPELINE TAB -->
  <div class="tab-pane" id="pipeline-tab">
    <div id="pipeline-main">
      <div id="pipe-header">
        <div class="info-section-title" style="margin:0">Pipeline Builder</div>
        <p>Chain operations on arrays. Steps run top to bottom.</p>
      </div>
      <div class="step-add-bar">
        <button class="add-step-btn" onclick="addStep('snap-to')">⊞ Snap to</button>
        <button class="add-step-btn" onclick="addStep('align')">↔ Align</button>
        <button class="add-step-btn" onclick="addStep('copy-data')">⎘ Copy data</button>
        <button class="add-step-btn" onclick="addStep('fill')">▦ Fill</button>
        <button class="add-step-btn" onclick="addStep('reshape')">⬡ Reshape</button>
        <button class="add-step-btn" onclick="addStep('move-to')">→ Move to</button>
        <button class="add-step-btn" onclick="addStep('scale')">⤢ Scale</button>
        <button class="add-step-btn" onclick="addStep('delete')">✕ Delete</button>
      </div>
      <div id="step-list"></div>
    <div id="pipe-controls">
      <button class="sm-btn" onclick="runPipeline()"
        style="flex:2;background:rgba(59,212,138,0.1);border-color:rgba(59,212,138,0.3);color:var(--green)">▶ Run</button>
      <button class="sm-btn" onclick="togglePipeCode()">Code</button>
      <button class="sm-btn" onclick="copyPipeCode()">Copy</button>
      <button class="sm-btn" onclick="resetStepStatuses()">↺ Reset</button>
      <button class="sm-btn red" onclick="clearPipeline()">Clear</button>
    </div>
  </div>

    <div id="pipe-code-drawer">
      <div id="pipe-code-tab" onclick="togglePipeCode()">Code</div>
      <div id="pipe-code-panel">
        <div id="pipe-code-header">
          <div id="pipe-code-title">Python</div>
          <div id="pipe-code-actions">
            <button class="mini-btn" onclick="copyPipeCode()">Copy</button>
          </div>
        </div>
        <pre id="pipe-python"># Add steps in the Pipeline tab to see Python code here.</pre>
      </div>
    </div>
  </div>

  <!-- INFO TAB -->
  <div class="tab-pane" id="info-tab">
    <div class="info-section">
      <div class="info-section-title">Camera</div>
      <div class="info-row"><span class="info-key">X</span><span class="info-val" id="i-cx">0.0</span></div>
      <div class="info-row"><span class="info-key">Y</span><span class="info-val" id="i-cy">0.0</span></div>
      <div class="info-row"><span class="info-key">Zoom</span><span class="info-val" id="i-zoom">62</span></div>
      <div class="info-row"><span class="info-key">Pitch</span><span class="info-val" id="i-pitch">28°</span></div>
      <div class="info-row"><span class="info-key">Yaw</span><span class="info-val" id="i-yaw">-30°</span></div>
    </div>
    <hr class="info-divider"/>
    <div class="info-section">
      <div class="info-section-title">Selected</div>
      <div class="info-row"><span class="info-key">Name</span><span class="info-val" id="i-name">—</span></div>
      <div class="info-row"><span class="info-key">Dims</span><span class="info-val" id="i-dims">—</span></div>
      <div class="info-row"><span class="info-key">Shape</span><span class="info-val" id="i-shape">—</span></div>
      <div class="info-row"><span class="info-key">Elements</span><span class="info-val" id="i-els">—</span></div>
      <div class="info-row"><span class="info-key">Pos X</span><span class="info-val" id="i-ox">—</span></div>
      <div class="info-row"><span class="info-key">Pos Z</span><span class="info-val" id="i-oz">—</span></div>
    </div>
    <hr class="info-divider"/>
    <div class="info-section">
      <div class="info-section-title">Scene</div>
      <div class="info-row"><span class="info-key">Arrays</span><span class="info-val" id="i-count">0</span></div>
      <div class="info-row"><span class="info-key">Pipeline steps</span><span class="info-val" id="i-steps">0</span></div>
    </div>
  </div>
</div>

<div id="sidebar-resizer" title="Drag to resize sidebar"></div>

<!-- ======== CANVAS ======== -->
<div id="canvas-wrap">
  <canvas id="c"></canvas>
  <div id="xhair"></div>

  <div id="toolbar">
    <button id="lock-btn" class="btn" onclick="toggleLock()">🔓 Free cam</button>
    <div class="sep"></div>
    <button class="btn" onclick="resetCamera()">⌂ Reset</button>
    <button class="btn" onclick="focusSelected()">◎ Focus sel</button>
  </div>

  <div id="cell-panel">
    <div class="panel-title" id="cell-title">Cell</div>
    <div style="display:flex;justify-content:space-between;margin-bottom:2px">
      <span style="color:var(--muted);font-size:11px">Index</span>
      <span style="font-family:var(--mono);font-size:11px" id="cell-idx">—</span>
    </div>
    <input id="cell-input" type="text" placeholder="value" onkeydown="commitCell(event)"/>
    <div class="hint">Enter to confirm · Esc to cancel</div>
  </div>

  <div id="hints">
    <kbd>WASD</kbd> move &nbsp;<kbd>Q</kbd><kbd>E</kbd> up/dn &nbsp;<kbd>drag</kbd> orbit &nbsp;<kbd>scroll</kbd> zoom<br>
    <kbd>shift+drag</kbd> move array &nbsp;<kbd>click</kbd> select/edit cell
  </div>
</div>

<script>
// ================================================================
//  CORE STATE
// ================================================================
const canvas = document.getElementById('c');
const ctx    = canvas.getContext('2d');

let cam = { x:0, y:0, z:0, zoom:62, pitch:28, yaw:-30 };
let keys = {};
let arrays = [], nextId = 1;
let sel = null, selCell = null;
let locked = false, hovered = null;

// drag
let dragMoved=false, dragStart={x:0,y:0}, dragMode='';
let orbitSnap={pitch:0,yaw:0}, moveArr=null, moveSnap={};

// pipeline
let pipeSteps = [], nextStepId = 1;
let pipeCodeOpen = false;

// ================================================================
//  RESIZE
// ================================================================
function resize() {
  const w = document.getElementById('canvas-wrap');
  canvas.width  = w.offsetWidth  * devicePixelRatio;
  canvas.height = w.offsetHeight * devicePixelRatio;
}
resize();
window.addEventListener('resize', resize);

// ================================================================
//  RESIZABLE SIDEBAR
// ================================================================
const SIDEBAR_KEY = 'av.sidebarWidth';
const sidebar = document.getElementById('sidebar');
const sidebarResizer = document.getElementById('sidebar-resizer');

function clamp(n, lo, hi){ return Math.max(lo, Math.min(hi, n)); }

function applySidebarWidth(px){
  const root = document.documentElement;
  const styles = getComputedStyle(root);
  const minW = parseInt(styles.getPropertyValue('--sidebar-min')) || 200;
  const maxW = parseInt(styles.getPropertyValue('--sidebar-max')) || 520;
  const w = clamp(Math.round(px), minW, maxW);
  root.style.setProperty('--sidebar-w', w + 'px');
  // canvas size depends on layout
  resize();
}

// restore
try{
  const saved = parseInt(localStorage.getItem(SIDEBAR_KEY) || '', 10);
  if(Number.isFinite(saved)) applySidebarWidth(saved);
}catch(e){}

let resizingSidebar = false;
let sidebarStartX = 0;
let sidebarStartW = 0;

if(sidebarResizer){
  sidebarResizer.addEventListener('mousedown', (e)=>{
    if(e.button !== 0) return;
    resizingSidebar = true;
    sidebarStartX = e.clientX;
    sidebarStartW = sidebar.getBoundingClientRect().width;
    sidebarResizer.classList.add('dragging');
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    e.preventDefault();
  });
}

window.addEventListener('mousemove', (e)=>{
  if(!resizingSidebar) return;
  const dx = e.clientX - sidebarStartX;
  applySidebarWidth(sidebarStartW + dx);
});

window.addEventListener('mouseup', ()=>{
  if(!resizingSidebar) return;
  resizingSidebar = false;
  if(sidebarResizer) sidebarResizer.classList.remove('dragging');
  document.body.style.cursor = '';
  document.body.style.userSelect = '';
  try{
    const root = document.documentElement;
    const cur = parseInt(getComputedStyle(root).getPropertyValue('--sidebar-w')) || 272;
    localStorage.setItem(SIDEBAR_KEY, String(cur));
  }catch(e){}
});

// ================================================================
//  PALETTE
// ================================================================
const PALETTE=['#6374ff','#3bd48a','#e86030','#3bb8d4','#d454a0','#f0a020','#aa88ff','#ff9955','#5dcaa5','#cc6688'];

// ================================================================
//  PROJECTION
// ================================================================
function project(x,y,z){
  const py=cam.pitch*Math.PI/180, pw=cam.yaw*Math.PI/180;
  // Camera translation (world-space) then yaw/pitch rotation
  const dx=x-cam.x, dy=y-cam.y, dz=z-cam.z;
  const rx= dx*Math.cos(pw)-dz*Math.sin(pw);
  const rz0=dx*Math.sin(pw)+dz*Math.cos(pw);
  const ry= dy*Math.cos(py)-rz0*Math.sin(py);
  const rz= dy*Math.sin(py)+rz0*Math.cos(py);
  const s=cam.zoom*devicePixelRatio;
  return {x:canvas.width/2+rx*s, y:canvas.height/2+ry*s, z:rz};
}

// ================================================================
//  LAYOUT
// ================================================================
const C=1.0, G=0.18;
function layout(arr){
  const d=arr.dims,nd=d.length,cells=[],step=C+G;
  if(nd===1){for(let i=0;i<d[0];i++)cells.push({idx:[i],wx:i*step,wy:0,wz:0});}
  else if(nd===2){for(let r=0;r<d[0];r++)for(let c=0;c<d[1];c++)cells.push({idx:[r,c],wx:c*step,wy:-r*step,wz:0});}
  else if(nd===3){for(let k=0;k<d[0];k++)for(let r=0;r<d[1];r++)for(let c=0;c<d[2];c++)cells.push({idx:[k,r,c],wx:c*step,wy:-r*step,wz:k*step*1.5});}
  else if(nd===4){const W=d[2]*step;for(let b=0;b<d[0];b++)for(let k=0;k<d[1];k++)for(let r=0;r<d[2];r++)for(let c=0;c<d[3];c++)cells.push({idx:[b,k,r,c],wx:b*(W+1.8)+c*step,wy:-r*step,wz:k*step*1.5});}
  else if(nd===5){const W=d[3]*step,H=d[2]*step;for(let s5=0;s5<d[0];s5++)for(let b=0;b<d[1];b++)for(let k=0;k<d[2];k++)for(let r=0;r<d[3];r++)for(let c=0;c<d[4];c++)cells.push({idx:[s5,b,k,r,c],wx:b*(W+1.8)+c*step,wy:-s5*(H+1.8)-r*step,wz:k*step*1.5});}
  return cells;
}

function flatIdx(arr,idx){let i=0,stride=1;for(let d=arr.dims.length-1;d>=0;d--){i+=idx[d]*stride;stride*=arr.dims[d];}return i;}
function totalEls(dims){return dims.reduce((a,b)=>a*b,1);}

function arrayBounds(arr){
  const cells=layout(arr);
  let minX=Infinity,maxX=-Infinity,minZ=Infinity,maxZ=-Infinity,minY=Infinity,maxY=-Infinity;
  for(const c of cells){
    const wx=arr.ox+c.wx,wy=arr.oy+c.wy,wz=arr.oz+c.wz;
    minX=Math.min(minX,wx);maxX=Math.max(maxX,wx+C);
    minY=Math.min(minY,wy-C);maxY=Math.max(maxY,wy);
    minZ=Math.min(minZ,wz);maxZ=Math.max(maxZ,wz+C);
  }
  return{minX,maxX,minY,maxY,minZ,maxZ,w:maxX-minX,h:maxY-minY,d:maxZ-minZ,cx:(minX+maxX)/2,cy:(minY+maxY)/2,cz:(minZ+maxZ)/2};
}

// ================================================================
//  ARRAY MANAGEMENT
// ================================================================
const DEFAULTS={1:[7],2:[4,5],3:[3,3,4],4:[2,2,3,3],5:[2,2,2,3,3]};

function addArray(nd,dims){
  const d=dims||DEFAULTS[nd]||[3];
  const n=totalEls(d);
  const arr={id:nextId++,dims:d,data:new Array(n).fill(0),
    ox:(arrays.length%4)*16-14, oy:0, oz:Math.floor(arrays.length/4)*-18,
    color:PALETTE[arrays.length%PALETTE.length], name:'arr'+(nextId-1)};
  arrays.push(arr);
  sel=arr; selCell=null;
  renderArrayList(); refreshStepSelects(); updateUI();
}

function addCustom(){
  const s=document.getElementById('dim-input').value.trim();
  if(!s)return;
  const dims=s.split(/[×x,\s]+/).map(Number).filter(n=>n>0&&n<64);
  if(!dims.length||dims.length>5){alert('1–5 dimensions, each 1–63');return;}
  addArray(dims.length,dims);
  document.getElementById('dim-input').value='';
}

function deleteArray(id){
  const a=arrays.find(a=>a.id===id);
  if(!a)return;
  arrays=arrays.filter(a=>a.id!==id);
  if(sel&&sel.id===id)sel=arrays.length?arrays[arrays.length-1]:null;
  selCell=null;
  renderArrayList(); refreshStepSelects(); updateUI();
}

function deleteSel(){if(sel)deleteArray(sel.id);}

function fillSel(mode){
  if(!sel)return;
  for(let i=0;i<sel.data.length;i++){
    if(mode==='rand')sel.data[i]=+(Math.random()*10).toFixed(2);
    else if(mode==='idx')sel.data[i]=i;
    else sel.data[i]=0;
  }
}

function snapSelected(){if(!sel)return;sel.ox=Math.round(sel.ox);sel.oy=Math.round(sel.oy);sel.oz=Math.round(sel.oz);}
function toggleLock(){locked=!locked;const b=document.getElementById('lock-btn');b.textContent=locked?'🔒 Locked':'🔓 Free cam';b.classList.toggle('active',locked);}
function resetCamera(){cam={x:0,y:0,z:0,zoom:62,pitch:28,yaw:-30};}
function focusSelected(){if(!sel)return;const b=arrayBounds(sel);cam.x=b.cx;cam.y=b.cy;cam.z=b.cz;cam.zoom=60;}

// ================================================================
//  SIDEBAR TABS
// ================================================================
function showTab(name){
  const names=['arrays','pipeline','info'];
  document.querySelectorAll('.stab').forEach((t,i)=>t.classList.toggle('active',names[i]===name));
  document.querySelectorAll('.tab-pane').forEach((p,i)=>p.classList.toggle('active',names[i]+'-tab'===name+'-tab'));
}

function renderArrayList(){
  const list=document.getElementById('array-list');
  list.innerHTML='';
  for(const arr of [...arrays].reverse()){
    const div=document.createElement('div');
    div.className='arr-item'+(arr===sel?' active':'');
    div.innerHTML=`
      <div class="arr-dot" style="background:${arr.color}"></div>
      <div class="arr-info">
        <div class="arr-name">${arr.name}</div>
        <div class="arr-meta">${arr.dims.join('×')} &nbsp;·&nbsp; ${totalEls(arr.dims).toLocaleString()} els &nbsp;·&nbsp; ${arr.dims.length}D</div>
      </div>
      <button class="arr-del" title="Delete array" onclick="event.stopPropagation();deleteArray(${arr.id})">×</button>
    `;
    div.onclick=()=>{sel=arr;selCell=null;renderArrayList();updateUI();};
    list.appendChild(div);
  }
}

// ================================================================
//  PIPELINE
// ================================================================
const STEP_DEFS={
  'snap-to':   {label:'⊞ Snap to array', fields:['src','tgt','axis']},
  'align':     {label:'↔ Align edge',    fields:['src','tgt','edge']},
  'copy-data': {label:'⎘ Copy data',     fields:['src','tgt']},
  'fill':      {label:'▦ Fill value',    fields:['src','fillval']},
  'reshape':   {label:'⬡ Reshape',       fields:['src','newshape']},
  'move-to':   {label:'→ Move to X,Z',  fields:['src','movex','movez']},
  'scale':     {label:'⤢ Scale data',   fields:['src','scaleval']},
  'delete':    {label:'✕ Delete array',  fields:['src']},
};

function addStep(type){
  const src0 = arrays[0]?.id ?? null;
  const tgt0 = arrays[1]?.id ?? arrays[0]?.id ?? null;
  const srcArr = src0 != null ? arrays.find(a => a.id === src0) : null;
  const defaults = { src: src0 };
  if(type==='snap-to') Object.assign(defaults, { src: src0, tgt: tgt0, axis: 'x+' });
  else if(type==='align') Object.assign(defaults, { src: src0, tgt: tgt0, edge: 'left' });
  else if(type==='copy-data') Object.assign(defaults, { src: src0, tgt: tgt0 });
  else if(type==='fill') Object.assign(defaults, { src: src0, fillval: '0' });
  else if(type==='reshape') Object.assign(defaults, { src: src0, newshape: (srcArr ? srcArr.dims.join('×') : '') });
  else if(type==='move-to') Object.assign(defaults, { src: src0, movex: 0, movez: 0 });
  else if(type==='scale') Object.assign(defaults, { src: src0, scaleval: 1 });
  else if(type==='delete') Object.assign(defaults, { src: src0 });

  pipeSteps.push({id:nextStepId++,type,params:defaults,status:'',msg:''});
  renderPipeline(); showTab('pipeline');
}
function removeStep(id){pipeSteps=pipeSteps.filter(s=>s.id!==id);renderPipeline();}
function clearPipeline(){pipeSteps=[];renderPipeline();}
function resetStepStatuses(){pipeSteps.forEach(s=>{s.status='';s.msg='';});renderPipeline();}
function refreshStepSelects(){renderPipeline();}

function arrOptions(selected){
  return arrays.map(a=>`<option value="${a.id}"${a.id==selected?' selected':''}>${a.name} [${a.dims.join('×')}]</option>`).join('');
}

function renderPipeline(){
  const list=document.getElementById('step-list');
  list.innerHTML='';
  pipeSteps.forEach((step,idx)=>{
    const def=STEP_DEFS[step.type];
    if(!def)return;
    const p=step.params;
    let fields='';

    if(def.fields.includes('src'))
      fields+=`<div class="step-row"><span class="step-label">Array</span><select class="step-select" onchange="upParam(${step.id},'src',+this.value)">${arrOptions(p.src)}</select></div>`;
    if(def.fields.includes('tgt'))
      fields+=`<div class="step-row"><span class="step-label">Target</span><select class="step-select" onchange="upParam(${step.id},'tgt',+this.value)">${arrOptions(p.tgt)}</select></div>`;
    if(def.fields.includes('axis')){
      const ax=p.axis||'x+';
      fields+=`<div class="step-row"><span class="step-label">Side</span><select class="step-select" onchange="upParam(${step.id},'axis',this.value)">${['x+','x-','z+','z-'].map(v=>`<option${ax===v?' selected':''}>${v}</option>`).join('')}</select></div>`;
    }
    if(def.fields.includes('edge')){
      const ed=p.edge||'left';
      fields+=`<div class="step-row"><span class="step-label">Edge</span><select class="step-select" onchange="upParam(${step.id},'edge',this.value)">${['left','right','front','back','top','bottom'].map(v=>`<option${ed===v?' selected':''}>${v}</option>`).join('')}</select></div>`;
    }
    if(def.fields.includes('fillval'))
      fields+=`<div class="step-row"><span class="step-label">Value</span><input class="step-num-in wide" type="text" placeholder="0 / rand / idx" value="${p.fillval||''}" onchange="upParam(${step.id},'fillval',this.value)"/></div>`;
    if(def.fields.includes('newshape'))
      fields+=`<div class="step-row"><span class="step-label">Shape</span><input class="step-num-in wide" type="text" placeholder="e.g. 2×3×4" value="${p.newshape||''}" onchange="upParam(${step.id},'newshape',this.value)"/></div>`;
    if(def.fields.includes('movex'))
      fields+=`<div class="step-row"><span class="step-label">X</span><input class="step-num-in" type="number" placeholder="0" value="${p.movex||0}" onchange="upParam(${step.id},'movex',+this.value)"/><span class="step-label" style="width:16px;text-align:center">Z</span><input class="step-num-in" type="number" placeholder="0" value="${p.movez||0}" onchange="upParam(${step.id},'movez',+this.value)"/></div>`;
    if(def.fields.includes('scaleval'))
      fields+=`<div class="step-row"><span class="step-label">Factor</span><input class="step-num-in" type="number" step="0.1" placeholder="1.0" value="${p.scaleval!=null?p.scaleval:1}" onchange="upParam(${step.id},'scaleval',+this.value)"/></div>`;

    const sc=step.status==='ok'?'done':step.status==='err'?'error':step.status==='run'?'running':'';
    const msgc=step.status==='ok'?'ok':step.status==='err'?'err':step.status==='run'?'run':'';
    const div=document.createElement('div');
    div.className=`step-card ${sc}`;
    div.innerHTML=`
      <div class="step-header">
        <div class="step-num">${idx+1}</div>
        <div class="step-type">${def.label}</div>
        <button class="step-del" onclick="removeStep(${step.id})">×</button>
      </div>
      ${fields}
      <div class="step-status ${msgc}">${step.msg||''}</div>
    `;
    list.appendChild(div);
  });
  document.getElementById('i-steps').textContent=pipeSteps.length;
  renderPipelineCode();
}

function upParam(sid,key,val){
  const s=pipeSteps.find(s=>s.id===sid);
  if(s){s.params[key]=val;s.status='';s.msg='';renderPipeline();}
}

function togglePipeCode(force){
  const drawer=document.getElementById('pipe-code-drawer');
  if(!drawer) return;
  pipeCodeOpen = (force==null) ? !pipeCodeOpen : !!force;
  drawer.classList.toggle('open', pipeCodeOpen);
  renderPipelineCode();
}

function copyPipeCode(){
  const el=document.getElementById('pipe-python');
  if(!el) return;
  const txt=el.textContent||'';
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(txt).catch(()=>{});
    return;
  }
  // Fallback for older browsers / blocked clipboard API.
  const ta=document.createElement('textarea');
  ta.value=txt;
  ta.style.position='fixed';
  ta.style.left='-9999px';
  ta.style.top='0';
  document.body.appendChild(ta);
  ta.focus();
  ta.select();
  try{document.execCommand('copy');}catch(e){}
  document.body.removeChild(ta);
}

function renderPipelineCode(){
  const el=document.getElementById('pipe-python');
  if(!el) return;
  el.textContent = buildPipePythonCode();
}

function pyIdent(s){
  const cleaned = String(s||'arr').replace(/[^a-zA-Z0-9_]/g,'_');
  const ident = cleaned.match(/^[a-zA-Z_]/) ? cleaned : ('arr_'+cleaned);
  return ident || 'arr';
}

function buildPipePythonCode(){
  if(!pipeSteps.length){
    return "# Add steps in the Pipeline tab to see Python code here.";
  }

  // Map ids -> names
  const byId = new Map(arrays.map(a => [a.id, a]));
  const names = new Map();
  for(const a of arrays){
    const base = pyIdent(a.name);
    let n = base, k = 2;
    while([...names.values()].includes(n)) { n = `${base}_${k++}`; }
    names.set(a.id, n);
  }

  const lines=[];
  lines.push("# Generated from Array Space Explorer pipeline");
  lines.push("from __future__ import annotations");
  lines.push("");
  lines.push("import numpy as np");
  lines.push("");

  // Declare arrays used in the pipeline (numpy-only: you can replace these with your real arrays)
  lines.push("# Provide your arrays here (replace np.zeros(...) with your real data):");
  const usedIds = new Set();
  for(const st of pipeSteps){
    const p = st.params || {};
    if(p.src != null) usedIds.add(p.src);
    if(p.tgt != null) usedIds.add(p.tgt);
  }
  for(const id of usedIds){
    const a = byId.get(id);
    if(!a) continue;
    const varName = names.get(id) || `arr_${id}`;
    let shape = a.dims.join(", ");
    if(a.dims.length === 1) shape = shape + ",";
    lines.push(`${varName} = np.zeros((${shape}), dtype=float)  # ${a.name}`);
  }
  lines.push("");
  lines.push("def snap_concat(src: np.ndarray, tgt: np.ndarray, side: str = 'x+', fill: float = 0.0) -> np.ndarray:");
  lines.push("    \"\"\"");
  lines.push("    Theoretical 'snap-to' as numpy array math:");
  lines.push("    - x+/x- concatenates along the last axis");
  lines.push("    - z+/z- concatenates along the first axis");
  lines.push("    - other axes are padded with `fill` so shapes line up");
  lines.push("    Returns the combined array (tgt with src snapped to the requested side).");
  lines.push("    \"\"\"");
  lines.push("    if src.ndim != tgt.ndim:");
  lines.push("        raise ValueError('src and tgt must have same ndim for snap_concat')");
  lines.push("    nd = src.ndim");
  lines.push("    if nd < 1:");
  lines.push("        raise ValueError('ndim must be >= 1')");
  lines.push("    if side in ('x+','x-'):");
  lines.push("        ax = nd - 1");
  lines.push("    elif side in ('z+','z-'):");
  lines.push("        ax = 0");
  lines.push("    else:");
  lines.push("        raise ValueError(\"side must be one of 'x+','x-','z+','z-'\")");
  lines.push("");
  lines.push("    # Pad all non-concat axes to the max shape so concat is valid.");
  lines.push("    max_shape = [max(src.shape[i], tgt.shape[i]) for i in range(nd)]");
  lines.push("");
  lines.push("    def _pad_to(a: np.ndarray) -> np.ndarray:");
  lines.push("        pad = []");
  lines.push("        for i in range(nd):");
  lines.push("            before = 0");
  lines.push("            after = max_shape[i] - a.shape[i]");
  lines.push("            pad.append((before, after))");
  lines.push("        return np.pad(a, pad, mode='constant', constant_values=fill)");
  lines.push("");
  lines.push("    src2 = _pad_to(src)");
  lines.push("    tgt2 = _pad_to(tgt)");
  lines.push("    if side in ('x+','z+'):");
  lines.push("        return np.concatenate([tgt2, src2], axis=ax)");
  lines.push("    else:");
  lines.push("        return np.concatenate([src2, tgt2], axis=ax)");
  lines.push("");
  lines.push("# Pipeline:");
  for(const [i, st] of pipeSteps.entries()){
    const p = st.params || {};
    const srcName = (p.src != null && names.get(p.src)) ? names.get(p.src) : null;
    const tgtName = (p.tgt != null && names.get(p.tgt)) ? names.get(p.tgt) : null;
    const stepNum = i + 1;
    if(st.type === 'snap-to'){
      lines.push(`# ${stepNum}. snap-to`);
      if(!srcName || !tgtName) lines.push("#   (select src/target)");
      else {
        lines.push(`# ${srcName} snapped to ${p.axis||'x+'} of ${tgtName}`);
        lines.push(`${tgtName}_snapped = snap_concat(${srcName}, ${tgtName}, side=${JSON.stringify(p.axis||'x+')}, fill=0.0)`);
      }
    } else if(st.type === 'align'){
      lines.push(`# ${stepNum}. align`);
      if(!srcName || !tgtName) lines.push("#   (select src/target)");
      else lines.push(`# Spatial align (${srcName} to ${tgtName}, edge=${p.edge||'left'}) has no direct numpy equivalent without defining a canvas/grid.`);
    } else if(st.type === 'copy-data'){
      lines.push(`# ${stepNum}. copy-data`);
      if(!srcName || !tgtName) lines.push("#   (select src/target)");
      else {
        lines.push(`# Copy up to the smaller array size (matches viewer behavior):`);
        lines.push(`_n = min(${srcName}.size, ${tgtName}.size)`);
        lines.push(`${tgtName}.ravel()[:_n] = ${srcName}.ravel()[:_n]`);
      }
    } else if(st.type === 'fill'){
      lines.push(`# ${stepNum}. fill`);
      if(!srcName) lines.push("#   (select array)");
      else {
        const v = (p.fillval ?? '0');
        const vv = String(v).trim();
        if(vv === 'rand') lines.push(`${srcName} = np.random.random(${srcName}.shape) * 10.0`);
        else if(vv === 'idx') lines.push(`${srcName} = np.arange(${srcName}.size, dtype=float).reshape(${srcName}.shape)`);
        else lines.push(`${srcName}.fill(${vv || '0'})`);
      }
    } else if(st.type === 'reshape'){
      lines.push(`# ${stepNum}. reshape`);
      if(!srcName) lines.push("#   (select array)");
      else {
        const dims = String(p.newshape||'').split(/[×x,\\s]+/).map(x=>parseInt(x,10)).filter(n=>Number.isFinite(n)&&n>0);
        if(!dims.length) lines.push(`# ${srcName} = ${srcName}.reshape((...))  # TODO: set shape`);
        else {
          let tup = dims.join(", ");
          if(dims.length === 1) tup = tup + ",";
          lines.push(`# Truncate/pad with zeros (matches viewer behavior):`);
          lines.push(`_flat = ${srcName}.ravel()`);
          lines.push(`_tmp = np.zeros(int(np.prod((${tup}))), dtype=${srcName}.dtype)`);
          lines.push(`_m = min(_flat.size, _tmp.size)`);
          lines.push(`_tmp[:_m] = _flat[:_m]`);
          lines.push(`${srcName} = _tmp.reshape((${tup}))`);
        }
      }
    } else if(st.type === 'move-to'){
      lines.push(`# ${stepNum}. move-to`);
      if(!srcName) lines.push("#   (select array)");
      else lines.push(`# Spatial move-to (${srcName} x=${+(p.movex||0)}, z=${+(p.movez||0)}) is view-positioning, not numpy math.`);
    } else if(st.type === 'scale'){
      lines.push(`# ${stepNum}. scale`);
      if(!srcName) lines.push("#   (select array)");
      else lines.push(`${srcName} = ${srcName} * ${p.scaleval!=null?p.scaleval:1}`);
    } else if(st.type === 'delete'){
      lines.push(`# ${stepNum}. delete`);
      if(!srcName) lines.push("#   (select array)");
      else lines.push(`del ${srcName}`);
    }
    lines.push("");
  }

  return lines.join("\n").trimEnd();
}

async function runPipeline(){
  for(const step of pipeSteps){
    step.status='run';step.msg='Running…';renderPipeline();
    await new Promise(r=>setTimeout(r,100));
    try{execStep(step);step.status='ok';step.msg='✓ Done';}
    catch(e){step.status='err';step.msg='✗ '+e.message;}
    renderPipeline();
  }
}

function getArr(id){const a=arrays.find(a=>a.id==id);if(!a)throw new Error('Array not found');return a;}

function execStep(step){
  const p=step.params;
  switch(step.type){
    case 'snap-to':{
      if(p.src==null||p.tgt==null) throw new Error('Select source and target');
      const src=getArr(p.src),tgt=getArr(p.tgt);
      const sb=arrayBounds(src),tb=arrayBounds(tgt);
      const gap=G; // match intra-cell spacing for a visually "flush" snap
      if(p.axis==='x+'||!p.axis)src.ox+=tb.maxX+gap-sb.minX;
      else if(p.axis==='x-')src.ox+=tb.minX-gap-sb.maxX;
      else if(p.axis==='z+')src.oz+=tb.maxZ+gap-sb.minZ;
      else if(p.axis==='z-')src.oz+=tb.minZ-gap-sb.maxZ;
      break;
    }
    case 'align':{
      if(p.src==null||p.tgt==null) throw new Error('Select source and target');
      const src=getArr(p.src),tgt=getArr(p.tgt);
      const sb=arrayBounds(src),tb=arrayBounds(tgt);
      if(p.edge==='left'||!p.edge)src.ox+=tb.minX-sb.minX;
      else if(p.edge==='right')src.ox+=tb.maxX-sb.maxX;
      else if(p.edge==='front')src.oz+=tb.minZ-sb.minZ;
      else if(p.edge==='back')src.oz+=tb.maxZ-sb.maxZ;
      else if(p.edge==='top')src.oy+=tb.maxY-sb.maxY;
      else if(p.edge==='bottom')src.oy+=tb.minY-sb.minY;
      break;
    }
    case 'copy-data':{
      if(p.src==null||p.tgt==null) throw new Error('Select source and target');
      const src=getArr(p.src),tgt=getArr(p.tgt);
      const n=Math.min(src.data.length,tgt.data.length);
      for(let i=0;i<n;i++)tgt.data[i]=src.data[i];
      break;
    }
    case 'fill':{
      if(p.src==null) throw new Error('Select an array');
      const src=getArr(p.src);
      let v=(p.fillval==null?'0':String(p.fillval)).trim();
      if(!v) v='0';
      if(v==='rand')for(let i=0;i<src.data.length;i++)src.data[i]=+(Math.random()*10).toFixed(2);
      else if(v==='idx')for(let i=0;i<src.data.length;i++)src.data[i]=i;
      else{const n=parseFloat(v);if(isNaN(n))throw new Error('Invalid value');for(let i=0;i<src.data.length;i++)src.data[i]=n;}
      break;
    }
    case 'reshape':{
      if(p.src==null) throw new Error('Select an array');
      const src=getArr(p.src);
      if(!p.newshape)throw new Error('No shape');
      const dims=p.newshape.split(/[×x,\s]+/).map(Number).filter(n=>n>0);
      if(!dims.length||dims.length>5)throw new Error('1–5 dims required');
      const newN=totalEls(dims);
      const old=src.data.slice();
      src.data=new Array(newN).fill(0);
      for(let i=0;i<Math.min(old.length,newN);i++)src.data[i]=old[i];
      src.dims=dims;
      renderArrayList();
      break;
    }
    case 'move-to':{
      if(p.src==null) throw new Error('Select an array');
      const src=getArr(p.src);src.ox=p.movex||0;src.oz=p.movez||0;break;
    }
    case 'scale':{
      if(p.src==null) throw new Error('Select an array');
      const src=getArr(p.src),f=p.scaleval!=null?p.scaleval:1;for(let i=0;i<src.data.length;i++)src.data[i]=+(src.data[i]*f).toFixed(4);break;
    }
    case 'delete':{
      if(p.src==null) throw new Error('Select an array');
      deleteArray(getArr(p.src).id);break;
    }
  }
}

// ================================================================
//  RENDERING
// ================================================================
const FACES=[
  {corners:[4,5,7,6],b:0.95},  // top (y+)
  {corners:[0,1,5,4],b:0.72},  // front (z=0)
  {corners:[1,3,7,5],b:0.58},  // right (x+)
  {corners:[0,2,6,4],b:0.44},  // left (x=0)
  {corners:[2,3,7,6],b:0.36},  // bottom
];

function cube8(wx,wy,wz){return[
  project(wx,wy,wz),project(wx+C,wy,wz),
  project(wx,wy-C,wz),project(wx+C,wy-C,wz),
  project(wx,wy,wz+C),project(wx+C,wy,wz+C),
  project(wx,wy-C,wz+C),project(wx+C,wy-C,wz+C),
];}

function hexRGB(h){return[parseInt(h.slice(1,3),16),parseInt(h.slice(3,5),16),parseInt(h.slice(5,7),16)];}
function shade(hex,b,a=1){const[r,g,bn]=hexRGB(hex);return`rgba(${Math.round(r*b)},${Math.round(g*b)},${Math.round(bn*b)},${a})`;}

function drawCell(pts,color,isSel,isHov){
  const sorted=FACES.map(f=>({...f,avgZ:f.corners.reduce((s,i)=>s+pts[i].z,0)/4})).sort((a,b)=>a.avgZ-b.avgZ);
  for(const face of sorted){
    const ps=face.corners.map(i=>pts[i]);
    ctx.beginPath();ctx.moveTo(ps[0].x,ps[0].y);
    for(let i=1;i<ps.length;i++)ctx.lineTo(ps[i].x,ps[i].y);
    ctx.closePath();
    const br=isSel?face.b*1.3:isHov?face.b*1.15:face.b*0.82;
    ctx.fillStyle=isSel?shade('#9aabff',br):shade(color,br);
    ctx.fill();
    ctx.strokeStyle=isSel?'rgba(160,180,255,0.75)':'rgba(0,0,0,0.28)';
    ctx.lineWidth=isSel?1.0*devicePixelRatio:0.35*devicePixelRatio;
    ctx.stroke();
  }
}

function ptInPoly(px,py,pts){
  let inside=false;
  for(let i=0,j=pts.length-1;i<pts.length;j=i++){
    const{x:xi,y:yi}=pts[i],{x:xj,y:yj}=pts[j];
    if(((yi>py)!==(yj>py))&&(px<(xj-xi)*(py-yi)/(yj-yi)+xi))inside=!inside;
  }
  return inside;
}

function pickCell(mx,my){
  const mx2=mx*devicePixelRatio,my2=my*devicePixelRatio;
  let best=null,bestZ=Infinity;
  for(const arr of arrays){
    for(const cell of layout(arr)){
      const wx=arr.ox+cell.wx,wy=arr.oy+cell.wy,wz=arr.oz+cell.wz;
      const pts=cube8(wx,wy,wz);
      for(const fi of[0,1,2,3]){
        const ps=FACES[fi].corners.map(i=>pts[i]);
        if(ptInPoly(mx2,my2,ps)){const z=ps.reduce((s,p)=>s+p.z,0)/4;if(z<bestZ){bestZ=z;best={arr,idx:cell.idx};}}
      }
    }
  }
  return best;
}

function renderFrame(){
  ctx.clearRect(0,0,canvas.width,canvas.height);
  drawGrid();
  const all=[];
  for(const arr of arrays){
    for(const cell of layout(arr)){
      const wx=arr.ox+cell.wx,wy=arr.oy+cell.wy,wz=arr.oz+cell.wz;
      all.push({arr,cell,wx,wy,wz,avgZ:project(wx+C/2,wy-C/2,wz+C/2).z});
    }
  }
  all.sort((a,b)=>a.avgZ-b.avgZ);
  for(const{arr,cell,wx,wy,wz}of all){
    const isSel=arr===sel&&selCell&&selCell.idx.join(',')===cell.idx.join(',');
    const isHov=hovered&&hovered.arr===arr&&hovered.idx.join(',')===cell.idx.join(',');
    const pts=cube8(wx,wy,wz);
    drawCell(pts,arr.color,isSel,isHov&&!isSel);
    if(cam.zoom>20){
      const top=FACES[0].corners.map(i=>pts[i]);
      const cx=top.reduce((s,p)=>s+p.x,0)/4,cy=top.reduce((s,p)=>s+p.y,0)/4;
      const v=arr.data[flatIdx(arr,cell.idx)];
      const label=Number.isInteger(v)?String(v):v.toFixed(1);
      const fs=Math.max(7,Math.min(12,cam.zoom*0.16))*devicePixelRatio;
      ctx.font=`${fs}px 'JetBrains Mono','Fira Code',monospace`;
      ctx.textAlign='center';ctx.textBaseline='middle';
      ctx.fillStyle=isSel?'#fff':'rgba(255,255,255,0.82)';
      ctx.fillText(label,cx,cy);
    }
  }
  for(const arr of arrays){
    const p=project(arr.ox,arr.oy+0.55,arr.oz-0.3);
    ctx.font=`500 ${11*devicePixelRatio}px 'Inter','Segoe UI',sans-serif`;
    ctx.textAlign='left';ctx.textBaseline='middle';
    ctx.fillStyle=arr===sel?'#a0abff':'rgba(200,200,220,0.42)';
    ctx.fillText(`${arr.name}  [${arr.dims.join('×')}]`,p.x,p.y);
  }
}

function drawGrid(){
  const N=40,step=1.1;
  ctx.lineWidth=0.3*devicePixelRatio;
  for(let i=-N;i<=N;i++){
    const a=project(i*step,-0.05,-N*step),b=project(i*step,-0.05,N*step);
    const c=project(-N*step,-0.05,i*step),d=project(N*step,-0.05,i*step);
    const alpha=Math.max(0,0.07-Math.abs(i)/N*0.05);
    ctx.strokeStyle=`rgba(100,120,200,${alpha})`;
    ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
    ctx.beginPath();ctx.moveTo(c.x,c.y);ctx.lineTo(d.x,d.y);ctx.stroke();
  }
}

function updateUI(){
  document.getElementById('i-cx').textContent=cam.x.toFixed(1);
  document.getElementById('i-cy').textContent=cam.y.toFixed(1);
  document.getElementById('i-zoom').textContent=Math.round(cam.zoom)+'%';
  document.getElementById('i-pitch').textContent=Math.round(cam.pitch)+'°';
  document.getElementById('i-yaw').textContent=Math.round(cam.yaw)+'°';
  document.getElementById('i-count').textContent=arrays.length;
  document.getElementById('i-steps').textContent=pipeSteps.length;
  if(sel){
    document.getElementById('i-name').textContent=sel.name;
    document.getElementById('i-dims').textContent=sel.dims.length+'D';
    document.getElementById('i-shape').textContent=sel.dims.join(' × ');
    document.getElementById('i-els').textContent=totalEls(sel.dims).toLocaleString();
    document.getElementById('i-ox').textContent=sel.ox.toFixed(1);
    document.getElementById('i-oz').textContent=sel.oz.toFixed(1);
  } else {
    ['i-name','i-dims','i-shape','i-els','i-ox','i-oz'].forEach(id=>document.getElementById(id).textContent='—');
  }
  const cp=document.getElementById('cell-panel');
  if(selCell&&sel){
    cp.style.display='block';
    document.getElementById('cell-title').textContent=`Cell  [${selCell.idx.join(', ')}]`;
    document.getElementById('cell-idx').textContent=selCell.idx.join(', ');
    document.getElementById('cell-input').value=sel.data[flatIdx(sel,selCell.idx)];
  } else cp.style.display='none';
}

// ================================================================
//  INPUT
// ================================================================
const cw=document.getElementById('canvas-wrap');

cw.addEventListener('mousedown',e=>{
  dragStart={x:e.clientX,y:e.clientY};dragMoved=false;
  if(e.shiftKey&&sel){dragMode='move';moveArr=sel;moveSnap={mx:e.clientX,my:e.clientY,ox:sel.ox,oy:sel.oy,oz:sel.oz};}
  else{dragMode='orbit';orbitSnap={pitch:cam.pitch,yaw:cam.yaw};}
});

cw.addEventListener('mousemove',e=>{
  const dx=e.clientX-dragStart.x,dy=e.clientY-dragStart.y;
  if(e.buttons&&(Math.abs(dx)+Math.abs(dy))>3)dragMoved=true;
  if(e.buttons&&dragMode==='orbit'&&!locked){
    cam.yaw=orbitSnap.yaw+dx*0.4;
    // Reverse vertical drag direction for pitch.
    cam.pitch=Math.max(-80,Math.min(80,orbitSnap.pitch+dy*0.35));
  }
  if(e.buttons&&dragMode==='move'&&moveArr){
    const s=cam.zoom,pw=cam.yaw*Math.PI/180;
    // Reverse vertical drag direction for moving arrays (left/right stays the same).
    const dxw=dx/s,dzw=dy/s;
    moveArr.ox=moveSnap.ox+dxw*Math.cos(pw)+dzw*Math.sin(pw);
    moveArr.oz=moveSnap.oz-dxw*Math.sin(pw)+dzw*Math.cos(pw);
  }
  if(!e.buttons){
    hovered=pickCell(e.clientX,e.clientY);
    canvas.style.cursor=hovered?'pointer':(locked?'default':'grab');
  }
});

cw.addEventListener('mouseup',e=>{
  if(!dragMoved){
    const hit=pickCell(e.clientX,e.clientY);
    if(hit){sel=hit.arr;selCell={idx:hit.idx};renderArrayList();setTimeout(()=>document.getElementById('cell-input').focus(),50);}
    else selCell=null;
  }
  dragMoved=false;moveArr=null;
});

cw.addEventListener('wheel',e=>{
  e.preventDefault();
  cam.zoom=Math.max(8,Math.min(280,cam.zoom*(e.deltaY<0?1.1:0.91)));
},{passive:false});

document.addEventListener('keydown',e=>{
  if(document.activeElement.tagName==='INPUT'||document.activeElement.tagName==='SELECT')return;
  keys[e.key.toLowerCase()]=true;
});
document.addEventListener('keyup',e=>{keys[e.key.toLowerCase()]=false;});

function commitCell(e){
  if(e.key==='Escape'){document.getElementById('cell-input').blur();return;}
  if(e.key!=='Enter')return;
  if(!sel||!selCell)return;
  const v=parseFloat(document.getElementById('cell-input').value);
  if(!isNaN(v))sel.data[flatIdx(sel,selCell.idx)]=v;
  document.getElementById('cell-input').blur();
}

// ================================================================
//  GAME LOOP  (fast movement: 0.14 units/frame)
// ================================================================
function handleKeys(){
  const spd=0.14;
  const pw=cam.yaw*Math.PI/180;
  if(keys['w']||keys['arrowup'])   {cam.x-=Math.sin(pw)*spd;cam.z-=Math.cos(pw)*spd;}
  if(keys['s']||keys['arrowdown']) {cam.x+=Math.sin(pw)*spd;cam.z+=Math.cos(pw)*spd;}
  if(keys['a']||keys['arrowleft']) {cam.x-=Math.cos(pw)*spd;cam.z+=Math.sin(pw)*spd;}
  if(keys['d']||keys['arrowright']){cam.x+=Math.cos(pw)*spd;cam.z-=Math.sin(pw)*spd;}
  if(keys['q'])cam.y+=spd;
  if(keys['e'])cam.y-=spd;
}

function loop(){handleKeys();renderFrame();updateUI();requestAnimationFrame(loop);}

// ================================================================
//  INIT
// ================================================================
addArray(2,[4,5]);
addArray(3,[2,3,4]);
addArray(1,[6]);
loop();
</script>
</body>
</html>
"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            # Browsers often request /favicon.ico; we only serve a single HTML page.
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-store, max-age=0')
        self.end_headers()
        self.wfile.write(HTML.encode('utf-8'))
    def log_message(self, *a): pass

def find_free_port(host: str, start: int = 8765) -> int:
    for port in range(start, start + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free port")

def main():
    parser = argparse.ArgumentParser(description="Array Space Explorer v2")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=0, help="Bind port (0 = auto)")
    parser.add_argument("--no-browser", action="store_true", help="Do not open a browser tab automatically")
    args = parser.parse_args()

    host = args.host
    port = args.port or find_free_port(host)
    url = f"http://{host}:{port}"

    ServerCls = getattr(http.server, "ThreadingHTTPServer", http.server.HTTPServer)
    server = ServerCls((host, port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    print("\n  Array Space Explorer  v2")
    print("  ------------------------")
    print(f"  {url}")
    print("\n  Navigation:")
    print("    WASD / Arrows  - move (3.5x faster than before)")
    print("    Q / E          - up / down")
    print("    Drag           - orbit camera")
    print("    Shift+drag     - move selected array")
    print("    Scroll         - zoom")
    print("\n  Sidebar tabs:")
    print("    Arrays   - add 1D-5D, fill, snap, delete (x button per row)")
    print("    Pipeline - snap-to, align, copy-data, fill, reshape, move, scale, delete")
    print("    Info     - camera & selected array stats")
    print("\n  Ctrl+C to stop.\n")

    if not args.no_browser:
        webbrowser.open(url)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n  Stopped.')
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

if __name__ == '__main__':
    main()
