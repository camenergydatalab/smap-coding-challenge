// type YSelector = (x: [string, number, number]) -> number;
// this script rely on the global variable aggData and queryPath

const dataRetrieved = new CustomEvent("data-retrieved");

const setupPlot = (elem, ySelector) => {
  const replot = () => {
    const xs = []
    const ys = [];
    for (const row of aggData) {
      xs.push(row[0]);
      ys.push(ySelector(row));
    }
    Plotly.newPlot(elem, [{ x:xs, y:ys }], { margin: { t: 0 } });
  };
  addEventListener("data-retrieved", replot);
  replot();
};
(() => {
  const queryForm = document.getElementById("query-form");
  if (queryForm === null) {
    return;
  }
  queryForm.onsubmit = (e) => {
    e.preventDefault();
    const data = new FormData(e.target);
    const queries = new URLSearchParams();
    for (const [k, v] of data) {
      if (v.length > 0) {
        queries.set(k, v);
      }
    }
    fetch(queryPath + "?" + queries.toString()).then(r => {
      if (r.status !== 200) {
        // TODO: handle it
        return;
      }
      r.json().then(j => {
        aggData = j.data;
        dispatchEvent(dataRetrieved);
      });
    });
  };
})();
