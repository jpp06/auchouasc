type: line
labels: [{labels}]
spanGaps: true
beginAtZero: true
series:
  - title: Item Count
    data: [{item_counts}]
    backgroundColor: 'rgba(34, 197, 94, 0.2)'
    borderColor: 'rgba(34, 197, 94, 1)'
    pointRadius: 0
yMin: 0
yMax: {max_count}
options:
  scales:
    y:
      ticks:
        color: 'rgba(34, 197, 94, 1)'
