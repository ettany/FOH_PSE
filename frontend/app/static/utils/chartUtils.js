// chartUtils.js
export function drawBarChart(data) {
    console.log('Drawing chart with data:', data);  // Debugging log

    const margin = { top: 20, right: 30, bottom: 40, left: 40 };
    const width = 600 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Select the chart div and create the SVG container
    const svg = d3.select('#stocks-chart')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

    // Set up the x and y scales
    const x = d3.scaleBand()
        .domain(data.map(d => d.symbol))
        .range([0, width])
        .padding(0.1);

    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.price)])
        .nice()
        .range([height, 0]);

    // Append the x-axis to the SVG
    svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0, ${height})`)
        .call(d3.axisBottom(x));

    // Append the y-axis to the SVG
    svg.append('g')
        .attr('class', 'y-axis')
        .call(d3.axisLeft(y));

    // Draw bars for each stock
    svg.selectAll('.bar')
        .data(data)
        .enter().append('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.symbol))
        .attr('y', d => y(d.price))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y(d.price))
        .attr('fill', 'steelblue');

    console.log('Chart drawn successfully');
}
export function drawLineChart(data) {
    console.log('Drawing line chart with data:', data);  // Debugging log

    const margin = { top: 20, right: 30, bottom: 40, left: 40 };
    const width = 600 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select('#search-results-chart')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);

    const parseTime = d3.timeParse("%Y-%m-%d");
    data.forEach(d => {
        d.date = parseTime(d.date);
        d.price = +d.price; // Convert price to number
    });

    const x = d3.scaleTime()
        .domain(d3.extent(data, d => d.date))
        .range([0, width]);

    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.price)])
        .nice()
        .range([height, 0]);

    svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', `translate(0, ${height})`)
        .call(d3.axisBottom(x));

    svg.append('g')
        .attr('class', 'y-axis')
        .call(d3.axisLeft(y));

    const line = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.price));

    svg.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', 'steelblue')
        .attr('stroke-width', 2)
        .attr('d', line);

    console.log('Line chart drawn successfully');
}