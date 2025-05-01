const path = require('path')
module.exports = {
  version: "3.0",
  title: "API Controller",
  description: "Contrôleur d'API avec interface Gradio permettant d'exécuter des commandes API préenregistrées",
  icon: "icon.png",
  menu: async (kernel, info) => {
    let installed = info.exists("env")
    let running = {
      install: info.running("install.js"),
      start: info.running("start.js")
    }
    if (running.install) {
      return [{
        default: true,
        icon: "fa-solid fa-plug",
        text: "Installing",
        href: "install.js",
      }]
    } else if (installed) {
      if (running.start) {
        let local = info.local("start.js")
        if (local && local.url) {
          return [{
            default: true,
            icon: "fa-solid fa-rocket",
            text: "Open Web UI",
            href: local.url,
          }, {
            icon: 'fa-solid fa-terminal',
            text: "Terminal",
            href: "start.js",
          }]
        } else {
          return [{
            default: true,
            icon: 'fa-solid fa-terminal',
            text: "Terminal",
            href: "start.js",
          }]
        }
      } else {
        return [{
          default: true,
          icon: "fa-solid fa-power-off",
          text: "Lancer API Controller",
          href: "start.js",
        }, {
          icon: "fa-solid fa-plug",
          text: "Réinstaller",
          href: "install.js",
        }]
      }
    } else {
      return [{
        default: true,
        html: "Installer",
        href: "install.js"
      }]
    }
  }
}
