document.addEventListener("DOMContentLoaded", function () {
  // Fetch stock data for chart
  fetch("/stock_chart")
    .then((response) => response.json())
    .then((data) => {
      const ctx = document.getElementById("stockChart").getContext("2d");
      new Chart(ctx, {
        type: "line",
        data: {
          labels: data.dates,
          datasets: [
            {
              label: "Stock Price",
              data: data.prices,
              borderColor: "rgba(75, 192, 192, 1)",
              borderWidth: 2,
              fill: false,
            },
          ],
        },
        options: {
          scales: {
            x: {
              display: true,
              title: {
                display: true,
                text: "Date",
              },
            },
            y: {
              display: true,
              title: {
                display: true,
                text: "Price (USD)",
              },
            },
          },
        },
      });
    })
    .catch((error) => console.error("Error fetching stock chart data:", error));

  // Fetch top 5 stocks for the table
  fetch("/top_stocks")
    .then((response) => response.json())
    .then((data) => {
      const topStocksTable = document.getElementById("topStocksTable");
      topStocksTable.innerHTML = ""; // Clear table before inserting

      for (const [ticker, stockData] of Object.entries(data)) {
        const row = document.createElement("tr");
        row.innerHTML = `
                    <td>${ticker}</td>
                    <td>${stockData.name}</td>
                    <td>$${stockData.price}</td>
                `;
        topStocksTable.appendChild(row);
      }
    })
    .catch((error) => console.error("Error fetching top stocks:", error));
});
