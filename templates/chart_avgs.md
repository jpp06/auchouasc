type: line
labels: ["{labels}"]
spanGaps: true
beginAtZero: true
series:
  - title: harmonic
    data: [{harmonics}]
    backgroundColor: 'rgba(34, 197, 94, 0.2)'
    borderColor: 'rgba(34, 197, 94, 1)'
  - title: median
    data: [{medians}]
    backgroundColor: 'rgba(59, 130, 246, 0.2)'
    borderColor: 'rgba(59, 130, 246, 1)'
  - title: median_grouped
    data: [{medians_groupe}]
    backgroundColor: 'rgba(147, 51, 234, 0.2)'
    borderColor: 'rgba(147, 51, 234, 1)'
  - title: median_low
    data: [{medians_low}]
    backgroundColor: 'rgba(59, 130, 246, 0.2)'
    borderColor: 'rgb(246, 137, 59)'
  - title: mean
    data: [{means}]
    backgroundColor: 'rgba(147, 51, 234, 0.2)'
    borderColor: 'rgb(234, 194, 51)'
yMin: 0
