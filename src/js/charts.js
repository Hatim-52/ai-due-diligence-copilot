let revenueChartInstance = null;
let leverageChartInstance = null;

// Destroys existing chart instances to avoid overlap bugs
export function destroyCharts() {
  if (revenueChartInstance) {
    revenueChartInstance.destroy();
    revenueChartInstance = null;
  }
  if (leverageChartInstance) {
    leverageChartInstance.destroy();
    leverageChartInstance = null;
  }
}

// Configures and renders financial charts using Chart.js
export function renderFinancialCharts(revenueCanvasId, leverageCanvasId, companyData) {
  if (!window.Chart) {
    console.warn("Chart.js is not loaded. Skipping chart rendering.");
    return;
  }

  destroyCharts();

  const revCtx = document.getElementById(revenueCanvasId).getContext('2d');
  const levCtx = document.getElementById(leverageCanvasId).getContext('2d');

  const years = companyData.metrics.years;
  const revenue = companyData.metrics.revenue;
  const cash = companyData.metrics.cash;
  const ebitda = companyData.metrics.ebitda;
  const debt = companyData.metrics.debt;

  // Chart Global Defaults for Light Editorial theme
  window.Chart.defaults.color = '#475569';
  window.Chart.defaults.font.family = "'Outfit', 'Inter', sans-serif";

  const gridOptions = {
    color: 'rgba(15, 23, 42, 0.06)',
    drawTicks: false
  };

  // 1. Revenue & Cash Chart (Bar)
  const revGradient = revCtx.createLinearGradient(0, 0, 0, 300);
  revGradient.addColorStop(0, 'rgba(16, 185, 129, 0.85)');
  revGradient.addColorStop(1, 'rgba(16, 185, 129, 0.2)');

  const cashGradient = revCtx.createLinearGradient(0, 0, 0, 300);
  cashGradient.addColorStop(0, 'rgba(37, 99, 235, 0.85)');
  cashGradient.addColorStop(1, 'rgba(37, 99, 235, 0.2)');

  revenueChartInstance = new window.Chart(revCtx, {
    type: 'bar',
    data: {
      labels: years,
      datasets: [
        {
          label: 'Revenue ($M)',
          data: revenue,
          backgroundColor: revGradient,
          borderColor: '#059669',
          borderWidth: 1.5,
          borderRadius: 8,
          barPercentage: 0.6,
          categoryPercentage: 0.6
        },
        {
          label: 'Cash Reserves ($M)',
          data: cash,
          backgroundColor: cashGradient,
          borderColor: '#2563eb',
          borderWidth: 1.5,
          borderRadius: 8,
          barPercentage: 0.6,
          categoryPercentage: 0.6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: { boxWidth: 12, padding: 15, color: '#334155' }
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.92)',
          titleColor: '#f8fafc',
          bodyColor: '#e2e8f0',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          padding: 10,
          displayColors: true
        }
      },
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: gridOptions,
          ticks: {
            callback: value => `$${value}M`
          }
        }
      }
    }
  });

// 2. EBITDA & Debt Chart (Line/Area)
const ebitdaGradient = levCtx.createLinearGradient(0, 0, 0, 300);
ebitdaGradient.addColorStop(0, 'rgba(124, 58, 237, 0.25)');
ebitdaGradient.addColorStop(1, 'rgba(124, 58, 237, 0.02)');

const debtGradient = levCtx.createLinearGradient(0, 0, 0, 300);
debtGradient.addColorStop(0, 'rgba(225, 29, 72, 0.25)');
debtGradient.addColorStop(1, 'rgba(225, 29, 72, 0.02)');

leverageChartInstance = new window.Chart(levCtx, {
  type: 'line',
  data: {
    labels: years,
    datasets: [
      {
        label: 'EBITDA ($M)',
        data: ebitda,
        fill: true,
        backgroundColor: ebitdaGradient,
        borderColor: '#7c3aed',
        borderWidth: 2.5,
        tension: 0.35,
        pointBackgroundColor: '#7c3aed',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      },
      {
        label: 'Total Outstanding Debt ($M)',
        data: debt,
        fill: true,
        backgroundColor: debtGradient,
        borderColor: '#e11d48',
        borderWidth: 2.5,
        tension: 0.35,
        pointBackgroundColor: '#e11d48',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: { boxWidth: 12, padding: 15, color: '#334155' }
      },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.92)',
        titleColor: '#f8fafc',
        bodyColor: '#e2e8f0',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        padding: 10,
        displayColors: true
      }
    },
    scales: {
      x: { grid: { display: false } },
      y: {
        grid: gridOptions,
        ticks: {
          callback: value => `$${value}M`
        }
      }
    }
  }
});
}
