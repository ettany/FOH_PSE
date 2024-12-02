// chartUtils.js
export function drawBarChart(data) {
  console.log("Drawing chart with data:", data); // Debugging log

  const margin = { top: 20, right: 30, bottom: 40, left: 40 };
  const width = 600 - margin.left - margin.right;
  const height = 400 - margin.top - margin.bottom;

  // Select the chart div and create the SVG container
  const svg = d3
    .select("#stocks-chart")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);

  // Set up the x and y scales
  const x = d3
    .scaleBand()
    .domain(data.map((d) => d.symbol))
    .range([0, width])
    .padding(0.1);

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(data, (d) => d.price)])
    .nice()
    .range([height, 0]);

  // Append the x-axis to the SVG
  svg
    .append("g")
    .attr("class", "x-axis")
    .attr("transform", `translate(0, ${height})`)
    .call(d3.axisBottom(x));

  // Append the y-axis to the SVG
  svg.append("g").attr("class", "y-axis").call(d3.axisLeft(y));

  // Draw bars for each stock
  svg
    .selectAll(".bar")
    .data(data)
    .enter()
    .append("rect")
    .attr("class", "bar")
    .attr("x", (d) => x(d.symbol))
    .attr("y", (d) => y(d.price))
    .attr("width", x.bandwidth())
    .attr("height", (d) => height - y(d.price))
    .attr("fill", "steelblue");

  console.log("Chart drawn successfully");
}
export function drawLineChart(data) {
  console.log("Drawing line chart with data:", data); // Debugging log

  const margin = { top: 20, right: 30, bottom: 40, left: 40 };
  const width = 600 - margin.left - margin.right;
  const height = 400 - margin.top - margin.bottom;

  const svg = d3
    .select("#search-results-chart")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);

  const parseTime = d3.timeParse("%Y-%m-%d");
  data.forEach((d) => {
    d.date = parseTime(d.date);
    d.price = +d.price; // Convert price to number
  });

  const x = d3
    .scaleTime()
    .domain(d3.extent(data, (d) => d.date))
    .range([0, width]);

  const y = d3
    .scaleLinear()
    .domain([0, d3.max(data, (d) => d.price)])
    .nice()
    .range([height, 0]);

  svg
    .append("g")
    .attr("class", "x-axis")
    .attr("transform", `translate(0, ${height})`)
    .call(d3.axisBottom(x));

  svg.append("g").attr("class", "y-axis").call(d3.axisLeft(y));

  const line = d3
    .line()
    .x((d) => x(d.date))
    .y((d) => y(d.price));

  svg
    .append("path")
    .datum(data)
    .attr("fill", "none")
    .attr("stroke", "steelblue")
    .attr("stroke-width", 2)
    .attr("d", line);

  console.log("Line chart drawn successfully");
}
// Function to draw scatter plot the D3 chart with new data
export function drawScatterPlotChart(data) {
  const margin = { top: 20, right: 30, bottom: 40, left: 60 };
  const width = 600 - margin.left - margin.right;
  const height = 400 - margin.top - margin.bottom;

  // Select the SVG container and group element
  const svg = d3.select("#stocks-chart svg g");

  // Calculate padding for domain adjustments
  const xPadding =
    (d3.max(data, (d) => d.change) - d3.min(data, (d) => d.change)) * 0.1 || 1; // Percentage padding
  const yPadding =
    (d3.max(data, (d) => d.profit) - d3.min(data, (d) => d.profit)) * 0.1 || 1; // Profit padding

  // Define scales with domains centered around 0
  const x = d3
    .scaleLinear()
    .domain([
      Math.min(0, d3.min(data, (d) => d.change) - xPadding),
      Math.max(0, d3.max(data, (d) => d.change) + xPadding),
    ])
    .range([0, width]);

  const y = d3
    .scaleLinear()
    .domain([
      Math.min(0, d3.min(data, (d) => d.profit) - yPadding),
      Math.max(0, d3.max(data, (d) => d.profit) + yPadding),
    ])
    .range([height, 0]);

  // Update x-axis and y-axis
  svg
    .select(".x-axis")
    .attr("transform", `translate(0,${y(0)})`) // Place x-axis at y=0
    .transition()
    .duration(750)
    .call(d3.axisBottom(x).tickFormat((d) => `${d}%`)); // Format ticks as percentage

  svg
    .select(".y-axis")
    .attr("transform", `translate(${x(0)},0)`) // Place y-axis at x=0
    .transition()
    .duration(750)
    .call(d3.axisLeft(y).tickFormat((d) => `$${d.toFixed(2)}`)); // Format ticks as currency

  // Add x-axis label
  svg.select(".x-axis-label").remove(); // Remove old label if any
  svg
    .append("text")
    .attr("class", "x-axis-label")
    .attr("x", width / 2)
    .attr("y", height + margin.bottom - 10)
    .attr("text-anchor", "middle")
    .text("Change (%)");

  // Add y-axis label
  svg.select(".y-axis-label").remove(); // Remove old label if any
  svg
    .append("text")
    .attr("class", "y-axis-label")
    .attr("x", -height / 2)
    .attr("y", -margin.left + 15)
    .attr("text-anchor", "middle")
    .attr("transform", "rotate(-90)")
    .text("Profit ($)");

  // Bind data and update dots
  const dots = svg.selectAll(".dot").data(data);

  // Enter new dots
  dots
    .enter()
    .append("circle")
    .attr("class", "dot")
    .attr("r", 6)
    .merge(dots) // Update existing dots
    .transition()
    .duration(750)
    .attr("cx", (d) => x(d.change))
    .attr("cy", (d) => y(d.profit))
    .attr("fill", (d) => (d.profit >= 0 ? "steelblue" : "red"));

  // Remove old dots
  dots.exit().remove();
}
