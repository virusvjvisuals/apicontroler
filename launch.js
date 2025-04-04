module.exports = {
  run: [{
    method: "shell.start",
    params: {
      commands: ["env/Scripts/python app.py"],
      pty: true
    }
  }, {
    method: "process.wait",
    params: {
      pattern: "Running on local URL:  http://(.*)"
    }
  }, {
    method: "browser.open",
    params: {
      uri: "http://{{process.wait.matches[0]}}"
    }
  }]
}
