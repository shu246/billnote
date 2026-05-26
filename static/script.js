const apiBaseUrl = "https://6ssxr2dq8d.execute-api.ap-northeast-1.amazonaws.com/default/billnote-api";
let currentMode = "file";

// モード切り替え (ファイル ↔ フォルダ)
function toggleMode(mode) {
  currentMode = mode;
  const btnFile = document.getElementById("modeFile");
  const btnFolder = document.getElementById("modeFolder");
  const fileInp = document.getElementById("fileInput");
  const folderInp = document.getElementById("folderInput");

  if (mode === "file") {
    btnFile.classList.add("active");
    btnFolder.classList.remove("active");
    fileInp.style.display = "block";
    folderInp.style.display = "none";
    document.getElementById("inputLabel").textContent =
      "エクセルファイルを選択";
  } else {
    btnFolder.classList.add("active");
    btnFile.classList.remove("active");
    fileInp.style.display = "none";
    folderInp.style.display = "block";
    document.getElementById("inputLabel").textContent = "フォルダーを選択";
  }
  document.getElementById("selectionDisplay").textContent = "未選択";
}

// 選択したファイルの一覧を下の枠に表示する処理
function updateDisplay(e) {
  const files = Array.from(e.target.files).filter((f) =>
    f.name.endsWith(".xlsx"),
  );
  const display = document.getElementById("selectionDisplay");
  if (files.length === 0) {
    display.textContent = "未選択";
    return;
  }
  const list = files
    .map((f) => `<li>${f.webkitrelativepath || f.name}</li>`)
    .join("");
  display.innerHTML = `<strong> 選択したファイル (${files.length}件):</strong><ul class="selected-file-list">${list}</ul>`;
}

document.getElementById("fileInput").onchange = updateDisplay;
document.getElementById("folderInput").onchange = updateDisplay;

// アップロード処理とリアルタイムログ
document.getElementById("uploadForm").onsubmit = async (e) => {
  e.preventDefault();
  const activeInput =
    currentMode === "file"
      ? document.getElementById("fileInput")
      : document.getElementById("folderInput");
  const files = Array.from(activeInput.files).filter((f) =>
    f.name.endsWith(".xlsx"),
  );
  if (files.length === 0) return alert("ファイルを選んでください");

  const msg = document.getElementById("message");
  const progArea = document.getElementById("progressArea");
  const progGauge = document.getElementById("progressGauge");

  msg.style.display = "block";
  msg.innerHTML = "<strong> 処理結果:</strong>";
  progArea.style.display = "block";

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const logId = `log-${i}`;
    msg.innerHTML += `<div id="${logId}" class="log-entry status-waiting">⏳ ${file.name} - 送信開始...</div>`;
    msg.scrollTop = msg.scrollHeight;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("year", document.getElementById("year").value);
    formData.append("month", document.getElementById("month").value);

    const logElem = document.getElementById(logId);
    try {
      const res = await fetch(apiBaseUrl + "/upload", {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        logElem.className = "log-entry status-success";
        logElem.textContent = `✔ ${file.name} - 成功`;
      } else {
        const err = await res.json().catch(() => ({ detail: "不明なエラー" }));
        logElem.className = "log-entry status-error";
        logElem.textContent = `✘ ${file.name} - 失敗 (${err.detail})`;
      }
    } catch (err) {
      logElem.className = "log-entry status-error";
      logElem.textContent = `✘ ${file.name} - 接続エラー`;
    }

    // 進捗バーと件数表示の更新
    const percent = Math.round(((i + 1) / files.length) * 100);
    progGauge.style.width = percent + "%";
    document.getElementById("progressPercent").textContent = percent + "%";
    document.getElementById("progressCount").textContent =
      `${i + 1} / ${files.length}`;
  }
};

// 検索処理
async function searchInvoices(type, val = null) {
  let url = "";
  if (type === "month") {
    url = `${apiBaseUrl}/search/month?year=${document.getElementById("searchYear").value}&month=${document.getElementById("searchMonth").value}`;
  } else if (type === "customer") {
    const name = document.getElementById("searchName").value;
    if (!name) return alert("氏名を入力");
    url = `${apiBaseUrl}/search/customer?name=${encodeURIComponent(name)}`;
  } else if (type === "id") {
    url = `${apiBaseUrl}/search/customer_id?customer_id=${val}`;
  }

  const tbody = document.getElementById("resultTable");
  tbody.innerHTML =
    '<tr><td colspan="7" style="text-align:center;">検索中...</td></tr>';

  try {
    const res = await fetch(url);
    const data = await res.json();
    tbody.innerHTML = "";
    if (!data.results || data.results.length === 0) {
      tbody.innerHTML =
        '<tr><td colspan="7" style="text-align:center;">該当なし</td></tr>';
      return;
    }
    data.results.forEach((item) => {
      const tr = document.createElement("tr");

      tr.id = `row-${item.invoice_id}`;

      tr.innerHTML = `
          <td><a class="id-link" onclick="searchInvoices('id', '${item.customer_id}')">${item.customer_id.substring(0, 8)}</a></td>
          <td>${item.invoice_month}</td>
          <td><b>${item.customer_name}</b></td>
          <td class="address-cell">${item.address || "-"}</td>
          <td class="phone-cell">${item.phone || "-"}</td>
          <td style="text-align: right;">${item.total_amount.toLocaleString()}円</td>
          <td>
            <div style="display: flex; gap: 4px;">
              <a href="${apiBaseUrl}/download?s3_path=${encodeURIComponent(item.s3_path)}" target="_blank">
               <button class="btn-save">保存</button>
              </a>
              <button class="button" onclick="enableEdit('${item.invoice_id}', '${item.address || ""}', '${item.phone || ""}')
              " style="background: #f39c12; colar: white; border:none; padding:4px 8px; border-radius]4px; cursor:pointer; font-size:11px;">編集</button>
            </div>
          </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    alert("エラーが発生しました");
  }
}

// 編集を有効にする
function enableEdit(invoiceId, currentAddress, currentPhone) {
  // ボタンが押された行（tr）を特定
  const row = document.getElementById(`row-${invoiceId}`);

  // その行の中から、住所と電話番号のセルを探す
  const addressCell = row.querySelector(".address-cell");
  const phoneCell = row.querySelector(".phone-cell");

  // 一番右端の「操作ボタン（保存・編集）」が入っているセル（7番目のセル）を探す
  const actionCell = row.cells[6];

  // 【住所と電話番号】のセルの中身を、文字から「入力ボックス」に変形
  addressCell.innerHTML = `<input type="text" id="edit-address-${invoiceId}" value="${currentAddress}" style="width:100%; height:30px; padding:4px;">`;
  phoneCell.innerHTML = `<input type="text" id="edit-phone-${invoiceId}" value="${currentPhone}" style="width:100%; height:30px; padding:4px;">`;

  // 【ボタン】を「確定」と「取消」に変更
  actionCell.innerHTML = `
    <div style="display: flex; gap: 4px;">
      <button type="button" onclick="saveEdit('${invoiceId}')" style="background:#2ecc71; color:white; border:none; padding:4px 8px; border-radius:4px; cursor:pointer; font-size:11px;">確定</button>
      <button type="button" onclick="searchInvoices('month')" style="background:#95a5a6; color:white; border:none; padding:4px 8px; border-radius:4px; cursor:pointer; font-size:11px;">取消</button>
    </div>
  `;
}

// 編集内容を保存
async function saveEdit(invoiceId) {
  // 画面の入力欄から、新しく打ち込まれた住所と電話番号を読み取る
  const newAddress = document.getElementById(`edit-address-${invoiceId}`).value;
  const newPhone = document.getElementById(`edit-phone-${invoiceId}`).value;

  try {
    // APIにデータを送るためのリクエストを作成して送信
    const res = await fetch(apiBaseUrl + "/update-customer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        invoice_id: invoiceId,
        address: newAddress,
        phone: newPhone,
      }),
    });

    // サーバーから「200 OK」が返ってきたら、画面をリフレッシュ
    if (res.ok) {
      alert("変更を保存しました");
      // 年月検索をもう一度実行して、画面を最新の表示に戻す
      searchInvoices("month");
    } else {
      alert("保存に失敗しました");
    }
  } catch (err) {
    alert("通信エラーが発生しました");
  }
}
