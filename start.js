module.exports = {
  daemon: true,
  run: [{
    method: "shell.run",
    params: {
      venv: "env",
      message: "python app.py",
      on: [{
        "event": "/http:\/\/\\S+/",
        "done": true
      }]
    }
  }, {
    method: "local.set",
    params: {
      url: "{{input.event[0]}}"
    }
  }]
}
