console.log('5555', 5555);

const renderChart = (data, labels) => {
  const ctx = document.getElementById('myChart').getContext('2d');

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        label: 'Last six months expenses',
        data: data,
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

const getChartData = () => {
  console.log('fetching');
  
  // beforeSend equivalent
  console.log('before sending fetch request');

  fetch('/expense-category')
    .then((res) => res.json())
    .then((results) => {
      console.log('results', results);
      const category_data = results.expense_category_data;
      const labels = Object.keys(category_data);
      const data = Object.values(category_data);
      renderChart(data, labels);
    })
    .catch((error) => {
      console.error('Error fetching the data:', error);
    });
}

document.addEventListener('DOMContentLoaded', getChartData);
