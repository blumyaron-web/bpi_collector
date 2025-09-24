let chart = null;

function fmtTime(iso) {
  // Convert UTC ISO string to local time
  // Explicitly convert UTC ISO string to Date object
  const d = new Date(iso);
  
  // Force browser to use the system's timezone
  const options = { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: false, // Use 24-hour format
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone // Use the system timezone explicitly
  };
  
  return d.toLocaleTimeString([], options);
}

function fmtDateTime(iso) {
  // Convert UTC ISO string to local time with full date and time
  // Explicitly convert UTC ISO string to Date object
  const d = new Date(iso);
  
  // Force browser to use the system's timezone
  return d.toLocaleString([], {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false, // Use 24-hour format
    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone // Use the system timezone explicitly
  });
}

async function refresh() {
  try {
    const res = await fetch('/latest/data');
    const data = await res.json();
    // prepare times and detect pairs
    const times = data.map(s => fmtTime(s.ts));
    const pairs = (data[0] && data[0].prices) ? Object.keys(data[0].prices) : ['BTC-USD'];

    // build datasets per pair with terminal colors
    const datasets = pairs.map((pair) => ({
      label: pair,
      data: data.map(s => (s.prices ? s.prices[pair] : null)),
      borderColor: '#33ff33',
      backgroundColor: 'rgba(51, 255, 51, 0.1)',
      pointRadius: 2,
      borderWidth: 1,
      spanGaps: true,
      tension: 0.1
    }));

    // update chart
    if (!chart) {
      const ctx = document.getElementById('chart').getContext('2d');
      chart = new Chart(ctx, {
        type: 'line',
        data: { labels: times, datasets: datasets },
        options: {
          animation: false,
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              labels: {
                color: '#33ff33',
                font: {
                  family: 'Fira Code'
                }
              }
            }
          },
          scales: {
            x: {
              grid: {
                color: '#1a1a1a',
                borderColor: '#33ff33'
              },
              ticks: {
                maxRotation: 0,
                color: '#33ff33',
                font: {
                  family: 'Fira Code'
                }
              }
            },
            y: {
              grid: {
                color: '#1a1a1a',
                borderColor: '#33ff33'
              },
              ticks: {
                callback: v => v.toFixed(2),
                color: '#33ff33',
                font: {
                  family: 'Fira Code'
                }
              }
            }
          }
        }
      });
    } else {
      chart.data.labels = times;
      chart.data.datasets = datasets;
      chart.update('none');
    }

    // update sample table (show last 10) using DocumentFragment to minimize reflows
    const tbody = document.querySelector('#samples tbody');
    const frag = document.createDocumentFragment();
    // Table: first column is time, following columns are pairs
    const thead = document.querySelector('#samples thead tr');
    thead.innerHTML = '';
    const thTime = document.createElement('th'); thTime.textContent = 'time'; thead.appendChild(thTime);
    pairs.forEach(p => { const th = document.createElement('th'); th.textContent = p; thead.appendChild(th); });

    data.slice(-10).reverse().forEach(s => {
      const tr = document.createElement('tr');
      const ts = document.createElement('td'); 
      
      // Always display timestamps in local time
      ts.textContent = fmtDateTime(s.ts);
      ts.title = "Local time (converted from UTC)"; // Add tooltip to clarify
      
      tr.appendChild(ts);
      pairs.forEach(p => {
        const td = document.createElement('td');
        const v = s.prices ? s.prices[p] : null;
        td.textContent = v == null ? '—' : v.toFixed(2);
        tr.appendChild(td);
      });
      frag.appendChild(tr);
    });
    // replace tbody contents in one op
    tbody.innerHTML = '';
    tbody.appendChild(frag);

    // Find the first pair's data for gauge values
    const firstPair = pairs[0];
    const firstPairVals = data.map(s => (s.prices ? s.prices[firstPair] : null)).filter(v => v != null);
    const firstPairMin = firstPairVals.length ? Math.min(...firstPairVals) : null;
    const firstPairMax = firstPairVals.length ? Math.max(...firstPairVals) : null;
    
    // Update the gauge min/max values
    document.getElementById('gauge-min').textContent = firstPairMin == null ? '—' : `$${firstPairMin.toFixed(2)}`;
    document.getElementById('gauge-max').textContent = firstPairMax == null ? '—' : `$${firstPairMax.toFixed(2)}`;

    // Update sample count
    document.getElementById('sample-count').textContent = data.length.toString();

    document.getElementById('status').textContent = 'on';
  } catch (e) {
    console.warn('refresh failed', e);
    document.getElementById('status').textContent = 'error';
  }
}

setInterval(refresh, 1000);
refresh();
