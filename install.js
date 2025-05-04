module.exports = {
  run: [{
    method: "shell.run",
    params: {
      venv: "env",
      message: [
        "python -m pip install --upgrade pip",
        "uv pip install gradio requests"
      ]
    }
  }, {
    method: "shell.run",
    params: {
      message: "mkdir recordings"
    }
  }, {
    method: "notify",
    params: {
      html: "Installation terminée! Vous pouvez maintenant lancer l'application."
    }
  }]
}