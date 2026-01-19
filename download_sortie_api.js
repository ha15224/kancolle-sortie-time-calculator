function getReplays(n) {
    let replays = [];
    let dataInput = CONVERT.uiToSimInput(COMMON.UI_MAIN);
    for (let i=0; i<n; i++) {
        let dataReplay = CONVERT.uiToReplay(COMMON.UI_MAIN);
        SIM.runReplay(dataInput,dataReplay,true);
        replays.push(dataReplay);
    }
    return replays;
}

const replays = getReplays(10000);  // or 100

(function() {
  const json = JSON.stringify(replays, null, 2);
  const blob = new Blob([json], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "kancolle_replays.json";
  a.click();
  URL.revokeObjectURL(url);
})();