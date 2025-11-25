type: line
labels: ["{labels}"]
spanGaps: true
beginAtZero: true
series:
  - title: Quantité TSM
    data: [{tsm_quantities}]
    backgroundColor: 'rgba(59, 130, 246, 0.2)'
    borderColor: 'rgba(59, 130, 246, 1)'
  - title: Quantité AHS
    data: [{ahs_quantities}]
    backgroundColor: 'rgba(59, 130, 246, 0.2)'
    borderColor: 'rgb(246, 181, 59)'
yMin: 0
