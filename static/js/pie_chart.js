var statuses = ['Верно', 'Неверно', 'Не пройдено'];
var data = JSON.parse(document.getElementById("stats").textContent);
console.log(data);

var ctx = document.getElementById("myPieChart");
var myPieChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: statuses,
    datasets: [{
      data: data,
      backgroundColor: ['#28a645', '#da3545', '#343a40'],
      hoverBackgroundColor: ['#39b755', '#e84252', '#4b4d54'],
      hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: true
    },
    cutoutPercentage: 57,
  },
});
