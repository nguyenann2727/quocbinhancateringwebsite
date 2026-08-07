const stage = document.querySelector("#pdf-stage");
const panel = document.querySelector("#property-panel");
const toast = document.querySelector("#editor-toast");
const modeAllButton = document.querySelector("#mode-all");
const modeImageButton = document.querySelector("#mode-image");
const modeTextButton = document.querySelector("#mode-text");
const saveButton = document.querySelector("#save-state");
const rebuildButton = document.querySelector("#rebuild-pdf");
const hidePdfEditButton = document.querySelector("#hide-pdf-edit-button");
const openFinalPdfLink = document.querySelector("#open-final-pdf");

let manifest = null;
let state = { version: 1, images: {}, texts: {} };
const requestedMode = new URLSearchParams(window.location.search).get("mode");
let currentMode = ["all", "image", "text"].includes(requestedMode) ? requestedMode : "all";
let selected = null;
let imageDragTool = "frame";
let interaction = null;
let toastTimer = null;
let autoSaveTimer = null;
let savingState = false;
const ASSET_VERSION = String(Date.now());
const COMPUTER_IMAGE_ACCEPT = "image/jpeg,image/png,image/webp,image/heic,image/heif,.jpg,.jpeg,.png,.webp,.heic,.heif";
const computerImageInput = document.createElement("input");
computerImageInput.type = "file";
computerImageInput.accept = COMPUTER_IMAGE_ACCEPT;
computerImageInput.hidden = true;
document.body.append(computerImageInput);

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2600);
}

async function readJson(path, fallback) {
  try {
    const response = await fetch(`${path}?v=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) return fallback;
    return await response.json();
  } catch (error) {
    return fallback;
  }
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function normalizeTextValue(value) {
  return String(value)
    .replace(/&(?:nbsp|#160|#xA0);/gi, " ")
    .replace(/\u00a0/g, " ");
}

function projectUrl(path) {
  return `../${String(path).split("/").map(encodeURIComponent).join("/")}`;
}

function pageSize() {
  return manifest.page || { width: 595.28, height: 841.89 };
}

function imageRecord(frame) {
  const id = frame.id;
  if (!state.images[id]) {
    state.images[id] = {
      x: frame.x,
      y: frame.y,
      w: frame.w,
      h: frame.h,
      alignX: frame.alignX ?? 0.5,
      alignY: frame.alignY ?? 0.5,
      zoom: frame.zoom ?? 100,
      rotate: frame.rotate ?? 0,
    };
  }
  return state.images[id];
}

function textRecord(frame) {
  const id = frame.id;
  if (state.texts[id] && state.texts[id].original && state.texts[id].original !== frame.original) {
    delete state.texts[id];
  }
  if (!state.texts[id]) {
    state.texts[id] = {
      original: frame.original,
      value: frame.value || frame.original,
      fontSize: frame.fontSize || frame.baseFontSize || 10,
      fontScale: frame.fontScale || 100,
    };
  }
  state.texts[id].value = normalizeTextValue(state.texts[id].value || frame.value || frame.original);
  return state.texts[id];
}

function textFontSize(frame, record) {
  return Number(record.fontSize || frame.fontSize || frame.baseFontSize || 10);
}

function applyTextStyle(element, frame, record) {
  const content = element.querySelector(".text-content");
  if (!content) return;
  const fontSize = textFontSize(frame, record);
  content.style.fontSize = `${Math.max(8, fontSize * 1.28)}px`;
  content.style.lineHeight = "1.32";
  content.style.textAlign = frame.align === "center" ? "center" : frame.align === "right" ? "right" : "left";
}

function frameBox(record) {
  const p = pageSize();
  return {
    left: `${(record.x / p.width) * 100}%`,
    top: `${((p.height - record.y - record.h) / p.height) * 100}%`,
    width: `${(record.w / p.width) * 100}%`,
    height: `${(record.h / p.height) * 100}%`,
  };
}

function applyFrameStyle(element, record) {
  const box = frameBox(record);
  element.style.left = box.left;
  element.style.top = box.top;
  element.style.width = box.width;
  element.style.height = box.height;
}

function imagePreviewUrl(record) {
  if (record.dataUrl) return record.dataUrl;
  if (record.replacement) return projectUrl(record.replacement);
  return "";
}

function applyImagePreviewStyle(element, record) {
  const preview = element.querySelector(".image-preview");
  if (!preview) return;
  const url = imagePreviewUrl(record);
  preview.style.backgroundImage = url ? `url("${url}")` : "";
  preview.style.backgroundPosition = `${(record.alignX ?? 0.5) * 100}% ${(record.alignY ?? 0.5) * 100}%`;
  preview.style.transform = `scale(${Math.max(0.25, (record.zoom ?? 100) / 100)}) rotate(${record.rotate ?? 0}deg)`;
  preview.style.transformOrigin = `${(record.alignX ?? 0.5) * 100}% ${(record.alignY ?? 0.5) * 100}%`;
}

function pagePreviewUrl(page, version = ASSET_VERSION) {
  return `hsnl-pdf-pages/page-${String(page).padStart(2, "0")}.jpg?v=${version}`;
}

function attachPagePreview(pageElement, page) {
  const img = document.createElement("img");
  const loader = document.createElement("div");
  const errorBox = document.createElement("div");
  const label = document.createElement("span");
  const retryButton = document.createElement("button");

  pageElement.classList.add("loading");
  loader.className = "page-loader";
  loader.textContent = `Đang tải trang ${String(page).padStart(2, "0")}...`;

  retryButton.type = "button";
  retryButton.textContent = "Tải lại trang";
  retryButton.addEventListener("click", () => {
    pageElement.classList.add("loading");
    pageElement.classList.remove("page-error");
    img.src = pagePreviewUrl(page, Date.now());
  });

  errorBox.className = "page-error-message";
  errorBox.append("Không tải được ảnh preview của trang này. ", retryButton);

  label.className = "page-label";
  label.textContent = `Trang ${String(page).padStart(2, "0")}`;

  img.alt = `Trang ${page}`;
  img.loading = "lazy";
  img.decoding = "async";
  img.addEventListener("load", () => {
    pageElement.classList.remove("loading", "page-error");
  });
  img.addEventListener("error", () => {
    pageElement.classList.remove("loading");
    pageElement.classList.add("page-error");
  });
  img.src = pagePreviewUrl(page);

  pageElement.append(loader, img, errorBox, label);
}

function renderPages() {
  stage.innerHTML = "";
  const p = pageSize();
  stage.classList.toggle("mode-all", currentMode === "all");
  stage.classList.toggle("mode-image", currentMode === "image");
  stage.classList.toggle("mode-text", currentMode === "text");
  for (let page = 1; page <= manifest.pageCount; page += 1) {
    const pageElement = document.createElement("section");
    pageElement.className = "pdf-page";
    pageElement.dataset.page = String(page);
    pageElement.style.aspectRatio = `${p.width} / ${p.height}`;
    attachPagePreview(pageElement, page);
    manifest.images.filter((item) => item.page === page).forEach((frame) => pageElement.append(renderImageFrame(frame)));
    manifest.texts.filter((item) => item.page === page).forEach((frame) => pageElement.append(renderTextFrame(frame)));
    stage.append(pageElement);
  }
}

function renderImageFrame(frame) {
  const record = imageRecord(frame);
  const element = document.createElement("div");
  element.className = "edit-frame image-frame";
  element.dataset.kind = "image";
  element.dataset.id = frame.id;
  element.dataset.page = String(frame.page);
  element.dataset.frame = JSON.stringify(frame);
  applyFrameStyle(element, record);
  element.innerHTML = `
    <span class="image-preview"></span>
    <span class="frame-label">${frame.label || frame.id}</span>
    <button class="quick-replace-image" type="button" title="Thay ảnh từ máy tính">Thay ảnh</button>
    ${["nw", "n", "ne", "e", "se", "s", "sw", "w"].map((handle) => `<span class="resize-handle ${handle}" data-handle="${handle}"></span>`).join("")}
  `;
  applyImagePreviewStyle(element, record);
  element.querySelector(".quick-replace-image").addEventListener("click", (event) => {
    event.stopPropagation();
    selectFrame("image", frame.id);
    openComputerFilePicker(frame);
  });
  element.addEventListener("pointerdown", startImageInteraction);
  element.addEventListener("dblclick", (event) => {
    event.stopPropagation();
    selectFrame("image", frame.id);
    openComputerFilePicker(frame);
  });
  element.addEventListener("click", (event) => {
    event.stopPropagation();
    selectFrame("image", frame.id);
  });
  return element;
}

function renderTextFrame(frame) {
  const record = textRecord(frame);
  const element = document.createElement("div");
  element.className = "edit-frame text-frame";
  element.dataset.kind = "text";
  element.dataset.id = frame.id;
  element.dataset.page = String(frame.page);
  element.dataset.frame = JSON.stringify(frame);
  applyFrameStyle(element, frame);
  element.innerHTML = `
    <div class="text-content" contenteditable="true" spellcheck="true">${record.value}</div>
    <span class="frame-label">Chữ</span>
  `;
  applyTextStyle(element, frame, record);
  const content = element.querySelector(".text-content");
  content.addEventListener("input", () => {
    const next = textRecord(frame);
    next.value = normalizeTextValue(content.innerHTML.trim());
    scheduleAutoSave();
    renderPanel();
  });
  element.addEventListener("click", (event) => {
    event.stopPropagation();
    selectFrame("text", frame.id);
  });
  return element;
}

function selectFrame(kind, id) {
  selected = { kind, id };
  document.querySelectorAll(".edit-frame.selected").forEach((item) => item.classList.remove("selected"));
  document.querySelector(`.edit-frame[data-id="${CSS.escape(id)}"]`)?.classList.add("selected");
  renderPanel();
}

function selectedManifestFrame() {
  if (!selected) return null;
  const list = selected.kind === "image" ? manifest.images : manifest.texts;
  return list.find((item) => item.id === selected.id) || null;
}

function selectedElement() {
  return selected ? document.querySelector(`.edit-frame[data-id="${CSS.escape(selected.id)}"]`) : null;
}

function renderPanel() {
  const frame = selectedManifestFrame();
  if (!frame) {
    panel.innerHTML = `<div class="panel-empty"><strong>Chọn một khung trên trang</strong><span>Bật chế độ Ảnh hoặc Chữ ở góc dưới, sau đó bấm vào khung cần chỉnh.</span></div>`;
    return;
  }
  if (selected.kind === "image") renderImagePanel(frame);
  if (selected.kind === "text") renderTextPanel(frame);
}

function renderImagePanel(frame) {
  const record = imageRecord(frame);
  panel.innerHTML = `
    <h2>Khung ảnh</h2>
    <small>Trang ${String(frame.page).padStart(2, "0")} - ${frame.label || frame.source}</small>
    <button id="choose-computer-image" class="wide-action local-action" type="button">Chọn file ảnh từ máy tính</button>
    <small class="panel-hint">Có thể bấm đúp trực tiếp lên khung ảnh/nền hero để thay nhanh.</small>
    <button id="open-downloads" class="wide-action" type="button">Chọn ảnh từ Downloads</button>
    <div id="download-picker" class="download-picker" hidden></div>
    <div class="panel-actions">
      <button id="tool-frame" class="${imageDragTool === "frame" ? "active" : ""}" type="button">Kéo khung</button>
      <button id="tool-image" class="${imageDragTool === "image" ? "active" : ""}" type="button">Kéo ảnh bên trong</button>
    </div>
    <div class="panel-actions">
      <button id="zoom-out" type="button">Zoom -</button>
      <button id="zoom-in" type="button">Zoom +</button>
      <button id="zoom-reset" type="button">Zoom 100%</button>
    </div>
    <div class="field-grid">
      <label>Trái/phải X<input data-image-field="x" type="number" step="1" value="${Math.round(record.x)}" /></label>
      <label>Lên/xuống Y<input data-image-field="y" type="number" step="1" value="${Math.round(record.y)}" /></label>
      <label>Rộng W<input data-image-field="w" type="number" step="1" value="${Math.round(record.w)}" /></label>
      <label>Cao H<input data-image-field="h" type="number" step="1" value="${Math.round(record.h)}" /></label>
      <label>Tâm ngang<input data-image-field="alignX" type="range" min="0" max="1" step="0.01" value="${record.alignX ?? 0.5}" /></label>
      <label>Tâm dọc<input data-image-field="alignY" type="range" min="0" max="1" step="0.01" value="${record.alignY ?? 0.5}" /></label>
      <label>Phóng ảnh<input data-image-field="zoom" type="range" min="20" max="600" step="1" value="${record.zoom ?? 100}" /></label>
      <label>Góc xoay<input data-image-field="rotate" type="range" min="-30" max="30" step="1" value="${record.rotate ?? 0}" /></label>
    </div>
    <div class="panel-actions">
      <button id="reset-frame" type="button">Khôi phục khung</button>
      <button id="clear-image" type="button">Bỏ ảnh thay</button>
    </div>
  `;
  panel.querySelector("#tool-frame").addEventListener("click", () => {
    imageDragTool = "frame";
    renderPanel();
  });
  panel.querySelector("#tool-image").addEventListener("click", () => {
    imageDragTool = "image";
    renderPanel();
  });
  panel.querySelector("#choose-computer-image").addEventListener("click", () => openComputerFilePicker(frame));
  panel.querySelector("#open-downloads").addEventListener("click", () => loadDownloadImages(frame));
  const setZoom = (nextZoom) => {
    record.zoom = Math.max(20, Math.min(600, Number(nextZoom) || 100));
    syncSelectedImage();
    const zoomInput = panel.querySelector('[data-image-field="zoom"]');
    if (zoomInput) zoomInput.value = String(record.zoom);
    scheduleAutoSave();
  };
  panel.querySelector("#zoom-out").addEventListener("click", () => setZoom((record.zoom ?? 100) - 20));
  panel.querySelector("#zoom-in").addEventListener("click", () => setZoom((record.zoom ?? 100) + 20));
  panel.querySelector("#zoom-reset").addEventListener("click", () => setZoom(100));
  panel.querySelector("#reset-frame").addEventListener("click", () => {
    const existing = imageRecord(frame);
    state.images[frame.id] = {
      x: frame.x,
      y: frame.y,
      w: frame.w,
      h: frame.h,
      alignX: frame.alignX ?? 0.5,
      alignY: frame.alignY ?? 0.5,
      zoom: frame.zoom ?? 100,
      rotate: frame.rotate ?? 0,
      ...(existing.dataUrl ? { dataUrl: existing.dataUrl } : {}),
      ...(existing.replacement ? { replacement: existing.replacement } : {}),
      ...(existing.filename ? { filename: existing.filename } : {}),
    };
    syncSelectedImage();
    scheduleAutoSave();
    renderPanel();
  });
  panel.querySelector("#clear-image").addEventListener("click", () => {
    delete record.dataUrl;
    delete record.replacement;
    delete record.filename;
    syncSelectedImage();
    scheduleAutoSave();
    renderPanel();
  });
  panel.querySelectorAll("[data-image-field]").forEach((input) => {
    input.addEventListener("input", () => {
      const key = input.dataset.imageField;
      record[key] = Number(input.value);
      if (["w", "h"].includes(key)) record[key] = Math.max(8, record[key]);
      syncSelectedImage();
      scheduleAutoSave();
    });
  });
}

function renderTextPanel(frame) {
  const record = textRecord(frame);
  const fontSize = textFontSize(frame, record);
  panel.innerHTML = `
    <h2>Khung chữ</h2>
    <small>Trang ${String(frame.page).padStart(2, "0")}. Nội dung có thể dùng thẻ &lt;br/&gt; để xuống dòng.</small>
    <label class="panel-field">Nội dung
      <textarea id="text-value">${escapeHtml(record.value)}</textarea>
    </label>
    <div class="panel-actions">
      <button id="text-smaller" type="button">A-</button>
      <button id="text-larger" type="button">A+</button>
    </div>
    <div class="field-grid">
      <label>Cỡ chữ<input id="text-font-range" type="range" min="4" max="72" step="0.5" value="${fontSize}" /></label>
      <label>Nhập cỡ<input id="text-font-number" type="number" min="4" max="72" step="0.5" value="${fontSize}" /></label>
    </div>
    <div class="panel-actions">
      <button id="reset-text" type="button">Khôi phục chữ</button>
      <button id="reset-text-size" type="button">Khôi phục cỡ chữ</button>
    </div>
  `;
  panel.querySelector("#text-value").addEventListener("input", (event) => {
    record.value = normalizeTextValue(event.target.value);
    const element = selectedElement();
    const content = element?.querySelector(".text-content");
    if (content) content.innerHTML = record.value;
    scheduleAutoSave();
  });
  const setTextSize = (nextSize) => {
    record.fontSize = Math.max(4, Math.min(72, Number(nextSize) || fontSize));
    record.fontScale = frame.baseFontSize ? (record.fontSize / frame.baseFontSize) * 100 : 100;
    const element = selectedElement();
    if (element) applyTextStyle(element, frame, record);
    const range = panel.querySelector("#text-font-range");
    const number = panel.querySelector("#text-font-number");
    if (range) range.value = String(record.fontSize);
    if (number) number.value = String(record.fontSize);
    scheduleAutoSave();
  };
  panel.querySelector("#text-font-range").addEventListener("input", (event) => {
    setTextSize(event.target.value);
  });
  panel.querySelector("#text-font-number").addEventListener("input", (event) => {
    setTextSize(event.target.value);
  });
  panel.querySelector("#text-smaller").addEventListener("click", () => {
    setTextSize(textFontSize(frame, record) - 1);
  });
  panel.querySelector("#text-larger").addEventListener("click", () => {
    setTextSize(textFontSize(frame, record) + 1);
  });
  panel.querySelector("#reset-text").addEventListener("click", () => {
    record.value = normalizeTextValue(frame.original);
    const element = selectedElement();
    const content = element?.querySelector(".text-content");
    if (content) content.innerHTML = record.value;
    scheduleAutoSave();
    renderPanel();
  });
  panel.querySelector("#reset-text-size").addEventListener("click", () => {
    record.fontSize = frame.baseFontSize || frame.fontSize || 10;
    record.fontScale = 100;
    const element = selectedElement();
    if (element) applyTextStyle(element, frame, record);
    scheduleAutoSave();
    renderPanel();
  });
}

function syncSelectedImage() {
  const frame = selectedManifestFrame();
  const element = selectedElement();
  if (!frame || !element) return;
  const record = imageRecord(frame);
  applyFrameStyle(element, record);
  applyImagePreviewStyle(element, record);
}

async function loadDownloadImages(frame) {
  const holder = panel.querySelector("#download-picker");
  if (!holder) return;
  holder.hidden = false;
  holder.innerHTML = `<div class="download-status">Đang đọc ảnh trong Downloads...</div>`;
  try {
    const response = await fetch("/api/download-images", { cache: "no-store" });
    const payload = await response.json();
    if (!payload.ok) throw new Error(payload.error || "Không đọc được Downloads");
    if (!payload.images.length) {
      holder.innerHTML = `<div class="download-status">Chưa thấy ảnh JPG/PNG/WebP/HEIC trong Downloads.</div>`;
      return;
    }
    holder.innerHTML = `
      <div class="download-title">Ảnh trong Downloads</div>
      <div class="download-grid">
        ${payload.images.map((item) => `
          <button class="download-card" type="button" data-download-path="${escapeHtml(item.path)}">
            ${[".heic", ".heif"].includes(item.ext) ? `<span class="download-heic">HEIC</span>` : `<img src="${item.preview}" alt="" loading="lazy" />`}
            <span>${escapeHtml(item.name)}</span>
          </button>
        `).join("")}
      </div>
    `;
    holder.querySelectorAll(".download-card").forEach((button) => {
      button.addEventListener("click", () => importDownloadImage(frame, button.dataset.downloadPath));
    });
  } catch (error) {
    holder.innerHTML = `<div class="download-status">Chưa mở được Downloads: ${escapeHtml(error.message)}</div>`;
  }
}

async function importDownloadImage(frame, downloadPath) {
  const record = imageRecord(frame);
  try {
    showToast("Đang thay ảnh từ Downloads...");
    const response = await fetch("/api/import-download-image", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: downloadPath, slotId: frame.id }),
    });
    const payload = await response.json();
    if (!payload.ok) throw new Error(payload.error || "Không thay được ảnh");
    record.replacement = payload.replacement;
    record.filename = payload.filename;
    delete record.dataUrl;
    record.zoom = Math.max(record.zoom || 100, 110);
    syncSelectedImage();
    scheduleAutoSave();
    renderPanel();
    showToast(`Đã thay ảnh: ${payload.filename}`);
  } catch (error) {
    showToast(`Lỗi thay ảnh: ${error.message}`);
  }
}

function openComputerFilePicker(frame) {
  if (!frame) return;
  computerImageInput.dataset.frameId = frame.id;
  computerImageInput.value = "";
  computerImageInput.click();
}

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error || new Error("Không đọc được file ảnh"));
    reader.readAsDataURL(file);
  });
}

async function uploadComputerImage(frame, file, dataUrl) {
  const response = await fetch("/api/upload-image", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      dataUrl,
      filename: file.name,
      mime: file.type,
      slotId: frame.id,
    }),
  });
  const payload = await response.json();
  if (!payload.ok) throw new Error(payload.error || "Không upload được ảnh");
  return payload;
}

async function replaceWithComputerFile(file, frame) {
  if (!file || !frame) return;
  const record = imageRecord(frame);
  showToast("Đang thay ảnh từ máy tính...");
  try {
    const dataUrl = await readFileAsDataUrl(file);
    try {
      const payload = await uploadComputerImage(frame, file, dataUrl);
      record.replacement = payload.replacement;
      record.filename = payload.filename;
      delete record.dataUrl;
    } catch (uploadError) {
      record.dataUrl = dataUrl;
      record.filename = file.name;
      delete record.replacement;
      if (/\.(heic|heif)$/i.test(file.name)) throw uploadError;
    }
    record.zoom = Math.max(record.zoom || 100, 100);
    syncSelectedImage();
    scheduleAutoSave();
    renderPanel();
    showToast(`Đã thay ảnh từ máy: ${file.name}`);
  } catch (error) {
    showToast(`Lỗi thay ảnh: ${error.message}`);
  }
}

function handleComputerImageInput(event) {
  const file = event.target.files?.[0];
  const frameId = computerImageInput.dataset.frameId;
  const frame = manifest?.images?.find((item) => item.id === frameId) || selectedManifestFrame();
  if (!file || !frame) return;
  selectFrame("image", frame.id);
  replaceWithComputerFile(file, frame);
}

computerImageInput.addEventListener("change", handleComputerImageInput);

function startImageInteraction(event) {
  if (!["all", "image"].includes(currentMode)) return;
  if (event.target.closest(".quick-replace-image")) return;
  const element = event.currentTarget;
  const frame = JSON.parse(element.dataset.frame);
  selectFrame("image", frame.id);
  const record = imageRecord(frame);
  const page = element.closest(".pdf-page");
  const pageRect = page.getBoundingClientRect();
  const handle = event.target.dataset.handle || "";
  interaction = {
    id: frame.id,
    handle,
    mode: handle ? "resize" : imageDragTool,
    pageRect,
    startX: event.clientX,
    startY: event.clientY,
    start: { ...record },
  };
  element.setPointerCapture?.(event.pointerId);
  event.preventDefault();
}

function moveInteraction(event) {
  if (!interaction) return;
  const frame = manifest.images.find((item) => item.id === interaction.id);
  if (!frame) return;
  const record = imageRecord(frame);
  const p = pageSize();
  const dx = ((event.clientX - interaction.startX) / interaction.pageRect.width) * p.width;
  const dy = ((event.clientY - interaction.startY) / interaction.pageRect.height) * p.height;
  if (interaction.mode === "image") {
    record.alignX = clamp((interaction.start.alignX ?? 0.5) - dx / Math.max(40, interaction.start.w), 0, 1);
    record.alignY = clamp((interaction.start.alignY ?? 0.5) - dy / Math.max(40, interaction.start.h), 0, 1);
  } else if (interaction.mode === "resize") {
    resizeRecord(record, interaction.start, interaction.handle, dx, dy);
  } else {
    record.x = clamp(interaction.start.x + dx, -p.width * 0.5, p.width * 1.2);
    record.y = clamp(interaction.start.y - dy, -p.height * 0.5, p.height * 1.2);
  }
  syncSelectedImage();
  renderPanel();
}

function resizeRecord(record, start, handle, dx, dy) {
  if (handle.includes("e")) record.w = Math.max(12, start.w + dx);
  if (handle.includes("w")) {
    record.x = start.x + dx;
    record.w = Math.max(12, start.w - dx);
  }
  if (handle.includes("n")) record.h = Math.max(12, start.h - dy);
  if (handle.includes("s")) {
    record.y = start.y - dy;
    record.h = Math.max(12, start.h + dy);
  }
}

function endInteraction() {
  if (interaction) scheduleAutoSave();
  interaction = null;
}

function setMode(mode) {
  currentMode = mode;
  modeAllButton.classList.toggle("active", mode === "all");
  modeImageButton.classList.toggle("active", mode === "image");
  modeTextButton.classList.toggle("active", mode === "text");
  stage.classList.toggle("mode-all", mode === "all");
  stage.classList.toggle("mode-image", mode === "image");
  stage.classList.toggle("mode-text", mode === "text");
  selected = null;
  document.querySelectorAll(".edit-frame.selected").forEach((item) => item.classList.remove("selected"));
  renderPanel();
}

function downloadState() {
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "hsnl-pdf-editor-state.json";
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

function scheduleAutoSave() {
  clearTimeout(autoSaveTimer);
  autoSaveTimer = setTimeout(() => saveState({ silent: true }), 700);
}

async function saveState(options = {}) {
  const silent = Boolean(options.silent);
  if (savingState) {
    scheduleAutoSave();
    return;
  }
  savingState = true;
  try {
    const response = await fetch("/api/save-state", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(state),
    });
    if (!response.ok) throw new Error("save failed");
    if (!silent) showToast("Đã lưu chỉnh sửa vào dự án.");
  } catch (error) {
    downloadState();
    showToast("Không có server lưu trực tiếp, đã tải file state về máy.");
  } finally {
    savingState = false;
  }
}

async function rebuildPdf() {
  await saveState();
  rebuildButton.disabled = true;
  rebuildButton.textContent = "Đang dựng...";
  try {
    const response = await fetch("/api/rebuild", { method: "POST" });
    if (!response.ok) throw new Error("rebuild failed");
    showToast("Đã dựng lại PDF và ảnh preview.");
    await loadEditor();
  } catch (error) {
    showToast("Nếu mở bằng file, hãy chạy script dựng lại PDF sau khi đặt file state vào editable/.");
  } finally {
    rebuildButton.disabled = false;
    rebuildButton.textContent = "Dựng lại PDF";
  }
}

async function hideTemporaryPdfButton() {
  const confirmed = window.confirm("Xoá nút chỉnh sửa tạm khỏi PDF và dựng lại bản sạch?");
  if (!confirmed) return;
  hidePdfEditButton.disabled = true;
  hidePdfEditButton.textContent = "Đang xoá...";
  try {
    const response = await fetch("/api/edit-button", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: false }),
    });
    if (!response.ok) throw new Error("toggle failed");
    await rebuildPdf();
    showToast("Đã xoá nút tạm khỏi PDF.");
  } catch (error) {
    showToast("Chưa xoá được nút tạm. Hãy kiểm tra server editor.");
  } finally {
    hidePdfEditButton.disabled = false;
    hidePdfEditButton.textContent = "Xoá nút tạm";
  }
}

async function loadEditor() {
  stage.innerHTML = `<div class="stage-status"><strong>Đang mở bản chỉnh sửa...</strong><span>Đang tải manifest và ảnh preview của hồ sơ năng lực.</span></div>`;
  manifest = await readJson("hsnl-pdf-editor-manifest.json", null);
  state = await readJson("hsnl-pdf-editor-state.json", { version: 1, images: {}, texts: {} });
  if (!state.images) state.images = {};
  if (!state.texts) state.texts = {};
  if (!manifest) {
    stage.innerHTML = `<div class="stage-status editor-error"><strong>Chưa tải được dữ liệu chỉnh sửa</strong><span>Hãy chạy lại server editor hoặc bấm reload sau khi PDF được dựng lại. Nếu một trang riêng lẻ bị trắng, dùng nút “Tải lại trang” trên trang đó.</span></div>`;
    return;
  }
  // Always open a fresh viewer session after a rebuild. Chromium otherwise can
  // retain an old thumbnail selection while the PDF body has been replaced.
  if (openFinalPdfLink) {
    openFinalPdfLink.href = `../output/pdf/HSNL-Quoc-Binh-An-Catering-FINAL.pdf?v=${encodeURIComponent(ASSET_VERSION)}`;
  }
  renderPages();
  renderPanel();
}

modeAllButton.addEventListener("click", () => setMode("all"));
modeImageButton.addEventListener("click", () => setMode("image"));
modeTextButton.addEventListener("click", () => setMode("text"));
saveButton.addEventListener("click", saveState);
rebuildButton.addEventListener("click", rebuildPdf);
hidePdfEditButton.addEventListener("click", hideTemporaryPdfButton);
document.addEventListener("pointermove", moveInteraction);
document.addEventListener("pointerup", endInteraction);
document.addEventListener("pointercancel", endInteraction);
document.addEventListener("click", (event) => {
  if (event.target.closest(".edit-frame, .property-panel, .editor-dock")) return;
  selected = null;
  document.querySelectorAll(".edit-frame.selected").forEach((item) => item.classList.remove("selected"));
  renderPanel();
});

loadEditor();
