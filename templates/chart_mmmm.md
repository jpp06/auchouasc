type: line
labels: ["{labels}"]
spanGaps: true
beginAtZero: true
series:
  - title: min
    data: [{mins}]
    backgroundColor: 'rgba(34, 197, 94, 0.2)'
    borderColor: 'rgba(34, 197, 94, 1)'
  - title: median
    data: [{medians}]
    backgroundColor: 'rgba(59, 130, 246, 0.2)'
    borderColor: 'rgba(59, 130, 246, 1)'
  - title: Verstappen
    data: [{maxs}]
    backgroundColor: 'rgba(147, 51, 234, 0.2)'
    borderColor: 'rgba(147, 51, 234, 1)'
  - title: mean
    data: [{means}]
    backgroundColor: 'rgba(147, 51, 234, 0.2)'
    borderColor: 'rgb(234, 194, 51)'
yMin: 0
