module.exports = {
  title: "API Controller",
  description: "Contrôleur d'API avec interface Gradio permettant d'exécuter des commandes API préenregistrées",
  icon: "🎮",
  menu: async (kernel) => {
    let installed = await kernel.exists(__dirname, "env")
    if (installed) {
      return [{
        html: "Lancer API Controller",
        href: "launch.js"
      }, {
        html: "Réinstaller",
        href: "install.js"
      }]
    } else {
      return [{
        html: "Installer",
        href: "install.js"
      }]
    }
  }
}
