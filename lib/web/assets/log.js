(function() {
  function http(url, result, error) {
    var req = new XMLHttpRequest();
    req.open("GET", url);
    req.send();
  
    req.onreadystatechange = function() {
      if (req.readyState === 4) {
        if (req.status === 200) {
          result(JSON.parse(req.responseText));
        } else {
          error(req.status, req.responseText);
        }
      }
    };
  }

  function iter(arr, func) {
    for (i = 0, size = arr.length; i < size; i++) {
      func(arr[i]);
    }
  }

  function createLineEl(text) {
    var el = document.createElement("div");
    el.className = "line";
    el.textContent = text;

    if (/error/gi.test(text)) {
      el.className += " error";
    } else if (/success/gi.test(text)) {
      el.className += " success"; 
    } else {
      el.className += " info";
    }

    return el;
  }

  function addLine(text) {
    var el = createLineEl(text);

    log.appendChild(el);

    scrollLogDown();
  }

  function scrollLogDown() {
    log.scrollTop = log.scrollHeight;
  }

  var lastLines = [];

  var log = document.querySelector(".log");

  var logId = window.logId;

  if (!logId) {
    alert("No log id found. Opened page manually?");
  }

  function loadLastLines() {
    http("/api/read-log/" + logId, function(result) {
      // console.log("Read last lines!");
      // console.log(result);
  
      iter(result, function(text) {
        if (lastLines.indexOf(text) === -1) {
          addLine(text);
          lastLines.push(text);
        }
      });

      setTimeout(loadLastLines, 1000);
    }, function(status, text) {
      alert("Unfortunately there was error accessing log file data from api")
      console.log("ERROR READING FILE");
    });
  }

  loadLastLines();
})();