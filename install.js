const path = require('path')

module.exports = {
  run: [{
    method: "shell.run",
    params: {
      message: [
        "python -m venv env",
        "env/Scripts/python -m pip install --upgrade pip",
        "env/Scripts/pip install gradio requests"
      ]
    }
  }, {
    method: "fs.mkdir",
    params: {
      path: "recordings"
    }
  }, {
    method: "notify",
    params: {
      html: "Installation terminée! Vous pouvez maintenant lancer l'application."
    }
  }, {
    method: "browser.open",
    params: {
      uri: "launch.js"
    }
  }]
}
