const API_BASE = "http://localhost:5000";

const statusDot      = document.getElementById("statusDot");
const statusText     = document.getElementById("statusText");

const uploadZone     = document.getElementById("uploadZone");
const uploadInner    = document.getElementById("uploadInner");
const previewWrapper = document.getElementById("previewWrapper");
const previewImg     = document.getElementById("previewImg");
const browseBtn      = document.getElementById("browseBtn");
const fileInput      = document.getElementById("fileInput");
const removeBtn      = document.getElementById("removeBtn");

const cameraToggleBtn = document.getElementById("cameraToggleBtn");
const snapBtn         = document.getElementById("snapBtn");
const videoEl         = document.getElementById("videoEl");
const snapCanvas      = document.getElementById("snapCanvas");
const cameraOverlay   = document.getElementById("cameraOverlay");

const analyzeBtn      = document.getElementById("analyzeBtn");
const resultsSection  = document.getElementById("resultsSection");
const loadingOverlay  = document.getElementById("loadingOverlay");

const diagnosisName   = document.getElementById("diagnosisName");
const confPct         = document.getElementById("confPct");
const confBarFill     = document.getElementById("confBarFill");
const breakdownList   = document.getElementById("breakdownList");
const analyzedThumb   = document.getElementById("analyzedThumb");

let currentImageSource = null; 
let currentFile        = null; 
let capturedDataURL    = null; 
let cameraStream       = null;
let modelReady         = false;

async function checkStatus() {
  statusDot.className = "status-dot pulse";
  statusText.textContent = "Cargando modelo…";
  try {
    const res  = await fetch(`${API_BASE}/status`);
    const data = await res.json();
    if (data.loaded) {
      statusDot.className = "status-dot ok";
      statusText.textContent = "Modelo listo ✓";
      modelReady = true;
      updateAnalyzeBtn();
    } else {
      setTimeout(checkStatus, 2000);
    }
  } catch {
    statusDot.className = "status-dot error";
    statusText.textContent = "Sin conexión con el servidor";
    setTimeout(checkStatus, 4000);
  }
}

function updateAnalyzeBtn() {
  const hasImage = currentFile || capturedDataURL;
  analyzeBtn.disabled = !(modelReady && hasImage);
}

browseBtn.addEventListener("click", (e) => { e.stopPropagation(); fileInput.click(); });
uploadZone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
  if (fileInput.files[0]) loadFile(fileInput.files[0]);
});

uploadZone.addEventListener("dragover", (e) => { e.preventDefault(); uploadZone.classList.add("dragover"); });
uploadZone.addEventListener("dragleave", ()  => uploadZone.classList.remove("dragover"));
uploadZone.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith("image/")) loadFile(file);
});

function loadFile(file) {
  currentFile        = file;
  currentImageSource = "file";
  capturedDataURL    = null;

  const reader = new FileReader();
  reader.onload = (ev) => {
    previewImg.src = ev.target.result;
    previewWrapper.classList.remove("hidden");
    uploadInner.classList.add("hidden");
    hideResults();
    updateAnalyzeBtn();
  };
  reader.readAsDataURL(file);
}

removeBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  clearUpload();
});

function clearUpload() {
  currentFile        = null;
  currentImageSource = null;
  previewImg.src     = "";
  fileInput.value    = "";
  previewWrapper.classList.add("hidden");
  uploadInner.classList.remove("hidden");
  hideResults();
  updateAnalyzeBtn();
}

cameraToggleBtn.addEventListener("click", toggleCamera);
snapBtn.addEventListener("click", takeSnapshot);

async function toggleCamera() {
  if (cameraStream) {
    stopCamera();
  } else {
    await startCamera();
  }
}

async function startCamera() {
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
    videoEl.srcObject = cameraStream;
    cameraOverlay.classList.add("hidden");
    cameraToggleBtn.textContent = "Detener cámara";
    snapBtn.disabled = false;
  } catch (err) {
    alert("No se pudo acceder a la cámara: " + err.message);
  }
}

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(t => t.stop());
    cameraStream = null;
  }
  videoEl.srcObject = null;
  cameraOverlay.classList.remove("hidden");
  cameraToggleBtn.textContent = "Activar cámara";
  snapBtn.disabled = true;
}

function takeSnapshot() {
  if (!cameraStream) return;

  snapCanvas.width  = videoEl.videoWidth;
  snapCanvas.height = videoEl.videoHeight;
  snapCanvas.getContext("2d").drawImage(videoEl, 0, 0);

  capturedDataURL    = snapCanvas.toDataURL("image/jpeg", 0.92);
  currentImageSource = "camera";
  currentFile        = null;

  previewImg.src = capturedDataURL;
  previewWrapper.classList.remove("hidden");
  uploadInner.classList.add("hidden");

  hideResults();
  updateAnalyzeBtn();
  stopCamera();
}

analyzeBtn.addEventListener("click", runAnalysis);

async function runAnalysis() {
  if (!modelReady) return;
  showLoading(true);
  hideResults();

  try {
    let response;

    if (currentImageSource === "file" && currentFile) {
      const form = new FormData();
      form.append("file", currentFile);
      response = await fetch(`${API_BASE}/predict`, { method: "POST", body: form });

    } else if (currentImageSource === "camera" && capturedDataURL) {
      response = await fetch(`${API_BASE}/predict`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ image: capturedDataURL })
      });

    } else {
      showLoading(false);
      return;
    }

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || "Error desconocido");
    }

    const data = await response.json();
    showResults(data);

  } catch (err) {
    alert("Error al analizar: " + err.message);
  } finally {
    showLoading(false);
  }
}

function showResults(data) {
  analyzedThumb.src = previewImg.src;

  diagnosisName.textContent = data.diagnosis;
  const isHealthy = data.diagnosis.toLowerCase() === "sana";
  diagnosisName.className = "diagnosis-name " + (isHealthy ? "healthy" : "disease");

  const pct = (data.confidence * 100).toFixed(1);
  confPct.textContent = pct + "%";
  setTimeout(() => { confBarFill.style.width = pct + "%"; }, 60);

  breakdownList.innerHTML = "";
  data.breakdown.forEach((item, idx) => {
    const p   = (item.probability * 100).toFixed(1);
    const div = document.createElement("div");
    div.className = "breakdown-item";
    div.innerHTML = `
      <div class="breakdown-meta">
        <span class="breakdown-label">${item.label}</span>
        <span class="breakdown-pct">${p}%</span>
      </div>
      <div class="breakdown-track">
        <div class="breakdown-bar ${idx === 0 ? 'top' : ''}" style="width:0%"></div>
      </div>`;
    breakdownList.appendChild(div);
    setTimeout(() => {
      div.querySelector(".breakdown-bar").style.width = p + "%";
    }, 80 + idx * 40);
  });

  resultsSection.classList.remove("hidden");
  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function hideResults() {
  resultsSection.classList.add("hidden");
}

function showLoading(on) {
  loadingOverlay.classList.toggle("hidden", !on);
  analyzeBtn.disabled = on;
}

checkStatus();