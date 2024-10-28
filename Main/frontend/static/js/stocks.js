function updateStocks() {
  fetch("/stocks_data")
    .then((response) => response.json())
    .then((data) => {
      const tableBody = document.querySelector("#stock-table-body");
      tableBody.innerHTML = "";

      let count = 0;
      for (const [ticker, stockData] of Object.entries(data)) {
        if (count >= 5) break;
        const row = `
                  <tr>
                      <td>${ticker}</td>
                      <td>${stockData.name}</td>
                      <td>$${stockData.price}</td>
                  </tr>
              `;
        tableBody.innerHTML += row;
        count++;
      }
    })
    .catch((error) => console.error("Error fetching stock data:", error));
}

// update every 10s
setInterval(updateStocks, 10000);

// Load stocks when page is loaded
window.onload = updateStocks;
