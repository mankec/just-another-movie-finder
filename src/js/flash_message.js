import Alpine from 'alpinejs';

export function showFlashMessage(flashMessageHTML) {
  const flashMessageContainer = document.querySelector("#flash-message-container")

  flashMessageContainer.innerHTML = flashMessageHTML
}

Alpine.magic('showFlashMessage', () => showFlashMessage);
