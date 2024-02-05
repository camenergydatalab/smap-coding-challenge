// type YSelector = (x: [string, number, number]) -> number;
// this script rely on the global variable aggData
const setupPlot = (elem, ySelector) => {
  const xs = []
  const ys = [];
  for (const row of aggData) {
    xs.push(row[0]);
    ys.push(ySelector(row));
  }
  Plotly.newPlot(elem, [{ x:xs, y:ys }], { margin: { t: 0 } });
};
