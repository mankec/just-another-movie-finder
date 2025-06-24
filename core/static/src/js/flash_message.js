import Alpine from 'alpinejs';

export function showFlashMessage(flashMessageHTML, message) {
  debugger
  const flashMessageContainer = document.querySelector("#flash-message-container")
  const html = flashMessageHTML.replace("__MESSAGE__", message)
  flashMessageContainer.innerHTML = html
}

Alpine.magic('showFlashMessage', () => showFlashMessage);
