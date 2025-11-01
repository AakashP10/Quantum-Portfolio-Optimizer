async function optimizePortfolio() {
  const tickers = document.getElementById("tickers").value;
  const loading = document.getElementById("loading");
  const result = document.getElementById("result");

  loading.style.display = "block";
  result.innerHTML = "";

  const formData = new FormData();
  formData.append("tickers", tickers);

  try {
    const response = await fetch("/optimize", { method: "POST", body: formData });
    const data = await response.json();

    loading.style.display = "none";

    if (data.error) {
      result.innerHTML = `<p style="color:red;"><b>Error:</b> ${data.error}</p>`;
      return;
    }

    if (!data.selected || !Array.isArray(data.selected)) {
      result.innerHTML = `<p style="color:red;"><b>Unexpected response:</b> ${JSON.stringify(data)}</p>`;
      return;
    }

    result.innerHTML = `
      <h3>🔹 Optimized Portfolio</h3>
      <p><b>Selected Assets:</b> ${data.selected.join(", ")}</p>
      <p><b>Expected Return:</b> ${data.expected_return.toFixed(6)}</p>
      <p><b>Risk:</b> ${data.risk.toFixed(6)}</p>
      <p><b>Method Used:</b> ${data.method}</p>
      <p><b>Job ID:</b> ${data.job_id}</p>

      <h4>Encrypted Ciphertext:</h4>
      <textarea rows="5" cols="60">${data.ciphertext_hex}</textarea>

      <h4>Nonce (for AES-GCM):</h4>
      <textarea rows="2" cols="60">${data.nonce_hex}</textarea>

      <button onclick="decryptData('${data.job_id}')"> Decrypt on Server</button>
    `;
  } catch (err) {
    loading.style.display = "none";
    result.innerHTML = `<p style="color:red;"><b>Fetch Error:</b> ${err.message}</p>`;
  }
}

async function decryptData(job_id) {
  const result = document.getElementById("result");
  result.innerHTML += `<p>Decrypting job ${job_id}...</p>`;

  try {
    const response = await fetch(`/decrypt?job_id=${job_id}`);
    const data = await response.json();

    if (data.error) {
      result.innerHTML += `<p style="color:red;">Error: ${data.error}</p>`;
    } else {
      result.innerHTML += `
        <h4>Decrypted Result:</h4>
        <pre>${JSON.stringify(data.plaintext, null, 2)}</pre>
      `;
    }
  } catch (err) {
    result.innerHTML += `<p style="color:red;">Decryption failed: ${err.message}</p>`;
  }
}
